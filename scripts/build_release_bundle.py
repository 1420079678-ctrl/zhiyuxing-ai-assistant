from __future__ import annotations

import argparse
import hashlib
import os
from pathlib import Path
from tempfile import TemporaryDirectory
from zipfile import ZIP_DEFLATED, ZipFile


ROOT = Path(__file__).resolve().parents[1]

INCLUDE_FILES = [
    ".env.example",
    ".python-version",
    "app.py",
    "CHANGELOG.md",
    "LICENSE",
    "README.md",
    "README_EN.md",
    "build-release.bat",
    "build-release.ps1",
    "doctor.bat",
    "doctor.ps1",
    "requirements.txt",
    "requirements-dev.txt",
    "run-tests.bat",
    "run-tests.ps1",
    "setup-deepseek-chat.bat",
    "setup-deepseek-chat.ps1",
    "setup-deepseek-r1.bat",
    "setup-deepseek-r1.ps1",
    "setup-openai.bat",
    "setup-openai.ps1",
    "start-public-demo.bat",
    "start-public-demo.ps1",
    "start-web.bat",
    "start-web.ps1",
]

INCLUDE_DIRS = [
    "backend",
    "docs",
    "knowledge_base",
    "scripts",
    "services",
    "static",
]

SKIP_DIRS = {
    ".git",
    ".github",
    ".pytest_cache",
    ".venv",
    "__pycache__",
    "data",
    "dist",
}

SKIP_SUFFIXES = {
    ".db",
    ".log",
    ".pyc",
    ".pyo",
}

SKIP_NAMES = {
    "public-demo-url.txt",
}


def iter_release_files() -> list[Path]:
    paths: list[Path] = []

    for relative in INCLUDE_FILES:
        path = ROOT / relative
        if path.exists():
            paths.append(path)

    for directory in INCLUDE_DIRS:
        base = ROOT / directory
        if not base.exists():
            continue
        for path in base.rglob("*"):
            if path.is_dir():
                continue
            if any(part in SKIP_DIRS for part in path.parts):
                continue
            if path.name in SKIP_NAMES:
                continue
            if path.suffix.lower() in SKIP_SUFFIXES:
                continue
            paths.append(path)

    return sorted({path.resolve() for path in paths})


def build_install_text(version: str) -> str:
    return f"""Zhiyuxing AI Assistant {version} Release Package

Quick Start (Windows)
1. Install Python 3.13 first. During installation, enable the PATH option.
2. Extract this package to a normal folder, for example:
   C:\\Users\\YourName\\Desktop\\zhiyuxing-ai-assistant
3. Open the extracted folder and double-click start-web.bat
4. When the launcher finishes, open http://127.0.0.1:8000/

If startup fails
- Double-click doctor.bat
- Read docs/troubleshooting.md

Important
- Demo mode works without any API key.
- Real model calls require your own API key.
- Model setup docs: docs/model-integration.md
- Public restricted backend demo docs: docs/public-demo.md

Maintenance
- Build a new release package locally:
  build-release.bat
"""


def create_bundle(version: str, output_dir: Path) -> tuple[Path, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    package_name = f"zhiyuxing-ai-assistant-release-{version}"
    zip_path = output_dir / f"{package_name}.zip"
    sha_path = output_dir / f"{package_name}.sha256"
    release_root = Path(package_name)

    files = iter_release_files()

    with TemporaryDirectory() as tmp_dir:
        install_path = Path(tmp_dir) / "INSTALL.txt"
        install_path.write_text(build_install_text(version), encoding="utf-8")

        with ZipFile(zip_path, "w", compression=ZIP_DEFLATED) as archive:
            archive.write(install_path, arcname=str(release_root / "INSTALL.txt"))
            for file_path in files:
                relative = file_path.relative_to(ROOT)
                archive.write(file_path, arcname=str(release_root / relative))

    digest = hashlib.sha256(zip_path.read_bytes()).hexdigest()
    sha_path.write_text(f"{digest}  {zip_path.name}\n", encoding="utf-8")
    return zip_path, sha_path


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a release-ready zip bundle.")
    parser.add_argument("--version", required=True, help="Release version, for example v0.7.0")
    parser.add_argument("--output-dir", default="dist", help="Output directory for the zip and checksum")
    args = parser.parse_args()

    version = args.version.strip()
    output_dir = (ROOT / args.output_dir).resolve()
    zip_path, sha_path = create_bundle(version, output_dir)

    print(f"Built: {zip_path}")
    print(f"SHA256: {sha_path}")
    print(f"Size: {os.path.getsize(zip_path)} bytes")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
