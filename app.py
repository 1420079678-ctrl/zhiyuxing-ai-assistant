from __future__ import annotations

import os
import secrets
from contextlib import asynccontextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import Literal, Optional

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from openai import OpenAI
from pydantic import BaseModel, Field
from services.knowledge import KnowledgeHitResult, knowledge_document_count, search_knowledge
from services.safety import RiskAssessment, assess_risk, high_risk_reply, safety_prompt_extension
from services.storage import ensure_database, ensure_session, recent_messages, save_feedback, save_turn, session_history

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"
DOCS_DIR = BASE_DIR / "docs"


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, description="用户输入")
    system_hint: Optional[str] = Field(default=None, description="可选的额外系统提示")
    response_style: Optional[str] = Field(default="balanced", description="回答风格")
    model_target: Optional[str] = Field(default="configured", description="模型目标")
    session_id: Optional[str] = Field(default=None, description="会话 ID；为空时自动创建")


class RetrievedKnowledge(BaseModel):
    title: str
    excerpt: str
    source_path: str
    score: float


class SafetyInfo(BaseModel):
    level: str
    label: str
    note: str
    needs_human_support: bool
    matched_keywords: list[str]


class ChatResponse(BaseModel):
    reply: str
    note: str
    mode: str
    provider_name: str
    model_name: str
    response_style: str
    session_id: str
    assistant_message_id: int
    memory_messages_used: int
    knowledge_hits: list[RetrievedKnowledge]
    safety: SafetyInfo


class ModelOption(BaseModel):
    id: str
    label: str
    provider_name: str
    model_name: str
    mode: str
    available: bool
    reason: Optional[str] = None


class StyleOption(BaseModel):
    id: str
    label: str
    helper_text: str


class ServiceInfo(BaseModel):
    name: str
    version: str
    description: str
    docs_url: str
    healthcheck: str
    demo_page: str
    deployment_note: str
    compatibility_url: str
    chat_mode: str
    api_key_configured: bool
    api_key_env: Optional[str]
    provider_name: str
    model_name: str
    base_url: str
    model_doc: str
    supports_temperature: bool
    persistence_enabled: bool
    knowledge_document_count: int
    session_history_url: str
    feedback_url: str
    knowledge_search_url: str
    available_models: list[ModelOption]
    available_styles: list[StyleOption]


class HealthResponse(BaseModel):
    status: str
    service: str
    version: str
    mode: str
    api_key_configured: bool
    api_key_env: Optional[str]
    provider_name: str
    model_name: str
    persistence_enabled: bool
    knowledge_document_count: int


class CompatibilityCheckItem(BaseModel):
    code: str
    status: str
    message: str


class QuickSetupOption(BaseModel):
    id: str
    label: str
    command: str
    description: str


class CompatibilityReport(BaseModel):
    status: str
    summary: str
    ready_for_model_call: bool
    mode: str
    provider_name: str
    model_name: str
    base_url: str
    api_key_env: Optional[str]
    api_key_configured: bool
    supports_temperature: bool
    checks: list[CompatibilityCheckItem]
    recommended_setups: list[QuickSetupOption]


class SessionMessage(BaseModel):
    id: int
    role: str
    content: str
    provider_name: Optional[str] = None
    model_name: Optional[str] = None
    mode: Optional[str] = None
    risk_level: Optional[str] = None
    created_at: str


class SessionHistoryResponse(BaseModel):
    session_id: str
    title: Optional[str]
    created_at: Optional[str]
    updated_at: Optional[str]
    total_messages: int
    messages: list[SessionMessage]


class KnowledgeSearchResponse(BaseModel):
    query: str
    total_hits: int
    hits: list[RetrievedKnowledge]


class FeedbackRequest(BaseModel):
    session_id: str
    assistant_message_id: int
    rating: Literal["helpful", "needs_more"]
    comment: Optional[str] = None


class FeedbackResponse(BaseModel):
    status: str
    message: str


@dataclass(frozen=True)
class ResolvedTarget:
    id: str
    label: str
    mode: str
    provider_name: str
    model_name: str
    base_url: str
    api_key: Optional[str] = None
    api_key_env: Optional[str] = None


@dataclass(frozen=True)
class ModelPreset:
    id: str
    label: str
    provider_name: str
    model_name: str
    base_url: str
    api_key_env: str
    mode: str = "openai"


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


@asynccontextmanager
async def lifespan(_: FastAPI):
    ensure_database()
    yield


app = FastAPI(
    title="Zhiyuxing AI Assistant API",
    description="面向大学生场景的 AI 情绪支持与学习辅助服务，支持本地演示模式与模型调用模式。",
    version="0.6.0",
    lifespan=lifespan,
)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
app.mount("/project-docs", StaticFiles(directory=DOCS_DIR), name="project-docs")


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


def build_demo_target() -> ResolvedTarget:
    return ResolvedTarget(
        id="demo",
        label="本地演示模式",
        mode="demo",
        provider_name="Local Demo",
        model_name="builtin-demo",
        base_url="local://demo-fallback",
    )


def build_configured_snapshot() -> ResolvedTarget:
    api_key_env = configured_api_key_env()
    return ResolvedTarget(
        id="configured",
        label="当前配置",
        mode="openai",
        provider_name=configured_provider_name(),
        model_name=configured_model_name(),
        base_url=configured_base_url(),
        api_key=resolve_api_key(api_key_env),
        api_key_env=api_key_env,
    )


def build_configured_target() -> ResolvedTarget:
    configured_target = build_configured_snapshot()
    if env_flag("DEMO_MODE") or not configured_target.api_key:
        return build_demo_target()
    return configured_target


