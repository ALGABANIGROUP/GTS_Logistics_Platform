# Test AI Invoice Extraction Endpoint
$base = "http://127.0.0.1:8000"

# Step 1: Login
Write-Host "🔐 Logging in..." -ForegroundColor Cyan
$loginBody = @{
    email = "admin@gtslogistics.com"
    password = "admin123"
}

$tokenResponse = Invoke-RestMethod `
    -Uri "$base/auth/token" `
    -Method Post `
    -ContentType "application/x-www-form-urlencoded" `
    -Body $loginBody

$token = $tokenResponse.access_token
Write-Host "✅ Logged in successfully" -ForegroundColor Green

# Step 2: Prepare headers
$headers = @{
    "Authorization" = "Bearer $token"
}

# Step 3: Create a simple test image invoice (you'd replace this with actual invoice)
Write-Host "`n📄 Testing AI Invoice Extraction..." -ForegroundColor Cyan
Write-Host "⚠️  Note: This requires a real invoice image (PNG/JPG)" -ForegroundColor Yellow
Write-Host "    Place your invoice image at: d:\GTS\test_invoice.png" -ForegroundColor Yellow

$invoicePath = "d:\GTS\test_invoice.png"

if (Test-Path $invoicePath) {
    Write-Host "`n🤖 Extracting invoice data with AI..." -ForegroundColor Cyan
    
    $form = @{
        file = Get-Item -Path $invoicePath
    }
    
    try {
        $extractResponse = Invoke-RestMethod `
            -Uri "$base/api/v1/platform/expenses/extract-invoice" `
            -Method Post `
            -Headers $headers `
            -Form $form
        
        Write-Host "`n✅ AI Extraction Successful!" -ForegroundColor Green
        Write-Host ($extractResponse | ConvertTo-Json -Depth 10)
    }
    catch {
        Write-Host "`n❌ AI Extraction Failed:" -ForegroundColor Red
        Write-Host $_.Exception.Message
        if ($_.ErrorDetails) {
            Write-Host ($_.ErrorDetails.Message | ConvertFrom-Json | ConvertTo-Json -Depth 10)
        }
    }
}
else {
    Write-Host "`n⚠️  No test invoice found at: $invoicePath" -ForegroundColor Yellow
    Write-Host "    Please add a test invoice image to test AI extraction" -ForegroundColor Yellow
}

Write-Host "`n✅ Test completed!" -ForegroundColor Green
