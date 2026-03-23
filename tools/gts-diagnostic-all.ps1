# ===============================
# GTS LOGISTICS - FULL DIAGNOSTIC ALL-IN-ONE (v2.4)
# ===============================
# Checks:
# - Python dependencies & app modules
# - Backend health (ping/docs/openapi)
# - Auth & JWT
# - Core protected APIs (shipments/documents/finance)
# - AI bots endpoints existence (/ai/.../run)
# ===============================

param(
    [string]$BaseUrl = "http://127.0.0.1:8020",
    [string]$EnvFile = ".env"
)

Write-Host ""
Write-Host "GTS FULL DIAGNOSTIC - ALL IN ONE" -ForegroundColor Cyan
Write-Host "Timestamp: $(Get-Date)" -ForegroundColor Gray
Write-Host ""

# -------------------------------
# ENV LOADER
# -------------------------------
function Import-EnvFile {
    param([string]$filePath)

    if (Test-Path $filePath) {
        Get-Content $filePath | ForEach-Object {
            if ($_ -match '^\s*([^#][^=]+)=(.*)') {
                $key = $matches[1].Trim()
                $value = $matches[2].Trim()
                [Environment]::SetEnvironmentVariable($key, $value)
            }
        }
        Write-Host "[ INFO ] Loaded environment from $filePath" -ForegroundColor Blue
    }
    else {
        Write-Host "[ WARN ] Env file not found: $filePath" -ForegroundColor Yellow
    }
}

Import-EnvFile $EnvFile

# -------------------------------
# HTTP ENDPOINT TESTER
# -------------------------------
function Test-Endpoint {
    param(
        [string]$Url,
        [string]$Method = "GET",
        [string]$Token = $null,
        [object]$Body = $null,
        [bool]$AllowNon200 = $false
    )

    try {
        $Headers = @{}

        if ($Method -in @("POST", "PUT", "PATCH") -and $Body) {
            $Headers["Content-Type"] = "application/json"
        }

        if ($Token) {
            $Headers["Authorization"] = "Bearer $Token"
        }

        $Params = @{
            Uri         = $Url
            Method      = $Method
            Headers     = $Headers
            TimeoutSec  = 15
            ErrorAction = "Stop"
        }

        if ($Body) {
            $Params["Body"] = ($Body | ConvertTo-Json -Depth 5)
        }

        $Response = Invoke-WebRequest @Params

        $content = $null
        try {
            if ($Response.Content) {
                $content = $Response.Content | ConvertFrom-Json
            }
        }
        catch {
            $content = $null
        }

        if ($Response.StatusCode -eq 200 -or $AllowNon200) {
            Write-Host "[ OK   ] $Url (HTTP $($Response.StatusCode))" -ForegroundColor Green
        }
        else {
            Write-Host "[ WARN ] $Url (HTTP $($Response.StatusCode))" -ForegroundColor Yellow
        }

        return $content
    }
    catch {
        $msg = $_.Exception.Message
        Write-Host ("[ FAIL ] {0} (Error: {1})" -f $Url, $msg) -ForegroundColor Red
        return $null
    }
}