def resolve_model_target(model_target: Optional[str]) -> ResolvedTarget:
    target_id = (model_target or "configured").strip().lower()

    if target_id == "configured":
        return build_configured_target()
    if target_id == "demo":
        return build_demo_target()

    preset = MODEL_PRESET_MAP.get(target_id)
    if not preset:
        raise HTTPException(status_code=400, detail=f"不支持的模型目标：{target_id}")

    api_key = resolve_api_key(preset.api_key_env)
    if not api_key:
        raise HTTPException(
            status_code=400,
            detail=f"未配置 {preset.api_key_env}，无法切换到 {preset.label}",
        )

    return ResolvedTarget(
        id=preset.id,
        label=preset.label,
        mode=preset.mode,
        provider_name=preset.provider_name,
        model_name=preset.model_name,
        base_url=preset.base_url,
        api_key=api_key,
        api_key_env=preset.api_key_env,
    )


def list_model_options() -> list[ModelOption]:
    configured_target = build_configured_snapshot()
    configured_mode = current_chat_mode()
    configured_reason = None

    if env_flag("DEMO_MODE"):
        configured_reason = "DEMO_MODE=true，当前配置会强制回退到本地演示模式"
    elif not configured_target.api_key and configured_target.api_key_env:
        configured_reason = f"未配置 {configured_target.api_key_env}，当前会回退到本地演示模式"

    options = [
        ModelOption(
            id="configured",
            label=f"当前配置（{configured_target.provider_name} / {configured_target.model_name}）",
            provider_name=configured_target.provider_name,
            model_name=configured_target.model_name,
            mode=configured_mode,
            available=True,
            reason=configured_reason,
        ),
        ModelOption(
            id="demo",
            label="本地演示模式",
            provider_name="Local Demo",
            model_name="builtin-demo",
            mode="demo",
            available=True,
        ),
    ]

    for preset in MODEL_PRESETS:
        available = bool(resolve_api_key(preset.api_key_env))
        options.append(
            ModelOption(
                id=preset.id,
                label=preset.label,
                provider_name=preset.provider_name,
                model_name=preset.model_name,
                mode=preset.mode,
                available=available,
                reason=None if available else f"未配置 {preset.api_key_env}",
            )
        )

    return options


def detect_model_family(model_name: str) -> str:
    normalized = model_name.strip().lower()
    if normalized.startswith("deepseek"):
        return "deepseek"
    if normalized.startswith(("gpt", "o1", "o3", "o4")):
        return "openai"
    return "compatible"


def detect_endpoint_family(base_url: str) -> str:
    normalized = base_url.strip().lower().rstrip("/")
    if "api.deepseek.com" in normalized:
        return "deepseek"
    if "api.openai.com" in normalized:
        return "openai"
    return "compatible"


def detect_provider_family(provider_name: str) -> str:
    normalized = provider_name.strip().lower()
    if "deepseek" in normalized:
        return "deepseek"
    if "openai" in normalized:
        return "openai"
    return "compatible"


def quick_setup_options() -> list[QuickSetupOption]:
    return [
        QuickSetupOption(
            id="openai",
            label="OpenAI",
            command=r".\setup-openai.ps1",
            description="一键写入 OpenAI 官方地址和 gpt-4o-mini 默认模型。",
        ),
        QuickSetupOption(
            id="deepseek-chat",
            label="DeepSeek Chat",
            command=r".\setup-deepseek-chat.ps1",
            description="一键写入 DeepSeek Chat 所需配置。",
        ),
        QuickSetupOption(
            id="deepseek-r1",
            label="DeepSeek R1 / Reasoner",
            command=r".\setup-deepseek-r1.ps1",
            description="一键写入 DeepSeek R1 所需配置，并自动适配 temperature 规则。",
        ),
    ]


