param(
    [switch]$IncludeDev
)

$ErrorActionPreference = "Stop"

$repoRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
Set-Location $repoRoot

$venvPython = Join-Path $repoRoot ".venv\Scripts\python.exe"

function Get-PythonLauncher {
    $py = Get-Command py -ErrorAction SilentlyContinue
    if ($py) {
        try {
            & py -3.13 --version *> $null
            if ($LASTEXITCODE -eq 0) {
                return @{
                    Command = "py"
                    Args = @("-3.13")
                    Label = "py -3.13"
                }
            }
        } catch {
        }

        return @{
            Command = "py"
            Args = @()
            Label = "py"
        }
    }

    $python = Get-Command python -ErrorAction SilentlyContinue
    if ($python) {
        return @{
            Command = "python"
            Args = @()
            Label = "python"
        }
    }

    throw "No Python launcher found. Please install Python 3.13 and make sure 'py' or 'python' works in your terminal."
}

function Test-RequiredModules([string[]]$Modules) {
    if (-not (Test-Path $venvPython)) {
        return $false
    }

    $imports = $Modules | ForEach-Object { "import $_" }
    $code = ($imports -join "; ")

    try {
        & $venvPython -c $code *> $null
        return $LASTEXITCODE -eq 0
    } catch {
        return $false
    }
}

if (-not (Test-Path $venvPython)) {
    $launcher = Get-PythonLauncher
    Write-Host "[setup] Creating .venv with $($launcher.Label) ..."
    & $launcher.Command @($launcher.Args) -m venv .venv
    if ($LASTEXITCODE -ne 0 -or -not (Test-Path $venvPython)) {
        throw "Failed to create .venv. Please check your Python installation."
    }
}

$requiredModules = @("fastapi", "uvicorn", "dotenv", "pydantic")
if ($IncludeDev) {
    $requiredModules += @("pytest", "httpx")
}

if (-not (Test-RequiredModules $requiredModules)) {
    Write-Host "[setup] Installing project dependencies..."
    & $venvPython -m pip install --upgrade pip
    if ($LASTEXITCODE -ne 0) {
        throw "Failed to upgrade pip."
    }

    & $venvPython -m pip install -r requirements.txt
    if ($LASTEXITCODE -ne 0) {
        throw "Failed to install requirements.txt."
    }

    if ($IncludeDev) {
        & $venvPython -m pip install -r requirements-dev.txt
        if ($LASTEXITCODE -ne 0) {
            throw "Failed to install requirements-dev.txt."
        }
    }
}

Write-Output $venvPython
