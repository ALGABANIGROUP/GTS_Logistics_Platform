param([string]$Root = "D:\GTS Logistics")
$ini = Join-Path $Root "backend\alembic.ini"
$env = Join-Path $Root "backend\alembic_migrations\env.py"
$versions = Join-Path $Root "backend\alembic_migrations\versions"

if (!(Test-Path $ini)) { Write-Warning "Missing backend\alembic.ini" } else { Write-Host "✅ alembic.ini exists" }
if (!(Test-Path $env)) { Write-Warning "Missing backend\alembic_migrations\env.py" } else { Write-Host "✅ env.py exists" }
if (!(Test-Path $versions)) { Write-Warning "Missing versions dir" } else {
  $count = (Get-ChildItem $versions -File -Filter "*.py").Count
  Write-Host "✅ versions present ($count files)"
}
