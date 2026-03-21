@echo off
setlocal

cd /d "%~dp0"

powershell -ExecutionPolicy Bypass -File "%~dp0run-tests.ps1"
exit /b %errorlevel%
