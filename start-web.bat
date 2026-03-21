@echo off
setlocal

cd /d "%~dp0"

powershell -ExecutionPolicy Bypass -File "%~dp0start-web.ps1"
exit /b %errorlevel%
