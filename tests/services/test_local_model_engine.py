"""Tests for local transformer engine, psychology corpus, and autonomous agent orchestration."""

import pytest
from services.corpus_loader import get_psychology_corpus
from services.transformer_engine import get_transformer_engine
from services.agent_automation import get_agent_orchestrator
from services.local_model_engine import get_local_model_engine


def test_psychology_corpus_loads_all_categories():
    corpus = get_psychology_corpus()
    stats = corpus.get_stats()
    assert stats["total_items"] >= 20
    assert "cbt_distortions" in stats["categories"]
    assert "somatic_and_behavioral_micro_actions" in stats["categories"]


def test_corpus_search_returns_relevant_results():
    corpus = get_psychology_corpus()
    results = corpus.search("考研 压力 焦虑", top_k=3)
    assert len(results) > 0
    assert any("academic" in r.get("category", "") or "cbt" in r.get("category", "") for r in results)


def test_transformer_engine_forward_and_telemetry():
    engine = get_transformer_engine()
    analysis = engine.analyze_text("最近准备面试很紧张，心跳好快")
    assert "vad_emotion" in analysis
    assert "svd_telemetry" in analysis
    assert analysis["token_count"] > 0
    vad = analysis["vad_emotion"]
    assert -1.0 <= vad["valence"] <= 1.0
    assert 0.0 <= vad["arousal"] <= 1.0


def test_autonomous_agent_orchestrator():
    orchestrator = get_agent_orchestrator()
    result = orchestrator.run("我总觉得领导对我要求太苛刻，每天加班很累")
    assert result.final_response
    assert len(result.steps) >= 4
    assert result.risk_level in {"low", "medium", "high", "crisis"}


def test_local_model_engine_contextual_matching():
    engine = get_local_model_engine()

    # 1. Tech query
    tech_res = engine.generate("local:transformer-medium", "什么是注意力机制？")
    assert "Attention" in tech_res["text"] or "注意力" in tech_res["text"]
    assert tech_res["model"] == "local:transformer-medium"

    # 2. Greeting query
    greeting_res = engine.generate("local:transformer-medium", "你好，你是谁？")
    assert "治愈星" in greeting_res["text"]

    # 3. Positive query
    pos_res = engine.generate("local:transformer-medium", "我今天考研过了，太开心了！")
    assert "品味" in pos_res["text"] or "欣喜" in pos_res["text"] or "开心" in pos_res["text"]

    # 4. Agent mode
    agent_res = engine.generate("local:autonomous-agent", "什么是注意力机制？")
    assert "智能体" in agent_res["text"]
    assert agent_res["model"] == "local:autonomous-agent"


@pytest.mark.anyio
async def test_local_model_engine_stream():
    engine = get_local_model_engine()
    chunks = []
    async for chunk in engine.generate_stream("local:transformer-medium", "压力好大睡不着"):
        chunks.append(chunk)
    assert len(chunks) > 0
    delta_texts = [c["content"] for c in chunks if c.get("type") == "delta"]
    assert len(delta_texts) > 0
    full_text = "".join(delta_texts)
    assert len(full_text) > 20
