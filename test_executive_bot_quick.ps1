# Executive Intelligence Bot - No Auth Test
# Test health endpoint (no authentication required)

$base = "http://127.0.0.1:8000"

Write-Host ""
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host "  Executive Intelligence Bot - Health Check Test" -ForegroundColor Cyan  
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "[1/2] Testing Health Endpoint (No Auth)..." -ForegroundColor Yellow
try {
    $health = Invoke-RestMethod -Uri "$base/api/v1/ai/bots/executive-intelligence/health" -Method Get
    Write-Host ""
    Write-Host "      SUCCESS!" -ForegroundColor Green
    Write-Host "      Status: $($health.status)" -ForegroundColor White
    Write-Host "      Bot: $($health.bot)" -ForegroundColor White
    Write-Host "      Timestamp: $($health.timestamp)" -ForegroundColor White
    Write-Host ""
} catch {
    Write-Host "      FAILED: $_" -ForegroundColor Red
    Write-Host ""
    Write-Host "      Make sure backend is running:" -ForegroundColor Yellow
    Write-Host "         cd d:\GTS" -ForegroundColor White
    Write-Host "         .\run-dev.ps1" -ForegroundColor White
    Write-Host ""
    exit 1
}

Write-Host "[2/2] Testing Bot Status (Direct)..." -ForegroundColor Yellow
try {
    $result = .\.venv\Scripts\python.exe -c "from backend.bots.executive_intelligence import ExecutiveIntelligenceBot; import asyncio; bot = ExecutiveIntelligenceBot(); result = asyncio.run(bot.status()); import json; print(json.dumps(result, indent=2))" 2>&1 | Out-String
    
    if ($result -match '\{') {
        $jsonStart = $result.IndexOf('{')
        $jsonText = $result.Substring($jsonStart)
        $botStatus = $jsonText | ConvertFrom-Json
        
        Write-Host ""
        Write-Host "      SUCCESS!" -ForegroundColor Green
        Write-Host "      Bot Name: $($botStatus.bot)" -ForegroundColor White
        Write-Host "      Display Name: $($botStatus.display_name)" -ForegroundColor White
        Write-Host "      Version: $($botStatus.version)" -ForegroundColor White
        Write-Host "      Active: $($botStatus.is_active)" -ForegroundColor White
        Write-Host "      Message: $($botStatus.message)" -ForegroundColor White
        Write-Host ""
    } else {
        Write-Host "      Result: $result" -ForegroundColor White
    }
} catch {
    Write-Host "      FAILED: $_" -ForegroundColor Red
}

Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host "  Tests Completed!" -ForegroundColor Green
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "NEXT STEPS:" -ForegroundColor Yellow
Write-Host "  1. Backend is running: http://127.0.0.1:8000" -ForegroundColor White
Write-Host "  2. API Docs available: http://127.0.0.1:8000/docs" -ForegroundColor White
Write-Host "  3. Executive Intelligence routes:" -ForegroundColor White
Write-Host "     - Health: /api/v1/ai/bots/executive-intelligence/health" -ForegroundColor Gray
Write-Host "     - Status: /api/v1/ai/bots/executive-intelligence/status" -ForegroundColor Gray
Write-Host "     - KPIs: /api/v1/ai/bots/executive-intelligence/kpis" -ForegroundColor Gray
Write-Host "     - Generate Report: /api/v1/ai/bots/executive-intelligence/generate-report" -ForegroundColor Gray
Write-Host ""
Write-Host "  4. Create user account to test authenticated endpoints:" -ForegroundColor White
Write-Host "     POST http://127.0.0.1:8000/auth/register" -ForegroundColor Gray
Write-Host ""
