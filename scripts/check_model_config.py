from __future__ import annotations

import argparse
import sys
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[1]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from app import evaluate_runtime_compatibility, probe_configured_model


def main() -> int:
    parser = argparse.ArgumentParser(description="Check whether the current .env can call the configured model.")
    parser.add_argument("--json", action="store_true", help="Output raw JSON instead of a readable summary.")
    parser.add_argument("--probe", action="store_true", help="Send a real minimal request to verify the configured model.")
    parser.add_argument("--strict", action="store_true", help="Treat warnings as a failing result.")
    args = parser.parse_args()

    report = evaluate_runtime_compatibility()
    if args.json:
        print(report.model_dump_json(indent=2))
    else:
        print(report.summary)
        print(f"运行模式: {report.mode}")
        print(f"当前提供商: {report.provider_name}")
        print(f"当前模型: {report.model_name}")
        print(f"API 地址: {report.base_url}")
        print(f"密钥变量: {report.api_key_env or '未指定'}")
        print("")
        print("检查明细:")
        for item in report.checks:
            tag = item.status.upper().ljust(7)
            print(f"[{tag}] {item.message}")
        print("")
        print("一键配置命令:")
        for option in report.recommended_setups:
            print(f"- {option.label}: {option.command}")

    if args.probe:
        if not report.ready_for_model_call:
            print("")
            print("未执行真实探测：当前配置还没有达到可调用真实模型的状态。")
            return 1

        print("")
        print("正在执行真实模型探测...")
        try:
            reply = probe_configured_model()
        except Exception as exc:
            print(f"真实探测失败：{exc}")
            return 1

        print("真实探测成功。模型已返回内容：")
        print(reply)

    if report.status == "error":
        return 1
    if args.strict and report.status == "warning":
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