def evaluate_runtime_compatibility() -> CompatibilityReport:
    configured_target = build_configured_snapshot()
    checks: list[CompatibilityCheckItem] = []

    def add_check(code: str, status: str, message: str) -> None:
        checks.append(CompatibilityCheckItem(code=code, status=status, message=message))

    if (BASE_DIR / ".env").exists():
        add_check("env-file", "ok", "已检测到 .env 文件。")
    else:
        add_check("env-file", "warning", "未检测到 .env 文件；启动脚本会自动从 .env.example 复制一份默认配置。")

    if env_flag("DEMO_MODE"):
        add_check("demo-mode", "warning", "DEMO_MODE=true，当前服务会强制使用本地演示模式。")
    else:
        add_check("demo-mode", "ok", "当前未强制启用本地演示模式。")

    if configured_target.base_url.startswith(("https://", "http://")):
        add_check("base-url", "ok", f"当前 API 地址为 {configured_target.base_url}。")
    else:
        add_check("base-url", "error", f"OPENAI_BASE_URL 无效：{configured_target.base_url}")

    if configured_target.api_key and configured_target.api_key_env:
        add_check("api-key", "ok", f"已检测到 {configured_target.api_key_env}。")
    else:
        missing_env = configured_target.api_key_env or "API_KEY"
        missing_status = "warning" if env_flag("DEMO_MODE") else "error"
        add_check(
            "api-key",
            missing_status,
            f"未检测到 {missing_env}。当前配置无法直接进入真实模型调用。",
        )

    model_family = detect_model_family(configured_target.model_name)
    endpoint_family = detect_endpoint_family(configured_target.base_url)
    provider_family = detect_provider_family(configured_target.provider_name)

    if endpoint_family == "compatible":
        add_check(
            "endpoint-family",
            "warning",
            "当前是自定义 OpenAI 兼容地址；请确认它支持 Chat Completions 接口和当前模型名。",
        )
    elif model_family in {"openai", "deepseek"} and endpoint_family != model_family:
        add_check(
            "endpoint-family",
            "warning",
            "当前模型名和 API 地址看起来不是同一家官方接口；如果不是代理层或兼容网关，真实调用可能失败。",
        )
    else:
        add_check("endpoint-family", "ok", "模型名与 API 地址的基础兼容关系正常。")

    if provider_family in {"openai", "deepseek"} and model_family in {"openai", "deepseek"} and provider_family != model_family:
        add_check(
            "provider-name",
            "warning",
            "MODEL_PROVIDER 展示名与当前模型家族不一致，建议修正后再对外展示。",
        )
    else:
        add_check("provider-name", "ok", "MODEL_PROVIDER 与当前模型家族展示一致。")

    if configured_target.model_name.lower() == "deepseek-reasoner":
        add_check(
            "temperature-rule",
            "ok",
            "当前模型为 deepseek-reasoner；服务会自动跳过 temperature 参数，兼容官方要求。",
        )
    elif supports_temperature(configured_target.model_name):
        add_check("temperature-rule", "ok", "当前模型支持 temperature 参数。")
    else:
        add_check("temperature-rule", "warning", "当前模型不建议传 temperature 参数。")

    has_error = any(item.status == "error" for item in checks)
    has_warning = any(item.status == "warning" for item in checks)
    ready_for_model_call = not env_flag("DEMO_MODE") and bool(configured_target.api_key) and not has_error

    if ready_for_model_call and not has_warning:
        status = "ok"
        summary = "当前配置已通过基础检查，可以直接调用真实模型。"
    elif has_error:
        status = "error"
        summary = "当前配置存在阻塞项，真实模型调用会失败；请先运行一键配置脚本或补齐密钥。"
    else:
        status = "warning"
        summary = "当前项目可以运行，但真实模型调用仍需确认配置或关闭 DEMO_MODE。"

    return CompatibilityReport(
        status=status,
        summary=summary,
        ready_for_model_call=ready_for_model_call,
        mode=current_chat_mode(),
        provider_name=configured_target.provider_name,
        model_name=configured_target.model_name,
        base_url=configured_target.base_url,
        api_key_env=configured_target.api_key_env,
        api_key_configured=bool(configured_target.api_key),
        supports_temperature=supports_temperature(configured_target.model_name),
        checks=checks,
        recommended_setups=quick_setup_options(),
    )


def probe_configured_model() -> str:
    configured_target = build_configured_snapshot()

    if env_flag("DEMO_MODE"):
        raise HTTPException(status_code=400, detail="DEMO_MODE=true，当前不会发起真实模型调用。")
    if not configured_target.api_key:
        missing_env = configured_target.api_key_env or "API_KEY"
        raise HTTPException(status_code=400, detail=f"未配置 {missing_env}，无法执行真实探测。")

    client = build_client(configured_target)
    completion = client.chat.completions.create(
        **build_completion_kwargs(
            [
                {"role": "system", "content": "你正在执行 API 连接探测。请只返回一句简短确认，不要展开说明。"},
                {"role": "user", "content": "请回复：连接测试成功"},
            ],
            model_name=configured_target.model_name,
        )
    )
    return completion.choices[0].message.content or "连接已建立，但没有返回文本内容。"


def to_safety_info(assessment: RiskAssessment) -> SafetyInfo:
    return SafetyInfo(
        level=assessment.level,
        label=assessment.label,
        note=assessment.note,
        needs_human_support=assessment.needs_human_support,
        matched_keywords=list(assessment.matched_keywords),
    )


def to_knowledge_models(hits: list[KnowledgeHitResult]) -> list[RetrievedKnowledge]:
    return [
        RetrievedKnowledge(
            title=hit.title,
            excerpt=hit.excerpt,
            source_path=hit.source_path,
            score=hit.score,
        )
        for hit in hits
    ]


def knowledge_sources(hits: list[KnowledgeHitResult]) -> list[str]:
    return [hit.title for hit in hits]


def format_knowledge_prompt(hits: list[KnowledgeHitResult]) -> str:
    if not hits:
        return ""
    sections = [
        f"- {hit.title}（{hit.source_path}）：{hit.excerpt}"
        for hit in hits
    ]
    return "\n可参考的知识库片段：\n" + "\n".join(sections)


def normalize_response_style(response_style: Optional[str], system_hint: Optional[str] = None) -> str:
    candidate = (response_style or "").strip().lower()
    if candidate in STYLE_LABELS:
        return candidate

    hint = (system_hint or "").strip()
    if any(keyword in hint for keyword in ("简洁", "简短", "直接")):
        return "brief"
    if any(keyword in hint for keyword in ("鼓励", "打气", "积极")):
        return "encouraging"
    if any(keyword in hint for keyword in ("结构", "分点", "计划", "步骤清晰")):
        return "structured"
    if any(keyword in hint for keyword in ("温柔", "陪伴", "安抚", "共情")):
        return "warm"
    return "balanced"


def build_client(target: ResolvedTarget) -> OpenAI:
    if not target.api_key:
        raise HTTPException(status_code=500, detail="当前模型目标没有可用密钥")

    return OpenAI(api_key=target.api_key, base_url=target.base_url)


def build_completion_kwargs(messages: list[dict[str, str]], model_name: Optional[str] = None) -> dict[str, object]:
    resolved_model_name = model_name or configured_model_name()
    payload: dict[str, object] = {
        "model": resolved_model_name,
        "messages": messages,
    }

    if supports_temperature(resolved_model_name):
        payload["temperature"] = current_temperature()

    return payload


