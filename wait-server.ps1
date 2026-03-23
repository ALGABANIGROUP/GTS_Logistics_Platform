param([string]$BaseUrl=$env:GTS_BASE_URL,[int]$TimeoutSec=45,[switch]$UseAuth)
if([string]::IsNullOrWhiteSpace($BaseUrl)){$BaseUrl="http://127.0.0.1:8001"}
$deadline=(Get-Date).AddSeconds($TimeoutSec)
$ok=$false
$headers=@{}

# ????? ????? ???? ?????? TCP
$uobj=[uri]$BaseUrl
do{
  $t=Test-NetConnection $uobj.Host -Port $uobj.Port -WarningAction SilentlyContinue
  if($t.TcpTestSucceeded){$ok=$true}else{Start-Sleep -Milliseconds 500}
}until($ok -or (Get-Date) -gt $deadline)
if(-not $ok){throw "Port $($uobj.Port) on $($uobj.Host) not ready"}

# (???????) ???? ??? ????
if($UseAuth){
  $u=$env:GTS_USERNAME; if([string]::IsNullOrWhiteSpace($u)){$u="yassir"}
  $r=$env:GTS_ROLE;     if([string]::IsNullOrWhiteSpace($r)){$r="admin"}
  try{
    $body=@{username=$u;role=$r;expires_minutes=60}|ConvertTo-Json -Compress
    $resp=Invoke-RestMethod -Method POST -Uri "$BaseUrl/auth/token" -ContentType "application/json" -Body $body -TimeoutSec 5
    $tok=$resp.access_token
    if($tok){$headers=@{Authorization="Bearer $tok"}}
  }catch{}
}

# ??? ??? ??????? ???? health (?? ?????? ?????)
try{Invoke-RestMethod -Uri "$BaseUrl/finance/health" -Headers $headers -TimeoutSec 2|Out-Null}catch{
  try{Invoke-RestMethod -Uri "$BaseUrl/health" -Headers $headers -TimeoutSec 2|Out-Null}catch{}
}
"Server is ready on $BaseUrl"
