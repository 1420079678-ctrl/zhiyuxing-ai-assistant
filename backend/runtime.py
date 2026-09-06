from __future__ import annotations

from fastapi import HTTPException
from openai import OpenAI

from backend.config import (
    BASE_DIR,
    MODEL_PRESETS,
    MODEL_PRESET_MAP,
    api_key_configured,
    configured_api_key,
    configured_api_key_env,
    configured_base_url,
    configured_model_name,
    configured_provider_name,
    current_chat_mode,
    current_temperature,
    env_flag,
    public_demo_mode,
    resolve_api_key,
    supports_temperature,
)
from backend.schemas import CompatibilityCheckItem, CompatibilityReport, ModelOption, QuickSetupOption, ResolvedTarget


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
    if public_demo_mode() or env_flag("DEMO_MODE") or not configured_target.api_key:
        return build_demo_target()
    return configured_target


def resolve_model_target(
    model_target: str | None,
    custom_provider: str | None = None,
    custom_base_url: str | None = None,
    custom_api_key: str | None = None,
) -> ResolvedTarget:
    if public_demo_mode():
        return build_demo_target()

    # If explicit custom parameters (provider/base_url/api_key) are provided along with a model target
    clean_base_url = (custom_base_url or "").strip()
    clean_api_key = (custom_api_key or "").strip()
    clean_provider = (custom_provider or "").strip()

    if clean_base_url:
        configured = build_configured_target()
        model_name = (model_target or "").strip()
        if model_name.startswith("custom:"):
            model_name = model_name[7:].strip()
        if not model_name or model_name in {"configured", "custom"}:
            model_name = configured.model_name or "custom-model"

        provider_name = clean_provider or configured.provider_name or "Custom Provider"
        resolved_key = clean_api_key or configured.api_key
        if not resolved_key and not env_flag("DEMO_MODE"):
            # Check if ollama or local service where key can be placeholder
            if "11434" not in clean_base_url and "localhost" not in clean_base_url:
                raise HTTPException(status_code=400, detail="自定义模型缺少 API Key")

        return ResolvedTarget(
            id=f"custom:{model_name}",
            label=f"{provider_name} · {model_name}",
            mode="openai",
            provider_name=provider_name,
            model_name=model_name,
            base_url=clean_base_url,
            api_key=resolved_key or "local-key",
            api_key_env=None,
        )

    target_id = (model_target or "configured").strip().lower()

    if target_id == "configured":
        return build_configured_target()
    if target_id == "demo":
        return build_demo_target()
    if target_id == "custom" or target_id.startswith("custom:"):
        configured = build_configured_target()
        if target_id.startswith("custom:") and len(target_id) > 7:
            custom_model = model_target.strip()[7:].strip()
            if custom_model:
                return ResolvedTarget(
                    id=f"custom:{custom_model}",
                    label=f"{clean_provider or configured.provider_name} · {custom_model}",
                    mode=configured.mode,
                    provider_name=clean_provider or configured.provider_name,
                    model_name=custom_model,
                    base_url=clean_base_url or configured.base_url,
                    api_key=clean_api_key or configured.api_key,
                    api_key_env=configured.api_key_env,
                )
        return configured

    preset = MODEL_PRESET_MAP.get(target_id)
    if not preset:
        # Check if the target matches current configured model name
        current_cfg = build_configured_snapshot()
        if target_id == current_cfg.model_name.lower():
            return build_configured_target()
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

    if public_demo_mode():
        configured_reason = "PUBLIC_DEMO_MODE=true，当前服务固定为受限公开演示模式"
    elif env_flag("DEMO_MODE"):
        configured_reason = "DEMO_MODE=true，当前配置会强制回退到本地演示模式"
    elif not configured_target.api_key and configured_target.api_key_env:
        configured_reason = f"未配置 {configured_target.api_key_env}，当前会回退到本地演示模式"

    is_preset_model = any(preset.model_name.lower() == configured_target.model_name.lower() for preset in MODEL_PRESETS)
    configured_label = (
        f"当前配置模型（{configured_target.provider_name} / {configured_target.model_name}）"
        if is_preset_model
        else f"自定义配置模型（{configured_target.provider_name} / {configured_target.model_name}）"
    )

    options = [
        ModelOption(
            id="configured",
            label=configured_label,
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
    if "qwen" in normalized:
        return "qwen"
    if "moonshot" in normalized or "kimi" in normalized:
        return "moonshot"
    if "glm" in normalized:
        return "zhipu"
    if "llama" in normalized:
        return "groq"
    return "compatible"


def detect_endpoint_family(base_url: str) -> str:
    normalized = base_url.strip().lower().rstrip("/")
    if "api.deepseek.com" in normalized:
        return "deepseek"
    if "api.openai.com" in normalized:
        return "openai"
    if "dashscope.aliyuncs.com" in normalized:
        return "qwen"
    if "api.moonshot.cn" in normalized:
        return "moonshot"
    if "bigmodel.cn" in normalized:
        return "zhipu"
    if "api.siliconflow.cn" in normalized:
        return "siliconflow"
    if "api.groq.com" in normalized:
        return "groq"
    if "11434" in normalized or "localhost" in normalized or "127.0.0.1" in normalized:
        return "ollama"
    return "compatible"


def detect_provider_family(provider_name: str) -> str:
    normalized = provider_name.strip().lower()
    if "deepseek" in normalized:
        return "deepseek"
    if "openai" in normalized:
        return "openai"
    if "qwen" in normalized or "tongyi" in normalized or "aliyun" in normalized:
        return "qwen"
    if "moonshot" in normalized or "kimi" in normalized:
        return "moonshot"
    if "zhipu" in normalized or "glm" in normalized:
        return "zhipu"
    if "siliconflow" in normalized:
        return "siliconflow"
    if "groq" in normalized:
        return "groq"
    if "ollama" in normalized:
        return "ollama"
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

    if public_demo_mode():
        add_check("public-demo-mode", "warning", "PUBLIC_DEMO_MODE=true，当前服务固定为受限公开演示模式，不会发起真实模型调用。")
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

    if (
        provider_family in {"openai", "deepseek"}
        and model_family in {"openai", "deepseek"}
        and provider_family != model_family
    ):
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
    ready_for_model_call = not public_demo_mode() and not env_flag("DEMO_MODE") and bool(configured_target.api_key) and not has_error

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


def build_client(target: ResolvedTarget) -> OpenAI:
    if not target.api_key:
        raise HTTPException(status_code=500, detail="当前模型目标没有可用密钥")

    return OpenAI(api_key=target.api_key, base_url=target.base_url)


def build_completion_kwargs(messages: list[dict[str, str]], model_name: str | None = None) -> dict[str, object]:
    resolved_model_name = model_name or configured_model_name()
    payload: dict[str, object] = {
        "model": resolved_model_name,
        "messages": messages,
    }

    if supports_temperature(resolved_model_name):
        payload["temperature"] = current_temperature()

    return payload


def probe_configured_model() -> str:
    configured_target = build_configured_snapshot()

    if public_demo_mode():
        raise HTTPException(status_code=400, detail="PUBLIC_DEMO_MODE=true，当前不会发起真实模型调用。")
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
