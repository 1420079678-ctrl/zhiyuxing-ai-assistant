from __future__ import annotations

import asyncio
import json
from typing import AsyncGenerator

from fastapi import HTTPException

from services.knowledge import search_knowledge
from services.safety import assess_risk, high_risk_reply
from services.storage import ensure_session, recent_messages, save_turn
from services.telemetry import telemetry

from backend.chat_logic import (
    build_demo_reply,
    build_messages,
    knowledge_sources,
    normalize_response_style,
    to_knowledge_models,
    to_safety_info,
)
from backend.config import STYLE_LABELS
from backend.runtime import build_client, build_completion_kwargs, resolve_model_target
from backend.schemas import ChatRequest, ChatResponse


def handle_chat_request(req: ChatRequest) -> ChatResponse:
    target = resolve_model_target(req.model_target)
    scenario = req.scenario or "campus"
    style = normalize_response_style(req.response_style, req.system_hint)
    session_id = ensure_session(req.session_id, req.message)
    conversation_history = recent_messages(session_id, limit=6)
    knowledge_hits = search_knowledge(req.message, limit=3)
    safety_assessment = assess_risk(req.message)

    telemetry.record_guardrail(safety_assessment.level)

    if safety_assessment.level == "high":
        reply = high_risk_reply()
        assistant_message_id = save_turn(
            session_id,
            req.message,
            reply,
            response_style=style,
            provider_name="Safety Guardrail",
            model_name="high-risk-template",
            mode="guardrail",
            risk_level=safety_assessment.level,
            knowledge_sources=knowledge_sources(knowledge_hits),
        )
        telemetry.record_chat(
            mode="guardrail",
            provider="Safety Guardrail",
            model="high-risk-template",
            scenario=scenario,
            is_stream=False,
        )
        return ChatResponse(
            reply=reply,
            note="检测到高风险表达，已优先切换到固定安全转介回复，而不是继续普通模型对话。",
            mode="guardrail",
            provider_name="Safety Guardrail",
            model_name="high-risk-template",
            response_style=style,
            session_id=session_id,
            assistant_message_id=assistant_message_id,
            memory_messages_used=len(conversation_history),
            knowledge_hits=to_knowledge_models(knowledge_hits),
            safety=to_safety_info(safety_assessment),
        )

    if target.mode == "demo":
        reply = build_demo_reply(
            req.message,
            req.system_hint,
            style,
            conversation_history=conversation_history,
            knowledge_hits=knowledge_hits,
            safety_assessment=safety_assessment,
        )
        assistant_message_id = save_turn(
            session_id,
            req.message,
            reply,
            response_style=style,
            provider_name=target.provider_name,
            model_name=target.model_name,
            mode=target.mode,
            risk_level=safety_assessment.level,
            knowledge_sources=knowledge_sources(knowledge_hits),
        )
        telemetry.record_chat(
            mode=target.mode,
            provider=target.provider_name,
            model=target.model_name,
            scenario=scenario,
            is_stream=False,
        )
        telemetry.record_tokens(len(req.message) + len(reply))
        knowledge_note = ""
        if knowledge_hits:
            knowledge_note = " 已结合本地知识库片段增强建议。"
        safety_note = ""
        if safety_assessment.level == "medium":
            safety_note = " 同时检测到需要额外关注的状态，回复里已补充线下支持提醒。"
        return ChatResponse(
            reply=reply,
            note=(
                f"当前为本地演示模式。已按“{STYLE_LABELS[style]}”返回演示回复；"
                f"本轮使用了 {len(conversation_history)} 条会话记忆。{knowledge_note}{safety_note}"
            ).strip(),
            mode=target.mode,
            provider_name=target.provider_name,
            model_name=target.model_name,
            response_style=style,
            session_id=session_id,
            assistant_message_id=assistant_message_id,
            memory_messages_used=len(conversation_history),
            knowledge_hits=to_knowledge_models(knowledge_hits),
            safety=to_safety_info(safety_assessment),
        )

    try:
        client = build_client(target)
        completion = client.chat.completions.create(
            **build_completion_kwargs(
                build_messages(
                    req.message,
                    req.system_hint,
                    style,
                    conversation_history=conversation_history,
                    knowledge_hits=knowledge_hits,
                    safety_assessment=safety_assessment,
                    scenario=scenario,
                ),
                model_name=target.model_name,
            )
        )
        reply = completion.choices[0].message.content or "抱歉，我这次没有成功生成回复。"
        assistant_message_id = save_turn(
            session_id,
            req.message,
            reply,
            response_style=style,
            provider_name=target.provider_name,
            model_name=target.model_name,
            mode=target.mode,
            risk_level=safety_assessment.level,
            knowledge_sources=knowledge_sources(knowledge_hits),
        )
        telemetry.record_chat(
            mode=target.mode,
            provider=target.provider_name,
            model=target.model_name,
            scenario=scenario,
            is_stream=False,
        )
        telemetry.record_tokens(len(req.message) + len(reply))
        note = (
            f"当前为模型调用模式。回复由 {target.provider_name} / {target.model_name} 生成，"
            f"风格为“{STYLE_LABELS[style]}”，使用了 {len(conversation_history)} 条会话记忆。"
        )
        if knowledge_hits:
            note += f" 已结合 {len(knowledge_hits)} 条知识库片段。"
        if safety_assessment.level == "medium":
            note += " 当前表达需要额外关注，系统已加强安全提醒。"
        return ChatResponse(
            reply=reply,
            note=note,
            mode=target.mode,
            provider_name=target.provider_name,
            model_name=target.model_name,
            response_style=style,
            session_id=session_id,
            assistant_message_id=assistant_message_id,
            memory_messages_used=len(conversation_history),
            knowledge_hits=to_knowledge_models(knowledge_hits),
            safety=to_safety_info(safety_assessment),
        )
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"调用模型失败：{exc}") from exc


