from __future__ import annotations

import os
import time
from pathlib import Path
from typing import Optional
from openai import OpenAI


BASE_DIR = Path(__file__).resolve().parents[1]
ENV_FILE = BASE_DIR / ".env"
ENV_EXAMPLE = BASE_DIR / ".env.example"


def save_runtime_settings(
    provider: str,
    model_name: str,
    base_url: str,
    api_key: Optional[str] = None,
    temperature: Optional[float] = None,
    demo_mode: Optional[bool] = None,
) -> dict:
    """Update runtime model settings immediately and persist to .env."""
    prov_lower = provider.lower()
    base_lower = base_url.lower()
    model_lower = model_name.lower()

    if "orcarouter" in prov_lower or "orcarouter" in base_lower:
        key_env = "ORCAROUTER_API_KEY"
    elif "deepseek" in prov_lower or "deepseek" in base_lower or model_lower.startswith("deepseek"):
        key_env = "DEEPSEEK_API_KEY"
    else:
        key_env = "OPENAI_API_KEY"

    # 1. Update active process environment
    os.environ["MODEL_PROVIDER"] = provider
    os.environ["MODEL_NAME"] = model_name
    os.environ["OPENAI_BASE_URL"] = base_url
    os.environ["MODEL_API_KEY_ENV"] = key_env

    if temperature is not None:
        os.environ["MODEL_TEMPERATURE"] = str(temperature)
    if demo_mode is not None:
        os.environ["DEMO_MODE"] = "true" if demo_mode else "false"

    if api_key is not None:
        clean_key = api_key.strip()
        if clean_key:
            os.environ[key_env] = clean_key
        elif key_env in os.environ:
            del os.environ[key_env]

    # 2. Persist to local .env file
    try:
        env_dict: dict[str, str] = {}
        if ENV_FILE.exists():
            for line in ENV_FILE.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    env_dict[k.strip()] = v.strip()
        elif ENV_EXAMPLE.exists():
            for line in ENV_EXAMPLE.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    env_dict[k.strip()] = v.strip()

        env_dict["MODEL_PROVIDER"] = provider
        env_dict["MODEL_NAME"] = model_name
        env_dict["OPENAI_BASE_URL"] = base_url
        env_dict["MODEL_API_KEY_ENV"] = key_env
        if temperature is not None:
            env_dict["MODEL_TEMPERATURE"] = str(temperature)
        if demo_mode is not None:
            env_dict["DEMO_MODE"] = "true" if demo_mode else "false"
        if api_key is not None:
            env_dict[key_env] = api_key.strip()

        output_lines = [
            "# =======================================================",
            "# ZhiYuXing AI Copilot Model Configuration",
            "# Updated via Web Console",
            "# =======================================================",
            f"MODEL_PROVIDER={env_dict.get('MODEL_PROVIDER', provider)}",
            f"MODEL_NAME={env_dict.get('MODEL_NAME', model_name)}",
            f"OPENAI_BASE_URL={env_dict.get('OPENAI_BASE_URL', base_url)}",
            f"MODEL_API_KEY_ENV={key_env}",
            f"MODEL_TEMPERATURE={env_dict.get('MODEL_TEMPERATURE', '0.7')}",
            f"DEMO_MODE={env_dict.get('DEMO_MODE', 'false')}",
            f"CHAT_DB_PATH={env_dict.get('CHAT_DB_PATH', '')}",
        ]
        for k in ("OPENAI_API_KEY", "DEEPSEEK_API_KEY", "ORCAROUTER_API_KEY"):
            if k in env_dict:
                output_lines.append(f"{k}={env_dict[k]}")

        ENV_FILE.write_text("\n".join(output_lines) + "\n", encoding="utf-8")
    except Exception as exc:
        print(f"Warning: could not write to .env: {exc}")

    current_key = os.getenv(key_env)
    is_demo = os.getenv("DEMO_MODE", "false").lower() in ("1", "true") or not current_key

    return {
        "provider": provider,
        "model_name": model_name,
        "base_url": base_url,
        "key_env": key_env,
        "has_key": bool(current_key),
        "mode": "demo" if is_demo else "openai",
    }


def test_connection_probe(
    provider: Optional[str] = None,
    model_name: Optional[str] = None,
    base_url: Optional[str] = None,
    api_key: Optional[str] = None,
) -> tuple[bool, str, float]:
    """Perform a live API probe to check if model credentials work."""
    resolved_provider = provider or os.getenv("MODEL_PROVIDER", "DeepSeek")
    resolved_model = model_name or os.getenv("MODEL_NAME", "deepseek-chat")
    resolved_base_url = base_url or os.getenv("OPENAI_BASE_URL", "https://api.deepseek.com")

    key_env = os.getenv("MODEL_API_KEY_ENV", "OPENAI_API_KEY")
    resolved_key = (
        api_key
        or os.getenv(key_env)
        or os.getenv("DEEPSEEK_API_KEY")
        or os.getenv("OPENAI_API_KEY")
        or os.getenv("ORCAROUTER_API_KEY")
    )

    if not resolved_key:
        return False, "未检测到 API Key，请先输入对应模型的密钥后再测试连通性。", 0.0

    t0 = time.time()
    try:
        client = OpenAI(api_key=resolved_key, base_url=resolved_base_url, timeout=12.0)
        messages = [
            {"role": "system", "content": "You are a connectivity test assistant."},
            {"role": "user", "content": "ping"},
        ]
        kwargs: dict[str, object] = {
            "model": resolved_model,
            "messages": messages,
            "max_tokens": 5,
        }
        if resolved_model.lower() != "deepseek-reasoner":
            kwargs["temperature"] = 0.7

        resp = client.chat.completions.create(**kwargs)
        latency = round((time.time() - t0) * 1000, 2)
        reply_content = resp.choices[0].message.content or "OK"
        return True, f"连通成功！模型已成功响应: '{reply_content.strip()}'", latency
    except Exception as exc:
        latency = round((time.time() - t0) * 1000, 2)
        return False, f"调用失败: {exc}", latency
