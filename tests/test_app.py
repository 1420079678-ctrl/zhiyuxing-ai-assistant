from fastapi.testclient import TestClient

from app import (
    STYLE_LABELS,
    app,
    build_completion_kwargs,
    build_demo_reply,
    build_messages,
    list_model_options,
    normalize_response_style,
    resolve_model_target,
)

client = TestClient(app)


def test_root_serves_demo_page() -> None:
    response = client.get("/")

    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "知愈星 AI Assistant" in response.text


def test_meta_returns_runtime_options() -> None:
    response = client.get("/api/meta")

    assert response.status_code == 200
    payload = response.json()
    assert payload["demo_page"] == "/"
    assert payload["docs_url"] == "/docs"
    assert payload["deployment_note"] == "/project-docs/dingtalk-integration.md"
    assert payload["model_doc"] == "/project-docs/model-integration.md"
    assert payload["available_models"]
    assert payload["available_styles"]


def test_health_exposes_service_version() -> None:
    response = client.get("/health")

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ok"
    assert payload["version"] == app.version
    assert "provider_name" in payload
    assert "model_name" in payload


def test_project_docs_are_exposed() -> None:
    response = client.get("/project-docs/model-integration.md")

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


def test_normalize_response_style_supports_hint_fallback() -> None:
    style = normalize_response_style(None, "更鼓励一点")

    assert style == "encouraging"


def test_chat_falls_back_to_demo_mode_without_api_key(monkeypatch) -> None:
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("DEEPSEEK_API_KEY", raising=False)
    monkeypatch.delenv("DEMO_MODE", raising=False)

    response = client.post(
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


def test_chat_rejects_unavailable_model_target(monkeypatch) -> None:
    monkeypatch.delenv("DEEPSEEK_API_KEY", raising=False)

    response = client.post(
        "/chat",
        json={
            "message": "我最近很焦虑。",
            "model_target": "deepseek-reasoner",
        },
    )

    assert response.status_code == 400
    assert "DEEPSEEK_API_KEY" in response.json()["detail"]


def test_build_completion_kwargs_omits_temperature_for_deepseek_reasoner() -> None:
    payload = build_completion_kwargs([{"role": "user", "content": "hello"}], model_name="deepseek-reasoner")

    assert payload["model"] == "deepseek-reasoner"
    assert "temperature" not in payload


def test_build_completion_kwargs_uses_temperature_for_regular_models(monkeypatch) -> None:
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
