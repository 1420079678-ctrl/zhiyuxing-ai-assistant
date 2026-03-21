$ErrorActionPreference = "Stop"

Set-Location $PSScriptRoot

$python = & "$PSScriptRoot\scripts\bootstrap_venv.ps1"

if (-not (Test-Path ".env")) {
    Copy-Item ".env.example" ".env"
}

Write-Host "Checking model configuration..."
& $python ".\scripts\check_model_config.py"
if ($LASTEXITCODE -ne 0) {
    Write-Host "[WARN] Real model call is not fully ready yet. The web app will still start and can fall back to demo mode."
}

Write-Host "Starting web server at http://127.0.0.1:8000/"
& $python -m uvicorn app:app --host 127.0.0.1 --port 8000 --reload
