from app import (
    build_completion_kwargs,
    build_configured_target,
    configured_api_key_env,
    evaluate_runtime_compatibility,
    list_model_options,
    resolve_model_target,
)


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
    monkeypatch.delenv("PUBLIC_DEMO_MODE", raising=False)
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
    monkeypatch.delenv("PUBLIC_DEMO_MODE", raising=False)
    monkeypatch.delenv("MODEL_API_KEY_ENV", raising=False)

    report = evaluate_runtime_compatibility()

    assert report.status == "error"
    assert report.api_key_env == "DEEPSEEK_API_KEY"
    assert any(item.status == "error" and "DEEPSEEK_API_KEY" in item.message for item in report.checks)


def test_public_demo_mode_forces_demo_target(monkeypatch) -> None:
    monkeypatch.setenv("PUBLIC_DEMO_MODE", "true")
    monkeypatch.setenv("OPENAI_API_KEY", "openai-key")

    target = build_configured_target()
    report = evaluate_runtime_compatibility()

    assert target.mode == "demo"
    assert report.ready_for_model_call is False


def test_multiple_provider_presets_resolution(monkeypatch) -> None:
    # Test Qwen
    monkeypatch.setenv("MODEL_PROVIDER", "Qwen")
    monkeypatch.setenv("MODEL_NAME", "qwen-plus")
    monkeypatch.setenv("OPENAI_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1")
    monkeypatch.delenv("MODEL_API_KEY_ENV", raising=False)
    assert configured_api_key_env() == "DASHSCOPE_API_KEY"

    # Test Moonshot
    monkeypatch.setenv("MODEL_PROVIDER", "Moonshot")
    monkeypatch.setenv("MODEL_NAME", "moonshot-v1-8k")
    monkeypatch.setenv("OPENAI_BASE_URL", "https://api.moonshot.cn/v1")
    assert configured_api_key_env() == "MOONSHOT_API_KEY"

    # Test Zhipu
    monkeypatch.setenv("MODEL_PROVIDER", "Zhipu")
    monkeypatch.setenv("MODEL_NAME", "glm-4-flash")
    monkeypatch.setenv("OPENAI_BASE_URL", "https://open.bigmodel.cn/api/paas/v4")
    assert configured_api_key_env() == "ZHIPU_API_KEY"

    # Test SiliconFlow
    monkeypatch.setenv("MODEL_PROVIDER", "SiliconFlow")
    monkeypatch.setenv("MODEL_NAME", "deepseek-ai/DeepSeek-V3")
    monkeypatch.setenv("OPENAI_BASE_URL", "https://api.siliconflow.cn/v1")
    assert configured_api_key_env() == "SILICONFLOW_API_KEY"

    # Test Groq
    monkeypatch.setenv("MODEL_PROVIDER", "Groq")
    monkeypatch.setenv("MODEL_NAME", "llama-3.3-70b-versatile")
    monkeypatch.setenv("OPENAI_BASE_URL", "https://api.groq.com/openai/v1")
    assert configured_api_key_env() == "GROQ_API_KEY"

    # Test Ollama
    monkeypatch.setenv("MODEL_PROVIDER", "Ollama")
    monkeypatch.setenv("MODEL_NAME", "qwen2.5:7b")
    monkeypatch.setenv("OPENAI_BASE_URL", "http://localhost:11434/v1")
    assert configured_api_key_env() == "OLLAMA_API_KEY"