# -------------------------------
# PYTHON DIAGNOSTIC (INLINE)
# -------------------------------
function Invoke-GtsPythonDiagnostic {
    Write-Host ""
    Write-Host "== Python Dependencies & Modules ==" -ForegroundColor Cyan

    $projectRoot = (Split-Path $PSScriptRoot -Parent)
    [Environment]::SetEnvironmentVariable("GTS_PROJECT_ROOT", $projectRoot)

    $pythonCode = @'
import sys
import os
import importlib
import pkg_resources
from datetime import datetime

REQUIRED_PACKAGES = [
    "fastapi",
    "uvicorn",
    "sqlalchemy",
    "asyncpg",
    "alembic",
    "pydantic",
    "python-dotenv",
    "python-jose",
    "passlib",
    "bcrypt",
    "httpx"
]

OPTIONAL_PACKAGES = {
    "aiofiles": "Static files / file IO",
    "redis": "Cache and pub/sub features",
    "celery": "Background jobs",
    "pandas": "Reporting and analysis",
    "openpyxl": "Excel export/import",
    "websockets": "WebSocket support",
}

APP_MODULES = [
    "backend.main",
    "backend.database.config",
    "backend.models.user",
    "backend.models.document",
    # Adjust this to your actual shipment model module name if different
    "backend.models.shipment",
]

def check_package(name):
    try:
        dist = pkg_resources.get_distribution(name)
        return True, dist.version
    except pkg_resources.DistributionNotFound:
        return False, None

def main():
    root = os.environ.get("GTS_PROJECT_ROOT")
    if root and root not in sys.path:
        sys.path.insert(0, root)

    print("GTS PYTHON MODULE DIAGNOSTIC")
    print("=" * 40)
    print("Timestamp:", datetime.now().isoformat())
    print("Python:", sys.version.replace("\\n"," "))
    print("Project root:", root)
    print("")

    print("REQUIRED PACKAGES")
    print("-" * 40)
    all_ok = True
    for pkg in REQUIRED_PACKAGES:
        ok, ver = check_package(pkg)
        if ok:
            print(f"[OK   ] {pkg} (v{ver})")
        else:
            print(f"[MISS ] {pkg}")
            all_ok = False

    print("")
    print("OPTIONAL PACKAGES")
    print("-" * 40)
    for pkg, desc in OPTIONAL_PACKAGES.items():
        ok, ver = check_package(pkg)
        if ok:
            print(f"[OK   ] {pkg} (v{ver}) - {desc}")
        else:
            print(f"[OPT  ] {pkg} not installed ({desc})")

    print("")
    print("APPLICATION MODULES")
    print("-" * 40)
    for mod in APP_MODULES:
        try:
            importlib.import_module(mod)
            print(f"[OK   ] {mod}")
        except Exception as e:
            print(f"[FAIL ] {mod} ({e})")

    print("")
    print("=" * 40)
    if all_ok:
        print("SUMMARY: ALL REQUIRED PACKAGES INSTALLED")
        sys.exit(0)
    else:
        print("SUMMARY: SOME REQUIRED PACKAGES ARE MISSING")
        sys.exit(1)

if __name__ == "__main__":
    main()
'@

    $tempPy = Join-Path $env:TEMP "gts_python_diagnostic_temp.py"
    $pythonCode | Out-File -FilePath $tempPy -Encoding UTF8

    try {
        python $tempPy
    }
    catch {
        $msg = $_.Exception.Message
        Write-Host ("[ FAIL ] Python diagnostic failed: {0}" -f $msg) -ForegroundColor Red
    }
    finally {
        if (Test-Path $tempPy) {
            Remove-Item $tempPy -ErrorAction SilentlyContinue
        }
    }
}

# -------------------------------
# DATABASE VIA /shipments/
# -------------------------------
function Test-Database {
    param(
        [string]$Token
    )

    Write-Host ""
    Write-Host "== Database Connectivity (via /shipments/) ==" -ForegroundColor Cyan

    $result = Test-Endpoint "$BaseUrl/shipments/" -Token $Token -AllowNon200:$true
    if ($result -ne $null) {
        Write-Host "[ OK   ] Database is reachable through /shipments/" -ForegroundColor Green
    }
    else {
        Write-Host "[ WARN ] Could not confirm DB via /shipments/" -ForegroundColor Yellow
    }
}