def build_messages(
    user_message: str,
    system_hint: Optional[str],
    response_style: Optional[str] = None,
    conversation_history: Optional[list[dict[str, str]]] = None,
    knowledge_hits: Optional[list[KnowledgeHitResult]] = None,
    safety_assessment: Optional[RiskAssessment] = None,
) -> list[dict[str, str]]:
    style = normalize_response_style(response_style, system_hint)
    system_prompt = (
        "你是一个面向大学生的 AI 心理支持与学习辅助助手。"
        "回答时保持温和、具体、不过度承诺，不将自己描述为专业心理医生。"
        "优先做三件事：识别情绪、给出可执行的小建议、必要时提醒寻求线下专业帮助。"
        "不要输出诊断结论，不要给出危险、自伤或伤人建议。"
    )
    system_prompt += "\n回答风格要求：" + STYLE_PROMPTS[style]

    if system_hint:
        system_prompt += "\n额外要求：" + system_hint

    if safety_assessment and safety_assessment.level == "medium":
        system_prompt += "\n安全提醒：" + safety_prompt_extension(safety_assessment)

    if knowledge_hits:
        system_prompt += format_knowledge_prompt(knowledge_hits)

    messages: list[dict[str, str]] = [{"role": "system", "content": system_prompt}]
    if conversation_history:
        messages.extend(conversation_history)
    messages.append({"role": "user", "content": user_message})

    return messages


def render_demo_reply(opening: str, steps: list[str], closing: str, style: str) -> str:
    action_list = "\n".join(f"{index}. {step}" for index, step in enumerate(steps, start=1))

    if style == "brief":
        return f"{opening}\n\n先做这 3 件事：\n{action_list}\n\n{closing}"
    if style == "encouraging":
        return (
            f"{opening}\n\n你不用一次把状态拉满，先拿回一点点主动权就够了：\n"
            f"{action_list}\n\n{closing}"
        )
    if style == "structured":
        return (
            f"{opening}\n\n当前更适合的顺序是：先稳住情绪，再缩小任务，最后决定是否继续推进。\n\n"
            f"建议按下面 3 步来：\n{action_list}\n\n{closing}"
        )
    if style == "warm":
        return (
            f"{opening}\n\n你现在不需要马上变得高效，先让自己从最难受的状态里稍微退出来一点就好。\n\n"
            f"可以温和地试这 3 步：\n{action_list}\n\n{closing}"
        )

    return f"{opening}\n\n可以先试试这 3 步：\n{action_list}\n\n{closing}"


def detect_demo_topic(user_message: str) -> str:
    text = user_message.strip()
    topic_rules = [
        ("interview_anxiety", ("面试", "群面", "二面", "hr", "求职", "简历", "offer", "实习")),
        ("exam_anxiety", ("考试", "期末", "复习", "挂科", "考研", "答辩", "备考")),
        ("procrastination", ("拖延", "不想学", "学不进去", "烦躁", "内耗", "不想开始", "开始不了")),
        ("sleep_exhaustion", ("失眠", "睡不着", "很累", "熬夜", "没精神", "睡眠", "疲惫")),
        ("self_doubt", ("不够好", "没信心", "自卑", "怀疑自己", "我不行", "比不上", "自我否定")),
        ("future_confusion", ("迷茫", "未来", "方向", "前途", "不知道以后", "不知道做什么", "职业选择")),
        ("social_stress", ("社交", "宿舍", "同学", "朋友", "孤独", "人际", "室友")),
        ("pressure_anxiety", ("焦虑", "压力", "慌", "紧张", "崩溃")),
    ]

    for topic, keywords in topic_rules:
        if any(keyword in text for keyword in keywords):
            return topic

    return "general"


