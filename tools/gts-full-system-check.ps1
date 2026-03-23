# ===============================
# GTS FULL SYSTEM DIAGNOSTIC v2.2
# ===============================
# Runs full health check on:
# Backend, Auth, APIs, AI Bots, WebSocket, Database
# ===============================

param(
    [string]$BaseUrl = "http://127.0.0.1:8020",
    [string]$EnvFile = ".env"
)

Write-Host ""
Write-Host "🚀 Starting Full GTS Diagnostic v2.2..." -ForegroundColor Cyan
Write-Host "Timestamp: $(Get-Date)" -ForegroundColor Gray
Write-Host ""

# Load environment variables
function Load-Env {
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
}

Load-Env $EnvFile

function Test-Endpoint {
    param(
        [string]$Url,
        [string]$Method = "GET",
        [string]$Token = $null,
        [object]$Body = $null
    )

    try {
        $Headers = @{
            "Content-Type" = "application/json"
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
            $Params["Body"] = ($Body | ConvertTo-Json)
        }

        $Response = Invoke-WebRequest @Params
        $Content = $Response.Content | ConvertFrom-Json

        if ($Response.StatusCode -eq 200) {
            Write-Host "[ OK   ] $Url" -ForegroundColor Green
            return $Content
        }
        else {
            Write-Host "[ WARN ] $Url (HTTP $($Response.StatusCode))" -ForegroundColor Yellow
            return $null
        }
    }
    catch {
        $msg = $_.Exception.Message
        Write-Host ("[ FAIL ] {0} (Error: {1})" -f $Url, $msg) -ForegroundColor Red
        return $null
    }
}

function Test-Database {
    Write-Host "== Database Connection Test ==" -ForegroundColor Cyan
    
    try {
        $dbUrl = [Environment]::GetEnvironmentVariable("DATABASE_URL")
        if (-not $dbUrl) {
            Write-Host "[ FAIL ] DATABASE_URL not found in environment" -ForegroundColor Red
            return $false
        }

        # Test with psql if available
        if (Get-Command psql -ErrorAction SilentlyContinue) {
            $connParts = $dbUrl -replace 'postgresql\+asyncpg://', '' -split '@'
            $userPass = $connParts[0] -split ':'
            $hostDb = $connParts[1] -split '/'
            $hostPort = $hostDb[0] -split ':'
            
            $env:PGPASSWORD = $userPass[1]
            $result = & psql -h $hostPort[0] -p $hostPort[1] -U $userPass[0] -d $hostDb[1] -c "SELECT version();" -t 2>$null
            
            if ($LASTEXITCODE -eq 0) {
                Write-Host "[ OK   ] Database connection successful" -ForegroundColor Green
                Write-Host "[ INFO ] PostgreSQL Version: $($result.Trim())" -ForegroundColor Blue
                return $true
            }
        }
        
        # Fallback: Test via API
        $testResult = Test-Endpoint "$BaseUrl/health/database"
        return ($testResult -ne $null)
    }
    catch {
        Write-Host "[ FAIL ] Database test failed: $($_.Exception.Message)" -ForegroundColor Red
        return $false
    }
}

function Test-AI-Bots {
    Write-Host "== AI Bots Health Check ==" -ForegroundColor Cyan
    
    $bots = @(
        @{Name = "General Manager"; Endpoint = "/ai/general_manager/health" },
        @{Name = "Finance Bot"; Endpoint = "/ai/finance_bot/health" },
        @{Name = "Freight Broker"; Endpoint = "/ai/freight_broker/health" },
        @{Name = "Operations Manager"; Endpoint = "/ai/operations_manager/health" },
        @{Name = "Maintenance Dev"; Endpoint = "/ai/maintenance_dev/health" }
    )
    
    foreach ($bot in $bots) {
        $result = Test-Endpoint "$BaseUrl$($bot.Endpoint)" -Token $Token
        if ($result) {
            Write-Host "[ OK   ] $($bot.Name) Bot" -ForegroundColor Green
        }
        else {
            Write-Host "[ FAIL ] $($bot.Name) Bot" -ForegroundColor Red
        }
    }
}

function Test-Services {
    Write-Host "== External Services ==" -ForegroundColor Cyan
    
    $services = @(
        @{Name = "Email Service"; Endpoint = "/health/email" },
        @{Name = "SMS Service"; Endpoint = "/health/sms" },
        @{Name = "File Storage"; Endpoint = "/health/storage" },
        @{Name = "Cache Service"; Endpoint = "/health/cache" }
    )
    
    foreach ($service in $services) {
        $result = Test-Endpoint "$BaseUrl$($service.Endpoint)" -Token $Token
        if ($result -and $result.status -eq "healthy") {
            Write-Host "[ OK   ] $($service.Name)" -ForegroundColor Green
        }
        else {
            Write-Host "[ WARN ] $($service.Name)" -ForegroundColor Yellow
        }
    }
}

# 1) Basic health
Write-Host "== Basic Health Endpoints ==" -ForegroundColor Cyan
Test-Endpoint "$BaseUrl/health"
Test-Endpoint "$BaseUrl/health/ping"
Test-Endpoint "$BaseUrl/docs"
Test-Endpoint "$BaseUrl/redoc"
Test-Endpoint "$BaseUrl/openapi.json"

# 2) Database Test
Test-Database

# 3) Get Admin Token
Write-Host ""
Write-Host "== Authentication Test ==" -ForegroundColor Cyan
$Token = $null

