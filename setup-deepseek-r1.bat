@echo off
setlocal

cd /d "%~dp0"

set "PYTHON=python"
if exist ".venv\Scripts\python.exe" (
  set "PYTHON=.venv\Scripts\python.exe"
)

if "%~1"=="" (
  "%PYTHON%" scripts\setup_model_config.py --preset deepseek-r1
) else (
  "%PYTHON%" scripts\setup_model_config.py --preset deepseek-r1 --api-key "%~1"
)