def build_demo_reply(
    user_message: str,
    system_hint: Optional[str] = None,
    response_style: Optional[str] = None,
    conversation_history: Optional[list[dict[str, str]]] = None,
    knowledge_hits: Optional[list[KnowledgeHitResult]] = None,
    safety_assessment: Optional[RiskAssessment] = None,
) -> str:
    if safety_assessment and safety_assessment.level == "high":
        return high_risk_reply()

    style = normalize_response_style(response_style, system_hint)
    topic = detect_demo_topic(user_message)

    if topic == "interview_anxiety":
        openings = [
            "面试焦虑很常见，很多人不是不会，而是在面试前把每一次回答都想得太重了。",
            "你现在更像是被“必须表现好”的压力顶住了，所以越准备越容易慌。",
            "面试前紧张并不说明你不行，更多是因为你正在把一场对话当成一次总评判。",
        ]
        step_sets = [
            [
                "先把面试准备压缩成 3 个最高频问题，比如自我介绍、项目亮点和一个失败经历。",
                "每个面试问题只先写 3 个关键词，不要求一次写成长稿，避免越写越僵。",
                "对着手机录 1 次 2 分钟模拟回答，重点看自己卡住的是内容、结构还是语速。",
            ],
            [
                "把“我要表现得很好”改成“我要把经历讲清楚”，先降低面试时的心理负担。",
                "选一个项目，按“做了什么、遇到什么问题、怎么解决、结果怎样”四句结构练一次面试表达。",
                "在正式面试前做一次 5 分钟热身，把嘴巴和思路先带起来，减少开场发紧。",
            ],
            [
                "先只准备今天最需要的 1 轮面试，不要一口气把所有可能问题都堆在脑子里。",
                "把最担心被问到的 2 个面试问题写下来，再各自补一条最核心的回答线索。",
                "如果一想到面试就心跳快，先离开屏幕两分钟，再回来练最短的那一题。",
            ],
        ]
        closings = [
            "如果面试焦虑已经严重影响睡眠和日常状态，先稳住身心状态，比继续堆准备量更重要。",
            "如果你愿意，也可以继续把你最怕被问到的面试问题发出来，我可以按真实面试节奏帮你拆答案。",
            "面试本质上是一次双向了解，不需要把它变成对自我价值的总检验。",
        ]
    elif topic == "exam_anxiety":
        openings = [
            "考试焦虑很常见，尤其当复习范围大、时间紧时，大脑很容易先被压力占满。",
            "你现在未必是真的不会复习，更像是被“复习不完”的感觉压住了启动。",
            "很多考试前的慌，不是能力问题，而是任务范围太大让人一下子进不去。",
        ]
        step_sets = [
            [
                "先把复习拆成最小复习块，比如今天只处理 1 章、1 套题或 3 个知识点。",
                "把“我要复习完”改成“我先完成一个复习块”，避免大脑一上来就被考试总量压住。",
                "做完后立刻写下自己还不会的 2 个点，下一轮复习只盯这 2 个点继续推进。",
            ],
            [
                "先不要急着做整套考试规划，先选最容易提分的一部分开始，比如错题、重点章节或高频题型。",
                "给自己一个 20 分钟复习时间块，只要求开始，不要求这一轮就进入最佳状态。",
                "如果越复习越慌，把慌张写成一句具体担心，再补一句“我下一步先复习哪部分”。",
            ],
            [
                "把最担心的考试科目压缩成今天的核心目标，别同时盯太多科目。",
                "先从看得懂、做得动的题目或知识点开始，先恢复一点复习节奏。",
                "每完成一小段复习，就停下来确认“我现在比 20 分钟前清楚了什么”，帮自己建立进展感。",
            ],
        ]
        closings = [
            "如果考试焦虑已经持续影响到睡眠、饮食或日常功能，及时找老师、同学或心理中心支持会更稳妥。",
            "考试准备更像是逐块推进，而不是一次性扛完整座山。",
            "如果你愿意，也可以继续发你正在准备的科目，我可以把复习块帮你拆得更细一点。",
        ]
    elif topic == "procrastination":
        openings = [
            "这更像是启动成本被情绪放大了，不一定是能力不够。",
            "很多时候拖延不是因为不重视，而是大脑把“开始”这一步放大得太难了。",
            "你现在卡住的点，未必是不会做，而是情绪和任务量一起把启动门槛抬高了。",
        ]
        step_sets = [
            [
                "先不要追求完整学习流程，只做一个 10 到 15 分钟的启动动作。",
                "把任务拆成可以立刻执行的最小步骤，例如打开资料、写标题、列 3 个要点。",
                "完成后给自己一个明确反馈，比如勾掉清单中的第一项，帮助大脑建立“我已经开始了”的信号。",
            ],
            [
                "先选一件最不费力的动作开始，比如打开课件、整理目录或写下要复习的 3 个主题。",
                "把“学一晚上”改成“先做 15 分钟”，先让身体和注意力进入任务。",
                "只要开始了，就允许自己在第一个时间块结束后决定是否继续，不要提前把整晚都想完。",
            ],
            [
                "把当前任务写成一句最小指令，例如“先看第一页并画出重点”。",
                "先把手机、聊天窗口或最容易分心的页面关掉 15 分钟，帮自己减少内耗来源。",
                "做完之后马上记录“我已经推进到哪一步”，不要让大脑继续把事情想成完全没动。",
            ],
        ]
        closings = [
            "如果拖延和烦躁已经持续很久，也可以留意最近是不是压力、睡眠或情绪状态本身就在消耗你。",
            "如果这种内耗已经变成长期状态，最好连同作息、压力源和情绪一起看，而不是只盯着“自律”两个字。",
            "如果你发现自己长期都在这种启动困难里打转，也值得尽快和身边可信任的人聊聊最近的压力来源。",
        ]
    elif topic == "sleep_exhaustion":
        openings = [
            "现在更重要的是先把状态稳住，而不是继续硬扛。",
            "如果身体已经很累，继续逼自己往前推，通常只会让烦躁和低效更明显。",
            "当睡眠和精力状态已经受影响时，先恢复一点基本状态，比继续加码任务更关键。",
        ]
        step_sets = [
            [
                "优先保证一段不被打断的休息时间，哪怕先从短暂闭眼和离开屏幕开始。",
                "把今天必须完成的事压缩到最关键的一项，减少因为任务过多带来的额外消耗。",
                "如果连续多天睡眠和精神状态都很差，尽快找校医院、心理中心或可信任的人聊一聊。",
            ],
            [
                "先暂停继续堆任务，给自己留一段真正不处理信息的缓冲时间。",
                "把今天的目标改成“保住最重要的一件事”，不要再对自己追加额外要求。",
                "如果已经连续几天睡不好，别只靠硬撑，尽快考虑线下求助或就医。",
            ],
            [
                "先把屏幕和高刺激信息关掉几分钟，让身体有机会慢下来。",
                "给今天的任务减负，只留最核心的一项，其他往后顺延。",
                "一旦发现失眠和疲惫已经持续，就要把它当成需要认真处理的信号，而不是小问题。",
            ],
        ]
        closings = [
            "如果这种状态已经连续几天甚至更久，尽快联系校医院、心理中心或可信任的成年人会更稳妥。",
            "如果疲惫和睡眠问题已经明显影响学习和生活，建议尽快找线下支持，不必一个人扛。",
            "如果已经出现持续失眠或明显的身心耗竭，及时寻求专业帮助会比继续硬撑更有效。",
        ]
    elif topic == "self_doubt":
        openings = [
            "这类自我怀疑很消耗人，因为你现在不仅在处理问题本身，还在同时否定自己。",
            "你现在难受的可能不只是事情没做好，而是脑子里一直在重复“我是不是不够好”。",
            "自我否定一旦上来，大脑会更容易忽略已经做成的部分，只盯着不够好的地方。",
        ]
        step_sets = [
            [
                "先不要急着证明自己行不行，先把当前最具体的一件事处理好，减少自我评价的噪音。",
                "写下 1 件你已经做过并且做成的事，让自己暂时从“全盘否定”里退出来。",
                "把“我不够好”换成“我现在最需要补哪一步”，让注意力回到可改进的部分。",
            ],
            [
                "先区分“事实”和“情绪判断”，例如事实是“我这次表现一般”，不是“我就是不行”。",
                "给自己一个小目标，只要求推进，不要求立刻证明价值。",
                "完成后记录一个客观反馈，帮自己重新建立比较稳定的自我评价。",
            ],
            [
                "先暂停反复回想哪里不够好，把问题缩成今天能修的一件小事。",
                "如果总在拿自己和别人比较，先把比较对象关掉 15 分钟，只看自己的下一步动作。",
                "做完后提醒自己：一次状态不好不等于整体能力不好。",
            ],
        ]
        closings = [
            "如果这种自我否定已经持续很久，及时和心理中心、辅导员或可信任的人聊聊会更有帮助。",
            "你现在需要的未必是立刻变强，而是先让自己从持续打击里缓一口气。",
            "如果你愿意，也可以继续说说最近是哪件事最容易触发你的自我怀疑。",
        ]
    elif topic == "future_confusion":
        openings = [
            "未来迷茫很正常，尤其在专业、就业和自我期待交织在一起的时候，很容易一下子看不清方向。",
            "你现在未必是真的没有方向，而是选项太多、评价太重，反而让人不敢先动。",
            "当“未来怎么办”这个问题太大时，大脑往往会先卡住，而不是马上给出清晰答案。",
        ]
        step_sets = [
            [
                "先别急着决定整条未来路线，只先确认最近 1 到 2 个月最值得尝试的一个方向。",
                "把迷茫拆成几个具体问题，例如“我更想做什么”“我能先试什么”“我缺什么信息”。",
                "选一个最低成本的探索动作，比如和学长聊一次、看一个岗位描述或做一版简历草稿。",
            ],
            [
                "先不要同时想所有可能性，只保留两个最现实的方向做比较。",
                "给每个方向各写 3 个吸引你的点和 3 个你担心的点，帮助自己从模糊迷茫变成可讨论的问题。",
                "这周只推进一个探索动作，不要求立刻得出最终答案。",
            ],
            [
                "把“我以后怎么办”改成“我下一个月想确认什么”，缩小问题范围。",
                "优先去补最缺的信息，而不是只在脑子里反复猜。",
                "每做完一次小探索，就更新一次自己的判断，不需要一开始就看得很远。",
            ],
        ]
        closings = [
            "方向感通常不是突然想出来的，而是在尝试和反馈里慢慢长出来的。",
            "如果你愿意，我也可以继续帮你把“未来迷茫”拆成更具体的选择题，而不是留在一个很大的问题里。",
            "现在先迈出一个探索动作，比逼自己立刻找到标准答案更重要。",
        ]
    elif topic == "social_stress":
        openings = [
            "人际和社交带来的消耗很真实，因为它不只是事情本身，还会牵动安全感和自我评价。",
            "如果最近宿舍、同学或朋友关系让你很累，先承认这种消耗本身就是会影响学习和状态的。",
            "社交压力最难受的地方，往往在于事情结束了，脑子还会继续反复想。",
        ]
        step_sets = [
            [
                "先把最困扰你的一段关系或一件事说清楚，别让所有社交压力混成一团。",
                "区分“我能处理的部分”和“暂时超出我控制的部分”，先别把所有责任都压到自己身上。",
                "给自己留一点从这段社交压力里抽开的时间，哪怕只是暂时少看消息、少反复回想。",
            ],
            [
                "先确认你现在最需要的是沟通、拉开距离，还是先稳定自己的情绪。",
                "如果要沟通，只先表达一件最核心的感受，不要一次把所有委屈都压进去。",
                "如果暂时不适合沟通，先把生活节奏稳住，别让这段关系拖垮整天状态。",
            ],
            [
                "先不要急着判断谁对谁错，先让自己从最上头的情绪里退一点出来。",
                "把最让你难受的触发点写下来，帮助自己看清到底是什么在消耗你。",
                "完成后优先做一件能让身体放松的事，别让社交压力继续占满整天。",
            ],
        ]
        closings = [
            "如果这段人际压力已经持续影响到睡眠、学习和情绪，也值得尽快找可信任的人一起想办法。",
            "社交问题不一定要立刻解决，但你可以先把自己从持续消耗里拉出来一点。",
            "如果你愿意，也可以继续说说最近具体是哪段关系最让你累。",
        ]
    elif topic == "pressure_anxiety":
        openings = [
            "能感觉到你现在已经被压力推得很紧了，先别要求自己立刻恢复到高效率。",
            "你现在更像是被压力一直顶着走，越想快点进入状态，越容易更慌。",
            "这种紧绷感很常见，尤其在任务堆积的时候，大脑会先被压力占满。",
        ]
        step_sets = [
            [
                "把目标缩到 15 分钟，只做一件最容易开始的小任务，比如整理提纲或看两页笔记。",
                "写下眼下最担心的一件事，再写一个能在今天完成的应对动作，避免脑子里反复打转。",
                "做完这一小步后先暂停 3 分钟，喝水、走动或深呼吸，再决定要不要继续下一步。",
            ],
            [
                "先把“我要赶紧恢复状态”改成“我先完成一个最小动作”，降低启动门槛。",
                "把今天的任务压缩成 1 个核心目标和 1 个保底目标，别让任务列表继续扩大压力。",
                "如果心跳快、脑子乱，先离开屏幕两三分钟，再回来处理最小那一项。",
            ],
            [
                "先不要整块规划整天，只选现在最容易动手的一件事。",
                "把担心写成一句话，再在后面补一句“我此刻能做的是……”，把注意力拉回行动。",
                "完成后给自己一个暂停点，不要一开始就要求连续高强度推进。",
            ],
        ]
        closings = [
            "如果这种压迫感已经持续很久，或者已经影响到睡眠、饮食和日常功能，建议尽快联系学校心理中心、辅导员或可信任的成年人获得线下支持。",
            "如果这种紧绷状态已经连续很多天，甚至开始影响睡眠和日常生活，最好尽快找学校心理中心、辅导员或可信任的人聊一聊。",
            "如果压力已经超出自己能慢慢消化的范围，及时寻求线下支持会比一个人硬扛更有效。",
        ]
    else:
        openings = [
            "你现在的状态值得先被看见，不需要一开始就把所有问题一次解决。",
            "先别急着要求自己立刻想明白全部，很多问题都是在行动里慢慢变清楚的。",
            "现在更适合先把问题收窄，而不是一上来就要求自己把整件事想透。",
        ]
        step_sets = [
            [
                "先说清楚眼下最困扰你的一个点，把问题收窄到可处理的范围内。",
                "给自己设一个很小的行动目标，优先恢复一点点掌控感。",
                "完成后再决定下一步，而不是一开始就要求自己把整件事做完。",
            ],
            [
                "先把“我到底怎么了”换成“我现在最卡的是哪一步”，减少模糊焦虑。",
                "只挑一个今天能推进的小动作，先把注意力从担心拉回到行动。",
                "做完这一小步后，再看需不需要继续，而不是提前被整件事压住。",
            ],
            [
                "用一句话写下你现在最想解决的核心问题。",
                "把它拆成一个今天能完成的小步骤，哪怕只推进 10 分钟也可以。",
                "先完成这一步，再重新判断接下来最值得做什么。",
            ],
        ]
        closings = [
            "如果你愿意，也可以继续把当前最卡的那个点说得更具体一点，我再帮你一起拆。",
            "如果这种状态已经持续很久，或者已经明显影响到日常生活，也值得尽快找线下支持一起处理。",
            "如果你发现自己已经长期被这类问题困住，及时和可信任的人或专业老师聊聊会更有帮助。",
        ]

    opening = secrets.choice(openings)
    steps = secrets.choice(step_sets)
    closing = secrets.choice(closings)
    reply = render_demo_reply(opening, steps, closing, style)

    if conversation_history:
        last_user_messages = [item["content"] for item in conversation_history if item["role"] == "user"]
        if last_user_messages:
            recent = last_user_messages[-1][:28]
            reply = f"延续你前面提到的“{recent}”，这次可以把重点放得更具体一些。\n\n{reply}"

    if knowledge_hits:
        references = "\n".join(f"- {hit.title}：{hit.excerpt}" for hit in knowledge_hits[:2])
        reply += f"\n\n结合当前知识库，还可以参考这两个方向：\n{references}"

    if safety_assessment and safety_assessment.level == "medium":
        reply += f"\n\n额外提醒：{safety_assessment.note}"

    return reply


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    target = build_configured_target()
    return HealthResponse(
        status="ok",
        service="zhiyuxing-ai-assistant",
        version=app.version,
        mode=target.mode,
        api_key_configured=api_key_configured(),
        api_key_env=configured_api_key_env(),
        provider_name=target.provider_name,
        model_name=target.model_name,
        persistence_enabled=True,
        knowledge_document_count=knowledge_document_count(),
    )


