# file: I:\GTS Logistics\backend\tools\smoke-docs.ps1
param(
  [string]$Base = "http://127.0.0.1:8001",
  [string]$User = "yassir",
  [string]$Role = "admin",
  [int]$Expire = 60
)

Write-Host "== Smoke Start on $Base =="

# 1) Token
$tokenResp = Invoke-RestMethod -Method POST -Uri "$Base/auth/token" -ContentType "application/json" `
  -Body (@{username=$User; role=$Role; expires_minutes=$Expire} | ConvertTo-Json)
$T = $tokenResp.access_token
if(-not $T){ throw "No token issued" }
$headers = @{ Authorization = "Bearer $T" }
Write-Host "[OK] Token issued"

# 2) DB ping
Invoke-RestMethod -Uri "$Base/documents/_debug/db" -Headers $headers -ErrorAction Stop | Out-Null
Write-Host "[OK] DB ping"

# 3) Create
$payload = @{ title="Smoke Doc"; file_url="/tmp/test.pdf"; notify_before_days=7 } | ConvertTo-Json
$doc = Invoke-RestMethod -Method POST -Uri "$Base/documents/" -Headers $headers -ContentType "application/json" -Body $payload
$DOC_ID = $doc.id
if(-not $DOC_ID){ throw "No DOC_ID returned" }
Write-Host "[OK] Created doc id=$DOC_ID"

# 4) Read + Update + Extend
Invoke-RestMethod -Uri "$Base/documents/$DOC_ID" -Headers $headers | Out-Null
Invoke-RestMethod -Method PUT -Uri "$Base/documents/$DOC_ID" -Headers $headers -ContentType "application/json" -Body '{"title":"Smoke Doc v2"}' | Out-Null
Invoke-RestMethod -Method POST -Uri "$Base/documents/$DOC_ID/extend" -Headers $headers -ContentType "application/json" -Body '{"days":30}' | Out-Null
Write-Host "[OK] Read/Update/Extend sequence"

# 5) Delete
Invoke-RestMethod -Method DELETE -Uri "$Base/documents/$DOC_ID" -Headers $headers | Out-Null
Write-Host "[OK] Deleted doc id=$DOC_ID"

# 6) Expect 404 after delete
try {
  Invoke-RestMethod -Uri "$Base/documents/$DOC_ID" -Headers $headers -ErrorAction Stop | Out-Null
  throw "Expected 404 but GET succeeded"
} catch {
  if($_.Exception.Response.StatusCode.value__ -ne 404){ throw "Expected 404, got different status" }
}
Write-Host "== SMOKE OK: Token+CRUD+Extend+Delete behaved as expected. =="
