param(
  [int]$Port = 5433,
  [string]$EnvFile = ".env"
)

Write-Host "Switching PostgreSQL port in file: $EnvFile to: $Port"

# Resolve .env path safely
try {
  $envPath = Resolve-Path -LiteralPath $EnvFile -ErrorAction Stop
}
catch {
  Write-Host "File not found: $EnvFile (current dir: $(Get-Location))"
  Write-Host "Tip: Run with -EnvFile 'F:\ASUS ROG Strix G614JV\GTS Logistics\.env'"
  exit 1
}

# Read content
try {
  $content = Get-Content -LiteralPath $envPath -ErrorAction Stop
}
catch {
  Write-Error "Unable to read file: $envPath"
  exit 1
}

# Make a backup
$backupFile = "$($envPath).bak"
try {
  Copy-Item -LiteralPath $envPath -Destination $backupFile -Force
  Write-Host "Backup created: $backupFile"
}
catch {
  Write-Error "Failed to create backup at: $backupFile"
  exit 1
}

# Replace common occurrences:
# - any host:port like 127.0.0.1:<digits>  --> set to selected $Port
# - DATABASE_PORT=<digits>                 --> set to selected $Port
# Notes:
# - We operate line-by-line to avoid accidental binary issues.
$updated = $content `
  -replace "127\.0\.0\.1:\d+", "127.0.0.1:$Port" `
  -replace "localhost:\d+", "localhost:$Port" `
  -replace "DATABASE_PORT=\d+", "DATABASE_PORT=$Port"

# Write back with UTF8 (no BOM)
try {
  $updated | Set-Content -LiteralPath $envPath -Encoding UTF8
}
catch {
  Write-Error "Failed to write updated content to: $envPath"
  exit 1
}

# Print a summary of key lines after update
Write-Host "Summary of updated DB settings:"
Select-String -Path $envPath -Pattern `
  "^DATABASE_URL=.*$", `
  "^SQLALCHEMY_DATABASE_URL=.*$", `
  "^ALEMBIC_SYNC_DATABASE_URL=.*$", `
  "^DATABASE_PORT=\d+$" |
ForEach-Object { $_.Line } |
ForEach-Object { Write-Host ("  " + $_) }

Write-Host "Done."