@app.get("/", include_in_schema=False)
def index() -> FileResponse:
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/api/meta", response_model=ServiceInfo)
def meta() -> ServiceInfo:
    target = build_configured_target()
    return ServiceInfo(
        name=app.title,
        version=app.version,
        description="可直接运行的 AI 情绪支持与学习辅助服务，支持本地演示模式和模型调用模式。",
        docs_url="/docs",
        healthcheck="/health",
        demo_page="/",
        deployment_note="/project-docs/dingtalk-integration.md",
        compatibility_url="/api/compatibility",
        chat_mode=target.mode,
        api_key_configured=api_key_configured(),
        api_key_env=configured_api_key_env(),
        provider_name=target.provider_name,
        model_name=target.model_name,
        base_url=target.base_url,
        model_doc="/project-docs/model-integration.md",
        supports_temperature=supports_temperature(target.model_name),
        persistence_enabled=True,
        knowledge_document_count=knowledge_document_count(),
        session_history_url="/api/session/{session_id}",
        feedback_url="/api/feedback",
        knowledge_search_url="/api/knowledge/search?q=关键词",
        available_models=list_model_options(),
        available_styles=STYLE_OPTIONS,
    )


@app.get("/api/compatibility", response_model=CompatibilityReport)
def compatibility() -> CompatibilityReport:
    return evaluate_runtime_compatibility()


