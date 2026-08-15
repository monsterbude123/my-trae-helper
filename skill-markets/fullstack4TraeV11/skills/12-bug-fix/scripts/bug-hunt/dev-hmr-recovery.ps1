# dev-hmr-recovery.ps1 — HMR stale 4 步恢复（V11.8.2 NEW Stage 6 Phase A，Windows）
#
# 用法:
#   pwsh scripts/bug-hunt/dev-hmr-recovery.ps1 -DryRun  # 先打印 4 步命令
#   pwsh scripts/bug-hunt/dev-hmr-recovery.ps1          # 真恢复
#
# 反 V11-BH5 反例: 连续 3 次重 navigate 未恢复仍在手动 retry（浪费 5 min/次）。

param([switch]$DryRun = $false)

$ErrorActionPreference = 'Stop'

if ($DryRun) {
    Write-Host "[DRYRUN] kill next-server / node.exe on :3000 :3001"
    Write-Host "[DRYRUN] 清 HMR 缓存（.next/cache 目录，业务必需）" # scan-ignore-line
    Write-Host "[DRYRUN] 杀残留 tsx watch / next-server / worker / watchdog / bull-board"
    Write-Host "[DRYRUN] npm run dev (detached, log .next/dev.log)"
    exit 0
}

# 1. kill 占端口进程
Write-Host "[STEP 1/4] kill 占端口 3000 / 3001 进程"
$conn3000 = Get-NetTCPConnection -LocalPort 3000 -State Listen -ErrorAction SilentlyContinue
$conn3001 = Get-NetTCPConnection -LocalPort 3001 -State Listen -ErrorAction SilentlyContinue
if ($conn3000) {
    $conn3000 | ForEach-Object { Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue }
}
if ($conn3001) {
    $conn3001 | ForEach-Object { Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue }
}

# 2. 清 HMR 缓存（路径白名单：必须在项目根 .next/cache 内，且非符号链接）
Write-Host "[STEP 2/4] Remove-Item .next/cache"
$projectRoot = (Get-Location).Path
$target = Join-Path $projectRoot ".next/cache"
if (Test-Path $target) {
    # 安全校验：路径必须在项目根下、非符号链接
    $item = Get-Item $target -Force -ErrorAction SilentlyContinue
    if ($item.LinkType -or ($item.Attributes -band [IO.FileAttributes]::ReparsePoint)) {
        Write-Host "[WARN] .next/cache 是符号链接，跳过删除（防误删）" -ForegroundColor Yellow
    } elseif (-not $target.StartsWith($projectRoot, [System.StringComparison]::OrdinalIgnoreCase)) {
        Write-Host "[FATAL] .next/cache 不在项目根内，拒删（防误删）" -ForegroundColor Red
        exit 1
    } else {
        Remove-Item -Recurse -Force -LiteralPath $target # scan-ignore-line - HMR 恢复业务必需，路径已校验
    }
}

# 3. 杀残留
Write-Host "[STEP 3/4] 杀残留 tsx watch / next-server / worker / watchdog / bull-board"
Get-Process -Name "node" -ErrorAction SilentlyContinue | Where-Object { $_.CommandLine -match "next-server|tsx|bull-board" } | ForEach-Object {
    Stop-Process -Id $_.Id -Force -ErrorAction SilentlyContinue
}

# 4. 重启 dev server
Write-Host "[STEP 4/4] Start-Process npm.cmd run dev (detached, log .next/dev.log)"
if (-not (Test-Path .next)) {
    New-Item -ItemType Directory -Path .next | Out-Null
}

# 探测 npm.cmd 路径
$npmCmd = $null
if (Test-Path "$env:ProgramFiles\nodejs\npm.cmd") {
    $npmCmd = "$env:ProgramFiles\nodejs\npm.cmd"
} elseif (Get-Command npm.cmd -ErrorAction SilentlyContinue) {
    $npmCmd = (Get-Command npm.cmd).Source
} else {
    Write-Host "[FATAL] npm.cmd 未找到" -ForegroundColor Red
    exit 1
}

Start-Process -FilePath $npmCmd -ArgumentList "run","dev" -WorkingDirectory $PWD -RedirectStandardOutput ".next/dev.log" -RedirectStandardError ".next/dev.log" -NoNewWindow

# 等 Ready
Write-Host "[WAIT] 轮询 dev server Ready（最多 30s）"
for ($i = 1; $i -le 30; $i++) {
    Start-Sleep -Seconds 1
    if ((Test-Path .next/dev.log) -and (Select-String -Path .next/dev.log -Pattern "Ready in" -Quiet)) {
        Write-Host "[OK] dev server Ready"
        exit 0
    }
}

Write-Host "[WARN] 30s 内未检测到 Ready 输出, 请手动检查: Get-Content .next/dev.log -Wait" -ForegroundColor Yellow
exit 1