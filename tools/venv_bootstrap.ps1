# Shared venv activation helper for GTS scripts (ASCII-safe).

function Find-GtsRepoRoot {
    param([string]$StartDir)

    $current = $StartDir
    if (-not $current) {
        return (Get-Location).Path
    }

    try {
        $current = (Resolve-Path -LiteralPath $current).Path
    }
    catch {
        $current = $StartDir
    }

    while ($current) {
        if (Test-Path (Join-Path $current ".venv")) { return $current }
        if (Test-Path (Join-Path $current ".git")) { return $current }

        $parent = Split-Path -Parent $current
        if (-not $parent -or $parent -eq $current) { break }
        $current = $parent
    }

    return $StartDir
}

function Use-GtsVenv {
    param(
        [string]$RepoRoot,
        [string]$StartDir
    )

    if (-not $RepoRoot) {
        $RepoRoot = $env:VENV_PATH
    }

    if (-not $RepoRoot) {
        $start = $StartDir
        if (-not $start) {
            if ($PSScriptRoot) {
                $start = $PSScriptRoot
            }
            else {
                $start = (Get-Location).Path
            }
        }
        $RepoRoot = Find-GtsRepoRoot -StartDir $start
    }


    $venvRoot = $env:VENV_PATH
    if (-not $venvRoot) {
        $venvRoot = Join-Path $RepoRoot ".venv"
    }

    # If .venv is not found in the root, try backend/.venv
    if (-not (Test-Path $venvRoot)) {
        $backendVenv = Join-Path $RepoRoot "backend\.venv"
        if (Test-Path $backendVenv) {
            $venvRoot = $backendVenv
        }
        else {
            $foundVenv = Get-ChildItem -Path $RepoRoot -Directory -Filter ".venv" -ErrorAction SilentlyContinue | Select-Object -First 1
            if ($foundVenv) {
                $venvRoot = $foundVenv.FullName
            }
        }
    }

    $venvActivate = Join-Path $venvRoot "Scripts\\Activate.ps1"

    if (Test-Path $venvActivate) {
        & $venvActivate
        if (-not $env:VIRTUAL_ENV) {
            Write-Warning "Activate.ps1 ran but VIRTUAL_ENV is not set. Check PowerShell execution policy."
        }
        return $true
    }

    Write-Warning "Virtual environment not found at $venvActivate. Set VENV_PATH to override."
    return $false
}
