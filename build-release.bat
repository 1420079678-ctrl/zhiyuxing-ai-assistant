@echo off
setlocal

cd /d "%~dp0"

set "VERSION=%~1"
if "%VERSION%"=="" set "VERSION=v0.7.0"

powershell -ExecutionPolicy Bypass -File "%~dp0build-release.ps1" -Version "%VERSION%"
exit /b %errorlevel%
