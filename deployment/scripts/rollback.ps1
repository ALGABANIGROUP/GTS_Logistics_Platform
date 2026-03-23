Param(
  [string]$ComposeFile = "docker-compose.production.yml",
  [string]$StableTag = "v1.2.3-stable"
)

Write-Host "🔄 Starting rollback..."

try { docker-compose -f $ComposeFile down } catch {}
if(Test-Path ./deployment/scripts/restore-backup.ps1){ ./deployment/scripts/restore-backup.ps1 latest_stable_backup }

Write-Host "📦 Checkout stable tag $StableTag"
& git checkout tags/$StableTag

Write-Host "🏗️ Rebuilding..."
docker-compose -f $ComposeFile build

Write-Host "🚀 Starting..."
docker-compose -f $ComposeFile up -d

Write-Host "✅ Rolled back to $StableTag"