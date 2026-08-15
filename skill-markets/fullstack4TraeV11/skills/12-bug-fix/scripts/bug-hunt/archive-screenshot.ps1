# archive-screenshot.ps1 — Playwright 截图归档脚本（V11.8.2 NEW Stage 6 Phase A，Windows）
#
# 用法:
#   pwsh scripts/bug-hunt/archive-screenshot.ps1 -Slug "BUG-017-fixed" -SubDir "bug-hunt"
#   pwsh scripts/bug-hunt/archive-screenshot.ps1 -Slug "BUG-017-fixed" -SubDir "bug-hunt" -DryRun
#
# 产物: docs/evidence/<YYYY-MM-DD>/<SubDir>/<Slug>.png
#
# 反 V11 §3.7 #2 反例: 手动 Copy-Item 7 次 → 归档脚本化。

param(
    [Parameter(Mandatory=$true)][string]$Slug,
    [string]$SubDir = "bug-hunt",
    [switch]$DryRun
)

$ErrorActionPreference = 'Stop'

$dateDir = (Get-Date -Format "yyyy-MM-dd")
$outDir = Join-Path "docs/evidence/$dateDir" $SubDir
$outFile = Join-Path $outDir "$Slug.png"

$downloads = $env:USERPROFILE + "\Downloads"
$screenshotFile = Get-ChildItem -Path $downloads -Filter "screenshot-*.png" -ErrorAction SilentlyContinue |
    Sort-Object LastWriteTime -Descending |
    Select-Object -First 1

if (-not $screenshotFile) {
    Write-Host "[FATAL] Downloads 下未找到 screenshot-*.png（先跑 playwright_screenshot）" -ForegroundColor Red
    exit 1
}

if ($DryRun) {
    Write-Host "[DRYRUN] mkdir $outDir"
    Write-Host "[DRYRUN] Copy-Item $($screenshotFile.FullName) $outFile"
    Write-Host "[DRYRUN] Remove-Item $($screenshotFile.FullName)"
    exit 0
}

if (-not (Test-Path $outDir)) {
    New-Item -ItemType Directory -Path $outDir -Force | Out-Null
}

Copy-Item -Path $screenshotFile.FullName -Destination $outFile -Force
Remove-Item -Path $screenshotFile.FullName -Force

Write-Host "[OK] 归档: $($screenshotFile.FullName) → $outFile"