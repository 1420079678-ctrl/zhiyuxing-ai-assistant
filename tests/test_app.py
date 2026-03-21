from fastapi.testclient import TestClient

from app import app, build_demo_reply, build_messages

client = TestClient(app)


def test_root_serves_demo_page() -> None:
    response = client.get("/")

    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "知愈星 AI Assistant" in response.text


def test_meta_returns_demo_entrypoints() -> None:
    response = client.get("/api/meta")

    assert response.status_code == 200
    payload = response.json()
    assert payload["demo_page"] == "/"
    assert payload["docs_url"] == "/docs"
    assert payload["deployment_note"] == "/project-docs/dingtalk-integration.md"
    assert "chat_mode" in payload


def test_health_exposes_service_version() -> None:
    response = client.get("/health")

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ok"
    assert payload["version"] == app.version
    assert "mode" in payload


def test_project_docs_are_exposed() -> None:
    response = client.get("/project-docs/dingtalk-integration.md")

    assert response.status_code == 200
    assert "钉钉集成与权限说明" in response.text


def test_build_messages_appends_system_hint() -> None:
    messages = build_messages("最近总拖延。", "给出 3 条具体建议")

    assert messages[0]["role"] == "system"
    assert "给出 3 条具体建议" in messages[0]["content"]
    assert messages[1]["content"] == "最近总拖延。"


def test_build_demo_reply_returns_structured_advice() -> None:
    reply = build_demo_reply("最近总拖延，学不进去。")

    assert "1." in reply
    assert "2." in reply
    assert "3." in reply


def test_build_demo_reply_respects_system_hint_style() -> None:
    reply = build_demo_reply("最近总拖延，学不进去。", "更简洁一点")

    assert "先做这 3 件事" in reply
    assert "1." in reply


def test_chat_falls_back_to_demo_mode_without_api_key(monkeypatch) -> None:
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("DEMO_MODE", raising=False)

    response = client.post(
        "/chat",
        json={"message": "这周压力很大，完全不想开始复习。"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["mode"] == "demo"
    assert "本地演示模式" in payload["note"]
    assert payload["reply"]
