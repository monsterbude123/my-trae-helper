# render-cockpit.ps1 — 读取 cockpit state-card，渲染驾驶舱快照
# > 来源：fullstack4TraeV9 cockpit 模式
# 用法: .\render-cockpit.ps1 -GameKey <game-dir>
# 输出: Markdown cockpit snapshot to stdout

param([string]$GameKey)

if (-not $GameKey) {
    Write-Error "Usage: .\render-cockpit.ps1 -GameKey <game-dir>"
    exit 1
}

$cockpitFile = Join-Path $GameKey ".project-cockpit.md"

function Check-FileFreshness($path) {
    if (Test-Path $path) {
        $lastWrite = (Get-Item $path).LastWriteTime
        $minutes = [int]((Get-Date) - $lastWrite).TotalMinutes
        if ($minutes -gt 30) { "⚠️ stale ($($minutes)min)" }
        else { "✅ fresh" }
    } else { "❌ MISSING" }
}

function Get-PhaseTimestamps($gameKey) {
    $artifacts = @(
        @{Phase=0; File="engine-confirmed.md"},
        @{Phase=1; File="story-design.md"},
        @{Phase=2; File="asset-manifest.md"},
        @{Phase=3; File="scene-manifest.json"},
        @{Phase=5; File="build.log"},
        @{Phase=6; File="deploy.log"}
    )
    foreach ($a in $artifacts) {
        $p = Join-Path $gameKey $a.File
        [PSCustomObject]@{Phase=$a.Phase; File=$a.File; Status=Check-FileFreshness $p}
    }
}

# Main
Write-Host "# 🛩️ Cockpit Snapshot — $GameKey`n"

if (Test-Path $cockpitFile) {
    Get-Content $cockpitFile -Raw | Write-Host
} else {
    Write-Host "⚠️ cockpit 不存在 — Phase 0 未完成或未初始化`n"
}

Write-Host "## 文件系统自检`n"
Get-PhaseTimestamps $GameKey | Format-Table -AutoSize
