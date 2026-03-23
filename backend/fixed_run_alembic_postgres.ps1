Write-Host "🚀 Activating Virtual Environment..."
$repoRoot = Split-Path -Parent $PSScriptRoot
$bootstrapPath = Join-Path $repoRoot "tools\\venv_bootstrap.ps1"
if (Test-Path $bootstrapPath) {
    . $bootstrapPath
    Use-GtsVenv -RepoRoot $repoRoot | Out-Null
} else {
    Write-Warning "Venv bootstrap helper not found at $bootstrapPath"
}

Write-Host "🛠️  Generating Alembic Revision..."
alembic -c backend\alembic.ini revision --autogenerate -m "PostgreSQL schema update"

Write-Host "⚙️  Applying Migration to PostgreSQL..."
alembic -c backend\alembic.ini upgrade head

Write-Host "✅ Done! PostgreSQL schema updated successfully."
