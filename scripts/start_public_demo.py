from __future__ import annotations

import argparse
import os
import re
import socket
import subprocess
import sys
import time
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[1]
URL_PATTERN = re.compile(r"https?://[^\s]+")


def wait_for_port(host: str, port: int, timeout: float = 20.0) -> bool:
    deadline = time.time() + timeout
    while time.time() < deadline:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(1.0)
            if sock.connect_ex((host, port)) == 0:
                return True
        time.sleep(0.3)
    return False


def terminate_process(process: subprocess.Popen[str] | None) -> None:
    if process is None or process.poll() is not None:
        return
    process.terminate()
    try:
        process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        process.kill()


def choose_public_url(line: str) -> str | None:
    for candidate in URL_PATTERN.findall(line):
        normalized = candidate.rstrip("].,)")
        if "twitter.com/localhost_run" in normalized:
            continue
        if "admin.localhost.run" in normalized:
            continue
        if ".lhr.life" in normalized:
            return normalized
        if normalized.startswith("https://") and normalized.endswith(".localhost.run"):
            return normalized
    return None


def build_env(port: int, db_path: str | None) -> dict[str, str]:
    env = os.environ.copy()
    env["DEMO_MODE"] = "true"
    env["PUBLIC_DEMO_MODE"] = "true"
    env.setdefault("MODEL_PROVIDER", "Local Demo")
    if db_path:
        env["CHAT_DB_PATH"] = db_path
    else:
        env.setdefault("CHAT_DB_PATH", str(BASE_DIR / "data" / f"public-demo-{port}.db"))
    return env


def main() -> int:
    parser = argparse.ArgumentParser(description="Start a restricted public backend demo via localhost.run")
    parser.add_argument("--port", type=int, default=8012, help="Local port for the dedicated demo backend")
    parser.add_argument(
        "--db-path",
        default=None,
        help="Optional SQLite path for the public demo backend. Defaults to data/public-demo-<port>.db",
    )
    parser.add_argument(
        "--url-file",
        default=None,
        help="Optional file path. When the public URL is ready, the script will write it to this file.",
    )
    args = parser.parse_args()

    env = build_env(args.port, args.db_path)
    python = Path(sys.executable)
    ssh_config_path = BASE_DIR / "data" / "empty-ssh-config"
    ssh_config_path.parent.mkdir(parents=True, exist_ok=True)
    ssh_config_path.write_text("", encoding="utf-8")

    print(f"[info] Starting restricted public backend on http://127.0.0.1:{args.port}/")
    backend = subprocess.Popen(
        [
            str(python),
            "-m",
            "uvicorn",
            "app:app",
            "--host",
            "127.0.0.1",
            "--port",
            str(args.port),
        ],
        cwd=BASE_DIR,
        env=env,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        text=True,
    )

    if not wait_for_port("127.0.0.1", args.port):
        terminate_process(backend)
        print("[error] Backend failed to start in time.")
        return 1

    print("[info] Backend is up. Opening temporary public tunnel via localhost.run ...")
    tunnel = subprocess.Popen(
        [
            "ssh",
            "-T",
            "-F",
            str(ssh_config_path),
            "-o",
            "StrictHostKeyChecking=no",
            "-o",
            "ExitOnForwardFailure=yes",
            "-o",
            "ServerAliveInterval=30",
            "-R",
            f"80:127.0.0.1:{args.port}",
            "nokey@localhost.run",
        ],
        cwd=BASE_DIR,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        stdin=subprocess.DEVNULL,
        text=True,
    )

    public_url = None
    try:
        deadline = time.time() + 30
        while time.time() < deadline:
            if tunnel.poll() is not None:
                break
            line = tunnel.stdout.readline() if tunnel.stdout else ""
            if not line:
                time.sleep(0.2)
                continue
            print(line.rstrip())
            match = choose_public_url(line)
            if match:
                public_url = match
                break

        if not public_url:
            terminate_process(tunnel)
            terminate_process(backend)
            print("[error] Did not receive a public URL from localhost.run.")
            return 1

        if args.url_file:
            Path(args.url_file).write_text(public_url + "\n", encoding="utf-8")

        print("")
        print("[ok] Temporary public backend is ready")
        print(f"[url] {public_url}")
        print(f"[local] http://127.0.0.1:{args.port}/docs")
        print("")
        print("限制说明：")
        print("- PUBLIC_DEMO_MODE=true")
        print("- 强制使用本地 demo 模式，不会发起真实模型调用")
        print("- /api/knowledge/documents 和 /api/feedback 已禁写")
        print("- 链接只在当前脚本和本机后端持续运行时可访问")
        print("")
        print("按 Ctrl+C 可关闭公网隧道和本地演示后端。")

        while True:
            if backend.poll() is not None:
                print("[error] Backend exited unexpectedly.")
                return 1
            if tunnel.poll() is not None:
                print("[error] Tunnel exited unexpectedly.")
                return 1
            time.sleep(1)
    except KeyboardInterrupt:
        print("")
        print("[info] Stopping public demo ...")
        return 0
    finally:
        terminate_process(tunnel)
        terminate_process(backend)


if __name__ == "__main__":
    raise SystemExit(main())
