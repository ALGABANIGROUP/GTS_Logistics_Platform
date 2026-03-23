# Executive Intelligence Bot - Quick API Test
# Simple PowerShell test script

$base = "http://127.0.0.1:8000"

Write-Host ""
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host "  Testing Executive Intelligence Bot API" -ForegroundColor Cyan
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Login
Write-Host "[1/8] Logging in..." -ForegroundColor Yellow
try {
    $loginBody = @{
        email = "admin@gts.local"
        password = "admin123"
    }
    
    $loginResponse = Invoke-RestMethod `
        -Uri "$base/auth/token" `
        -Method Post `
        -ContentType "application/x-www-form-urlencoded" `
        -Body $loginBody
    
    $token = $loginResponse.access_token
    Write-Host "      Success! Token obtained" -ForegroundColor Green
} catch {
    Write-Host "      Failed: $_" -ForegroundColor Red
    Write-Host ""
    Write-Host "NOTE: Make sure backend server is running:" -ForegroundColor Yellow
    Write-Host "      cd d:\GTS" -ForegroundColor White
    Write-Host "      .\run-dev.ps1" -ForegroundColor White
    exit 1
}

$headers = @{
    "Authorization" = "Bearer $token"
    "Content-Type" = "application/json"
}

Write-Host ""

# Test 2: Health Check
Write-Host "[2/8] Health Check..." -ForegroundColor Yellow
try {
    $health = Invoke-RestMethod -Uri "$base/api/v1/ai/bots/executive-intelligence/health" -Method Get
    Write-Host "      Status: $($health.status)" -ForegroundColor Green
} catch {
    Write-Host "      Failed: $_" -ForegroundColor Red
}

Write-Host ""

# Test 3: Get Status
Write-Host "[3/8] Get Bot Status..." -ForegroundColor Yellow
try {
    $status = Invoke-RestMethod `
        -Uri "$base/api/v1/ai/bots/executive-intelligence/status" `
        -Method Get `
        -Headers $headers
    
    Write-Host "      Reports Generated: $($status.metrics.reports_generated)" -ForegroundColor Green
    Write-Host "      Accuracy Rate: $($status.metrics.accuracy_rate)" -ForegroundColor Green
} catch {
    Write-Host "      Failed: $_" -ForegroundColor Red
}

Write-Host ""

# Test 4: Get KPIs
Write-Host "[4/8] Get Executive KPIs..." -ForegroundColor Yellow
try {
    $kpis = Invoke-RestMethod `
        -Uri "$base/api/v1/ai/bots/executive-intelligence/kpis" `
        -Method Get `
        -Headers $headers
    
    Write-Host "      Financial KPIs: $($kpis.financial_kpis.Count)" -ForegroundColor Green
    Write-Host "      Operational KPIs: $($kpis.operational_kpis.Count)" -ForegroundColor Green
    Write-Host "      Strategic KPIs: $($kpis.strategic_kpis.Count)" -ForegroundColor Green
} catch {
    Write-Host "      Failed: $_" -ForegroundColor Red
}

Write-Host ""

# Test 5: Generate Report
Write-Host "[5/8] Generate Executive Report..." -ForegroundColor Yellow
try {
    $reportRequest = @{
        report_type = "executive_summary"
        period = "weekly"
        departments = @("sales", "operations", "finance")
        include_forecast = $true
    } | ConvertTo-Json
    
    $report = Invoke-RestMethod `
        -Uri "$base/api/v1/ai/bots/executive-intelligence/generate-report" `
        -Method Post `
        -Headers $headers `
        -Body $reportRequest
    
    Write-Host "      Report ID: $($report.execution_id)" -ForegroundColor Green
    Write-Host "      Status: $($report.status)" -ForegroundColor Green
} catch {
    Write-Host "      Failed: $_" -ForegroundColor Red
}

Write-Host ""

# Test 6: Analyze Performance
Write-Host "[6/8] Analyze Performance..." -ForegroundColor Yellow
try {
    $analysisRequest = @{
        kpi_type = "financial"
        compare_period = "previous_month"
        depth = "detailed"
    } | ConvertTo-Json
    
    $analysis = Invoke-RestMethod `
        -Uri "$base/api/v1/ai/bots/executive-intelligence/analyze-performance" `
        -Method Post `
        -Headers $headers `
        -Body $analysisRequest
    
    Write-Host "      Analysis ID: $($analysis.execution_id)" -ForegroundColor Green
    Write-Host "      Status: $($analysis.status)" -ForegroundColor Green
} catch {
    Write-Host "      Failed: $_" -ForegroundColor Red
}

Write-Host ""

# Test 7: Market Analysis
Write-Host "[7/8] Market Analysis..." -ForegroundColor Yellow
try {
    $marketRequest = @{
        market_scope = "domestic"
        competitors = @("all")
        time_horizon = "quarterly"
    } | ConvertTo-Json
    
    $market = Invoke-RestMethod `
        -Uri "$base/api/v1/ai/bots/executive-intelligence/market-analysis" `
        -Method Post `
        -Headers $headers `
        -Body $marketRequest
    
    Write-Host "      Analysis ID: $($market.execution_id)" -ForegroundColor Green
    Write-Host "      Status: $($market.status)" -ForegroundColor Green
} catch {
    Write-Host "      Failed: $_" -ForegroundColor Red
}

Write-Host ""

# Test 8: Strategic Recommendations
Write-Host "[8/8] Generate Strategic Recommendations..." -ForegroundColor Yellow
try {
    $recsRequest = @{
        focus_areas = @("growth", "efficiency", "innovation")
        risk_tolerance = "medium"
        time_frame = "6_months"
    } | ConvertTo-Json
    
    $recs = Invoke-RestMethod `
        -Uri "$base/api/v1/ai/bots/executive-intelligence/strategic-recommendations" `
        -Method Post `
        -Headers $headers `
        -Body $recsRequest
    
    Write-Host "      Recommendations ID: $($recs.execution_id)" -ForegroundColor Green
    Write-Host "      Status: $($recs.status)" -ForegroundColor Green
} catch {
    Write-Host "      Failed: $_" -ForegroundColor Red
}

Write-Host ""
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host "  All Tests Completed!" -ForegroundColor Green
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host ""
