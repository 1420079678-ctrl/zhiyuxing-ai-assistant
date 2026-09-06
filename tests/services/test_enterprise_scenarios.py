from services.auth import is_auth_enabled, verify_api_key
from services.telemetry import telemetry
from backend.chat_logic import build_messages, detect_demo_topic


def test_detect_workplace_burnout_topic() -> None:
    topic = detect_demo_topic("连续加班两周了，感觉严重倦怠，心很累不想去工位。")
    assert topic == "workplace_burnout"


def test_detect_career_alignment_topic() -> None:
    topic = detect_demo_topic("跨部门协作方案一直对齐不了口径，主管又要催汇报了。")
    assert topic == "career_alignment"


def test_build_messages_enterprise_scenario() -> None:
    messages = build_messages(
        user_message="最近项目压力非常大",
        system_hint="重点关注目标拆解",
        scenario="enterprise",
    )
    system_msg = next(m["content"] for m in messages if m["role"] == "system")
    assert "EAP Copilot" in system_msg
    assert "职业倦怠" in system_msg


def test_telemetry_metrics_accumulation() -> None:
    initial_tokens = telemetry.tokens_estimated
    telemetry.record_tokens(100)
    assert telemetry.tokens_estimated == initial_tokens + 100

    telemetry.record_guardrail("high")
    assert telemetry.guardrail_triggers["high"] >= 1

    summary = telemetry.get_summary()
    assert "uptime_seconds" in summary
    assert summary["guardrail_triggers"] >= 1


def test_auth_key_verification(monkeypatch) -> None:
    # 1. When auth disabled (default), passes freely
    monkeypatch.delenv("API_KEY_AUTH_ENABLED", raising=False)
    assert verify_api_key(authorization=None, x_api_key=None) == "anonymous-dev"

    # 2. When auth enabled, validates correctly
    monkeypatch.setenv("API_KEY_AUTH_ENABLED", "true")
    monkeypatch.setenv("API_MASTER_KEYS", "secret-key-1,secret-key-2")

    # Valid token via Bearer
    assert verify_api_key(authorization="Bearer secret-key-1", x_api_key=None) == "secret-key-1"
    # Valid token via X-API-Key
    assert verify_api_key(authorization=None, x_api_key="secret-key-2") == "secret-key-2"
