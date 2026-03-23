# Executive Intelligence Bot API Testing Script
# PowerShell script to test all endpoints

$base = "http://127.0.0.1:8000"

Write-Host "ðŸ” Step 1: Login to get token..." -ForegroundColor Cyan
$loginBody = @{
    email = "admin@gts.local"
    password = "admin123"
}

try {
    $loginResponse = Invoke-RestMethod `
        -Uri "$base/auth/token" `
        -Method Post `
        -ContentType "application/x-www-form-urlencoded" `
        -Body $loginBody
    
    $token = $loginResponse.access_token
    Write-Host "âœ… Token obtained: $($token.Substring(0,20))..." -ForegroundColor Green
} catch {
    Write-Host "âŒ Login failed: $_" -ForegroundColor Red
    exit 1
}

$headers = @{
    "Authorization" = "Bearer $token"
    "Content-Type" = "application/json"
}

Write-Host ""
Write-Host ("=" * 80) -ForegroundColor Yellow
Write-Host "Testing Executive Intelligence Bot API Endpoints" -ForegroundColor Yellow
Write-Host ("=" * 80) -ForegroundColor Yellow
Write-Host ""

# Test 1: Health Check (no auth required)
Write-Host "ðŸ“Š Test 1: Health Check (no auth)" -ForegroundColor Cyan
try {
    $health = Invoke-RestMethod -Uri "$base/api/v1/ai/bots/executive-intelligence/health" -Method Get
    Write-Host "âœ… Health: $($health.status)" -ForegroundColor Green
    $health | ConvertTo-Json -Depth 3
} catch {
    Write-Host "âŒ Failed: $_" -ForegroundColor Red
}

Write-Host ""
Write-Host ("-" * 80)

# Test 2: Get Status
Write-Host "ðŸ“Š Test 2: Get Bot Status" -ForegroundColor Cyan
try {
    $status = Invoke-RestMethod `
        -Uri "$base/api/v1/ai/bots/executive-intelligence/status" `
        -Method Get `
        -Headers $headers
    
    Write-Host "âœ… Status retrieved" -ForegroundColor Green
    Write-Host "Reports: $($status.metrics.reports_generated)" -ForegroundColor White
    Write-Host "Accuracy: $($status.metrics.accuracy_rate)" -ForegroundColor White
    $status | ConvertTo-Json -Depth 3
} catch {
    Write-Host "âŒ Failed: $_" -ForegroundColor Red
}

Write-Host ""
Write-Host ("-" * 80)

# Test 3: Get KPIs
Write-Host "ðŸ“Š Test 3: Get Executive KPIs" -ForegroundColor Cyan
try {
    $kpis = Invoke-RestMethod `
        -Uri "$base/api/v1/ai/bots/executive-intelligence/kpis" `
        -Method Get `
        -Headers $headers
    
    Write-Host "âœ… KPIs retrieved" -ForegroundColor Green
    Write-Host "Financial KPIs: $($kpis.financial_kpis.Count)" -ForegroundColor White
    Write-Host "Operational KPIs: $($kpis.operational_kpis.Count)" -ForegroundColor White
    Write-Host "Strategic KPIs: $($kpis.strategic_kpis.Count)" -ForegroundColor White
    $kpis | ConvertTo-Json -Depth 3
} catch {
    Write-Host "âŒ Failed: $_" -ForegroundColor Red
}

Write-Host ""
Write-Host ("-" * 80)

# Test 4: Generate Executive Report
Write-Host "ðŸ“Š Test 4: Generate Executive Report" -ForegroundColor Cyan
$reportRequest = @{
    report_type = "executive_summary"
    period = "weekly"
    departments = @("sales", "operations", "finance")
    include_forecast = $true
} | ConvertTo-Json

try {
    $report = Invoke-RestMethod `
        -Uri "$base/api/v1/ai/bots/executive-intelligence/generate-report" `
        -Method Post `
        -Headers $headers `
        -Body $reportRequest
    
    Write-Host "âœ… Report generated" -ForegroundColor Green
    Write-Host "Execution ID: $($report.execution_id)" -ForegroundColor White
    Write-Host "Status: $($report.status)" -ForegroundColor White
    $report | ConvertTo-Json -Depth 5
} catch {
    Write-Host "âŒ Failed: $_" -ForegroundColor Red
}

