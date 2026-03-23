param(
  [string]$BaseUrl = "http://127.0.0.1:8000",
  [string]$Username = "",
  [string]$Password = "",
  [string]$Token = "",
  [switch]$RunWriteChecks
)

$ErrorActionPreference = "Stop"

function Write-Section {
  param([string]$Title)
  Write-Host ""
  Write-Host ("=" * 72) -ForegroundColor DarkGray
  Write-Host $Title -ForegroundColor Cyan
  Write-Host ("=" * 72) -ForegroundColor DarkGray
}

function Write-Pass {
  param([string]$Message)
  Write-Host "[PASS] $Message" -ForegroundColor Green
}

function Write-Fail {
  param([string]$Message)
  Write-Host "[FAIL] $Message" -ForegroundColor Red
}

function Write-WarnLine {
  param([string]$Message)
  Write-Host "[WARN] $Message" -ForegroundColor Yellow
}

function Invoke-JsonGet {
  param(
    [string]$Url,
    [hashtable]$Headers = @{}
  )
  return Invoke-RestMethod -Method Get -Uri $Url -Headers $Headers
}

function Invoke-JsonPost {
  param(
    [string]$Url,
    [object]$Body,
    [hashtable]$Headers = @{}
  )
  $jsonBody = $Body | ConvertTo-Json -Depth 10
  $localHeaders = @{}
  foreach ($k in $Headers.Keys) {
    $localHeaders[$k] = $Headers[$k]
  }
  $localHeaders["Content-Type"] = "application/json"
  return Invoke-RestMethod -Method Post -Uri $Url -Headers $localHeaders -Body $jsonBody
}

function Test-Step {
  param(
    [string]$Name,
    [scriptblock]$Action
  )

  try {
    $result = & $Action
    Write-Pass $Name
    return [pscustomobject]@{
      name = $Name
      ok = $true
      result = $result
    }
  }
  catch {
    $message = $_.Exception.Message
    if ($_.ErrorDetails.Message) {
      $message = $_.ErrorDetails.Message
    }
    Write-Fail ("{0} -> {1}" -f $Name, $message)
    return [pscustomobject]@{
      name = $Name
      ok = $false
      result = $null
      error = $message
    }
  }
}

Write-Section "GTS Full Project Verification"

$headers = @{}

if (-not $Token) {
  if (-not $Username -or -not $Password) {
    throw "Provide -Token or both -Username and -Password."
  }

  Write-Section "Authentication"

  $authBody = "username=$([uri]::EscapeDataString($Username))&password=$([uri]::EscapeDataString($Password))"
  $authResponse = Invoke-RestMethod `
    -Method Post `
    -Uri "$BaseUrl/api/v1/auth/token" `
    -ContentType "application/x-www-form-urlencoded" `
    -Body $authBody

  if (-not $authResponse.access_token) {
    throw "Authentication succeeded but no access token was returned."
  }

  $Token = [string]$authResponse.access_token
  Write-Pass "Access token acquired"
}
else {
  Write-Section "Authentication"
  Write-Pass "Using provided bearer token"
}

$headers["Authorization"] = "Bearer $Token"

$results = @()

Write-Section "Read-Only Checks"

$results += Test-Step "Users stats" {
  $data = Invoke-JsonGet -Url "$BaseUrl/api/v1/admin/users/management?skip=0&limit=5" -Headers $headers
  $userCount = @($data.users).Count
  if ($null -eq $data -or $null -eq $data.users) { throw "Users payload missing." }
  @{
    users_count = $userCount
  }
}

$results += Test-Step "Shipments stats" {
  $data = Invoke-JsonGet -Url "$BaseUrl/api/v1/shipments/stats" -Headers $headers
  if ($null -eq $data) { throw "No payload returned." }
  $data
}

$results += Test-Step "Email mailboxes" {
  $data = Invoke-JsonGet -Url "$BaseUrl/api/v1/email/mailboxes" -Headers $headers
  if ($null -eq $data) { throw "No payload returned." }
  $data
}