try {
    $loginBody = @{
        username   = "admin@gts.local"
        password   = "__SET_FROM_ENV__"
        grant_type = "password"
    }

    $tokenResponse = Test-Endpoint "$BaseUrl/auth/token" -Method "POST" -Body $loginBody
    
    if ($tokenResponse -and $tokenResponse.access_token) {
        $Token = $tokenResponse.access_token
        Write-Host "[ OK   ] JWT Token Acquired" -ForegroundColor Green
        Write-Host "[ INFO ] Token Type: $($tokenResponse.token_type)" -ForegroundColor Blue
    }
    else {
        Write-Host "[ FAIL ] Authentication failed" -ForegroundColor Red
        exit 1
    }
}
catch {
    Write-Host "[ FAIL ] Auth endpoint unreachable: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# 4) Protected APIs
Write-Host ""
Write-Host "== Protected API Endpoints ==" -ForegroundColor Cyan

$protectedEndpoints = @(
    @{Path = "/shipments/"; Method = "GET"; Name = "Shipments List" },
    @{Path = "/shipments/stats"; Method = "GET"; Name = "Shipments Stats" },
    @{Path = "/vehicles/"; Method = "GET"; Name = "Vehicles List" },
    @{Path = "/drivers/"; Method = "GET"; Name = "Drivers List" },
    @{Path = "/finance/transactions"; Method = "GET"; Name = "Transactions" },
    @{Path = "/reports/shipments"; Method = "GET"; Name = "Shipments Report" },
    @{Path = "/notifications/"; Method = "GET"; Name = "Notifications" },
    @{Path = "/users/me"; Method = "GET"; Name = "User Profile" }
)

foreach ($ep in $protectedEndpoints) {
    $result = Test-Endpoint "$BaseUrl$($ep.Path)" -Token $Token -Method $ep.Method
    if ($result) {
        Write-Host "[ OK   ] $($ep.Name)" -ForegroundColor Green
    }
}

# 5) AI Bots Test
Test-AI-Bots

# 6) Services Test
Test-Services

# 7) WebSocket check
Write-Host ""
Write-Host "== WebSocket Connection Test ==" -ForegroundColor Cyan

try {
    Add-Type -Path "System.Net.WebSockets.Client.dll" -ErrorAction SilentlyContinue
    
    $ws = New-Object System.Net.WebSockets.ClientWebSocket
    $uri = [System.Uri]::new("$BaseUrl/ws/status".Replace("http", "ws"))
    $cts = New-Object System.Threading.CancellationTokenSource
    $task = $ws.ConnectAsync($uri, $cts.Token)
    
    # Wait with timeout
    if ($task.Wait(5000)) {
        if ($ws.State -eq [System.Net.WebSockets.WebSocketState]::Open) {
            Write-Host "[ OK   ] WebSocket Connected" -ForegroundColor Green
            
            # Test message sending
            $message = [System.Text.Encoding]::UTF8.GetBytes('{"type":"ping"}')
            $sendTask = $ws.SendAsync(
                [System.ArraySegment[byte]]::new($message),
                [System.Net.WebSockets.WebSocketMessageType]::Text,
                $true,
                $cts.Token
            )
            $sendTask.Wait(2000)
            
            Write-Host "[ OK   ] WebSocket Message Sent" -ForegroundColor Green
            $ws.Dispose()
        }
        else {
            Write-Host "[ FAIL ] WebSocket Not Open (State: $($ws.State))" -ForegroundColor Red
        }
    }
    else {
        Write-Host "[ FAIL ] WebSocket Connection Timeout" -ForegroundColor Red
        $cts.Cancel()
    }
}
catch {
    $msg = $_.Exception.Message
    Write-Host ("[ FAIL ] WebSocket Error: {0}" -f $msg) -ForegroundColor Red
}

# 8) Background Jobs
Write-Host ""
Write-Host "== Background Jobs & Bots ==" -ForegroundColor Cyan

$jobs = @(
    "/jobs/tracking/status",
    "/jobs/notifications/status",
    "/jobs/reports/status"
)

foreach ($job in $jobs) {
    $result = Test-Endpoint "$BaseUrl$job" -Token $Token
    if ($result -and $result.status -eq "running") {
        Write-Host "[ OK   ] $($job.Split('/')[-2]) Job" -ForegroundColor Green
    }
    else {
        Write-Host "[ WARN ] $($job.Split('/')[-2]) Job" -ForegroundColor Yellow
    }
}

# 9) System Metrics
Write-Host ""
Write-Host "== System Metrics ==" -ForegroundColor Cyan

$metrics = Test-Endpoint "$BaseUrl/health/metrics" -Token $Token
if ($metrics) {
    Write-Host "[ INFO ] Active Shipments: $($metrics.active_shipments)" -ForegroundColor Blue
    Write-Host "[ INFO ] Total Users: $($metrics.total_users)" -ForegroundColor Blue
    Write-Host "[ INFO ] API Requests Today: $($metrics.daily_requests)" -ForegroundColor Blue
    Write-Host "[ INFO ] Database Size: $($metrics.db_size)" -ForegroundColor Blue
}

Write-Host ""
Write-Host "=================================" -ForegroundColor Cyan
Write-Host "DIAGNOSTIC COMPLETED SUCCESSFULLY" -ForegroundColor Green
Write-Host "Timestamp: $(Get-Date)" -ForegroundColor Gray
Write-Host "=================================" -ForegroundColor Cyan
Write-Host ""