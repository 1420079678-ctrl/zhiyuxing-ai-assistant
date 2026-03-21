from __future__ import annotations

import argparse
import sys
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[1]
ENV_FILE = BASE_DIR / ".env"
ENV_EXAMPLE = BASE_DIR / ".env.example"

PRESETS = {
    "openai": {
        "OPENAI_BASE_URL": "https://api.openai.com/v1",
        "MODEL_NAME": "gpt-4o-mini",
        "MODEL_PROVIDER": "OpenAI",
        "MODEL_API_KEY_ENV": "OPENAI_API_KEY",
        "MODEL_TEMPERATURE": "0.7",
        "DEMO_MODE": "false",
    },
    "deepseek-chat": {
        "OPENAI_BASE_URL": "https://api.deepseek.com",
        "MODEL_NAME": "deepseek-chat",
        "MODEL_PROVIDER": "DeepSeek",
        "MODEL_API_KEY_ENV": "DEEPSEEK_API_KEY",
        "MODEL_TEMPERATURE": "0.7",
        "DEMO_MODE": "false",
    },
    "deepseek-r1": {
        "OPENAI_BASE_URL": "https://api.deepseek.com",
        "MODEL_NAME": "deepseek-reasoner",
        "MODEL_PROVIDER": "DeepSeek",
        "MODEL_API_KEY_ENV": "DEEPSEEK_API_KEY",
        "MODEL_TEMPERATURE": "0.7",
        "DEMO_MODE": "false",
    },
}

ENV_ORDER = [
    "OPENAI_API_KEY",
    "DEEPSEEK_API_KEY",
    "OPENAI_BASE_URL",
    "MODEL_NAME",
    "MODEL_PROVIDER",
    "MODEL_API_KEY_ENV",
    "MODEL_TEMPERATURE",
    "DEMO_MODE",
]


def parse_env_lines(text: str) -> tuple[dict[str, str], list[str]]:
    data: dict[str, str] = {}
    comments: list[str] = []

    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if line.startswith("#"):
            comments.append(line)
            continue
        if "=" not in raw_line:
            continue

        key, value = raw_line.split("=", 1)
        data[key.strip()] = value.strip()

    return data, comments


def load_env_data() -> tuple[dict[str, str], list[str]]:
    if ENV_FILE.exists():
        return parse_env_lines(ENV_FILE.read_text(encoding="utf-8"))
    if ENV_EXAMPLE.exists():
        return parse_env_lines(ENV_EXAMPLE.read_text(encoding="utf-8"))
    return {}, ["# 留空时会自动使用本地演示模式"]


def prompt_if_needed(api_key: str | None, env_name: str, existing_value: str) -> str:
    if api_key is not None:
        return api_key.strip()
    if existing_value:
        return existing_value
    if not sys.stdin.isatty():
        return ""

    prompt = f"请输入 {env_name}（可直接回车留空，此时仍可用本地演示模式运行）: "
    return input(prompt).strip()


def render_env(data: dict[str, str], comments: list[str]) -> str:
    lines: list[str] = []
    header_comments = comments or ["# 留空时会自动使用本地演示模式"]

    for comment in header_comments:
        if comment not in lines:
            lines.append(comment)

    for key in ENV_ORDER:
        lines.append(f"{key}={data.get(key, '')}")

    extra_keys = sorted(key for key in data if key not in ENV_ORDER)
    for key in extra_keys:
        lines.append(f"{key}={data[key]}")

    return "\n".join(lines) + "\n"


def resolve_python_command() -> str:
    venv_python = BASE_DIR / ".venv" / "Scripts" / "python.exe"
    if venv_python.exists():
        return r".\.venv\Scripts\python"
    return "python"


def main() -> int:
    parser = argparse.ArgumentParser(description="Write one-click model settings into .env")
    parser.add_argument("--preset", choices=sorted(PRESETS), required=True)
    parser.add_argument("--api-key")
    parser.add_argument("--base-url")
    parser.add_argument("--model-name")
    parser.add_argument("--provider-name")
    parser.add_argument("--api-key-env")
    parser.add_argument("--temperature")
    parser.add_argument("--demo-mode", choices=["true", "false"])
    args = parser.parse_args()

    env_data, comments = load_env_data()
    preset = dict(PRESETS[args.preset])

    if args.base_url:
        preset["OPENAI_BASE_URL"] = args.base_url.strip()
    if args.model_name:
        preset["MODEL_NAME"] = args.model_name.strip()
    if args.provider_name:
        preset["MODEL_PROVIDER"] = args.provider_name.strip()
    if args.api_key_env:
        preset["MODEL_API_KEY_ENV"] = args.api_key_env.strip()
    if args.temperature:
        preset["MODEL_TEMPERATURE"] = args.temperature.strip()
    if args.demo_mode:
        preset["DEMO_MODE"] = args.demo_mode.strip()

    key_env_name = preset["MODEL_API_KEY_ENV"]
    api_key_value = prompt_if_needed(args.api_key, key_env_name, env_data.get(key_env_name, ""))

    env_data.update(preset)
    env_data.setdefault("OPENAI_API_KEY", "")
    env_data.setdefault("DEEPSEEK_API_KEY", "")
    env_data[key_env_name] = api_key_value

    ENV_FILE.write_text(render_env(env_data, comments), encoding="utf-8")

    print(f"已写入 {ENV_FILE}")
    print(
        "当前模型配置："
        f"{env_data['MODEL_PROVIDER']} / {env_data['MODEL_NAME']} / {env_data['OPENAI_BASE_URL']}"
    )
    print(f"当前密钥变量：{key_env_name}")
    if api_key_value:
        print(f"已写入 {key_env_name}。")
    else:
        print(f"{key_env_name} 仍为空；项目仍可运行，但会回退到本地演示模式。")

    python_command = resolve_python_command()
    print("建议下一步运行：")
    print(f"  {python_command} scripts\\check_model_config.py")
    print(r"  .\start-web.ps1")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