$results += Test-Step "Customer service chat" {
  $data = Invoke-JsonPost -Url "$BaseUrl/api/v1/customer-service/chat" -Headers $headers -Body @{
    message = "I need help with my invoice"
    user_id = "smoke-user"
  }
  if (-not $data.response) { throw "Response field missing." }
  $data
}

$results += Test-Step "Freight broker match" {
  $data = Invoke-JsonPost -Url "$BaseUrl/api/v1/freight-broker/match" -Headers $headers -Body @{
    origin = "Toronto"
    destination = "Chicago"
    weight = 24000
  }
  if ($null -eq $data) { throw "No payload returned." }
  $data
}

$results += Test-Step "Reports stats" {
  $data = Invoke-JsonGet -Url "$BaseUrl/api/v1/reports/stats" -Headers $headers
  if ($null -eq $data) { throw "No payload returned." }
  $data
}

$results += Test-Step "Learning stats" {
  $data = Invoke-JsonGet -Url "$BaseUrl/ai/learning/stats"
  if ($null -eq $data) { throw "No payload returned." }
  $data
}

$results += Test-Step "Maintenance health summary" {
  $data = Invoke-JsonGet -Url "$BaseUrl/api/v1/maintenance-dev/health-summary"
  if ($null -eq $data) { throw "No payload returned." }
  $data
}

$results += Test-Step "Database user count" {
  $command = @'
import asyncio
from sqlalchemy import text
from backend.database.config import get_sessionmaker

async def main():
    maker = get_sessionmaker()
    async with maker() as session:
        result = await session.execute(text("SELECT COUNT(*) FROM users"))
        print(result.scalar() or 0)

asyncio.run(main())
'@
  $count = $command | python -
  if (-not $count) { throw "No count returned." }
  [int]($count | Select-Object -Last 1)
}

$results += Test-Step "Database shipment count" {
  $command = @'
import asyncio
from sqlalchemy import text
from backend.database.config import get_sessionmaker

async def main():
    maker = get_sessionmaker()
    async with maker() as session:
        result = await session.execute(text("SELECT COUNT(*) FROM shipments"))
        print(result.scalar() or 0)

asyncio.run(main())
'@
  $count = $command | python -
  if (-not $count) { throw "No count returned." }
  [int]($count | Select-Object -Last 1)
}

if ($RunWriteChecks) {
  Write-Section "Optional Write Checks"

  $results += Test-Step "Learning trigger for customer_service" {
    $data = Invoke-JsonPost -Url "$BaseUrl/ai/learning/trigger/customer_service" -Body @{}
    if ($null -eq $data) { throw "No payload returned." }
    $data
  }

  $results += Test-Step "Maintenance auto-repair" {
    $data = Invoke-JsonPost -Url "$BaseUrl/api/v1/maintenance-dev/auto-repair" -Body @{}
    if ($null -eq $data) { throw "No payload returned." }
    $data
  }
}
else {
  Write-WarnLine "Write checks skipped. Re-run with -RunWriteChecks to trigger learning and auto-repair."
}

Write-Section "Summary"

$passed = @($results | Where-Object { $_.ok }).Count
$failed = @($results | Where-Object { -not $_.ok }).Count
$total = $results.Count

Write-Host ("Passed: {0}/{1}" -f $passed, $total) -ForegroundColor Green
Write-Host ("Failed: {0}/{1}" -f $failed, $total) -ForegroundColor ($(if ($failed -gt 0) { "Red" } else { "Green" }))

if ($failed -gt 0) {
  Write-Host ""
  Write-Host "Failed checks:" -ForegroundColor Yellow
  $results | Where-Object { -not $_.ok } | ForEach-Object {
    Write-Host ("- {0}: {1}" -f $_.name, $_.error) -ForegroundColor Yellow
  }
  exit 1
}

Write-Pass "All selected checks completed successfully."
