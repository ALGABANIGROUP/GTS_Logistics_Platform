$BASE = "http://127.0.0.1:8001"
$body = '{"username":"yassir","role":"admin","expires_minutes":15}'
try {
  $tok = (Invoke-RestMethod -Method POST "$BASE/auth/token" -ContentType "application/json" -Body $body -TimeoutSec 10).access_token
  $h = @{ Authorization = "Bearer $tok" }
  $r = Invoke-RestMethod "$BASE/finance/health" -Headers $h -TimeoutSec 10
  $line = ('{0:yyyy-MM-dd HH:mm} OK={1} DB={2}' -f (Get-Date), $r.ok, $r.db_ok)
} catch {
  $line = ('{0:yyyy-MM-dd HH:mm} ERROR={1}' -f (Get-Date), $_.Exception.Message)
}
$log = "I:\GTS Logistics\logs\health.log"
Add-Content -Path $log -Value $line
