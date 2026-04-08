param(
    [switch]$Full
)

$ErrorActionPreference = "Continue"

Write-Host "GTS Platform - Diagnostic Tool" -ForegroundColor Cyan
Write-Host "==============================" -ForegroundColor Cyan
Write-Host ""

function Show-Section([string]$Title) {
    Write-Host ""
    Write-Host $Title -ForegroundColor Yellow
}

function Read-EnvValue([string]$Path, [string]$Key) {
    if (-not (Test-Path $Path)) { return $null }
    $content = Get-Content -Path $Path -Raw
    $pattern = '(?m)^' + [regex]::Escape($Key) + '=(.*)$'
    $match = [regex]::Match($content, $pattern)
    if ($match.Success) {
        return $match.Groups[1].Value
    }
    return $null
}

function Invoke-DebugRequest([string]$Method, [string]$Url, [hashtable]$Headers = $null, [string]$Body = $null) {
    try {
        $params = @{
            Uri = $Url
            Method = $Method
            UseBasicParsing = $true
            TimeoutSec = 12
        }
        if ($Headers) { $params.Headers = $Headers }
        if ($Body) {
            $params.Body = $Body
            $params.ContentType = "application/json"
        }
        $resp = Invoke-WebRequest @params
        return [PSCustomObject]@{
            Url = $Url
            Status = $resp.StatusCode
            Body = $resp.Content.Substring(0, [Math]::Min(250, $resp.Content.Length))
        }
    } catch {
        $status = $null
        try { $status = $_.Exception.Response.StatusCode.value__ } catch {}
        [PSCustomObject]@{
            Url = $Url
            Status = if ($status) { $status } else { "ERROR" }
            Body = $_.Exception.Message
        }
    }
}

Show-Section "1. Environment"
Write-Host "Working directory: $(Get-Location)" -ForegroundColor DarkGray
if (Test-Path ".venv\Scripts\python.exe") {
    $py = & .\.venv\Scripts\python.exe --version 2>&1
    Write-Host "Python: $py" -ForegroundColor Green
} else {
    Write-Host "Python venv: missing (.venv)" -ForegroundColor Red
}

Show-Section "2. Key Variables"
$envFiles = @(
    (Join-Path $PSScriptRoot "backend\.env"),
    (Join-Path $PSScriptRoot ".env")
) | Where-Object { Test-Path $_ }
if ($envFiles.Count -eq 0) {
    Write-Host "No local env file found." -ForegroundColor Yellow
} else {
    $envPath = $envFiles[0]
    foreach ($key in @("DATABASE_URL", "JWT_SECRET_KEY", "ENVIRONMENT", "SMTP_HOST", "SMTP_FROM")) {
        $value = Read-EnvValue -Path $envPath -Key $key
        if ($value) {
            $preview = if ($value.Length -gt 40) { $value.Substring(0, 40) + "..." } else { $value }
            Write-Host "$key = $preview" -ForegroundColor Green
        } else {
            Write-Host "$key = NOT SET" -ForegroundColor Yellow
        }
    }
}

Show-Section "3. Ports"
foreach ($port in @(8000, 5173, 5432, 6379)) {
    $bound = Get-NetTCPConnection -LocalPort $port -ErrorAction SilentlyContinue
    if ($bound) {
        Write-Host "Port $port in use" -ForegroundColor Green
    } else {
        Write-Host "Port $port free" -ForegroundColor DarkGray
    }
}

Show-Section "4. Public Endpoints"
$publicChecks = @(
    @{ Method = "GET"; Url = "http://localhost:8000/health" },
    @{ Method = "GET"; Url = "http://localhost:8000/" },
    @{ Method = "GET"; Url = "http://localhost:8000/docs" },
    @{ Method = "GET"; Url = "http://localhost:8000/api/v1/system/health" },
    @{ Method = "GET"; Url = "http://localhost:8000/api/v1/admin/health" },
    @{ Method = "GET"; Url = "http://localhost:8000/api/v1/system/bots/status" },
    @{ Method = "GET"; Url = "http://localhost:8000/api/v1/support/health" },
    @{ Method = "GET"; Url = "http://localhost:8000/finance/health" },
    @{ Method = "GET"; Url = "http://localhost:5173" }
)

foreach ($check in $publicChecks) {
    $result = Invoke-DebugRequest -Method $check.Method -Url $check.Url
    $color = if ($result.Status -eq 200) { "Green" } else { "Red" }
    Write-Host "$($result.Url) -> $($result.Status)" -ForegroundColor $color
}

Show-Section "5. Authentication"
$loginBody = '{"email":"enjoy983@hotmail.com","password":"Gabani@2026"}'
$login = Invoke-DebugRequest -Method "POST" -Url "http://localhost:8000/api/v1/auth/login" -Body $loginBody
Write-Host "Login -> $($login.Status)" -ForegroundColor $(if ($login.Status -eq 200) { "Green" } else { "Red" })

$token = $null
if ($login.Status -eq 200) {
    try {
        $rawLogin = Invoke-WebRequest -Uri "http://localhost:8000/api/v1/auth/login" -Method POST -Body $loginBody -ContentType "application/json" -UseBasicParsing -TimeoutSec 12
        $loginJson = $rawLogin.Content | ConvertFrom-Json
        $token = $loginJson.access_token
    } catch {}
}

if ($token) {
    $headers = @{ Authorization = "Bearer $token" }
    foreach ($url in @(
        "http://localhost:8000/api/v1/auth/me",
        "http://localhost:8000/api/v1/ai/bots/available",
        "http://localhost:8000/api/v1/ai/bots/current-user/available",
        "http://localhost:8000/api/v1/admin/users"
    )) {
        $result = Invoke-DebugRequest -Method "GET" -Url $url -Headers $headers
        $color = if ($result.Status -eq 200) { "Green" } elseif ($result.Status -eq 401) { "Yellow" } else { "Red" }
        Write-Host "$url -> $($result.Status)" -ForegroundColor $color
        if ($Full) {
            Write-Host "  $($result.Body)" -ForegroundColor DarkGray
        }
    }
} else {
    Write-Host "Protected endpoint checks skipped because token extraction failed." -ForegroundColor Yellow
}

Show-Section "6. Notes"
Write-Host "Current project uses .venv in the repository root." -ForegroundColor DarkGray
Write-Host "Current backend start command: .\\.venv\\Scripts\\python.exe -m uvicorn backend.main:app --host 127.0.0.1 --port 8000" -ForegroundColor DarkGray
Write-Host "Some protected bot/admin endpoints may return 'Session revoked' depending on the current auth/session layer." -ForegroundColor DarkGray

Write-Host ""
Write-Host "Diagnostic complete." -ForegroundColor Cyan
