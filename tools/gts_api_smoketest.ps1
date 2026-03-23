
param(
  [string[]]$Bases = @("http://127.0.0.1:8000", "http://localhost:8000"),
  [string]$User = "yassir",
  [string]$Role = "admin",
  [int]$TTL = 60,
  [int]$TimeoutSec = 7
)

Write-Host "=== GTS API Smoke Test v2 ==="
Write-Host "Candidates:" ($Bases -join ", ")
try { Remove-Module PSReadLine -ErrorAction SilentlyContinue } catch {}

Add-Type -AssemblyName System.Net.Http
$h = [System.Net.Http.HttpClientHandler]::new()
$h.UseProxy = $false
$hc = [System.Net.Http.HttpClient]::new($h)
$hc.Timeout = [TimeSpan]::FromSeconds($TimeoutSec)

function Show-Resp([System.Net.Http.HttpResponseMessage]$resp) {
  $code = [int]$resp.StatusCode
  $reason = $resp.ReasonPhrase
  $body = ""
  try { $body = $resp.Content.ReadAsStringAsync().Result } catch {}
  Write-Host ("HTTP {0} {1}" -f $code, $reason)
  if ($null -ne $body -and $body.Length -gt 0) {
    if ($body.Length -gt 2000) { 
      Write-Host ($body.Substring(0,2000) + "...(truncated)")
    } else {
      Write-Host $body
    }
  }
  Write-Host "---------------------------"
}

foreach ($Base in $Bases) {
  Write-Host ""
  Write-Host ">>> Trying base: $Base"
  try {
    $r = $hc.GetAsync("$Base/").Result
    Write-Host "GET /"
    Show-Resp $r
  } catch {
    Write-Host "ERROR GET / : $($_.Exception.GetType().FullName) - $($_.Exception.Message)"
    continue
  }

  try {
    $r = $hc.GetAsync("$Base/_debug/routes").Result
    Write-Host "GET /_debug/routes"
    Show-Resp $r
  } catch {
    Write-Host "ERROR GET /_debug/routes : $($_.Exception.GetType().FullName) - $($_.Exception.Message)"
    continue
  }

  try {
    $payloadObj = @{ username = $User; role = $Role; expires_minutes = $TTL }
    $payload = ($payloadObj | ConvertTo-Json -Compress)
    $content = New-Object System.Net.Http.StringContent($payload, [Text.Encoding]::UTF8, "application/json")
    $r = $hc.PostAsync("$Base/auth/token", $content).Result
    Write-Host "POST /auth/token"
    Show-Resp $r
    $tokJson = $r.Content.ReadAsStringAsync().Result
    try { $global:token = (ConvertFrom-Json $tokJson).access_token } catch { $global:token = $null }
    if (-not $global:token) { 
      Write-Host "Token not obtained. Trying next base..."
      continue
    }
    $hc.DefaultRequestHeaders.Authorization = New-Object System.Net.Http.Headers.AuthenticationHeaderValue('Bearer', $global:token)
    Write-Host "Token acquired."
  } catch {
    Write-Host "ERROR POST /auth/token : $($_.Exception.GetType().FullName) - $($_.Exception.Message)"
    continue
  }

  try {
    $r = $hc.GetAsync("$Base/ai/bots").Result
    Write-Host "GET /ai/bots (authorized)"
    Show-Resp $r
  } catch {
    Write-Host "ERROR GET /ai/bots : $($_.Exception.GetType().FullName) - $($_.Exception.Message)"
  }

  try {
    $r = $hc.GetAsync("$Base/documents/").Result
    Write-Host "GET /documents/ (authorized)"
    Show-Resp $r
  } catch {
    Write-Host "ERROR GET /documents/ : $($_.Exception.GetType().FullName) - $($_.Exception.Message)"
  }

  break
}

Write-Host "=== Done ==="
