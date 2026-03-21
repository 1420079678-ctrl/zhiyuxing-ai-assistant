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

if not exist ".env" (
  copy /Y ".env.example" ".env" >nul
)

echo Checking model configuration...
".venv\Scripts\python.exe" scripts\check_model_config.py
if errorlevel 1 (
  echo [WARN] Real model call is not fully ready yet. The web app will still start and can fall back to demo mode.
)

echo Starting web server at http://127.0.0.1:8000/
".venv\Scripts\python.exe" -m uvicorn app:app --host 127.0.0.1 --port 8000 --reload
