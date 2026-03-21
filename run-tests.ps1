$ErrorActionPreference = "Stop"

Set-Location $PSScriptRoot

$python = & "$PSScriptRoot\scripts\bootstrap_venv.ps1" -IncludeDev

Write-Host "Running test suite..."
& $python -m pytest tests -vv
