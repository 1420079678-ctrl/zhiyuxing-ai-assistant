$ErrorActionPreference = "Stop"

Set-Location $PSScriptRoot

$python = Join-Path $PSScriptRoot ".venv\Scripts\python.exe"

if (-not (Test-Path $python)) {
    Write-Host "[ERROR] Missing virtual environment: .venv\Scripts\python.exe"
    Write-Host "Please run:"
    Write-Host "  python -m venv .venv"
    Write-Host "  .venv\Scripts\python -m pip install -r requirements.txt -r requirements-dev.txt"
    exit 1
}

Write-Host "Starting restricted public backend demo..."
& $python ".\scripts\start_public_demo.py"
