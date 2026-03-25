# Smoke Test Script for GTS Logistics
$BaseUrl = "http://127.0.0.1:8000"
$FrontendUrl = "http://127.0.0.1:5173"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "GTS Logistics Smoke Test" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Test 1: Backend Health
Write-Host "Test 1: Backend Health Check" -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "$BaseUrl/health/ping" -UseBasicParsing
    if ($response.StatusCode -eq 200) {
        Write-Host "✅ Backend health check passed" -ForegroundColor Green
    } else {
        Write-Host "❌ Backend health check failed: $($response.StatusCode)" -ForegroundColor Red
    }
} catch {
    Write-Host "❌ Backend health check failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 2: API Root
Write-Host ""
Write-Host "Test 2: API Root" -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "$BaseUrl/" -UseBasicParsing
    if ($response.StatusCode -eq 200) {
        Write-Host "✅ API root accessible" -ForegroundColor Green
    } else {
        Write-Host "❌ API root failed: $($response.StatusCode)" -ForegroundColor Red
    }
} catch {
    Write-Host "❌ API root failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 3: Frontend
Write-Host ""
Write-Host "Test 3: Frontend" -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "$FrontendUrl" -UseBasicParsing
    if ($response.StatusCode -eq 200) {
        Write-Host "✅ Frontend accessible" -ForegroundColor Green
    } else {
        Write-Host "❌ Frontend failed: $($response.StatusCode)" -ForegroundColor Red
    }
} catch {
    Write-Host "❌ Frontend failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 4: API Docs (if enabled)
Write-Host ""
Write-Host "Test 4: API Docs" -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "$BaseUrl/docs" -UseBasicParsing
    if ($response.StatusCode -eq 200) {
        Write-Host "✅ API docs accessible" -ForegroundColor Green
    } else {
        Write-Host "⚠️ API docs not accessible (may be disabled in production)" -ForegroundColor Yellow
    }
} catch {
    Write-Host "⚠️ API docs not accessible: $($_.Exception.Message)" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Smoke test completed" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan