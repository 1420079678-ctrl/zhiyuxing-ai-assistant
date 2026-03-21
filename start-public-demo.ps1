$ErrorActionPreference = "Stop"

Set-Location $PSScriptRoot

$python = & "$PSScriptRoot\scripts\bootstrap_venv.ps1"

Write-Host "Starting restricted public backend demo..."
& $python ".\scripts\start_public_demo.py"
