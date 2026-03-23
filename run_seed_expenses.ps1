Write-Host "🚀 Activating Virtual Environment..."
$repoRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$bootstrapPath = Join-Path $repoRoot "tools\\venv_bootstrap.ps1"
if (Test-Path $bootstrapPath) {
    . $bootstrapPath
    Use-GtsVenv -RepoRoot $repoRoot | Out-Null
} else {
    Write-Warning "Venv bootstrap helper not found at $bootstrapPath"
}

Write-Host "🧱  Generating Alembic Revision..."
alembic -c alembic.ini revision --autogenerate -m "auto migration"

Write-Host "⚙️  Applying Migration to SQLite..."
alembic -c alembic.ini upgrade head

Write-Host "✅ Done! SQLite schema updated successfully."
