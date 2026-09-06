import json
from app import app


def test_request_id_and_response_time_headers_present(test_client) -> None:
    response = test_client.get("/health")
    assert response.status_code == 200
    assert "x-request-id" in response.headers
    assert "x-response-time" in response.headers


def test_metrics_endpoint_returns_prometheus_format(test_client) -> None:
    # Trigger a request first so telemetry records it
    test_client.get("/health")

    response = test_client.get("/metrics")
    assert response.status_code == 200
    assert "text/plain" in response.headers["content-type"]
    text = response.text
    assert "zhiyuxing_uptime_seconds" in text
    assert "zhiyuxing_http_requests_total" in text


def test_scenarios_endpoint_lists_options(test_client) -> None:
    response = test_client.get("/api/scenarios")
    assert response.status_code == 200
    scenarios = response.json()
    scenario_ids = [item["id"] for item in scenarios]
    assert "campus" in scenario_ids
    assert "enterprise" in scenario_ids


def test_chat_stream_endpoint_demo_mode(test_client) -> None:
    response = test_client.post(
        "/chat/stream",
        json={
            "message": "最近工作压力很大，有点职业倦怠了。",
            "scenario": "enterprise",
            "response_style": "balanced",
        },
    )
    assert response.status_code == 200
    assert "text/event-stream" in response.headers["content-type"]
    events = []
    for line in response.text.splitlines():
        if line.startswith("data: "):
            events.append(json.loads(line[6:]))

    assert any(e.get("event") == "start" for e in events)
    assert any(e.get("event") == "delta" for e in events)
    assert any(e.get("event") == "done" for e in events)


def test_session_list_and_deletion(test_client) -> None:
    # 1. Create a session via chat
    chat_resp = test_client.post("/chat", json={"message": "测试会话创建与删除"})
    assert chat_resp.status_code == 200
    session_id = chat_resp.json()["session_id"]

    # 2. Verify it shows in list
    list_resp = test_client.get("/api/sessions")
    assert list_resp.status_code == 200
    sessions = list_resp.json()["sessions"]
    assert any(s["session_id"] == session_id for s in sessions)

    # 3. Delete the session
    del_resp = test_client.delete(f"/api/sessions/{session_id}")
    assert del_resp.status_code == 200
    assert del_resp.json()["status"] == "ok"

    # 4. Verify deleting non-existent session returns 404
    del_again = test_client.delete(f"/api/sessions/{session_id}")
    assert del_again.status_code == 404


def test_knowledge_document_deletion(test_client) -> None:
    # 1. Create custom document
    doc_id = "test-doc-to-delete-2026"
    create_resp = test_client.post(
        "/api/knowledge/documents",
        json={
            "title": "临时知识条目",
            "content": "这是一条待删除的临时企业政策说明与知识库验证内容，用于测试删除接口。",
            "document_id": doc_id,
        },
    )
    assert create_resp.status_code == 201

    # 2. Delete the document
    del_resp = test_client.delete(f"/api/knowledge/documents/{doc_id}")
    assert del_resp.status_code == 200
    assert del_resp.json()["status"] == "ok"

    # 3. Deleting it again returns 404
    del_again = test_client.delete(f"/api/knowledge/documents/{doc_id}")
    assert del_again.status_code == 404


def test_update_model_settings_and_meta(test_client) -> None:
    # 1. Update settings
    resp = test_client.post(
        "/api/settings/model",
        json={
            "provider": "DeepSeek",
            "model_name": "deepseek-chat",
            "base_url": "https://api.deepseek.com",
            "api_key": "sk-test-mock-key-12345",
            "temperature": 0.8,
            "demo_mode": False,
        },
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"
    assert data["api_key_configured"] is True

    # 2. Check meta reflects changes
    meta_resp = test_client.get("/api/meta")
    assert meta_resp.status_code == 200
    meta = meta_resp.json()
    assert meta["api_key_configured"] is True

    # 3. Reset back to demo
    reset_resp = test_client.post(
        "/api/settings/model",
        json={
            "provider": "DeepSeek",
            "model_name": "deepseek-chat",
            "base_url": "https://api.deepseek.com",
            "demo_mode": True,
        },
    )
    assert reset_resp.status_code == 200
    assert reset_resp.json()["mode"] == "demo"


def test_probe_settings_endpoint(test_client) -> None:
    # Probe with invalid url or local address
    resp = test_client.post(
        "/api/settings/probe",
        json={
            "provider": "MockProvider",
            "model_name": "mock-model",
            "base_url": "https://127.0.0.1:9999",
            "api_key": "sk-fake",
        },
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "status" in data
    assert "message" in data

