param(
  [string]$RepoDir = "D:\GTS-Logistics",
  [string]$Branch  = "",
  [int]$DebounceSeconds = 7,
  [switch]$AutoPullRebase
)

function Write-Info($m){ Write-Host "[auto-sync] $m" -ForegroundColor Cyan }
function Write-Ok($m){ Write-Host "[auto-sync] $m" -ForegroundColor Green }
function Write-Err($m){ Write-Host "[auto-sync] $m" -ForegroundColor Red }

if (-not (Test-Path $RepoDir)) { Write-Err "RepoDir not found: $RepoDir"; exit 1 }
Set-Location $RepoDir
if (-not (Test-Path ".git")) { Write-Err "Not a git repo: $RepoDir"; exit 1 }

# If branch not specified, use current
if ([string]::IsNullOrWhiteSpace($Branch)) {
  $Branch = (git branch --show-current).Trim()
  if (-not $Branch) { Write-Err "Cannot detect current branch."; exit 1 }
}

# Exclusions (folders/extensions we don't monitor)
$IgnoreDirs = @("\.git\", "\.venv\", "\node_modules\", "\__pycache__\", "\dist\", "\build\")
$IgnoreExtensions = @(".pyc", ".pyo", ".pyd", ".log", ".tmp", ".swp")

# Timer for debouncing
$script:pending = $false
$timer = New-Object System.Timers.Timer
$timer.Interval = $DebounceSeconds * 1000
$timer.AutoReset = $false
$timer.add_Elapsed({
  try {
    Set-Location $RepoDir
    # Skip if no changes
    $status = git status --porcelain
    if (-not $status) { Write-Info "No changes to sync."; return }

    Write-Info "Staging changes..."
    git add -A

    $pending = (git diff --cached --name-only)
    if ($pending) {
      $msg = "auto: sync @ $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
      Write-Info "Committing: $msg"
      git commit -m $msg | Out-Null
    }

    if ($AutoPullRebase -or (-not $PSBoundParameters.ContainsKey('AutoPullRebase'))) {
      Write-Info "Pull --rebase from origin/$Branch..."
      git fetch origin | Out-Null
      git pull --rebase origin $Branch
      if ($LASTEXITCODE -ne 0) {
        Write-Err "Rebase stopped. Resolve conflicts then run: git add -A; git rebase --continue; git push"
        return
      }
    }

    Write-Info "Pushing to origin/$Branch..."
    git push -u origin $Branch
    if ($LASTEXITCODE -eq 0) { Write-Ok "Pushed." }
  } catch {
    Write-Err $_
  } finally {
    $script:pending = $false
  }
})

# FileSystemWatcher
$watcher = New-Object System.IO.FileSystemWatcher
$watcher.Path = $RepoDir
$watcher.IncludeSubdirectories = $true
$watcher.Filter = "*.*"
$watcher.EnableRaisingEvents = $true

# EN
function Test-Ignore($fullPath) {
  if (-not $fullPath) { return $true }
  foreach ($d in $IgnoreDirs) {
    if ($fullPath -replace '/','\' -match [regex]::Escape($d)) { return $true }
  }
  $ext = [System.IO.Path]::GetExtension($fullPath)
  if ($IgnoreExtensions -contains $ext) { return $true }
  return $false
}

$action = {
  param($src, $fsEventArgs)
  $p = $fsEventArgs.FullPath
  if (Test-Ignore $p) { return }
  # EN (debounce)
  $script:pending = $true
  $timer.Stop()
  $timer.Start()
}

# EN
$created  = Register-ObjectEvent $watcher Created  -Action $action
$changed  = Register-ObjectEvent $watcher Changed  -Action $action
$deleted  = Register-ObjectEvent $watcher Deleted  -Action $action
$renamed  = Register-ObjectEvent $watcher Renamed  -Action $action

Write-Ok "Auto sync watching '$RepoDir' on branch '$Branch' (debounce ${DebounceSeconds}s)."
Write-Info "Press Ctrl+C to stop."

# EN
try {
  while ($true) { Start-Sleep -Seconds 1 }
} finally {
  Unregister-Event -SourceIdentifier $created.Name  -ErrorAction SilentlyContinue
  Unregister-Event -SourceIdentifier $changed.Name  -ErrorAction SilentlyContinue
  Unregister-Event -SourceIdentifier $deleted.Name  -ErrorAction SilentlyContinue
  Unregister-Event -SourceIdentifier $renamed.Name  -ErrorAction SilentlyContinue
  $watcher.EnableRaisingEvents = $false
  $watcher.Dispose()
  $timer.Dispose()
  Write-Info "Auto sync stopped."
}
