param(
  [int]$Port = 8020,
  [string]$Root = "D:\GTS Logistics",
  [int]$TimeoutSec = 20
)

$ErrorActionPreference = "Stop"

# Ping helper
function Test-ApiUp {
  try {
    $r = Invoke-WebRequest -Uri "http://127.0.0.1:$Port/health/ping" -UseBasicParsing -TimeoutSec 3
    return $r.StatusCode -eq 200
  }
  catch {
    return $false
  }
}

# If up, return
if (Test-ApiUp) { Write-Host "✅ API is up on :$Port"; return }

# Start API minimized
Write-Host "⏳ Starting API on :$Port ..."
$run = Join-Path $Root "tools\run-api.ps1"
Start-Process -WindowStyle Minimized -FilePath "powershell.exe" -ArgumentList "-ExecutionPolicy Bypass -File `"$run`" -Port $Port"

# Wait for health/ping
$sw = [System.Diagnostics.Stopwatch]::StartNew()
while (-not (Test-ApiUp)) {
  if ($sw.Elapsed.TotalSeconds -ge $TimeoutSec) { throw "API did not come up within $TimeoutSec seconds." }
  Start-Sleep -Milliseconds 500
}
Write-Host "✅ API is up on :$Port"
