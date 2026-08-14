# Wrapper: run daily-vibe-coding pipeline
# Step 1: collect-baseline.py writes _baseline.json
# Step 2: generate-templates.py creates 5 skeleton .md files
# Step 3: run agent (if run-daily-vibe-coding.mjs exists)
#
# Usage:
#   powershell -ExecutionPolicy Bypass -File scripts\run-daily-vibe-coding.ps1
#   powershell ... -- --history-date 2026-08-14
#   powershell ... -- --no-scan --only self-audit

$ErrorActionPreference = "Stop"
$ScriptDir = $PSScriptRoot

# Detect Python (avoid Git Bash /usr/bin/python3 missing pip; see AGENTS.md 4.1.3)
$py = $null
$candidates = @(
    "C:\ProgramData\miniconda3\python.exe",
    "C:\Users\septe\AppData\Local\Programs\Python\Python312\python.exe",
    "python.exe",
    "python",
    "py"
)
foreach ($c in $candidates) {
    try {
        $r = & $c --version 2>&1
        if ($LASTEXITCODE -eq 0) { $py = $c; break }
    } catch { }
}
if (-not $py) {
    Write-Host "[run-daily-vibe-coding.ps1] FATAL: python not found" -ForegroundColor Red
    exit 1
}

# Collect args (skip leading -- separator if present)
$pyArgs = @()
foreach ($a in $args) {
    if ($a -ne "--") { $pyArgs += $a }
}

# Step 1: precheck
Write-Host "[run-daily-vibe-coding.ps1] Step 1: precheck ($py)..." -ForegroundColor Cyan
& $py "$ScriptDir\daily-vibe-coding\collect-baseline.py" @pyArgs
$precheckExit = $LASTEXITCODE
if ($precheckExit -notin @(0, 2)) {
    Write-Host "[run-daily-vibe-coding.ps1] precheck failed, exit=$precheckExit" -ForegroundColor Red
    exit $precheckExit
}

# Step 2: generate skeleton (filter --no-scan which is collect-only)
Write-Host "[run-daily-vibe-coding.ps1] Step 2: generate templates..." -ForegroundColor Cyan
$genArgs = @()
foreach ($a in $pyArgs) {
    if ($a -eq "--no-scan") { continue }
    $genArgs += $a
}
try {
    & $py "$ScriptDir\daily-vibe-coding\generate-templates.py" @genArgs
} catch {
    Write-Host "[run-daily-vibe-coding.ps1] Step 2 warning: $_" -ForegroundColor Yellow
}

# Step 3: run agent (if .mjs exists)
$mjsScript = "$ScriptDir\run-daily-vibe-coding.mjs"
if (Test-Path $mjsScript) {
    Write-Host "[run-daily-vibe-coding.ps1] Step 3: launch agent..." -ForegroundColor Cyan
    $nodePath = (where.exe node | Select-Object -First 1).ToString().Trim()
    & "$nodePath" "$mjsScript" 2>&1 | Out-Null
    exit $LASTEXITCODE
} else {
    Write-Host "[run-daily-vibe-coding.ps1] Step 3: SKIP (run-daily-vibe-coding.mjs missing)" -ForegroundColor Yellow
    Write-Host "[run-daily-vibe-coding.ps1] precheck + templates done:" -ForegroundColor Green
    Write-Host "  -> logs/daily-vibe-coding/<today>/_baseline.json" -ForegroundColor Green
    Write-Host "  -> 5 .md skeletons generated" -ForegroundColor Green
    Write-Host "[run-daily-vibe-coding.ps1] DONE" -ForegroundColor Green
    exit 0
}