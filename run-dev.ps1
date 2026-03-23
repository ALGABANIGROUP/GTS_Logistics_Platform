# run-dev.ps1
$PGURL = $env:ASYNC_DATABASE_URL

if (-not $PGURL) {
    Write-Error "ASYNC_DATABASE_URL is not set. Configure it in your local .env or shell before running run-dev.ps1."
    exit 1
}

$env:DATABASE_URL = $PGURL
$env:ASYNC_DATABASE_URL = $PGURL
$env:SQLALCHEMY_DATABASE_URL = $PGURL
$env:DB_URL = $PGURL
$env:OFFLINE = "false"

$env:PYTHONPATH = (Get-Location).Path

# Optional Arabic code lint guard (set GTS_LINT_ARABIC_ON_DEV=1 to enable)
if ($env:GTS_LINT_ARABIC_ON_DEV -and ($env:GTS_LINT_ARABIC_ON_DEV.ToLower() -in @("1","true","yes"))) {
	Write-Host "[run-dev] Arabic lint enabled; scanning code..."
	$npmCmd = Get-Command npm -ErrorAction SilentlyContinue
	if ($null -ne $npmCmd) {
		npm run lint:arabic
		if ($LASTEXITCODE -ne 0) {
			Write-Error "[run-dev] Arabic lint failed. Fix findings or unset GTS_LINT_ARABIC_ON_DEV to bypass."
			exit $LASTEXITCODE
		}
	} else {
		Write-Host "[run-dev] npm not found; skipping arabic lint"
	}
} else {
	Write-Host "[run-dev] Arabic lint disabled (set GTS_LINT_ARABIC_ON_DEV=1 to enable)"
}

uvicorn backend.main:app --reload
