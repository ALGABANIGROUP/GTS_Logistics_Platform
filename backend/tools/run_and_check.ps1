param(
  [string]$BaseUrl = "http://127.0.0.1:8000"
)

$repoRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$bootstrapPath = Join-Path $repoRoot "tools\\venv_bootstrap.ps1"
if (Test-Path $bootstrapPath) {
  . $bootstrapPath
  Use-GtsVenv -RepoRoot $repoRoot | Out-Null
} else {
  Write-Warning "Venv bootstrap helper not found at $bootstrapPath"
}

$env:HOST = "127.0.0.1"
$env:PORT = "8000"
$env:SELF_CHECK_BASE_URL = $BaseUrl

Get-Process uvicorn, python -ErrorAction SilentlyContinue | Stop-Process -Force

Start-Process `
  -FilePath "python" `
  -ArgumentList "-m", "uvicorn", "backend.main:app", "--host", $env:HOST, "--port", $env:PORT, "--reload"

Write-Host "Waiting for /health/ping..."
$ok = $false
for ($i = 0; $i -lt 30; $i++) {
  Start-Sleep -Seconds 1
  try {
    $resp = Invoke-RestMethod "$BaseUrl/health/ping" -TimeoutSec 2
    if ($resp.ok -and $resp.pong) { $ok = $true; break }
  }
  catch {}
}
if (-not $ok) {
  Write-Host "Server didn't respond to /health/ping in time."
  exit 1
}

Write-Host "Server is up. Running self-check..."
$pythonExe = if ($env:VIRTUAL_ENV) { Join-Path $env:VIRTUAL_ENV "Scripts\\python.exe" } else { "python" }
$selfCheck = Join-Path $repoRoot "backend\\tools\\system_self_check.py"
& $pythonExe $selfCheck
Get-Content (Join-Path $repoRoot "backend\\self_check_report.json")
