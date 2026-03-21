import os
import sqlite3
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app import (
    STYLE_LABELS,
    app,
    build_completion_kwargs,
    build_configured_target,
    build_demo_reply,
    build_messages,
    configured_api_key_env,
    detect_demo_topic,
    evaluate_runtime_compatibility,
    list_model_options,
    normalize_response_style,
    resolve_model_target,
)


@pytest.fixture
def test_client(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> TestClient:
    monkeypatch.setenv("CHAT_DB_PATH", str(tmp_path / "zhiyuxing-test.db"))
    monkeypatch.setenv("KNOWLEDGE_UPLOAD_DIR", str(tmp_path / "knowledge_uploads"))
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("DEEPSEEK_API_KEY", raising=False)
    monkeypatch.delenv("DEMO_MODE", raising=False)

    with TestClient(app) as client:
        yield client


def test_root_serves_demo_page(test_client: TestClient) -> None:
    response = test_client.get("/")

    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "知愈星 AI Assistant" in response.text


def test_meta_returns_runtime_options(test_client: TestClient) -> None:
    response = test_client.get("/api/meta")

    assert response.status_code == 200
    payload = response.json()
    assert payload["demo_page"] == "/"
    assert payload["docs_url"] == "/docs"
    assert payload["deployment_note"] == "/project-docs/dingtalk-integration.md"
    assert payload["compatibility_url"] == "/api/compatibility"
    assert payload["model_doc"] == "/project-docs/model-integration.md"
    assert payload["persistence_enabled"] is True
    assert payload["knowledge_document_count"] >= 1
    assert payload["session_history_url"] == "/api/session/{session_id}"
    assert payload["feedback_url"] == "/api/feedback"
    assert payload["knowledge_search_url"].startswith("/api/knowledge/search")
    assert payload["knowledge_documents_url"] == "/api/knowledge/documents"
    assert payload["knowledge_upload_url"] == "/api/knowledge/documents"
    assert payload["available_models"]
    assert payload["available_styles"]


def test_health_exposes_service_version(test_client: TestClient) -> None:
    response = test_client.get("/health")

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ok"
    assert payload["version"] == app.version
    assert payload["persistence_enabled"] is True
    assert payload["knowledge_document_count"] >= 1
    assert "provider_name" in payload
    assert "model_name" in payload
    assert "api_key_env" in payload


def test_project_docs_are_exposed(test_client: TestClient) -> None:
    response = test_client.get("/project-docs/model-integration.md")

    assert response.status_code == 200
    assert "模型接入说明" in response.text


def test_build_messages_appends_system_hint_and_style() -> None:
    messages = build_messages("最近总拖延。", "给出 3 条具体建议", "structured")

    assert messages[0]["role"] == "system"
    assert "给出 3 条具体建议" in messages[0]["content"]
    assert STYLE_LABELS["structured"]
    assert messages[1]["content"] == "最近总拖延。"


def test_build_demo_reply_returns_structured_advice() -> None:
    reply = build_demo_reply("最近总拖延，学不进去。")

    assert "1." in reply
    assert "2." in reply
    assert "3." in reply


def test_build_demo_reply_respects_response_style() -> None:
    reply = build_demo_reply("最近总拖延，学不进去。", response_style="brief")

    assert "先做这 3 件事" in reply


def test_detect_demo_topic_distinguishes_common_scenarios() -> None:
    assert detect_demo_topic("我马上要面试了，特别紧张。") == "interview_anxiety"
    assert detect_demo_topic("期末考试快到了，我复习不进去。") == "exam_anxiety"
    assert detect_demo_topic("最近总失眠，白天也很累。") == "sleep_exhaustion"


def test_build_demo_reply_changes_with_question_topic() -> None:
    interview_reply = build_demo_reply("我最近实习面试很紧张，总怕答不上来。")
    future_reply = build_demo_reply("我对未来很迷茫，不知道以后该做什么。")

    assert "面试" in interview_reply
    assert "方向" in future_reply or "未来" in future_reply or "探索" in future_reply


def test_normalize_response_style_supports_hint_fallback() -> None:
    style = normalize_response_style(None, "更鼓励一点")

    assert style == "encouraging"


def test_chat_falls_back_to_demo_mode_without_api_key(test_client: TestClient) -> None:
    response = test_client.post(
        "/chat",
        json={
            "message": "这周压力很大，完全不想开始复习。",
            "model_target": "configured",
            "response_style": "warm",
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["mode"] == "demo"
    assert payload["provider_name"] == "Local Demo"
    assert payload["response_style"] == "warm"
    assert payload["session_id"].startswith("sess_")
    assert payload["assistant_message_id"] > 0


def test_chat_rejects_unavailable_model_target(
    test_client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.delenv("DEEPSEEK_API_KEY", raising=False)

    response = test_client.post(
        "/chat",
        json={
            "message": "我最近很焦虑。",
            "model_target": "deepseek-reasoner",
        },
    )

    assert response.status_code == 400
    assert "DEEPSEEK_API_KEY" in response.json()["detail"]


def test_knowledge_search_endpoint_returns_hits(test_client: TestClient) -> None:
    response = test_client.get("/api/knowledge/search", params={"q": "失眠"})

    assert response.status_code == 200
    payload = response.json()
    assert payload["query"] == "失眠"
    assert payload["total_hits"] >= 1
    assert payload["hits"][0]["source_path"].startswith("knowledge_base/")


def test_knowledge_documents_endpoint_supports_custom_documents(test_client: TestClient) -> None:
    create_response = test_client.post(
        "/api/knowledge/documents",
        json={
            "title": "校园求助渠道",
            "content": "如果用户提到长期崩溃、严重失眠或明显无助感，应明确建议联系学校心理中心、辅导员或校医院，并给出先联系一个现实中的人的行动建议。",
        },
    )

    assert create_response.status_code == 201
    create_payload = create_response.json()
    assert create_payload["status"] == "ok"
    assert create_payload["document"]["category"] == "custom"

    list_response = test_client.get("/api/knowledge/documents")
    assert list_response.status_code == 200
    list_payload = list_response.json()
    assert list_payload["total_documents"] >= 6
    assert any(item["document_id"] == create_payload["document"]["document_id"] for item in list_payload["documents"])

    search_response = test_client.get("/api/knowledge/search", params={"q": "心理中心"})
    assert search_response.status_code == 200
    search_payload = search_response.json()
    assert any("knowledge_uploads" in hit["source_path"] for hit in search_payload["hits"])


def test_chat_returns_memory_knowledge_and_safety_fields(test_client: TestClient) -> None:
    response = test_client.post(
        "/chat",
        json={
            "message": "最近总失眠，白天也很累。",
            "model_target": "configured",
            "response_style": "warm",
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["mode"] == "demo"
    assert payload["memory_messages_used"] == 0
    assert payload["knowledge_hits"]
    assert payload["safety"]["level"] == "medium"
    assert payload["safety"]["needs_human_support"] is True


def test_chat_uses_session_memory_and_exposes_history(test_client: TestClient) -> None:
    first = test_client.post(
        "/chat",
        json={
            "message": "最近总拖延，完全不想开始。",
            "model_target": "configured",
            "response_style": "balanced",
        },
    )
    first_payload = first.json()
    session_id = first_payload["session_id"]

    second = test_client.post(
        "/chat",
        json={
            "message": "而且我还担心考试复习会来不及。",
            "model_target": "configured",
            "session_id": session_id,
            "response_style": "structured",
        },
    )

    assert second.status_code == 200
    second_payload = second.json()
    assert second_payload["session_id"] == session_id
    assert second_payload["memory_messages_used"] == 2
    assert "延续你前面提到的" in second_payload["reply"]

    history_response = test_client.get(f"/api/session/{session_id}")
    assert history_response.status_code == 200
    history_payload = history_response.json()
    assert history_payload["total_messages"] == 4
    assert len(history_payload["messages"]) == 4
    assert history_payload["messages"][0]["role"] == "user"
    assert history_payload["messages"][-1]["role"] == "assistant"


def test_high_risk_message_uses_guardrail(test_client: TestClient) -> None:
    response = test_client.post(
        "/chat",
        json={
            "message": "我真的不想活了，想结束生命。",
            "model_target": "configured",
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["mode"] == "guardrail"
    assert payload["provider_name"] == "Safety Guardrail"
    assert payload["safety"]["level"] == "high"
    assert "请先做这 3 件事" in payload["reply"]


def test_feedback_endpoint_persists_to_sqlite(test_client: TestClient) -> None:
    chat_response = test_client.post(
        "/chat",
        json={
            "message": "我最近总拖延，想要更具体一点的建议。",
            "model_target": "configured",
        },
    )
    chat_payload = chat_response.json()

    feedback_response = test_client.post(
        "/api/feedback",
        json={
            "session_id": chat_payload["session_id"],
            "assistant_message_id": chat_payload["assistant_message_id"],
            "rating": "helpful",
            "comment": "这次建议比较能落地。",
        },
    )

    assert feedback_response.status_code == 200
    assert feedback_response.json()["status"] == "ok"

    with sqlite3.connect(os.environ["CHAT_DB_PATH"]) as connection:
        row = connection.execute(
            "SELECT rating, comment FROM feedback WHERE assistant_message_id = ?",
            (chat_payload["assistant_message_id"],),
        ).fetchone()

    assert row == ("helpful", "这次建议比较能落地。")


def test_build_completion_kwargs_omits_temperature_for_deepseek_reasoner() -> None:
    payload = build_completion_kwargs([{"role": "user", "content": "hello"}], model_name="deepseek-reasoner")

    assert payload["model"] == "deepseek-reasoner"
    assert "temperature" not in payload


def test_build_completion_kwargs_uses_temperature_for_regular_models(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("MODEL_TEMPERATURE", "0.3")
    payload = build_completion_kwargs([{"role": "user", "content": "hello"}], model_name="gpt-4o-mini")

    assert payload["model"] == "gpt-4o-mini"
    assert payload["temperature"] == 0.3


def test_list_model_options_contains_demo_and_configured() -> None:
    options = list_model_options()
    ids = {option.id for option in options}

    assert "configured" in ids
    assert "demo" in ids


def test_resolve_model_target_demo() -> None:
    target = resolve_model_target("demo")

    assert target.mode == "demo"
    assert target.provider_name == "Local Demo"


def test_configured_api_key_env_matches_model_family(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("MODEL_NAME", "deepseek-chat")
    monkeypatch.setenv("OPENAI_BASE_URL", "https://api.deepseek.com")
    monkeypatch.delenv("MODEL_API_KEY_ENV", raising=False)

    assert configured_api_key_env() == "DEEPSEEK_API_KEY"


def test_build_configured_target_uses_expected_key_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("MODEL_NAME", "deepseek-chat")
    monkeypatch.setenv("MODEL_PROVIDER", "DeepSeek")
    monkeypatch.setenv("OPENAI_BASE_URL", "https://api.deepseek.com")
    monkeypatch.setenv("OPENAI_API_KEY", "openai-key")
    monkeypatch.setenv("DEEPSEEK_API_KEY", "deepseek-key")
    monkeypatch.delenv("DEMO_MODE", raising=False)
    monkeypatch.delenv("MODEL_API_KEY_ENV", raising=False)

    target = build_configured_target()

    assert target.mode == "openai"
    assert target.api_key_env == "DEEPSEEK_API_KEY"
    assert target.api_key == "deepseek-key"


def test_compatibility_report_flags_missing_expected_key(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("MODEL_NAME", "deepseek-chat")
    monkeypatch.setenv("MODEL_PROVIDER", "DeepSeek")
    monkeypatch.setenv("OPENAI_BASE_URL", "https://api.deepseek.com")
    monkeypatch.setenv("OPENAI_API_KEY", "openai-key")
    monkeypatch.delenv("DEEPSEEK_API_KEY", raising=False)
    monkeypatch.setenv("DEMO_MODE", "false")
    monkeypatch.delenv("MODEL_API_KEY_ENV", raising=False)

    report = evaluate_runtime_compatibility()

    assert report.status == "error"
    assert report.api_key_env == "DEEPSEEK_API_KEY"
    assert any(item.status == "error" and "DEEPSEEK_API_KEY" in item.message for item in report.checks)


def test_compatibility_endpoint_returns_report(test_client: TestClient) -> None:
    response = test_client.get("/api/compatibility")

    assert response.status_code == 200
    payload = response.json()
    assert "status" in payload
    assert "checks" in payload
    assert "recommended_setups" in payload
