param(
  [switch]$Reload
)

# ---------- settings ----------
$ErrorActionPreference = "Stop"
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$workDir = (Resolve-Path (Join-Path $scriptDir "..\..")).Path   # repo root
$envFile1 = Join-Path $workDir "backend\.env"
$envFile2 = Join-Path $workDir ".env"                            # optional root .env
$hostIp = "127.0.0.1"
$port = 8001

# ---------- helpers ----------
function Import-DotEnvFile([string]$path) {
  if (-not (Test-Path $path)) { return }
  $lines = Get-Content -Path $path -Encoding UTF8
  foreach ($line in $lines) {
    $trim = $line.Trim()
    if ($trim -eq "" -or $trim.StartsWith("#")) { continue }

    # KEY=VALUE
    if ($trim -match '^\s*([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.*)\s*$') {
      $key = $matches[1]
      $val = $matches[2]

      # strip quotes if present
      if ($val.StartsWith('"') -and $val.EndsWith('"')) {
        $val = $val.Substring(1, $val.Length - 2)
      }
      elseif ($val.StartsWith("'") -and $val.EndsWith("'")) {
        $val = $val.Substring(1, $val.Length - 2)
      }

      # simple ${VAR} expansion from current environment
      $val = [regex]::Replace($val, '\$\{([A-Za-z_][A-Za-z0-9_]*)\}', {
          param($m)
          $name = $m.Groups[1].Value
          (Get-Item "Env:$name" -ErrorAction SilentlyContinue).Value
        })

      try {
        Set-Item -Path "Env:$key" -Value $val
      }
      catch {
        Write-Warning ("Failed to set Env:{0} - {1}" -f $key, $_.Exception.Message)
      }
    }
  }
}

function Test-PortFree([int]$p) {
  # suppress informational noise from Test-NetConnection across PS versions
  try {
    $cmd = Get-Command Test-NetConnection -ErrorAction SilentlyContinue
    if ($null -ne $cmd -and $cmd.Parameters.ContainsKey('InformationLevel')) {
      $r = Test-NetConnection -ComputerName $hostIp -Port $p -WarningAction SilentlyContinue -InformationLevel Quiet
    }
    else {
      $r = Test-NetConnection -ComputerName $hostIp -Port $p -WarningAction SilentlyContinue
    }
    return -not $r.TcpTestSucceeded
  }
  catch { return $true }
}

function ConvertTo-MaskedDsn([string]$dsn) {
  if ([string]::IsNullOrWhiteSpace($dsn)) { return "" }
  return ([regex]::Replace($dsn, '://([^:]+):([^@]+)@', '://$1:****@'))
}

# ---------- load env ----------
Import-DotEnvFile $envFile1
Import-DotEnvFile $envFile2

# asyncpg: translate sslmode=require -> ssl=true (defensive)
if ($env:ASYNC_DATABASE_URL -and $env:ASYNC_DATABASE_URL -match '(^postgresql\+asyncpg:.*)([?&])sslmode=require(.*)$') {
  $env:ASYNC_DATABASE_URL = ($env:ASYNC_DATABASE_URL -replace 'sslmode=require', 'ssl=true')
}

# choose free port (prefer 8001, fallback 8010)
if (-not (Test-PortFree $port)) {
  $port = 8010
  if (-not (Test-PortFree $port)) {
    Write-Error "Both ports 8001 and 8010 are in use."
    exit 1
  }
  Write-Warning ("Port 8001 is in use. Switching to {0}." -f $port)
}

# ---------- print env summary ----------
Write-Host "[ENV] APP_TITLE         = $($env:APP_TITLE)"
Write-Host "[ENV] ASYNC_DATABASE_URL= $(ConvertTo-MaskedDsn $env:ASYNC_DATABASE_URL)"
Write-Host "[ENV] MAIL_ENABLED      = $($env:MAIL_ENABLED)"
Write-Host "[ENV] WorkDir           = $workDir"
Write-Host "[ENV] App Module        = backend.main:app"

# ---------- run uvicorn ----------
Set-Location $workDir

$bootstrapPath = Join-Path $workDir "tools\\venv_bootstrap.ps1"
if (Test-Path $bootstrapPath) {
  . $bootstrapPath
  Use-GtsVenv -RepoRoot $workDir | Out-Null
} else {
  Write-Warning "Venv bootstrap helper not found at $bootstrapPath"
}

$uvArgs = @("backend.main:app", "--host", $hostIp, "--port", $port)
if ($Reload) { $uvArgs += "--reload" }
$reloadText = if ($Reload) { "--reload" } else { "" }

# prefer venv python if available
$venvPy = if ($env:VIRTUAL_ENV) { Join-Path $env:VIRTUAL_ENV "Scripts\\python.exe" } else { Join-Path $workDir ".venv\\Scripts\\python.exe" }
if (Test-Path $venvPy) {
  Write-Host ("Starting API on http://{0}:{1} {2} ..." -f $hostIp, $port, $reloadText)
  & $venvPy -m uvicorn @uvArgs
  exit $LASTEXITCODE
}

# fallback to python on PATH
if (Get-Command python -ErrorAction SilentlyContinue) {
  Write-Host ("Starting API on http://{0}:{1} {2} ..." -f $hostIp, $port, $reloadText)
  python -m uvicorn @uvArgs
  exit $LASTEXITCODE
}

# final fallback to py launcher
if (Get-Command py -ErrorAction SilentlyContinue) {
  Write-Host ("Starting API on http://{0}:{1} {2} ..." -f $hostIp, $port, $reloadText)
  py -m uvicorn @uvArgs
  exit $LASTEXITCODE
}

Write-Error "Python launcher not found on PATH (python or py)."
exit 1
