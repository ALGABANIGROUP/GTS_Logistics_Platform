$base = "http://127.0.0.1:8000"

function Read-BodyFromWebException($_err) {
  try {
    $resp = $_err.Exception.Response
    if ($resp -and $resp.GetResponseStream()) {
      $reader = New-Object System.IO.StreamReader($resp.GetResponseStream())
      return $reader.ReadToEnd()
    }
  } catch {}
  return ""
}

function Call-Api($method, $url, $headers = $null) {
  try {
    $res = Invoke-WebRequest $url -Method $method -Headers $headers -UseBasicParsing
    $body = $res.Content
    $json = $null
    try { $json = ($body | ConvertFrom-Json) } catch { $json = $body }
    return @{ ok = $true; status = [int]$res.StatusCode; data = $json }
  } catch {
    $code = -1
    try { $code = $_.Exception.Response.StatusCode.value__ } catch {}
    $b = Read-BodyFromWebException($_)
    return @{ ok = $false; status = $code; data = $b }
  }
}

$t = Call-Api "GET" "$base/auth/dev-token?role=admin"
if (-not $t.ok) { "DEV TOKEN FAILED: $($t.status)"; $t.data; exit 1 }

$token = $t.data.access_token
if (-not $token) { "DEV TOKEN HAS NO access_token"; $t.data; exit 1 }

$headers = @{ Authorization = "Bearer $token" }

$me = Call-Api "GET" "$base/users/me" $headers
"USERS/ME => $($me.status)"
$me.data
