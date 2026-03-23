cd D:\GTS\backend
& .\.venv\Scripts\Activate.ps1

function Get-DevToken { ([string](Invoke-RestMethod "http://127.0.0.1:8000/auth/dev-token").access_token).Trim() }

$token = Get-DevToken
Invoke-RestMethod "http://127.0.0.1:8000/api/v1/maintenance/health" -Headers @{Authorization="Bearer $token"} | ConvertTo-Json -Depth 10
