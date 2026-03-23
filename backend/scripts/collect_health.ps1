$ErrorActionPreference = "Stop"

function Get-DevToken {
  ($((Invoke-RestMethod "http://127.0.0.1:8000/auth/dev-token").access_token) | Out-String).Trim()
}

$token = Get-DevToken

Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/v1/maintenance/health/collect" `
  -Method Post `
  -Headers @{ Authorization = "Bearer $token" } | Out-Null

"OK $(Get-Date -Format o)"
