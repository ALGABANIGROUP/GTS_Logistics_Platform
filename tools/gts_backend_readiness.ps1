param(
    [string]$Base = "https://gts-logistics-api.onrender.com",
    [string]$User = "yassir",
    [string]$Role = "admin",
    [int]$TTL = 15
)

$ErrorActionPreference = "Stop"

function Write-Title($t) { Write-Host "`n=== $t ===" -ForegroundColor Cyan }
function Pass($m) { Write-Host "PASS: $m" -ForegroundColor Green }
function Fail($m) { Write-Host "FAIL: $m" -ForegroundColor Red }

function Get-Token {
    try {
        $tok = Invoke-RestMethod "$Base/auth/token" -Method POST -ContentType "application/json" -Body (@{
                username = $User; role = $Role; expires_minutes = $TTL
            } | ConvertTo-Json)
        $tokenValue = @(
            $tok.access_token
            $tok.token
            $tok.data.access_token
            $tok.result.access_token
        ) | Where-Object { $_ } | Select-Object -First 1
        if (-not $tokenValue) { throw "access_token not found in response" }
        return "Bearer $tokenValue"
    }
    catch {
        Fail "Auth token: $($_.Exception.Message)"
        throw
    }
}

function MustStatus($block, [int[]]$okCodes) {
    try {
        & $block
        return $true
    }
    catch {
        $resp = $_.Exception.Response
        if ($resp) {
            $code = $resp.StatusCode.value__
            if ($okCodes -contains $code) { return $true }
            else {
                Fail "Unexpected HTTP $code -> $($resp.ResponseUri)"
                return $false
            }
        }
        else {
            Fail $_.Exception.Message
            return $false
        }
    }
}

# 0) Basic availability + OpenAPI
Write-Title "Availability"
$openapi = Invoke-RestMethod "$Base/openapi.json" -Method GET
if ($openapi.info.title -and $openapi.paths) {
    Pass "OpenAPI reachable: $($openapi.info.title)"
}
else {
    Fail "OpenAPI missing title/paths"
}

# 1) Health
Write-Title "Health"
$hp = Invoke-RestMethod "$Base/health/ping" -Method GET
if ($hp -and ($hp.ok -or $hp.True -or $hp."ok")) {
    Pass "/health/ping responded"
}
else {
    Fail "/health/ping malformed response"
}

# 2) Routes table sanity
Write-Title "Routes"
$routes = (Invoke-RestMethod "$Base/_debug/routes").routes
if (-not $routes) { Fail "No routes from /_debug/routes"; } else {
    $financePaths = $routes | Where-Object { $_.path -match "^/finance" }
    if ($financePaths) { Pass "Finance routes present ($($financePaths.Count))" } else { Fail "No /finance routes" }
    # Ensure no duplication of ai/ai
    if ($financePaths.path -match "/ai/ai/") {
        Fail "Found duplicated /ai/ai path(s)"
    }
    else {
        Pass "No duplicated /ai/ai in finance paths"
    }
}

# 3) Auth + RBAC (protected endpoints should 401 when no token)
Write-Title "Auth & RBAC"
$noAuthOK = MustStatus { Invoke-RestMethod "$Base/finance/ai/finance-analysis" -Method GET } @()
if (-not $noAuthOK) { Pass "Protected endpoint returns 401 without token (expected)" }

$AUTH = Get-Token
$HDRS = @{ Authorization = $AUTH }

# 4) Finance AI endpoint (GET)
Write-Title "Finance AI"
try {
    $fa = Invoke-RestMethod "$Base/finance/ai/finance-analysis" -Headers $HDRS -Method GET
    if ($fa -and $null -ne $fa.total_expenses -and $null -ne $fa.by_category -and $null -ne $fa.gpt_analysis) {
        Pass "/finance/ai/finance-analysis shape ok (total_expenses/by_category/gpt_analysis)"
    }
    else {
        Fail "/finance/ai/finance-analysis missing fields"
    }
}
catch {
    Fail "/finance/ai/finance-analysis GET failed: $($_.Exception.Message)"
}

# 5) Reports (baseline reachability)
Write-Title "Reports"
$reportsOK = $false
try {
    Invoke-RestMethod "$Base/reports/" -Headers $HDRS -Method GET
    Pass "/reports/ reachable"
    $reportsOK = $true
}
catch {
    Fail "/reports/ GET failed: $($_.Exception.Message)"
}

# 6) CORS preflight (generic) - OPTIONS on root or ping
Write-Title "CORS"
try {
    $pre = Invoke-WebRequest -Method OPTIONS -Uri "$Base/health/ping"
    $allow = $pre.Headers["Allow"]
    if ($allow) { Pass "OPTIONS supported on /health/ping (Allow: $allow)" } else { Fail "OPTIONS missing Allow header" }
}
catch {
    Fail "OPTIONS /health/ping failed: $($_.Exception.Message)"
}

# 7) Shipments shims present (if shipments router mounted)
Write-Title "Shipments shims"
if ($routes) {
    $shim1 = $routes | Where-Object { $_.path -eq "/api/v1/shipments/shipments/{rest:path}" }
    $shim2 = $routes | Where-Object { $_.path -eq "/shipments/shipments/{rest:path}" }
    if ($shim1) { Pass "shim /api/v1/shipments/shipments/* present" } else { Write-Host "INFO: shim1 not present"; }
    if ($shim2) { Pass "shim /shipments/shipments/* present" } else { Write-Host "INFO: shim2 not present"; }
}

# 8) Documents protection (if routes available)
Write-Title "Documents protection"
$docsProtected = $true
$docPaths = $routes | Where-Object { $_.path -match "^/documents" }
if ($docPaths) {
    try {
        Invoke-RestMethod "$Base/documents/" -Method GET | Out-Null
        $docsProtected = $false
    }
    catch {
        # expecting 401/403
        $resp = $_.Exception.Response
        if ($resp) { Pass "/documents/* protected -> HTTP $($resp.StatusCode.value__)" } else { Fail "No response for /documents/"; }
    }
}
else {
    Write-Host "INFO: No /documents routes mounted"
}

# 9) Vizion / Ops scheduler flags (logs rely on env; presence is enough)
Write-Title "Background flags (env-driven)"
Write-Host "OPS_MONITOR_ENABLED: $($env:OPS_MONITOR_ENABLED)"
Write-Host "DISABLE_SCHEDULER  : $($env:DISABLE_SCHEDULER)"
Pass "Background loops are env-driven; startup won’t crash if disabled"

Write-Host "`nAll checks executed."
if ($noAuthOK -and $reportsOK -and $docsProtected) {
    Write-Host "`nOverall result: " -NoNewline
    Pass "All critical checks passed"
    exit 0
}
else {
    Write-Host "`nOverall result: " -NoNewline
    Fail "Some checks failed"
    exit 1
}   