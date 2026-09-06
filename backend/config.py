from __future__ import annotations

import os
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv

from backend.schemas import ModelPreset, ScenarioOption, StyleOption


load_dotenv()

BASE_DIR = Path(__file__).resolve().parents[1]
STATIC_DIR = BASE_DIR / "static"
DOCS_DIR = BASE_DIR / "docs"


SCENARIO_OPTIONS = [
    ScenarioOption(
        id="campus",
        label="高校青年成长",
        description="聚焦学业压力排解、拖延内耗阻断、考研答辩与求职抗压，提供温和可落地的微步建议。",
        prompt_hint="作为知愈星高校青年成长伴读教练，聚焦学业压力排解、拖延内耗阻断与考试求职辅导。",
    ),
    ScenarioOption(
        id="enterprise",
        label="企业员工 EAP 关怀",
        description="面向职场人士与企业团队，聚焦职业倦怠(Burnout)修复、高压交付应对、行动破冰与沟通对齐。",
        prompt_hint="作为知愈星企业员工关怀 EAP 辅导顾问，聚焦职场高压排解、精力回血、任务切片与跨部门沟通对齐。",
    ),
]

SCENARIO_MAP = {option.id: option for option in SCENARIO_OPTIONS}

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
        id="openai-gpt-4o",
        label="OpenAI · GPT-4o",
        provider_name="OpenAI",
        model_name="gpt-4o",
        base_url="https://api.openai.com/v1",
        api_key_env="OPENAI_API_KEY",
    ),
    ModelPreset(
        id="deepseek-chat",
        label="DeepSeek · Chat (V3)",
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
    ModelPreset(
        id="orcarouter-deepseek-chat",
        label="OrcaRouter · DeepSeek Chat (推荐网关)",
        provider_name="OrcaRouter",
        model_name="deepseek/deepseek-chat",
        base_url="https://api.orcarouter.com/v1",
        api_key_env="ORCAROUTER_API_KEY",
    ),
    ModelPreset(
        id="orcarouter-gpt-4o-mini",
        label="OrcaRouter · GPT-4o mini",
        provider_name="OrcaRouter",
        model_name="openai/gpt-4o-mini",
        base_url="https://api.orcarouter.com/v1",
        api_key_env="ORCAROUTER_API_KEY",
    ),
    ModelPreset(
        id="qwen-plus",
        label="通义千问 · Qwen Plus",
        provider_name="Qwen",
        model_name="qwen-plus",
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
        api_key_env="DASHSCOPE_API_KEY",
    ),
    ModelPreset(
        id="moonshot-v1-8k",
        label="Moonshot · Kimi (v1-8k)",
        provider_name="Moonshot",
        model_name="moonshot-v1-8k",
        base_url="https://api.moonshot.cn/v1",
        api_key_env="MOONSHOT_API_KEY",
    ),
    ModelPreset(
        id="zhipu-glm-4-flash",
        label="智谱清言 · GLM-4-Flash",
        provider_name="Zhipu",
        model_name="glm-4-flash",
        base_url="https://open.bigmodel.cn/api/paas/v4",
        api_key_env="ZHIPU_API_KEY",
    ),
    ModelPreset(
        id="siliconflow-deepseek-chat",
        label="硅基流动 · DeepSeek-V3",
        provider_name="SiliconFlow",
        model_name="deepseek-ai/DeepSeek-V3",
        base_url="https://api.siliconflow.cn/v1",
        api_key_env="SILICONFLOW_API_KEY",
    ),
    ModelPreset(
        id="groq-llama-3.3-70b",
        label="Groq · Llama 3.3 70B",
        provider_name="Groq",
        model_name="llama-3.3-70b-versatile",
        base_url="https://api.groq.com/openai/v1",
        api_key_env="GROQ_API_KEY",
    ),
    ModelPreset(
        id="ollama-local",
        label="Ollama · 本地私有化大模型",
        provider_name="Ollama",
        model_name="qwen2.5:7b",
        base_url="http://localhost:11434/v1",
        api_key_env="OLLAMA_API_KEY",
    ),
]

MODEL_PRESET_MAP = {preset.id: preset for preset in MODEL_PRESETS}


def env_flag(name: str) -> bool:
    return os.getenv(name, "").strip().lower() in {"1", "true", "yes", "on"}


def public_demo_mode() -> bool:
    return env_flag("PUBLIC_DEMO_MODE")


def resolve_api_key(env_name: Optional[str] = None) -> Optional[str]:
    if env_name:
        value = os.getenv(env_name)
        return value if value else None

    for candidate in (
        "OPENAI_API_KEY",
        "DEEPSEEK_API_KEY",
        "ORCAROUTER_API_KEY",
        "DASHSCOPE_API_KEY",
        "MOONSHOT_API_KEY",
        "ZHIPU_API_KEY",
        "SILICONFLOW_API_KEY",
        "GROQ_API_KEY",
        "OLLAMA_API_KEY",
    ):
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

    if "orcarouter" in provider_name or "orcarouter" in base_url:
        return "ORCAROUTER_API_KEY"

    if "siliconflow" in provider_name or "siliconflow" in base_url:
        return "SILICONFLOW_API_KEY"

    if "dashscope" in base_url or "qwen" in provider_name or "aliyun" in base_url:
        return "DASHSCOPE_API_KEY"

    if "moonshot" in provider_name or "moonshot" in base_url or "kimi" in provider_name:
        return "MOONSHOT_API_KEY"

    if "bigmodel" in base_url or "zhipu" in provider_name or "glm" in model_name:
        return "ZHIPU_API_KEY"

    if "groq" in provider_name or "groq" in base_url:
        return "GROQ_API_KEY"

    if "11434" in base_url or "ollama" in provider_name or "ollama" in base_url:
        return "OLLAMA_API_KEY"

    if "deepseek" in provider_name or "deepseek" in base_url or model_name.startswith("deepseek"):
        return "DEEPSEEK_API_KEY"

    return "OPENAI_API_KEY"


def cors_origins() -> list[str]:
    raw = os.getenv("CORS_ORIGINS", "*").strip()
    return [item.strip() for item in raw.split(",") if item.strip()]



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
    if public_demo_mode() or env_flag("DEMO_MODE"):
        return "demo"
    return "openai" if configured_api_key() else "demo"
