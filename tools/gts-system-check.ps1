param(
    [string]$BaseUrl = "http://127.0.0.1:8020",
    [int]$TimeoutSec = 5
)

Write-Host "=== GTS Logistics - System Self Check ==="
Write-Host "Base URL: $BaseUrl"
Write-Host ""

$tests = @(
    @{ Name = "Backend Health"; Path = "/health/ping"; Method = "GET"; Expect = 200; Allow401 = $false },
    @{ Name = "OpenAPI JSON"; Path = "/openapi.json"; Method = "GET"; Expect = 200; Allow401 = $false },
    @{ Name = "Swagger Docs"; Path = "/docs"; Method = "GET"; Expect = 200; Allow401 = $false },
    @{ Name = "Auth Debug"; Path = "/auth/debug"; Method = "GET"; Expect = 200; Allow401 = $false },
    @{ Name = "Finance Health"; Path = "/finance/health"; Method = "GET"; Expect = 200; Allow401 = $true },
    @{ Name = "Shipments List"; Path = "/shipments/"; Method = "GET"; Expect = 200; Allow401 = $true },
    @{ Name = "Documents List"; Path = "/documents/"; Method = "GET"; Expect = 200; Allow401 = $true }
    # We disabled AI Bots Registry because it's not an official route
)

function Test-Endpoint {
    param(
        [string]$Name,
        [string]$Url,
        [string]$Method,
        [int]$Expect,
        [int]$TimeoutSec,
        [bool]$Allow401
    )

    try {
        $resp = Invoke-WebRequest -Uri $Url -Method $Method -TimeoutSec $TimeoutSec -ErrorAction Stop
        if ($resp.StatusCode -eq $Expect) {
            return [pscustomobject]@{
                Component = $Name
                Url       = $Url
                Status    = "OK"
                Detail    = "HTTP $($resp.StatusCode)"
            }
        }
        else {
            return [pscustomobject]@{
                Component = $Name
                Url       = $Url
                Status    = "WARN"
                Detail    = "Expected $Expect, got $($resp.StatusCode)"
            }
        }
    }
    catch {
        $msg = $_.Exception.Message
        $code = $null
        if ($_.Exception.Response -and $_.Exception.Response.StatusCode) {
            $code = [int]$_.Exception.Response.StatusCode
            if ($code -eq 401 -and $Allow401) {
                return [pscustomobject]@{
                    Component = $Name
                    Url       = $Url
                    Status    = "WARN"
                    Detail    = "Protected endpoint (HTTP 401) - Auth required"
                }
            }
            $msg = "HTTP $code - $msg"
        }
        return [pscustomobject]@{
            Component = $Name
            Url       = $Url
            Status    = "FAIL"
            Detail    = $msg
        }
    }
}

$results = @()

foreach ($t in $tests) {
    $url = $BaseUrl.TrimEnd('/') + $t.Path
    Write-Host "Checking $($t.Name) [$url] ..."
    $res = Test-Endpoint -Name $t.Name -Url $url -Method $t.Method -Expect $t.Expect -TimeoutSec $TimeoutSec -Allow401 $t.Allow401
    switch ($res.Status) {
        "OK" { Write-Host "  OK   - $($res.Component): $($res.Detail)" }
        "WARN" { Write-Host "  WARN - $($res.Component): $($res.Detail)" }
        "FAIL" { Write-Host "  FAIL - $($res.Component): $($res.Detail)" }
    }
    $results += $res
}

Write-Host ""
Write-Host "=== Summary ==="

$ok = ($results | Where-Object { $_.Status -eq "OK" }).Count
$warn = ($results | Where-Object { $_.Status -eq "WARN" }).Count
$fail = ($results | Where-Object { $_.Status -eq "FAIL" }).Count

Write-Host "OK   : $ok"
Write-Host "WARN : $warn"
Write-Host "FAIL : $fail"
Write-Host ""

$results | Sort-Object Status, Component | Format-Table Component, Status, Detail -AutoSize

if ($fail -gt 0) {
    Write-Host ""
    Write-Host "Some checks FAILED. Investigate the components marked as FAIL."
    exit 1
}
elseif ($warn -gt 0) {
    Write-Host ""
    Write-Host "All critical checks passed, but there are WARNINGS to review."
    exit 0
}
else {
    Write-Host ""
    Write-Host "All checks passed. System looks healthy."
    exit 0
}
