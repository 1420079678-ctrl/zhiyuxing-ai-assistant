$ErrorActionPreference = "Stop"

Set-Location $PSScriptRoot

$python = "python"
$venvPython = Join-Path $PSScriptRoot ".venv\Scripts\python.exe"
if (Test-Path $venvPython) {
    $python = $venvPython
}

$arguments = @(".\scripts\setup_model_config.py", "--preset", "deepseek-chat")
if ($args.Count -gt 0 -and $args[0]) {
    $arguments += @("--api-key", $args[0])
}

& $python @arguments