async def handle_chat_stream(req: ChatRequest) -> AsyncGenerator[str, None]:
    """Server-Sent Events (SSE) streaming chat generator."""
    target = resolve_model_target(req.model_target)
    scenario = req.scenario or "campus"
    style = normalize_response_style(req.response_style, req.system_hint)
    session_id = ensure_session(req.session_id, req.message)
    conversation_history = recent_messages(session_id, limit=6)
    knowledge_hits = search_knowledge(req.message, limit=3)
    safety_assessment = assess_risk(req.message)

    telemetry.record_guardrail(safety_assessment.level)

    # 1. Send initial start event with metadata
    start_payload = {
        "event": "start",
        "session_id": session_id,
        "mode": target.mode,
        "provider_name": target.provider_name,
        "model_name": target.model_name,
        "response_style": style,
        "memory_messages_used": len(conversation_history),
        "knowledge_hits": [hit.model_dump() for hit in to_knowledge_models(knowledge_hits)],
        "safety": to_safety_info(safety_assessment).model_dump(),
    }
    yield f"data: {json.dumps(start_payload, ensure_ascii=False)}\n\n"

    # 2. Check high-risk safety guardrail
    if safety_assessment.level == "high":
        reply = high_risk_reply()
        assistant_message_id = save_turn(
            session_id,
            req.message,
            reply,
            response_style=style,
            provider_name="Safety Guardrail",
            model_name="high-risk-template",
            mode="guardrail",
            risk_level=safety_assessment.level,
            knowledge_sources=knowledge_sources(knowledge_hits),
        )
        telemetry.record_chat(
            mode="guardrail",
            provider="Safety Guardrail",
            model="high-risk-template",
            scenario=scenario,
            is_stream=True,
        )
        yield f"data: {json.dumps({'event': 'delta', 'content': reply}, ensure_ascii=False)}\n\n"
        done_payload = {
            "event": "done",
            "reply": reply,
            "session_id": session_id,
            "assistant_message_id": assistant_message_id,
            "note": "检测到高风险表达，已优先切换到固定安全转介回复。",
        }
        yield f"data: {json.dumps(done_payload, ensure_ascii=False)}\n\n"
        return

    # 3. Demo mode streaming: smooth word-by-word emission
    if target.mode == "demo":
        reply = build_demo_reply(
            req.message,
            req.system_hint,
            style,
            conversation_history=conversation_history,
            knowledge_hits=knowledge_hits,
            safety_assessment=safety_assessment,
        )
        # Stream chunks with small delays to emulate real-time typing
        chunk_size = 4
        for idx in range(0, len(reply), chunk_size):
            chunk = reply[idx : idx + chunk_size]
            yield f"data: {json.dumps({'event': 'delta', 'content': chunk}, ensure_ascii=False)}\n\n"
            await asyncio.sleep(0.012)

        assistant_message_id = save_turn(
            session_id,
            req.message,
            reply,
            response_style=style,
            provider_name=target.provider_name,
            model_name=target.model_name,
            mode=target.mode,
            risk_level=safety_assessment.level,
            knowledge_sources=knowledge_sources(knowledge_hits),
        )
        telemetry.record_chat(
            mode=target.mode,
            provider=target.provider_name,
            model=target.model_name,
            scenario=scenario,
            is_stream=True,
        )
        telemetry.record_tokens(len(req.message) + len(reply))
        done_payload = {
            "event": "done",
            "reply": reply,
            "session_id": session_id,
            "assistant_message_id": assistant_message_id,
            "note": f"当前为本地演示模式。已按“{STYLE_LABELS[style]}”流式生成回复。",
        }
        yield f"data: {json.dumps(done_payload, ensure_ascii=False)}\n\n"
        return

    # 4. Real OpenAI / DeepSeek / OrcaRouter streaming mode
    accumulated_chunks: list[str] = []
    try:
        client = build_client(target)
        stream_response = client.chat.completions.create(
            **build_completion_kwargs(
                build_messages(
                    req.message,
                    req.system_hint,
                    style,
                    conversation_history=conversation_history,
                    knowledge_hits=knowledge_hits,
                    safety_assessment=safety_assessment,
                    scenario=scenario,
                ),
                model_name=target.model_name,
            ),
            stream=True,
        )
        for chunk in stream_response:
            if chunk.choices and chunk.choices[0].delta and chunk.choices[0].delta.content:
                text_part = chunk.choices[0].delta.content
                accumulated_chunks.append(text_part)
                yield f"data: {json.dumps({'event': 'delta', 'content': text_part}, ensure_ascii=False)}\n\n"
                await asyncio.sleep(0)

        full_reply = "".join(accumulated_chunks) or "抱歉，我这次没有成功生成回复。"
        assistant_message_id = save_turn(
            session_id,
            req.message,
            full_reply,
            response_style=style,
            provider_name=target.provider_name,
            model_name=target.model_name,
            mode=target.mode,
            risk_level=safety_assessment.level,
            knowledge_sources=knowledge_sources(knowledge_hits),
        )
        telemetry.record_chat(
            mode=target.mode,
            provider=target.provider_name,
            model=target.model_name,
            scenario=scenario,
            is_stream=True,
        )
        telemetry.record_tokens(len(req.message) + len(full_reply))
        done_payload = {
            "event": "done",
            "reply": full_reply,
            "session_id": session_id,
            "assistant_message_id": assistant_message_id,
            "note": f"当前为模型调用模式。流式生成完毕，由 {target.provider_name} / {target.model_name} 提供支持。",
        }
        yield f"data: {json.dumps(done_payload, ensure_ascii=False)}\n\n"
    except Exception as exc:
        yield f"data: {json.dumps({'event': 'error', 'message': f'流式生成失败: {exc}'}, ensure_ascii=False)}\n\n"
