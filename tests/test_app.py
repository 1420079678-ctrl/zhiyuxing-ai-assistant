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
    assert payload["compatibility_url"] == "/api/compatibility"
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
    assert "api_key_env" in payload


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


def test_configured_api_key_env_matches_model_family(monkeypatch) -> None:
    monkeypatch.setenv("MODEL_NAME", "deepseek-chat")
    monkeypatch.setenv("OPENAI_BASE_URL", "https://api.deepseek.com")
    monkeypatch.delenv("MODEL_API_KEY_ENV", raising=False)

    assert configured_api_key_env() == "DEEPSEEK_API_KEY"


def test_build_configured_target_uses_expected_key_env(monkeypatch) -> None:
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


def test_compatibility_report_flags_missing_expected_key(monkeypatch) -> None:
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


def test_compatibility_endpoint_returns_report() -> None:
    response = client.get("/api/compatibility")

    assert response.status_code == 200
    payload = response.json()
    assert "status" in payload
    assert "checks" in payload
    assert "recommended_setups" in payload
