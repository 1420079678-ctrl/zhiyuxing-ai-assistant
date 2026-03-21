@echo off
setlocal

cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
  echo [ERROR] Missing virtual environment: .venv\Scripts\python.exe
  echo Please run:
  echo   python -m venv .venv
  echo   .venv\Scripts\python -m pip install -r requirements.txt -r requirements-dev.txt
  exit /b 1
)

echo Starting restricted public backend demo...
".venv\Scripts\python.exe" scripts\start_public_demo.py
