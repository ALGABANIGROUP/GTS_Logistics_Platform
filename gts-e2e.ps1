param(
  [string]$ProjectRoot = ".",
  [int]$Port = 8000,
  [int]$WaitSeconds = 25,
  [string]$Host = "127.0.0.1",
  [string]$Username = "x",
  [string]$Password = "y"
)

$ErrorActionPreference = "Stop"

function Write-Section($t) {
  Write-Host "`n==============================="
  Write-Host $t
  Write-Host "==============================="
}

function Invoke-Http {
  param(
    [string]$Method,
    [string]$Url,
    [hashtable]$Headers = @{},
    $Body = $null,
    [string]$ContentType = $null
  )
  try {
    $params = @{
      Uri = $Url
      Method = $Method
      Headers = $Headers
      ErrorAction = "Stop"
    }
    if ($null -ne $Body) { $params["Body"] = $Body }
    if ($null -ne $ContentType) { $params["ContentType"] = $ContentType }

    $resp = Invoke-WebRequest @params
    return @{
      ok = $true
      status = [int]$resp.StatusCode
      body = $resp.Content
      headers = $resp.Headers
    }
  } catch {
    $r = $_.Exception.Response
    if ($null -ne $r) {
      $status = [int]$r.StatusCode
      $reader = New-Object System.IO.StreamReader($r.GetResponseStream())
      $txt = $reader.ReadToEnd()
      return @{ ok=$false; status=$status; body=$txt; headers=@{} }
    }
    return @{ ok=$false; status=0; body=$_.Exception.Message; headers=@{} }
  }
}

function Wait-Healthy {
  param([string]$BaseUrl, [int]$Seconds)

  $deadline = (Get-Date).AddSeconds($Seconds)
  do {
    $r1 = Invoke-Http -Method "GET" -Url "$BaseUrl/healthz"
    if ($r1.ok -and $r1.status -eq 200) { return $true }

    $r2 = Invoke-Http -Method "GET" -Url "$BaseUrl/health/ping"
    if ($r2.ok -and $r2.status -eq 200) { return $true }

    Start-Sleep -Milliseconds 700
  } while ((Get-Date) -lt $deadline)

  return $false
}

function Apply-Patch {
  param([string]$MainPath)

  if (!(Test-Path $MainPath)) { throw "Not found: $MainPath" }

  $ts = Get-Date -Format "yyyyMMdd-HHmmss"
  Copy-Item $MainPath "$MainPath.bak.$ts"
  Write-Host "✅ Backup: $MainPath.bak.$ts"

  $content = Get-Content $MainPath -Raw

  if ($content -notmatch "(?m)^\s*import\s+os\s*$") {
    $content = $content -replace "(?s)^(.*?)(\r?\n\r?\n)", "`$1`r`nimport os`r`n`r`n"
    Write-Host "✅ Inserted: import os"
  }

  if ($content -notmatch "(?m)^\s*def\s+_is_prod\(") {
$prodHelper = @'
def _is_prod() -> bool:
    # Treat Render as production by default
    return os.getenv("ENV", "").lower() in ("prod", "production") or os.getenv("RENDER", "").lower() == "true"
'@
    $content = $content -replace "(?m)^\s*app\s*=\s*FastAPI\(", "$prodHelper`r`n`r`napp = FastAPI("
    Write-Host "✅ Inserted: _is_prod()"
  }

  if ($content -notmatch "(?m)block_auth_token_in_prod") {
$mw = @'
from starlette.responses import JSONResponse

@app.middleware("http")
async def block_auth_token_in_prod(request: Request, call_next):
    if _is_prod() and request.url.path == "/auth/token":
        return JSONResponse({"detail": "Auth temporarily disabled (security fix in progress)."}, status_code=503)
    return await call_next(request)

'@
    $content = $content -replace "(?m)^app\s*=\s*FastAPI\([^\r\n]*\r?\n", "`$0`r`n$mw"
    Write-Host "✅ Inserted: prod block middleware"
  }

  # DEV-only auth_token router include
  $content = $content -replace "(?s)if\s+auth_token_router:\s*\r?\n\s*app\.include_router\(auth_token_router\)\s*\r?\n\s*print\(\"?\[main\]\s*auth_token router mounted\"?\)\s*",
@'
if auth_token_router and (not _is_prod()):
    app.include_router(auth_token_router)
    print("[main] auth_token router mounted (DEV only)")
else:
    print("[main] auth_token router disabled")
'@

  # DEV-only fallback /auth/token
  $content = $content -replace "(?m)^if\s+not\s+_auth_token_exists\(\):", "if (not _auth_token_exists()) and (not _is_prod()):"

  if ($content -notmatch "(?m)FATAL:\s*auth_router failed to load") {
$failClosed = @'
if _is_prod() and not auth_router:
    raise RuntimeError("FATAL: auth_router failed to load in production (fail closed).")

'@
    $content = $content -replace "(?s)(if\s+auth_router:\s*\r?\n\s*app\.include_router\(auth_router\)\s*\r?\n\s*print\(\"?\[main\]\s*security\.auth router mounted\"?\)\s*\r?\n\s*print\(\"?\[main\]\s*WARN:\s*security\.auth router not available\"?\)\s*\r?\n?)",
"`$1`r`n$failClosed"
    Write-Host "✅ Inserted: fail-closed guard"
  }

  Set-Content $MainPath $content -Encoding UTF8
  Write-Host "✅ Patched: $MainPath"
}

