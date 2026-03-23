param([switch]$Reset)

$ErrorActionPreference = 'Stop'
chcp 65001 > $null
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$api = 'http://127.0.0.1:8001'

# Optional: reset local SQLite database for a clean run
if ($Reset) {
  $db = Join-Path $PSScriptRoot 'vizion.db'
  if (Test-Path $db) { Remove-Item $db -Force }
  Start-Sleep -Milliseconds 200
}

Write-Host "== Health ==" -ForegroundColor Cyan
$health = Invoke-RestMethod -Uri "$api/health" -Method GET
$health | ConvertTo-Json

# Example records to activate all types of alerts
$logs = @(
  @{ project_name = "The VIZION"; platform = "youtube"; likes = 0; comments = 0; shares = 0; views = 0; engagement_score = 0.0 } # No views
  @{ project_name = "The VIZION"; platform = "tiktok"; likes = 5; comments = 1; shares = 0; views = 200; engagement_score = 1.3 } # Low engagement
  @{ project_name = "The VIZION"; platform = "instagram"; likes = 150; comments = 25; shares = 30; views = 8000; engagement_score = 5.2 } # Great traction
  @{ project_name = "The VIZION"; platform = "facebook"; likes = 40; comments = 65; shares = 5; views = 1200; engagement_score = 3.1 } # High comments
)

foreach ($l in $logs) {
  $payload = $l | ConvertTo-Json
  Invoke-RestMethod -Uri "$api/log-performance" -Method POST -ContentType "application/json" -Body $payload
  Write-Host ("Logged: {0}/{1}" -f $l.project_name, $l.platform)
}

Write-Host "`n== Alerts ==" -ForegroundColor Cyan
$alerts = (Invoke-RestMethod -Uri "$api/generate-alerts" -Method GET).alerts | Select-Object -Unique
$alerts | ForEach-Object { Write-Host $_ }
