# smoke.ps1
# NOTE: ASCII only. No non-English characters.
param(
  [string]$BaseUrl = "http://127.0.0.1:8001",
  [string]$User = "yassir",
  [string]$Role = "admin"
)

$tok = (irm -Method POST "$BaseUrl/auth/token" -ContentType "application/json" -Body (@{username=$User; role=$Role; expires_minutes=60} | ConvertTo-Json)).access_token
$h = @{ Authorization = "Bearer $tok" }

"== Health =="
irm -Headers $h "$BaseUrl/finance/health" | Format-List

"== Create =="
$new = irm -Headers $h -Method POST "$BaseUrl/finance/expenses" -ContentType "application/json" -Body (@{category="fuel"; amount=25.75; description="smoke"; vendor="ps1"; status="PENDING"} | ConvertTo-Json)
$new | Format-List
$id = $new.id

"== List =="
irm -Headers $h "$BaseUrl/finance/expenses" | Format-List

"== Toggle =="
irm -Headers $h -Method PUT "$BaseUrl/finance/expenses/$id/status" | Format-List

"== Summary =="
irm -Headers $h "$BaseUrl/finance/summary" | Format-List

"== Delete =="
irm -Headers $h -Method DELETE "$BaseUrl/finance/expenses/$id"
