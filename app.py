from __future__ import annotations

import os
from typing import Optional

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from openai import OpenAI
from pydantic import BaseModel, Field

load_dotenv()

app = FastAPI(
    title="Zhiyuxing AI Assistant Demo API",
    description="面向大学生场景的 AI 心理支持与学习辅助最小可运行演示接口。",
    version="0.2.0",
)


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, description="用户输入")
    system_hint: Optional[str] = Field(default=None, description="可选的额外系统提示")


class ChatResponse(BaseModel):
    reply: str
    note: str


class ServiceInfo(BaseModel):
    name: str
    version: str
    description: str
    docs_url: str
    healthcheck: str


def build_client() -> OpenAI:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="缺少 OPENAI_API_KEY，请先配置 .env")

    base_url = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
    return OpenAI(api_key=api_key, base_url=base_url)


def build_messages(user_message: str, system_hint: Optional[str]) -> list[dict[str, str]]:
    system_prompt = (
        "你是一个面向大学生的 AI 心理支持与学习辅助助手。"
        "回答时保持温和、具体、不过度承诺，不将自己描述为专业心理医生。"
        "优先做三件事：识别情绪、给出可执行的小建议、必要时提醒寻求线下专业帮助。"
        "不要输出诊断结论，不要给出危险、自伤或伤人建议。"
    )
    if system_hint:
        system_prompt += "\n补充要求：" + system_hint

    return [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_message},
    ]


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "zhiyuxing-demo", "version": app.version}


@app.get("/", response_model=ServiceInfo)
def index() -> ServiceInfo:
    return ServiceInfo(
        name=app.title,
        version=app.version,
        description="作品集仓库中的最小可运行后端 Demo，用于展示项目方向与接口能力。",
        docs_url="/docs",
        healthcheck="/health",
    )


@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest) -> ChatResponse:
    try:
        client = build_client()
        model_name = os.getenv("MODEL_NAME", "gpt-4o-mini")
        completion = client.chat.completions.create(
            model=model_name,
            messages=build_messages(req.message, req.system_hint),
            temperature=0.7,
        )
        reply = completion.choices[0].message.content or "抱歉，我这次没有成功生成回复。"
        return ChatResponse(
            reply=reply,
            note="这是作品集仓库中的最小可运行 Demo，用于展示项目方向与接口能力。",
        )
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"调用模型失败：{exc}") from exc
