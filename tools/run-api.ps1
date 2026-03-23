param([int]$Port = 8020)

$root = Split-Path -Parent $MyInvocation.MyCommand.Path | Split-Path -Parent
Set-Location $root

$bootstrapPath = Join-Path $root "tools\\venv_bootstrap.ps1"
if (Test-Path $bootstrapPath) {
  . $bootstrapPath
  Use-GtsVenv -RepoRoot $root | Out-Null
}
else {
  Write-Warning "Venv bootstrap helper not found at $bootstrapPath"
}
$env:PYTHONPATH = $root

if (-not $env:DATABASE_URL -and -not $env:POSTGRES_DSN -and -not $env:SQLALCHEMY_DATABASE_URI) {
  python -m pip install aiosqlite | Out-Null
  $env:DATABASE_URL = "sqlite+aiosqlite:///./gts.db"
}

python -m uvicorn backend.main:app --host 0.0.0.0 --port $Port --reload
