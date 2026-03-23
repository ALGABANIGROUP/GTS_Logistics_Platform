param(
  [string]$RepoDir = "D:\GTS-Logistics",
  [string]$Branch  = "mvp-free",
  [string]$Message = "chore: local sync",
  [switch]$CreateFeatureBranch,
  [string]$FeatureBranchName = ""
)

function Fail($m){ Write-Host "ERROR: $m" -ForegroundColor Red; exit 1 }
function Ok($m){ Write-Host $m -ForegroundColor Green }
function Info($m){ Write-Host $m -ForegroundColor Cyan }

if (-not (Test-Path $RepoDir)) { Fail "RepoDir not found: $RepoDir" }
Set-Location $RepoDir
if (-not (Test-Path ".git")) { Fail "Not a git repo: $RepoDir" }

# Ensure git identity (once)
if (-not (git config user.name))  { git config --global user.name "Yassir Mossttafa" }
if (-not (git config user.email)) { git config --global user.email "you@example.com" }
git config core.autocrlf true | Out-Null

Info "Fetching origin..."
git fetch origin
if ($LASTEXITCODE -ne 0) { Fail "git fetch failed" }

if ($CreateFeatureBranch) {
  if (-not $FeatureBranchName) { $FeatureBranchName = "feat/$(Get-Date -Format yyyyMMdd-HHmmss)" }
  Info "Creating feature branch: $FeatureBranchName"
  git checkout -b $FeatureBranchName
  if ($LASTEXITCODE -ne 0) { Fail "Cannot create branch $FeatureBranchName" }
  $Branch = $FeatureBranchName
} else {
  $current = (git branch --show-current).Trim()
  if ($current -ne $Branch) {
    Info "Checking out $Branch"
    git checkout $Branch 2>$null
    if ($LASTEXITCODE -ne 0) {
      Info "Creating local branch from origin/$Branch"
      git checkout -b $Branch "origin/$Branch"
      if ($LASTEXITCODE -ne 0) { Fail "Cannot checkout $Branch" }
    }
  }
}

# abort stuck rebase if any
if (Test-Path ".git\REBASE_HEAD") { Write-Host "Aborting in-progress rebase..." -ForegroundColor Yellow; git rebase --abort }

Info "Staging all changes..."
git add -A

$pending = (git diff --cached --name-only)
if ($pending) {
  Info "Committing: $Message"
  git commit -m "$Message"
  if ($LASTEXITCODE -ne 0) { Fail "Commit failed" }
} else {
  Write-Host "No staged changes to commit." -ForegroundColor Yellow
}

Info "Rebasing with origin/$Branch..."
git pull --rebase origin $Branch
if ($LASTEXITCODE -ne 0) {
  Write-Host "`nResolve conflicts, then run:" -ForegroundColor Yellow
  Write-Host "  git add -A"
  Write-Host "  git rebase --continue"
  Write-Host "  git push origin $Branch"
  exit 1
}

Info "Pushing to origin/$Branch..."
git push -u origin $Branch
if ($LASTEXITCODE -ne 0) { Fail "Push failed" }

Ok "Done. Branch: $Branch"
git status
