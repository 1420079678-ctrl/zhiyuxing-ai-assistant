$ErrorActionPreference = "Continue"

Set-Location $PSScriptRoot

$failures = New-Object System.Collections.Generic.List[string]
$warnings = New-Object System.Collections.Generic.List[string]
$passes = New-Object System.Collections.Generic.List[string]

function Add-Pass([string]$Message) {
    $passes.Add($Message) | Out-Null
    Write-Host "[PASS] $Message"
}

function Add-Warn([string]$Message) {
    $warnings.Add($Message) | Out-Null
    Write-Host "[WARN] $Message"
}

function Add-Fail([string]$Message) {
    $failures.Add($Message) | Out-Null
    Write-Host "[FAIL] $Message"
}

Write-Host "Zhiyuxing AI Assistant doctor"
Write-Host "Working directory: $PSScriptRoot"
Write-Host ""

if ((Test-Path ".\app.py") -and (Test-Path ".\requirements.txt")) {
    Add-Pass "You are in the project root."
} else {
    Add-Fail "Current directory does not look like the project root. Please enter the repository folder first."
}

$pythonLauncher = $null
$py = Get-Command py -ErrorAction SilentlyContinue
if ($py) {
    $pythonLauncher = "py"
    Add-Pass "Found Python launcher: py"
} else {
    $python = Get-Command python -ErrorAction SilentlyContinue
    if ($python) {
        $pythonLauncher = "python"
        Add-Pass "Found Python launcher: python"
    } else {
        Add-Fail "No usable Python launcher found. Install Python 3.13 first."
    }
}

$venvPython = Join-Path $PSScriptRoot ".venv\Scripts\python.exe"
if (Test-Path $venvPython) {
    Add-Pass "Virtual environment already exists."
} else {
    Add-Warn "Virtual environment is missing. The startup script will create it automatically."
}

try {
    $bootstrapOutput = & "$PSScriptRoot\scripts\bootstrap_venv.ps1" -IncludeDev 2>&1
    if ($LASTEXITCODE -eq 0 -and (Test-Path $venvPython)) {
        Add-Pass "bootstrap_venv.ps1 completed successfully."
    } else {
        Add-Fail "bootstrap_venv.ps1 did not finish successfully."
        if ($bootstrapOutput) {
            Write-Host $bootstrapOutput
        }
    }
} catch {
    Add-Fail "bootstrap_venv.ps1 failed: $($_.Exception.Message)"
}

if (Test-Path $venvPython) {
    try {
        & $venvPython -c "import fastapi, uvicorn, dotenv, pydantic, pytest, httpx; print('ok')" *> $null
        if ($LASTEXITCODE -eq 0) {
            Add-Pass "Required runtime and test packages are installed."
        } else {
            Add-Fail "Some required packages are still missing inside .venv."
        }
    } catch {
        Add-Fail "Could not import required packages from .venv."
    }
}

if (Test-Path ".\.env") {
    Add-Pass ".env exists."
} else {
    Add-Warn ".env is missing. start-web.ps1 will copy it from .env.example."
}

try {
    $portInUse = Get-NetTCPConnection -LocalPort 8000 -ErrorAction Stop
    if ($portInUse) {
        Add-Warn "Port 8000 is already in use. start-web.ps1 may fail until that process is stopped."
    }
} catch {
    Add-Pass "Port 8000 looks available."
}

if (Test-Path $venvPython) {
    try {
        & $venvPython ".\scripts\check_model_config.py" *> $null
        if ($LASTEXITCODE -eq 0) {
            Add-Pass "Model configuration looks compatible for real API calls."
        } else {
            Add-Warn "Real model configuration is not fully ready. The project can still run in demo mode."
        }
    } catch {
        Add-Warn "Could not complete the model compatibility check. Demo mode is still available."
    }
}

Write-Host ""
Write-Host "Summary"
Write-Host "PASS: $($passes.Count)"
Write-Host "WARN: $($warnings.Count)"
Write-Host "FAIL: $($failures.Count)"

if ($failures.Count -gt 0) {
    Write-Host ""
    Write-Host "Recommended next steps"
    Write-Host "1. Make sure you are inside the repository root folder."
    Write-Host "2. Run: powershell -ExecutionPolicy Bypass -File .\start-web.ps1"
    Write-Host "3. If it still fails, send the full terminal output or a screenshot."
    exit 1
}

Write-Host ""
Write-Host "Environment looks usable."
Write-Host "Next:"
Write-Host "  powershell -ExecutionPolicy Bypass -File .\start-web.ps1"
exit 0
