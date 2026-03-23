Write-Host "Activating GTS Virtual Environment..."
$repoRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $repoRoot

$bootstrapPath = Join-Path $repoRoot "tools\\venv_bootstrap.ps1"
if (Test-Path $bootstrapPath) {
    . $bootstrapPath
    Use-GtsVenv -RepoRoot $repoRoot | Out-Null
} else {
    Write-Warning "Venv bootstrap helper not found at $bootstrapPath"
}

$env:PYTHONPATH = Join-Path $repoRoot "backend"

Write-Host "Running alembic upgrade..."
$alembicConfig = Join-Path $repoRoot "backend\\alembic.ini"
alembic -c $alembicConfig upgrade head

Write-Host "Launching FastAPI server on http://127.0.0.1:8000 ..."
uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