function Start-Server {
  param([string]$Root, [int]$Port, [string]$Host)

  $candidates = @(
    @{ name="uvicorn direct"; cmd="uvicorn"; args=@("backend.main:app","--host",$Host,"--port",$Port.ToString()) },
    @{ name="python -m uvicorn"; cmd="python"; args=@("-m","uvicorn","backend.main:app","--host",$Host,"--port",$Port.ToString()) },
    @{ name="poetry"; cmd="poetry"; args=@("run","uvicorn","backend.main:app","--host",$Host,"--port",$Port.ToString()) },
    @{ name="pipenv"; cmd="pipenv"; args=@("run","uvicorn","backend.main:app","--host",$Host,"--port",$Port.ToString()) }
  )

  foreach ($c in $candidates) {
    try {
      Write-Host "🚀 Trying: $($c.name) -> $($c.cmd) $($c.args -join ' ')"
      $p = Start-Process -FilePath $c.cmd -ArgumentList $c.args -WorkingDirectory $Root -PassThru -WindowStyle Hidden
      Start-Sleep -Seconds 2
      if (!$p.HasExited) {
        return @{ process=$p; launcher=$c.name }
      }
    } catch {
      # ignore and try next
    }
  }

  throw "Could not start server using uvicorn/python/poetry/pipenv. Provide your run command and I'll adapt it."
}

# -------------------- MAIN --------------------
Push-Location $ProjectRoot

$report = [ordered]@{
  started_at = (Get-Date).ToString("s")
  project_root = (Resolve-Path ".").Path
  patch = @{}
  server = @{}
  tests = @()
  summary = @{}
}

Write-Section "1) Apply Patch"
$mainPath = Join-Path (Resolve-Path ".").Path "backend\main.py"
Apply-Patch -MainPath $mainPath
$report.patch.applied = $true
$report.patch.main_py = $mainPath

Write-Section "2) Start Server"
$server = Start-Server -Root (Resolve-Path ".").Path -Port $Port -Host $Host
$report.server.launcher = $server.launcher
$report.server.pid = $server.process.Id

$baseUrl = "http://$Host`:$Port"
Write-Host "🌐 Base URL: $baseUrl"
Write-Host "🧩 PID: $($server.process.Id) ($($server.launcher))"

Write-Section "3) Wait for Health"
$healthy = Wait-Healthy -BaseUrl $baseUrl -Seconds $WaitSeconds
$report.server.healthy = $healthy
if (-not $healthy) {
  Write-Host "❌ Server didn't become healthy in time."
}

Write-Section "4) Auth Token"
$token = $null
$authResp = Invoke-Http -Method "POST" -Url "$baseUrl/auth/token" -ContentType "application/x-www-form-urlencoded" -Body @{ username=$Username; password=$Password }
$report.tests += [ordered]@{ name="POST /auth/token"; status=$authResp.status; ok=$authResp.ok; body=$authResp.body }

if ($authResp.ok -and $authResp.status -eq 200) {
  try {
    $tokObj = $authResp.body | ConvertFrom-Json
    $token = $tokObj.access_token
  } catch {}
}

$headersAuth = @{}
if ($token) { $headersAuth["Authorization"] = "Bearer $token" }

Write-Section "5) Test 5 Endpoints"
$endpoints = @(
  @{ name="GET /"; method="GET"; path="/" ; auth=$false },
  @{ name="GET /_debug/routes"; method="GET"; path="/_debug/routes"; auth=$false },
  @{ name="GET /health/ping"; method="GET"; path="/health/ping"; auth=$false },
  @{ name="GET /ai/bots"; method="GET"; path="/ai/bots"; auth=$true },
  @{ name="GET /finance/ai/finance-analysis"; method="GET"; path="/finance/ai/finance-analysis"; auth=$true }
)

foreach ($e in $endpoints) {
  $h = @{}
  if ($e.auth) { $h = $headersAuth }
  $r = Invoke-Http -Method $e.method -Url ($baseUrl + $e.path) -Headers $h
  $report.tests += [ordered]@{
    name = $e.name
    status = $r.status
    ok = $r.ok
    needs_auth = $e.auth
    sample = ($r.body.Substring(0, [Math]::Min(300, $r.body.Length)))
  }
  Write-Host ("{0,-30} -> {1}" -f $e.name, $r.status)
}

Write-Section "6) Stop Server + Write Report"
try {
  if (!$server.process.HasExited) {
    Stop-Process -Id $server.process.Id -Force
    Start-Sleep -Milliseconds 500
  }
} catch {}

$okCount = ($report.tests | Where-Object { $_.ok -eq $true -and $_.status -ge 200 -and $_.status -lt 400 }).Count
$total = $report.tests.Count
$report.summary.ok = $okCount
$report.summary.total = $total

$ts2 = Get-Date -Format "yyyyMMdd-HHmmss"
$jsonPath = Join-Path (Resolve-Path ".").Path "e2e-report-$ts2.json"
$txtPath  = Join-Path (Resolve-Path ".").Path "e2e-report-$ts2.txt"

($report | ConvertTo-Json -Depth 10) | Set-Content $jsonPath -Encoding UTF8

$lines = @()
$lines += "E2E REPORT @ $($report.started_at)"
$lines += "Root: $($report.project_root)"
$lines += "Patch: applied=$($report.patch.applied) main=$($report.patch.main_py)"
$lines += "Server: launcher=$($report.server.launcher) pid=$($report.server.pid) healthy=$($report.server.healthy)"
$lines += "Results: $okCount/$total OK"
$lines += ""
foreach ($t in $report.tests) {
  $lines += ("- {0} | status={1} ok={2}" -f $t.name, $t.status, $t.ok)
}
$lines | Set-Content $txtPath -Encoding UTF8

Write-Host "✅ Report JSON: $jsonPath"
Write-Host "✅ Report TXT : $txtPath"
Write-Host "✅ Done."

Pop-Location
