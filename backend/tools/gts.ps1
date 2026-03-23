# gts.ps1
param(
  [ValidateSet('Reset','Run','Smoke','All')]
  [string]$Action = 'All',

  [string]$AppHost = '127.0.0.1',
  [int]$Port = 8001,

  # DB (Render) params for Run/All
  [string]$DbUser,
  [string]$DbPass,
  [string]$DbHost = 'dpg-cuicq2qj1k6c73asm5c0-a.oregon-postgres.render.com',
  [int]$DbPort = 5432,
  [string]$DbName = 'gabani_transport_solutions',

  # Smoke params
  [string]$Base,
  [string]$User = 'yassir',
  [string]$Role = 'admin'
)

$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\\..")).Path
$bootstrapPath = Join-Path $repoRoot "tools\\venv_bootstrap.ps1"
if (Test-Path $bootstrapPath) {
  . $bootstrapPath
  Use-GtsVenv -RepoRoot $repoRoot | Out-Null
} else {
  Write-Warning "Venv bootstrap helper not found at $bootstrapPath"
}

function Get-PythonExe {
  param([string]$RepoRoot)
  if ($env:VIRTUAL_ENV) {
    $venvPy = Join-Path $env:VIRTUAL_ENV "Scripts\\python.exe"
    if (Test-Path $venvPy) { return $venvPy }
  }
  $fallback = Join-Path $RepoRoot ".venv\\Scripts\\python.exe"
  if (Test-Path $fallback) { return $fallback }
  return "python"
}

function Stop-Port {
  param([int]$Port)
  $cons = Get-NetTCPConnection -LocalPort $Port -ErrorAction SilentlyContinue
  if ($cons) {
    $pids = $cons | Select-Object -ExpandProperty OwningProcess -Unique
    foreach ($procId in $pids) {
      try { Stop-Process -Id $procId -Force -ErrorAction SilentlyContinue; "Killed PID $procId" } catch {}
    }
  } else { "No process on port $Port" }
}

function Reset-Env {
  param([int]$Port)
  Write-Host ">>> Killing port $Port ..."
  Stop-Port -Port $Port

  Write-Host ">>> Clearing environment variables ..."
  $keys = "ASYNC_DATABASE_URL","SQLALCHEMY_DATABASE_URL","DB_URL","DATABASE_URL"
  foreach ($k in $keys) {
    Remove-Item "Env:$k" -ErrorAction SilentlyContinue
    try { [Environment]::SetEnvironmentVariable($k,$null,"User") } catch {}
  }

  if (Test-Path ".env") {
    $stamp = Get-Date -Format "yyyyMMdd-HHmmss"
    Move-Item ".env" ".env.bak.$stamp" -ErrorAction SilentlyContinue
    "Backed up .env -> .env.bak.$stamp"
  }

  Write-Host ">>> Removing python caches ..."
  $trash = @("__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache")
  foreach ($t in $trash) {
    if (Test-Path $t) { Remove-Item $t -Recurse -Force -ErrorAction SilentlyContinue }
  }
  Get-ChildItem -Path . -Recurse -Include *.pyc -ErrorAction SilentlyContinue |
    Remove-Item -Force -ErrorAction SilentlyContinue

  "Reset done."
}

function Start-Server {
  param([string]$AppHost,[int]$Port,[string]$DbUser,[string]$DbPass,[string]$DbHost,[int]$DbPort,[string]$DbName)
  if (-not $DbUser -or -not $DbPass) { throw "DbUser/DbPass are required for -Action Run." }
  $pythonExe = Get-PythonExe -RepoRoot (Get-Location).Path

  $ASYNC = "postgresql+asyncpg://${DbUser}:${DbPass}@${DbHost}:${DbPort}/${DbName}"

  $env:ASYNC_DATABASE_URL      = $ASYNC
  $env:SQLALCHEMY_DATABASE_URL = $ASYNC
  $env:DB_URL                  = $ASYNC
  $env:DISABLE_SCHEDULER       = "1"
  $env:PYTHONPATH              = (Get-Location).Path

  "[ENV] ASYNC_DATABASE_URL=$($env:ASYNC_DATABASE_URL)"
  "[ENV] PYTHONPATH=$($env:PYTHONPATH)"
  "Starting uvicorn on http://$AppHost`:$Port ..."
  & $pythonExe -m uvicorn backend.main:app --host $AppHost --port $Port --access-log
}

function Test-Smoke {
  param([string]$Base,[string]$User,[string]$Role)
  if (-not $Base) { throw "Base is required for -Action Smoke." }

  "BASE=$Base"
  $token = (curl.exe -s -X POST "$Base/auth/token" `
    -H "Content-Type: application/x-www-form-urlencoded" `
    --data-urlencode "username=$User" `
    --data-urlencode "role=$Role" `
    --data-urlencode "expires_minutes=60" | ConvertFrom-Json).access_token

  "Token length: $($token.Length)"
  if (-not $token) { Write-Host "Failed to get token"; return }

  "---- /_debug/routes ----"
  curl.exe -s "$Base/_debug/routes" | Out-Host

  "---- /documents/_debug/db ----"
  curl.exe -s -H "Authorization: Bearer $token" "$Base/documents/_debug/db" | Out-Host

  "---- /documents/ (list) ----"
  curl.exe -s -H "Authorization: Bearer $token" "$Base/documents/" | Out-Host
}

switch ($Action) {
  'Reset' { Reset-Env -Port $Port; break }
  'Run'   { Start-Server -AppHost $AppHost -Port $Port -DbUser $DbUser -DbPass $DbPass -DbHost $DbHost -DbPort $DbPort -DbName $DbName; break }
  'Smoke' { if (-not $Base) { $Base = "http://$AppHost`:$Port" }; Test-Smoke -Base $Base -User $User -Role $Role; break }
  'All'   {
    Reset-Env -Port $Port
    Start-Job -Name "uvicorn-$Port" -ScriptBlock {
      param($AppHost,$Port,$DbUser,$DbPass,$DbHost,$DbPort,$DbName,$pwdPath,$pythonExe)
      Set-Location $pwdPath
      $env:ASYNC_DATABASE_URL      = "postgresql+asyncpg://$DbUser`:$DbPass@$DbHost`:$DbPort/$DbName"
      $env:SQLALCHEMY_DATABASE_URL = $env:ASYNC_DATABASE_URL
      $env:DB_URL                  = $env:ASYNC_DATABASE_URL
      $env:DISABLE_SCHEDULER       = "1"
      $env:PYTHONPATH              = $pwdPath
      & $pythonExe -m uvicorn backend.main:app --host $AppHost --port $Port --access-log
    } -ArgumentList $AppHost,$Port,$DbUser,$DbPass,$DbHost,$DbPort,$DbName,$((Get-Location).Path),(Get-PythonExe -RepoRoot $pwdPath) | Out-Null

    Start-Sleep -Seconds 4
    $baseUrl = "http://$AppHost`:$Port"
    Test-Smoke -Base $baseUrl -User $User -Role $Role
    Write-Host "Tip: Get-Job 'uvicorn-$Port' | Stop-Job  # to stop the background server"
  }
}
