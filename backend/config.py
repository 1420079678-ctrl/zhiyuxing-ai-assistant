from __future__ import annotations

import os
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv

from backend.schemas import ModelPreset, StyleOption


load_dotenv()

BASE_DIR = Path(__file__).resolve().parents[1]
STATIC_DIR = BASE_DIR / "static"
DOCS_DIR = BASE_DIR / "docs"


STYLE_OPTIONS = [
    StyleOption(id="balanced", label="平衡建议", helper_text="兼顾共情、行动建议和安全提醒"),
    StyleOption(id="warm", label="温和陪伴", helper_text="更重视情绪承接与安抚"),
    StyleOption(id="structured", label="三步计划", helper_text="用更清晰的分步结构给建议"),
    StyleOption(id="encouraging", label="鼓励支持", helper_text="语气更积极，强调可恢复性"),
    StyleOption(id="brief", label="简洁直接", helper_text="减少铺垫，更快给出核心建议"),
]

STYLE_LABELS = {option.id: option.label for option in STYLE_OPTIONS}
STYLE_PROMPTS = {
    "balanced": "保持温和、具体和平衡，兼顾情绪承接与行动建议。",
    "warm": "更偏温柔陪伴式表达，先接住情绪，再给建议。",
    "structured": "使用更清晰的分步结构，优先输出 3 步以内的行动建议。",
    "encouraging": "语气更鼓励，强调事情是可以逐步处理的。",
    "brief": "尽量简洁直接，减少铺垫，优先给出核心建议。",
}

MODEL_PRESETS = [
    ModelPreset(
        id="openai-gpt-4o-mini",
        label="OpenAI · GPT-4o mini",
        provider_name="OpenAI",
        model_name="gpt-4o-mini",
        base_url="https://api.openai.com/v1",
        api_key_env="OPENAI_API_KEY",
    ),
    ModelPreset(
        id="deepseek-chat",
        label="DeepSeek · Chat",
        provider_name="DeepSeek",
        model_name="deepseek-chat",
        base_url="https://api.deepseek.com",
        api_key_env="DEEPSEEK_API_KEY",
    ),
    ModelPreset(
        id="deepseek-reasoner",
        label="DeepSeek · R1 / Reasoner",
        provider_name="DeepSeek",
        model_name="deepseek-reasoner",
        base_url="https://api.deepseek.com",
        api_key_env="DEEPSEEK_API_KEY",
    ),
]

MODEL_PRESET_MAP = {preset.id: preset for preset in MODEL_PRESETS}


def env_flag(name: str) -> bool:
    return os.getenv(name, "").strip().lower() in {"1", "true", "yes", "on"}


def resolve_api_key(env_name: Optional[str] = None) -> Optional[str]:
    if env_name:
        value = os.getenv(env_name)
        return value if value else None

    for candidate in ("OPENAI_API_KEY", "DEEPSEEK_API_KEY"):
        value = os.getenv(candidate)
        if value:
            return value
    return None


def configured_api_key_env() -> str:
    explicit_env = os.getenv("MODEL_API_KEY_ENV", "").strip()
    if explicit_env:
        return explicit_env

    provider_name = os.getenv("MODEL_PROVIDER", "").strip().lower()
    base_url = configured_base_url().lower()
    model_name = configured_model_name().lower()

    if "deepseek" in provider_name or "deepseek" in base_url or model_name.startswith("deepseek"):
        return "DEEPSEEK_API_KEY"

    return "OPENAI_API_KEY"


def configured_api_key() -> Optional[str]:
    return resolve_api_key(configured_api_key_env())


def api_key_configured() -> bool:
    return bool(configured_api_key())


def configured_model_name() -> str:
    return os.getenv("MODEL_NAME", "gpt-4o-mini")


def configured_base_url() -> str:
    return os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")


def configured_provider_name() -> str:
    configured = os.getenv("MODEL_PROVIDER")
    if configured:
        return configured

    base_url = configured_base_url().lower()
    model_name = configured_model_name().lower()

    if "deepseek" in base_url or model_name.startswith("deepseek"):
        return "DeepSeek"
    if "openai" in base_url or model_name.startswith("gpt"):
        return "OpenAI"
    return "OpenAI Compatible"


def current_temperature() -> float:
    raw_value = os.getenv("MODEL_TEMPERATURE", "0.7")
    try:
        return float(raw_value)
    except ValueError:
        return 0.7


def supports_temperature(model_name: Optional[str] = None) -> bool:
    return (model_name or configured_model_name()).lower() != "deepseek-reasoner"


def current_chat_mode() -> str:
    if env_flag("DEMO_MODE"):
        return "demo"
    return "openai" if configured_api_key() else "demo"