# -------------------------------
# AI BOTS TEST (USING /ai/.../run)
# -------------------------------
function Test-AI-Bots {
    param(
        [string]$Token
    )

    Write-Host ""
    Write-Host "== AI Bots Endpoints Check ==" -ForegroundColor Cyan

    $bots = @(
        @{Name = "General Manager"; Path = "/ai/general_manager/run" },
        @{Name = "Finance Bot"; Path = "/ai/finance_bot/run" },
        @{Name = "Freight Broker"; Path = "/ai/freight_broker/run" },
        @{Name = "Operations Manager"; Path = "/ai/operations_manager/run" },
        @{Name = "Documents Manager"; Path = "/ai/documents_manager/run" },
        @{Name = "Maintenance Dev"; Path = "/ai/maintenance_dev/run" }
    )

    foreach ($bot in $bots) {
        $body = @{ prompt = "health check" }
        $result = Test-Endpoint "$BaseUrl$($bot.Path)" -Method "POST" -Token $Token -Body $body -AllowNon200:$true
        if ($null -ne $result) {
            Write-Host "[ OK   ] $($bot.Name) endpoint responded" -ForegroundColor Green
        }
        else {
            Write-Host "[ WARN ] $($bot.Name) endpoint not responding or not implemented" -ForegroundColor Yellow
        }
    }
}

# -------------------------------
# BASIC HEALTH
# -------------------------------
Write-Host "== Basic Health Endpoints ==" -ForegroundColor Cyan
Test-Endpoint "$BaseUrl/health/ping" -AllowNon200:$true
Test-Endpoint "$BaseUrl/docs" -AllowNon200:$true
Test-Endpoint "$BaseUrl/redoc" -AllowNon200:$true
Test-Endpoint "$BaseUrl/openapi.json" -AllowNon200:$true

# -------------------------------
# PYTHON DIAGNOSTIC
# -------------------------------
Invoke-GtsPythonDiagnostic

# -------------------------------
# AUTH / JWT
# -------------------------------
Write-Host ""
Write-Host "== Authentication Test ==" -ForegroundColor Cyan
$Token = $null

try {
    $loginBody = @{
        username   = "admin@gts.local"
        password   = "__SET_FROM_ENV__"
        grant_type = "password"
    }

    $tokenResponse = Test-Endpoint "$BaseUrl/auth/token" -Method "POST" -Body $loginBody -AllowNon200:$true

    if ($tokenResponse -and $tokenResponse.access_token) {
        $Token = $tokenResponse.access_token
        Write-Host "[ OK   ] JWT Token Acquired" -ForegroundColor Green
        Write-Host "[ INFO ] Token Type: $($tokenResponse.token_type)" -ForegroundColor Blue
    }
    else {
        Write-Host "[ FAIL ] Authentication failed or /auth/token response invalid" -ForegroundColor Red
    }
}
catch {
    Write-Host "[ FAIL ] Auth endpoint unreachable: $($_.Exception.Message)" -ForegroundColor Red
}

# -------------------------------
# CORE PROTECTED API ENDPOINTS
# -------------------------------
Write-Host ""
Write-Host "== Core Protected API Endpoints ==" -ForegroundColor Cyan

$protectedEndpoints = @(
    @{Path = "/shipments/"; Method = "GET"; Name = "Shipments List" },
    @{Path = "/documents/"; Method = "GET"; Name = "Documents List" },
    @{Path = "/finance/health"; Method = "GET"; Name = "Finance Health" }
)

foreach ($ep in $protectedEndpoints) {
    $result = Test-Endpoint "$BaseUrl$($ep.Path)" -Token $Token -Method $ep.Method -AllowNon200:$true
    if ($result) {
        Write-Host "[ INFO ] $($ep.Name) responded" -ForegroundColor Blue
    }
}

# -------------------------------
# DATABASE VIA /shipments/
# -------------------------------
Test-Database -Token $Token

# -------------------------------
# AI BOTS
# -------------------------------
Test-AI-Bots -Token $Token

Write-Host ""
Write-Host "=================================" -ForegroundColor Cyan
Write-Host "GTS FULL DIAGNOSTIC COMPLETED" -ForegroundColor Green
Write-Host "Timestamp: $(Get-Date)" -ForegroundColor Gray
Write-Host "=================================" -ForegroundColor Cyan
Write-Host ""