@app.get("/api/knowledge/search", response_model=KnowledgeSearchResponse)
def knowledge_search(q: str = Query(..., min_length=2, description="检索关键词")) -> KnowledgeSearchResponse:
    hits = search_knowledge(q)
    return KnowledgeSearchResponse(query=q, total_hits=len(hits), hits=to_knowledge_models(hits))


@app.get("/api/session/{session_id}", response_model=SessionHistoryResponse)
def get_session_history(session_id: str) -> SessionHistoryResponse:
    payload = session_history(session_id)
    return SessionHistoryResponse(
        session_id=payload["session_id"],
        title=payload["title"],
        created_at=payload["created_at"],
        updated_at=payload["updated_at"],
        total_messages=payload["total_messages"],
        messages=[SessionMessage(**message) for message in payload["messages"]],
    )


@app.post("/api/feedback", response_model=FeedbackResponse)
def feedback(req: FeedbackRequest) -> FeedbackResponse:
    save_feedback(req.session_id, req.assistant_message_id, req.rating, req.comment)
    return FeedbackResponse(status="ok", message="反馈已记录，可用于后续改进回复质量。")


@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest) -> ChatResponse:
    target = resolve_model_target(req.model_target)
    style = normalize_response_style(req.response_style, req.system_hint)
    session_id = ensure_session(req.session_id, req.message)
    conversation_history = recent_messages(session_id, limit=6)
    knowledge_hits = search_knowledge(req.message, limit=3)
    safety_assessment = assess_risk(req.message)

    if safety_assessment.level == "high":
        reply = high_risk_reply()
        assistant_message_id = save_turn(
            session_id,
            req.message,
            reply,
            response_style=style,
            provider_name="Safety Guardrail",
            model_name="high-risk-template",
            mode="guardrail",
            risk_level=safety_assessment.level,
            knowledge_sources=knowledge_sources(knowledge_hits),
        )
        return ChatResponse(
            reply=reply,
            note="检测到高风险表达，已优先切换到固定安全转介回复，而不是继续普通模型对话。",
            mode="guardrail",
            provider_name="Safety Guardrail",
            model_name="high-risk-template",
            response_style=style,
            session_id=session_id,
            assistant_message_id=assistant_message_id,
            memory_messages_used=len(conversation_history),
            knowledge_hits=to_knowledge_models(knowledge_hits),
            safety=to_safety_info(safety_assessment),
        )

    if target.mode == "demo":
        reply = build_demo_reply(
            req.message,
            req.system_hint,
            style,
            conversation_history=conversation_history,
            knowledge_hits=knowledge_hits,
            safety_assessment=safety_assessment,
        )
        assistant_message_id = save_turn(
            session_id,
            req.message,
            reply,
            response_style=style,
            provider_name=target.provider_name,
            model_name=target.model_name,
            mode=target.mode,
            risk_level=safety_assessment.level,
            knowledge_sources=knowledge_sources(knowledge_hits),
        )
        knowledge_note = ""
        if knowledge_hits:
            knowledge_note = " 已结合本地知识库片段增强建议。"
        safety_note = ""
        if safety_assessment.level == "medium":
            safety_note = " 同时检测到需要额外关注的状态，回复里已补充线下支持提醒。"
        return ChatResponse(
            reply=reply,
            note=(
                f"当前为本地演示模式。已按“{STYLE_LABELS[style]}”返回演示回复；"
                f"本轮使用了 {len(conversation_history)} 条会话记忆。{knowledge_note}{safety_note}"
            ).strip(),
            mode=target.mode,
            provider_name=target.provider_name,
            model_name=target.model_name,
            response_style=style,
            session_id=session_id,
            assistant_message_id=assistant_message_id,
            memory_messages_used=len(conversation_history),
            knowledge_hits=to_knowledge_models(knowledge_hits),
            safety=to_safety_info(safety_assessment),
        )

    try:
        client = build_client(target)
        completion = client.chat.completions.create(
            **build_completion_kwargs(
                build_messages(
                    req.message,
                    req.system_hint,
                    style,
                    conversation_history=conversation_history,
                    knowledge_hits=knowledge_hits,
                    safety_assessment=safety_assessment,
                ),
                model_name=target.model_name,
            )
        )
        reply = completion.choices[0].message.content or "抱歉，我这次没有成功生成回复。"
        assistant_message_id = save_turn(
            session_id,
            req.message,
            reply,
            response_style=style,
            provider_name=target.provider_name,
            model_name=target.model_name,
            mode=target.mode,
            risk_level=safety_assessment.level,
            knowledge_sources=knowledge_sources(knowledge_hits),
        )
        note = (
            f"当前为模型调用模式。回复由 {target.provider_name} / {target.model_name} 生成，"
            f"风格为“{STYLE_LABELS[style]}”，使用了 {len(conversation_history)} 条会话记忆。"
        )
        if knowledge_hits:
            note += f" 已结合 {len(knowledge_hits)} 条知识库片段。"
        if safety_assessment.level == "medium":
            note += " 当前表达需要额外关注，系统已加强安全提醒。"
        return ChatResponse(
            reply=reply,
            note=note,
            mode=target.mode,
            provider_name=target.provider_name,
            model_name=target.model_name,
            response_style=style,
            session_id=session_id,
            assistant_message_id=assistant_message_id,
            memory_messages_used=len(conversation_history),
            knowledge_hits=to_knowledge_models(knowledge_hits),
            safety=to_safety_info(safety_assessment),
        )
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"调用模型失败：{exc}") from exc
