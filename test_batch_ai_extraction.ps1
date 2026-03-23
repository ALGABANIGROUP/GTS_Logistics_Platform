# Test Batch AI Invoice Extraction
$base = "http://127.0.0.1:8000"

Write-Host "╔═══════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║   Batch AI Invoice Extraction Test           ║" -ForegroundColor Cyan
Write-Host "║   Supports: PDF, Excel, Word, Images         ║" -ForegroundColor Cyan
Write-Host "║   Max: 30 files per batch                    ║" -ForegroundColor Cyan
Write-Host "╚═══════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

# Step 1: Login
Write-Host "🔐 Logging in..." -ForegroundColor Cyan
$loginBody = @{
    email = "admin@gtslogistics.com"
    password = "admin123"
}

try {
    $tokenResponse = Invoke-RestMethod `
        -Uri "$base/auth/token" `
        -Method Post `
        -ContentType "application/x-www-form-urlencoded" `
        -Body $loginBody

    $token = $tokenResponse.access_token
    Write-Host "✅ Logged in successfully" -ForegroundColor Green
}
catch {
    Write-Host "❌ Login failed: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# Step 2: Prepare headers
$headers = @{
    "Authorization" = "Bearer $token"
}

# Step 3: Test batch extraction
Write-Host "`n📄 Testing Batch AI Extraction..." -ForegroundColor Cyan
Write-Host "⚠️  Note: Place your invoice files in: d:\GTS\test_invoices\" -ForegroundColor Yellow

$testInvoicesDir = "d:\GTS\test_invoices"

if (-not (Test-Path $testInvoicesDir)) {
    Write-Host "`n📁 Creating test_invoices directory..." -ForegroundColor Yellow
    New-Item -ItemType Directory -Path $testInvoicesDir | Out-Null
    Write-Host "✅ Directory created: $testInvoicesDir" -ForegroundColor Green
    Write-Host "`n⚠️  Please add invoice files (PDF, Excel, Word, or Images) to this folder" -ForegroundColor Yellow
    Write-Host "   Supported formats: .pdf .xls .xlsx .doc .docx .png .jpg .jpeg" -ForegroundColor Yellow
    exit 0
}

# Find all invoice files
$invoiceFiles = Get-ChildItem -Path $testInvoicesDir -File | Where-Object {
    $_.Extension -in @('.pdf', '.xls', '.xlsx', '.doc', '.docx', '.png', '.jpg', '.jpeg')
}

if ($invoiceFiles.Count -eq 0) {
    Write-Host "`n⚠️  No invoice files found in: $testInvoicesDir" -ForegroundColor Yellow
    Write-Host "   Please add invoice files with these extensions:" -ForegroundColor Yellow
    Write-Host "   .pdf .xls .xlsx .doc .docx .png .jpg .jpeg" -ForegroundColor Yellow
    exit 0
}

Write-Host "`n📊 Found $($invoiceFiles.Count) invoice file(s):" -ForegroundColor Green
foreach ($file in $invoiceFiles) {
    Write-Host "   • $($file.Name) ($($file.Extension))" -ForegroundColor White
}

if ($invoiceFiles.Count -gt 30) {
    Write-Host "`n⚠️  More than 30 files found. Only first 30 will be processed." -ForegroundColor Yellow
    $invoiceFiles = $invoiceFiles | Select-Object -First 30
}

Write-Host "`n🤖 Extracting invoice data with AI..." -ForegroundColor Cyan
Write-Host "   Processing $($invoiceFiles.Count) file(s)..." -ForegroundColor White

# Prepare multipart form
$boundary = [System.Guid]::NewGuid().ToString()
$LF = "`r`n"

$bodyLines = @()
foreach ($file in $invoiceFiles) {
    $bodyLines += "--$boundary"
    $bodyLines += "Content-Disposition: form-data; name=`"files`"; filename=`"$($file.Name)`""
    $bodyLines += "Content-Type: application/octet-stream"
    $bodyLines += ""
    $fileContent = [System.IO.File]::ReadAllBytes($file.FullName)
    $bodyLines += [System.Text.Encoding]::GetEncoding("ISO-8859-1").GetString($fileContent)
}
$bodyLines += "--$boundary--"

$body = $bodyLines -join $LF

try {
    $extractResponse = Invoke-RestMethod `
        -Uri "$base/api/v1/platform/expenses/extract-invoice" `
        -Method Post `
        -Headers @{
            "Authorization" = "Bearer $token"
            "Content-Type" = "multipart/form-data; boundary=$boundary"
        } `
        -Body ([System.Text.Encoding]::GetEncoding("ISO-8859-1").GetBytes($body))
    
    Write-Host "`n✅ Extraction Completed!" -ForegroundColor Green
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
    Write-Host "📊 Summary:" -ForegroundColor Cyan
    Write-Host "   Total Files:       $($extractResponse.total_files)" -ForegroundColor White
    Write-Host "   ✅ Successful:     $($extractResponse.successful_extractions)" -ForegroundColor Green
    Write-Host "   ❌ Failed:         $($extractResponse.failed_extractions)" -ForegroundColor Red
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
    
    Write-Host "`n📋 Detailed Results:" -ForegroundColor Cyan
    $idx = 1
    foreach ($result in $extractResponse.results) {
        Write-Host "`n$idx. 📄 $($result.filename)" -ForegroundColor White
        if ($result.success) {
            Write-Host "   ✅ Status: Extracted Successfully" -ForegroundColor Green
            $data = $result.extracted_data
            Write-Host "   ┌─ Vendor:         $($data.vendor)" -ForegroundColor White
            Write-Host "   ├─ Service:        $($data.service_name)" -ForegroundColor White
            Write-Host "   ├─ Amount:         $($data.amount) $($data.currency)" -ForegroundColor White
            Write-Host "   ├─ Invoice #:      $($data.invoice_number)" -ForegroundColor White
            Write-Host "   ├─ Billing Date:   $($data.billing_date)" -ForegroundColor White
            Write-Host "   ├─ Due Date:       $($data.due_date)" -ForegroundColor White
            Write-Host "   ├─ Category:       $($data.category)" -ForegroundColor White
            Write-Host "   └─ Description:    $($data.description)" -ForegroundColor White
        }
        else {
            Write-Host "   ❌ Status: Failed" -ForegroundColor Red
            Write-Host "   └─ Error: $($result.error)" -ForegroundColor Red
        }
        $idx++
    }
    
    Write-Host "`n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
    Write-Host "💡 Message: $($extractResponse.message)" -ForegroundColor Yellow
}
catch {
    Write-Host "`n❌ AI Extraction Failed:" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    if ($_.ErrorDetails) {
        try {
            $errorObj = $_.ErrorDetails.Message | ConvertFrom-Json
            Write-Host ($errorObj | ConvertTo-Json -Depth 10) -ForegroundColor Red
        }
        catch {
            Write-Host $_.ErrorDetails.Message -ForegroundColor Red
        }
    }
}

Write-Host "`n✅ Test completed!" -ForegroundColor Green
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
