param(
  [string]$Base = "http://127.0.0.1:8001",
  [string]$ServiceName = "gts-api",
  [int]$Tail = 100
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Write-Title([string]$text) { Write-Host "`n=== $text ===" -ForegroundColor Cyan }
function Write-Ok([string]$msg) { Write-Host "[OK]  $msg" -ForegroundColor Green }
function Write-Warn([string]$msg) { Write-Host "[WARN] $msg" -ForegroundColor Yellow }
function Write-Err([string]$msg) { Write-Host "[ERR] $msg" -ForegroundColor Red }

function Invoke-Json {
  param(
    [Parameter(Mandatory)][string]$Method,
    [Parameter(Mandatory)][string]$Url,
    [hashtable]$Headers = $null,
    [object]$Body = $null,
    [int]$TimeoutSec = 20
  )
  $params = @{
    Method = $Method; Uri = $Url; TimeoutSec = $TimeoutSec; ErrorAction = 'Stop'
  }
  if ($Headers) { $params['Headers'] = $Headers }
  if ($null -ne $Body) {
    $params['ContentType'] = 'application/json'
    $params['Body'] = if ($Body -is [string]) { $Body } else { $Body | ConvertTo-Json -Depth 6 }
  }
  return Invoke-RestMethod @params
}

function Test-PortListen {
  param([int]$Port)
  try { if (Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction Stop) { $true } else { $false } }
  catch { $false }
}

function Is-HealthyObject($obj) {
  # Accepts multiple response formats: {ok:true, healthy:true} or {ok:true, status:"ok"} or just {ok:true}
  if ($null -eq $obj) { return $false }
  if ($obj.PSObject.Properties.Name -contains 'healthy') { if ($obj.healthy) { return $true } }
  if ($obj.PSObject.Properties.Name -contains 'status') { if ($obj.status -in @('ok', 'healthy', 'pass', 'up')) { return $true } }
  if ($obj.PSObject.Properties.Name -contains 'ok') { if ($obj.ok) { return $true } }
  return $false
}

# Paths
$root = "I:\GTS Logistics"
$logDir = Join-Path $root "logs"
$outLog = Join-Path $logDir "gts-api.out.log"
$errLog = Join-Path $logDir "gts-api.err.log"

$overallOk = $true
$uri = [Uri]$Base
$port = if ($uri.IsDefaultPort) { if ($uri.Scheme -eq 'https') { 443 } else { 80 } } else { $uri.Port }

Write-Title "Environment"
Write-Host "Base          : $Base"
Write-Host "Service       : $ServiceName"
Write-Host "Expect Listen : 127.0.0.1:$port"
Write-Host "Logs          : $outLog , $errLog"

Write-Title "Service status"
try {
  $svc = Get-Service -Name $ServiceName -ErrorAction Stop
  Write-Host ("Name={0} | Status={1} | StartType={2}" -f $svc.Name, $svc.Status, $svc.StartType)
}
catch {
  Write-Warn "Service '$ServiceName' not found."
  $overallOk = $false
}

Write-Title "Port listening"
if (Test-PortListen -Port $port) { Write-Ok "Port $port is LISTEN on 127.0.0.1" } else { Write-Err "Port $port NOT listening."; $overallOk = $false }

Write-Title "Health"
try {
  $r = Invoke-Json -Method GET -Url ("{0}/health/ping" -f $Base)
  if ($r.ok -and $r.pong) { Write-Ok "/health/ping => ok=true pong=true" }
  else { Write-Warn "/health/ping unexpected: $($r | ConvertTo-Json -Depth 4)"; $overallOk = $false }
}
catch { Write-Err "/health/ping failed: $($_.Exception.Message)"; $overallOk = $false }

Write-Title "Auth token"
$headers = @{}
try {
  $tokResp = Invoke-Json -Method POST -Url ("{0}/auth/token" -f $Base) -Body @{ username = "mvp-user"; role = "admin"; expires_minutes = 60 }
  $token = $tokResp.access_token
  if ([string]::IsNullOrWhiteSpace($token)) { throw "Empty token" }
  $headers = @{ Authorization = "Bearer $token" }
  Write-Ok "Token acquired."
}
catch { Write-Err "Auth/token failed: $($_.Exception.Message)"; $overallOk = $false }

Write-Title "Finance health"
if ($headers.Count -gt 0) {
  try {
    $fh = Invoke-Json -Method GET -Url ("{0}/finance/health" -f $Base) -Headers $headers
    if (Is-HealthyObject $fh) { Write-Ok "/finance/health => healthy" }
    else { Write-Warn "/finance/health payload: $($fh | ConvertTo-Json -Depth 5)"; $overallOk = $false }
  }
  catch { Write-Err "/finance/health failed: $($_.Exception.Message)"; $overallOk = $false }
}
else { Write-Warn "Skip finance (no token)." }

Write-Title "Routes"
try {
  $dbg = Invoke-Json -Method GET -Url ("{0}/_debug/routes" -f $Base)
  Write-Host ("Routes count: {0}" -f $dbg.count)
  $sample = ($dbg.routes | Select-Object -First 6 | ConvertTo-Json -Depth 4)
  Write-Host $sample
}
catch { Write-Warn "_debug/routes failed: $($_.Exception.Message)" }

Write-Title "Shipments"
if ($headers.Count -gt 0) {
  # GET
  try {
    $s1 = Invoke-Json -Method GET -Url ("{0}/shipments" -f $Base) -Headers $headers
    Write-Ok "GET /shipments OK (items: $((($s1.items,$s1.data,$s1) | ? {$_} | Select-Object -First 1).Count))"
  }
  catch { Write-Warn "GET /shipments: $($_.Exception.Message)" }

  # POST: Try multiple paths
  $payload = @{
    pickup_location  = "Houston, TX"
    dropoff_location = "Dallas, TX"
    trailer_type     = "Dry Van"
    status           = "Imported"
  }
  $endpoints = @(
    "/shipments/",
    "/shipments",                   # without slash
    "/api/v1/shipments/",
    "/api/v1/shipments/shipments/", # some existing schemes
    "/api/v1/shipments/shipments"
  )
  $posted = $false
  foreach ($ep in $endpoints) {
    try {
      $url = "{0}{1}" -f $Base, $ep
      $res = Invoke-Json -Method POST -Url $url -Headers $headers -Body $payload
      Write-Ok ("POST {0} => OK" -f $ep)
      $posted = $true
      break
    }
    catch {
      $msg = $_.Exception.Message
      if ($msg -match '405' -or $msg -match 'Not Allowed' -or $msg -match 'Method Not Allowed') {
        Write-Warn ("POST {0} => 405, trying next..." -f $ep)
      }
      else {
        Write-Warn ("POST {0} => {1}" -f $ep, $msg)
      }
    }
  }
  if (-not $posted) { Write-Warn "Could not create shipment through tried paths." }
}
else { Write-Warn "Skip shipments (no token)." }

Write-Title "Logs (tail)"
if (Test-Path $outLog) { Write-Host "---- gts-api.out.log (last $Tail) ----" -ForegroundColor DarkCyan; Get-Content -Path $outLog -Tail $Tail } else { Write-Warn "Missing: $outLog" }
if (Test-Path $errLog) { Write-Host "---- gts-api.err.log (last $Tail) ----" -ForegroundColor DarkCyan; Get-Content -Path $errLog -Tail $Tail } else { Write-Warn "Missing: $errLog" }

Write-Title "Summary"
if ($overallOk) { Write-Ok "Smoke test PASSED."; exit 0 } else { Write-Err "Smoke test FAILED. Check warnings/errors above."; exit 1 }
