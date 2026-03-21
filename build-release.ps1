param(
    [string]$Version = "v0.7.0"
)

$ErrorActionPreference = "Stop"

Set-Location $PSScriptRoot

if (Get-Command py -ErrorAction SilentlyContinue) {
    & py -3.13 --version *> $null
    if ($LASTEXITCODE -eq 0) {
        & py -3.13 .\scripts\build_release_bundle.py --version $Version --output-dir dist
        exit $LASTEXITCODE
    }

    & py .\scripts\build_release_bundle.py --version $Version --output-dir dist
    exit $LASTEXITCODE
}

if (Get-Command python -ErrorAction SilentlyContinue) {
    & python .\scripts\build_release_bundle.py --version $Version --output-dir dist
    exit $LASTEXITCODE
}

Write-Host "[ERROR] Python launcher not found. Install Python 3.13 first."
exit 1
