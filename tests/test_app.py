from fastapi.testclient import TestClient

from app import app, build_messages

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


def test_health_exposes_service_version() -> None:
    response = client.get("/health")

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ok"
    assert payload["version"] == app.version


def test_project_docs_are_exposed() -> None:
    response = client.get("/project-docs/dingtalk-integration.md")

    assert response.status_code == 200
    assert "钉钉集成与权限说明" in response.text


def test_build_messages_appends_system_hint() -> None:
    messages = build_messages("最近总拖延。", "给出 3 条具体建议")

    assert messages[0]["role"] == "system"
    assert "给出 3 条具体建议" in messages[0]["content"]
    assert messages[1]["content"] == "最近总拖延。"