Write-Host ""
Write-Host ("-" * 80)

# Test 5: Analyze Performance
Write-Host "ðŸ“Š Test 5: Analyze Performance" -ForegroundColor Cyan
$analysisRequest = @{
    kpi_type = "financial"
    compare_period = "previous_month"
    depth = "detailed"
} | ConvertTo-Json

try {
    $analysis = Invoke-RestMethod `
        -Uri "$base/api/v1/ai/bots/executive-intelligence/analyze-performance" `
        -Method Post `
        -Headers $headers `
        -Body $analysisRequest
    
    Write-Host "âœ… Analysis completed" -ForegroundColor Green
    Write-Host "Execution ID: $($analysis.execution_id)" -ForegroundColor White
    Write-Host "Status: $($analysis.status)" -ForegroundColor White
    $analysis | ConvertTo-Json -Depth 5
} catch {
    Write-Host "âŒ Failed: $_" -ForegroundColor Red
}

Write-Host ""
Write-Host ("-" * 80)

# Test 6: Market Analysis
Write-Host "ðŸ“Š Test 6: Conduct Market Analysis" -ForegroundColor Cyan
$marketRequest = @{
    market_scope = "domestic"
    competitors = @("all")
    time_horizon = "quarterly"
} | ConvertTo-Json

try {
    $market = Invoke-RestMethod `
        -Uri "$base/api/v1/ai/bots/executive-intelligence/market-analysis" `
        -Method Post `
        -Headers $headers `
        -Body $marketRequest
    
    Write-Host "âœ… Market analysis completed" -ForegroundColor Green
    Write-Host "Execution ID: $($market.execution_id)" -ForegroundColor White
    Write-Host "Status: $($market.status)" -ForegroundColor White
    $market | ConvertTo-Json -Depth 5
} catch {
    Write-Host "âŒ Failed: $_" -ForegroundColor Red
}

Write-Host ""
Write-Host ("-" * 80)

# Test 7: Strategic Recommendations
Write-Host "ðŸ“Š Test 7: Generate Strategic Recommendations" -ForegroundColor Cyan
$recommendationsRequest = @{
    focus_areas = @("growth", "efficiency", "innovation")
    risk_tolerance = "medium"
    time_frame = "6_months"
} | ConvertTo-Json

try {
    $recommendations = Invoke-RestMethod `
        -Uri "$base/api/v1/ai/bots/executive-intelligence/strategic-recommendations" `
        -Method Post `
        -Headers $headers `
        -Body $recommendationsRequest
    
    Write-Host "âœ… Recommendations generated" -ForegroundColor Green
    Write-Host "Execution ID: $($recommendations.execution_id)" -ForegroundColor White
    Write-Host "Status: $($recommendations.status)" -ForegroundColor White
    $recommendations | ConvertTo-Json -Depth 5
} catch {
    Write-Host "âŒ Failed: $_" -ForegroundColor Red
}

Write-Host ""
Write-Host ("-" * 80)

# Test 8: Get Capabilities
Write-Host "ðŸ“Š Test 8: Get Bot Capabilities" -ForegroundColor Cyan
try {
    $capabilities = Invoke-RestMethod `
        -Uri "$base/api/v1/ai/bots/executive-intelligence/capabilities" `
        -Method Get `
        -Headers $headers
    
    Write-Host "âœ… Capabilities retrieved" -ForegroundColor Green
    Write-Host "Supported Report Types: $($capabilities.supported_report_types.Count)" -ForegroundColor White
    Write-Host "Market Scopes: $($capabilities.market_scopes.Count)" -ForegroundColor White
    $capabilities | ConvertTo-Json -Depth 3
} catch {
    Write-Host "âŒ Failed: $_" -ForegroundColor Red
}

Write-Host ""
Write-Host ("=" * 80) -ForegroundColor Yellow
Write-Host "âœ… All tests completed!" -ForegroundColor Green
Write-Host ("=" * 80) -ForegroundColor Yellow

