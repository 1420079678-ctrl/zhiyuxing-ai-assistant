@echo off
setlocal

cd /d "%~dp0"

powershell -ExecutionPolicy Bypass -File "%~dp0start-public-demo.ps1"
exit /b %errorlevel%
