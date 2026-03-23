#!/usr/bin/env pwsh
# MapleLoad Canada Bot - Integration Test Script
# Tests all backend endpoints and integration

Write-Host "=" -ForegroundColor Cyan
Write-Host "🍁 MapleLoad Canada Bot - Integration Tests" -ForegroundColor Green -BackgroundColor Black
Write-Host "=" -ForegroundColor Cyan
Write-Host ""

$baseURL = "http://127.0.0.1:8000"
$botEndpoint = "$baseURL/api/v1/ai/bots/mapleload-canada"
$token = $env:TEST_TOKEN

# Test 1: Health Check
Write-Host "[1/11] 🏥 Testing Health Check..." -ForegroundColor Cyan
try {
    $response = Invoke-RestMethod "$botEndpoint/health" -Method Get -ErrorAction Stop
    Write-Host "✅ Health: $($response.status)" -ForegroundColor Green
} catch {
    Write-Host "❌ Health check failed: $_" -ForegroundColor Red
}

Write-Host ""

# Test 2: Status
Write-Host "[2/11] 📊 Testing Status Endpoint..." -ForegroundColor Cyan
try {
    $response = Invoke-RestMethod "$botEndpoint/status" `
        -Method Get `
        -Headers @{"Authorization" = "Bearer $token"} `
        -ErrorAction Stop
    Write-Host "✅ Status: Bot is active" -ForegroundColor Green
    Write-Host "   Version: $($response.data.version)" -ForegroundColor Gray
    Write-Host "   Capabilities: $($response.data.capabilities.Count) features" -ForegroundColor Gray
} catch {
    Write-Host "❌ Status test failed: $_" -ForegroundColor Red
}

Write-Host ""

# Test 3: Market Intelligence
Write-Host "[3/11] 📈 Testing Market Intelligence..." -ForegroundColor Cyan
try {
    $body = @{} | ConvertTo-Json
    $response = Invoke-RestMethod "$botEndpoint/market-intelligence" `
        -Method Post `
        -Headers @{"Authorization" = "Bearer $token"; "Content-Type" = "application/json"} `
        -Body $body `
        -ErrorAction Stop
    Write-Host "✅ Market Intelligence: Retrieved" -ForegroundColor Green
    Write-Host "   Market Coverage: $($response.data.market_snapshot.market_coverage)" -ForegroundColor Gray
} catch {
    Write-Host "❌ Market Intelligence test failed: $_" -ForegroundColor Red
}

Write-Host ""

# Test 4: Carrier Discovery
Write-Host "[4/11] 🚚 Testing Carrier Discovery..." -ForegroundColor Cyan
try {
    $body = @{ province = "ontario" } | ConvertTo-Json
    $response = Invoke-RestMethod "$botEndpoint/carrier-discovery" `
        -Method Post `
        -Headers @{"Authorization" = "Bearer $token"; "Content-Type" = "application/json"} `
        -Body $body `
        -ErrorAction Stop
    Write-Host "✅ Carrier Discovery: Found carriers" -ForegroundColor Green
    Write-Host "   Count: $($response.data.carriers.Count)" -ForegroundColor Gray
} catch {
    Write-Host "❌ Carrier Discovery test failed: $_" -ForegroundColor Red
}

Write-Host ""

# Test 5: Freight Sourcing
Write-Host "[5/11] 📦 Testing Freight Sourcing..." -ForegroundColor Cyan
try {
    $body = @{} | ConvertTo-Json
    $response = Invoke-RestMethod "$botEndpoint/freight-sourcing" `
        -Method Post `
        -Headers @{"Authorization" = "Bearer $token"; "Content-Type" = "application/json"} `
        -Body $body `
        -ErrorAction Stop
    Write-Host "✅ Freight Sourcing: Found loads" -ForegroundColor Green
    Write-Host "   Available: $($response.data.available_loads) loads" -ForegroundColor Gray
} catch {
    Write-Host "❌ Freight Sourcing test failed: $_" -ForegroundColor Red
}

Write-Host ""

# Test 6: Outreach Campaign
Write-Host "[6/11] 📧 Testing Outreach Campaign..." -ForegroundColor Cyan
try {
    $body = @{
        name = "Test Campaign"
        target = "all_carriers"
    } | ConvertTo-Json
    $response = Invoke-RestMethod "$botEndpoint/outreach-campaign" `
        -Method Post `
        -Headers @{"Authorization" = "Bearer $token"; "Content-Type" = "application/json"} `
        -Body $body `
        -ErrorAction Stop
    Write-Host "✅ Outreach Campaign: Created" -ForegroundColor Green
    Write-Host "   Campaign ID: $($response.data.campaign_id)" -ForegroundColor Gray
} catch {
    Write-Host "❌ Outreach Campaign test failed: $_" -ForegroundColor Red
}

Write-Host ""

# Test 7: Lead Generation
Write-Host "[7/11] 🎯 Testing Lead Generation..." -ForegroundColor Cyan
try {
    $body = @{
        industry = "manufacturing"
    } | ConvertTo-Json
    $response = Invoke-RestMethod "$botEndpoint/lead-generation" `
        -Method Post `
        -Headers @{"Authorization" = "Bearer $token"; "Content-Type" = "application/json"} `
        -Body $body `
        -ErrorAction Stop
    Write-Host "✅ Lead Generation: Generated leads" -ForegroundColor Green
    Write-Host "   Total: $($response.data.total) leads" -ForegroundColor Gray
    Write-Host "   High Quality: $($response.data.high_quality)" -ForegroundColor Gray
} catch {
    Write-Host "❌ Lead Generation test failed: $_" -ForegroundColor Red
}

Write-Host ""

# Test 8: Predictive Analytics
Write-Host "[8/11] 🔮 Testing Predictive Analytics..." -ForegroundColor Cyan
try {
    $body = @{
        forecast_type = "demand"
        confidence_level = 85
    } | ConvertTo-Json
    $response = Invoke-RestMethod "$botEndpoint/predictive-analytics" `
        -Method Post `
        -Headers @{"Authorization" = "Bearer $token"; "Content-Type" = "application/json"} `
        -Body $body `
        -ErrorAction Stop
    Write-Host "✅ Predictive Analytics: Forecast generated" -ForegroundColor Green
    Write-Host "   Confidence: $($response.data.confidence_level)" -ForegroundColor Gray
} catch {
    Write-Host "❌ Predictive Analytics test failed: $_" -ForegroundColor Red
}

Write-Host ""

# Test 9: Smart Matching
Write-Host "[9/11] 🤝 Testing Smart Matching..." -ForegroundColor Cyan
try {
    $body = @{
        algorithm = "hybrid"
        optimization_goal = "balanced"
    } | ConvertTo-Json
    $response = Invoke-RestMethod "$botEndpoint/smart-matching" `
        -Method Post `
        -Headers @{"Authorization" = "Bearer $token"; "Content-Type" = "application/json"} `
        -Body $body `
        -ErrorAction Stop
    Write-Host "✅ Smart Matching: Matches generated" -ForegroundColor Green
    Write-Host "   Total Matches: $($response.data.total_matches)" -ForegroundColor Gray
    Write-Host "   High Confidence: $($response.data.high_confidence_matches)" -ForegroundColor Gray
} catch {
    Write-Host "❌ Smart Matching test failed: $_" -ForegroundColor Red
}

Write-Host ""

# Test 10: Advanced Report
Write-Host "[10/11] 📑 Testing Advanced Report..." -ForegroundColor Cyan
try {
    $body = @{
        report_type = "performance"
        output_format = "json"
    } | ConvertTo-Json
    $response = Invoke-RestMethod "$botEndpoint/advanced-report" `
        -Method Post `
        -Headers @{"Authorization" = "Bearer $token"; "Content-Type" = "application/json"} `
        -Body $body `
        -ErrorAction Stop
    Write-Host "✅ Advanced Report: Generated" -ForegroundColor Green
    Write-Host "   Report ID: $($response.data.report_id)" -ForegroundColor Gray
} catch {
    Write-Host "❌ Advanced Report test failed: $_" -ForegroundColor Red
}

Write-Host ""

# Test 11: Integrations Status
Write-Host "[11/11] 🔌 Testing Integrations Status..." -ForegroundColor Cyan
try {
    $response = Invoke-RestMethod "$botEndpoint/integrations" `
        -Method Get `
        -Headers @{"Authorization" = "Bearer $token"} `
        -ErrorAction Stop
    Write-Host "✅ Integrations: Status retrieved" -ForegroundColor Green
    Write-Host "   Connected Systems: $($response.data.connected_systems.Count)" -ForegroundColor Gray
} catch {
    Write-Host "❌ Integrations Status test failed: $_" -ForegroundColor Red
}

Write-Host ""
Write-Host "=" -ForegroundColor Cyan
Write-Host "✅ MapleLoad Canada Bot - All tests completed!" -ForegroundColor Green
Write-Host "=" -ForegroundColor Cyan
Write-Host ""
Write-Host "🌐 Bot URL: http://127.0.0.1:5173/ai-bots/mapleload-canada" -ForegroundColor Yellow
Write-Host "📡 API Docs: http://127.0.0.1:8000/docs#/MapleLoad%20Canada%20Bot" -ForegroundColor Yellow
Write-Host ""
