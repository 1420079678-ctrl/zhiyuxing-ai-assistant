import os
import sqlite3

from app import app


def test_root_serves_demo_page(test_client) -> None:
    response = test_client.get("/")

    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "知愈星 AI Assistant" in response.text


def test_meta_returns_runtime_options(test_client) -> None:
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
    assert payload["public_demo_mode"] is False
    assert payload["available_models"]
    assert payload["available_styles"]


def test_health_exposes_service_version(test_client) -> None:
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


def test_project_docs_are_exposed(test_client) -> None:
    response = test_client.get("/project-docs/model-integration.md")

    assert response.status_code == 200
    assert "模型接入说明" in response.text


def test_knowledge_search_endpoint_returns_hits(test_client) -> None:
    response = test_client.get("/api/knowledge/search", params={"q": "失眠"})

    assert response.status_code == 200
    payload = response.json()
    assert payload["query"] == "失眠"
    assert payload["total_hits"] >= 1
    assert payload["hits"][0]["source_path"].startswith("knowledge_base/")


def test_knowledge_documents_endpoint_supports_custom_documents(test_client) -> None:
    unique_keyword = "zhiyuxing_custom_signal_2026"
    create_response = test_client.post(
        "/api/knowledge/documents",
        json={
            "title": "校园求助渠道",
            "content": (
                "如果用户提到长期崩溃、严重失眠或明显无助感，应明确建议联系学校心理中心、辅导员或校医院，"
                f"并记录唯一标记 {unique_keyword}，用于验证自定义知识文档已参与检索。"
            ),
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

    search_response = test_client.get("/api/knowledge/search", params={"q": unique_keyword})
    assert search_response.status_code == 200
    search_payload = search_response.json()
    assert any("knowledge_uploads" in hit["source_path"] for hit in search_payload["hits"])


def test_chat_falls_back_to_demo_mode_without_api_key(test_client) -> None:
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


def test_chat_returns_memory_knowledge_and_safety_fields(test_client) -> None:
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


def test_chat_uses_session_memory_and_exposes_history(test_client) -> None:
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


def test_high_risk_message_uses_guardrail(test_client) -> None:
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


def test_feedback_endpoint_persists_to_sqlite(test_client) -> None:
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


def test_compatibility_endpoint_returns_report(test_client) -> None:
    response = test_client.get("/api/compatibility")

    assert response.status_code == 200
    payload = response.json()
    assert "status" in payload
    assert "checks" in payload
    assert "recommended_setups" in payload


def test_public_demo_mode_blocks_write_endpoints(test_client, monkeypatch) -> None:
    monkeypatch.setenv("PUBLIC_DEMO_MODE", "true")

    knowledge_response = test_client.post(
        "/api/knowledge/documents",
        json={"title": "demo", "content": "这是一个用于测试公开演示模式写保护的唯一内容。"},
    )
    feedback_response = test_client.post(
        "/api/feedback",
        json={"session_id": "sess_demo", "assistant_message_id": 1, "rating": "helpful"},
    )
    meta_response = test_client.get("/api/meta")

    assert knowledge_response.status_code == 403
    assert feedback_response.status_code == 403
    assert meta_response.status_code == 200
    assert meta_response.json()["public_demo_mode"] is True
