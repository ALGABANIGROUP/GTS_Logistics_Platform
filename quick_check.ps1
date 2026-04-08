param(
    [switch]$Verbose,
    [switch]$Fix
)

$ErrorActionPreference = "Stop"

Write-Host "GTS Platform - Quick Check" -ForegroundColor Cyan
Write-Host "==========================" -ForegroundColor Cyan
Write-Host "Started: $(Get-Date)" -ForegroundColor DarkGray
Write-Host ""

$passed = 0
$failed = 0

function Write-Pass([string]$Message) {
    Write-Host "$Message PASS" -ForegroundColor Green
    $script:passed++
}

function Write-Fail([string]$Message, [string]$Hint = "") {
    Write-Host "$Message FAIL" -ForegroundColor Red
    if ($Fix -and $Hint) {
        Write-Host "  Fix: $Hint" -ForegroundColor Yellow
    }
    $script:failed++
}

function Test-Url([string]$Label, [string]$Url, [int]$TimeoutSec = 8) {
    Write-Host "$Label " -NoNewline
    try {
        $resp = Invoke-WebRequest -Uri $Url -UseBasicParsing -TimeoutSec $TimeoutSec
        if ($resp.StatusCode -ge 200 -and $resp.StatusCode -lt 300) {
            if ($Verbose) {
                Write-Host ""
                Write-Host "  $Url -> $($resp.StatusCode)" -ForegroundColor DarkGray
            }
            Write-Pass ""
            return $true
        }
        Write-Fail "" "Check service bound to $Url"
        return $false
    } catch {
        Write-Fail "" "Start the service for $Url"
        if ($Verbose) {
            Write-Host "  $($_.Exception.Message)" -ForegroundColor DarkGray
        }
        return $false
    }
}

Write-Host "Python installation... " -NoNewline
try {
    $version = & .\.venv\Scripts\python.exe --version 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Pass ""
        if ($Verbose) { Write-Host "  $version" -ForegroundColor DarkGray }
    } else {
        Write-Fail "" "Create the environment with: python -m venv .venv"
    }
} catch {
    Write-Fail "" "Create the environment with: python -m venv .venv"
}

Write-Host "Virtual environment... " -NoNewline
if (Test-Path ".venv\Scripts\python.exe") {
    Write-Pass ""
} else {
    Write-Fail "" "Create the environment with: python -m venv .venv"
}

Write-Host "Backend environment file... " -NoNewline
if ((Test-Path "backend\.env") -or (Test-Path ".env")) {
    Write-Pass ""
} else {
    Write-Fail "" "Copy backend\env.example to backend\.env"
}

Write-Host "Backend health... " -NoNewline
$backendOk = Test-Url "" "http://localhost:8000/health"

Write-Host "Backend docs... " -NoNewline
$null = Test-Url "" "http://localhost:8000/docs"

Write-Host "Frontend health... " -NoNewline
$null = Test-Url "" "http://localhost:5173"

Write-Host "System health API... " -NoNewline
$null = Test-Url "" "http://localhost:8000/api/v1/system/health"

Write-Host "Support health API... " -NoNewline
$null = Test-Url "" "http://localhost:8000/api/v1/support/health"

Write-Host "Bots status API... " -NoNewline
$null = Test-Url "" "http://localhost:8000/api/v1/system/bots/status"

Write-Host "Login test... " -NoNewline
try {
    $body = '{"email":"enjoy983@hotmail.com","password":"Gabani@2026"}'
    $login = Invoke-WebRequest -Uri "http://localhost:8000/api/v1/auth/login" -Method POST -Body $body -ContentType "application/json" -UseBasicParsing -TimeoutSec 10
    if ($login.StatusCode -eq 200) {
        Write-Pass ""
        if ($Verbose) {
            $json = $login.Content | ConvertFrom-Json
            Write-Host "  Token received for: $($json.user.email)" -ForegroundColor DarkGray
        }
    } else {
        Write-Fail "" "Verify credentials or auth service"
    }
} catch {
    Write-Fail "" "Verify credentials or auth service"
    if ($Verbose) {
        Write-Host "  $($_.Exception.Message)" -ForegroundColor DarkGray
    }
}

Write-Host ""
Write-Host "Summary" -ForegroundColor Cyan
Write-Host "-------" -ForegroundColor Cyan
Write-Host "Passed: $passed" -ForegroundColor Green
Write-Host "Failed: $failed" -ForegroundColor Red

if ($failed -eq 0) {
    Write-Host "All quick checks passed." -ForegroundColor Green
} else {
    Write-Host "Some checks failed. Review the hints above." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Completed: $(Get-Date)" -ForegroundColor DarkGray
