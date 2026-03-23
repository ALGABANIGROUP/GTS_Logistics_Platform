#!/usr/bin/env pwsh
# Test script for Document Upload API

$API_BASE = "http://127.0.0.1:8000"
$TOKEN = "your_test_token_here"  # Replace with real token

Write-Host "🧪 Testing Document Upload API..." -ForegroundColor Cyan
Write-Host "API Base: $API_BASE" -ForegroundColor Gray

# Function to test upload
function Test-Upload {
    param(
        [string]$FilePath
    )
    
    Write-Host "`n📤 Testing Upload: $FilePath" -ForegroundColor Yellow
    
    if (!(Test-Path $FilePath)) {
        Write-Host "❌ File not found: $FilePath" -ForegroundColor Red
        return
    }
    
    try {
        $Form = @{
            file          = Get-Item -Path $FilePath
            document_type = "document"
        }
        
        $Response = Invoke-WebRequest `
            -Uri "$API_BASE/api/v1/documents/upload" `
            -Method Post `
            -Form $Form `
            -Headers @{ "Authorization" = "Bearer $TOKEN" } `
            -UseBasicParsing
        
        Write-Host "✅ Upload successful!" -ForegroundColor Green
        $Response.Content | ConvertFrom-Json | ConvertTo-Json | Write-Host
        
    }
    catch {
        Write-Host "❌ Upload failed: $($_.Exception.Message)" -ForegroundColor Red
    }
}

# Function to list documents
function Get-Documents {
    Write-Host "`n📋 Getting Document List..." -ForegroundColor Yellow
    
    try {
        $Response = Invoke-WebRequest `
            -Uri "$API_BASE/api/v1/documents/" `
            -Method Get `
            -Headers @{ "Authorization" = "Bearer $TOKEN" } `
            -UseBasicParsing
        
        Write-Host "✅ Documents retrieved!" -ForegroundColor Green
        $Response.Content | ConvertFrom-Json | ConvertTo-Json | Write-Host
        
    }
    catch {
        Write-Host "❌ Failed to get documents: $($_.Exception.Message)" -ForegroundColor Red
    }
}

# Test with a sample file
$TestFile = "$PSScriptRoot\sample.txt"
if (Test-Path $TestFile) {
    Test-Upload $TestFile
}

# Try to get documents
Get-Documents

Write-Host "`n✅ Test complete!" -ForegroundColor Green
