<#
.SYNOPSIS
    game-production-kit 脚本串联入口（PowerShell 版 Makefile）
.DESCRIPTION
    串联 scripts/ 下 10 个独立 Python 脚本，按阶段分组执行。
    非零退出 → 标记 FAIL 但继续执行后续脚本，最后打印失败列表。
.PARAMETER Phase
    执行阶段: all（全部）/ assets（素材生成）/ gate（质量门禁）/ proof（Proof bundle）
.PARAMETER VerboseOutput
    输出每条命令的 stderr
.PARAMETER DryRun
    只打印将要执行的命令，不实际执行
.EXAMPLE
    .\Makefile.ps1 -Phase assets
    .\Makefile.ps1 -Phase gate -VerboseOutput
    .\Makefile.ps1 -Phase all -DryRun
#>

[CmdletBinding()]
param(
    [Parameter(Position = 0)]
    [ValidateSet('all', 'assets', 'gate', 'proof')]
    [string] $Phase = 'all',

    [switch] $VerboseOutput,

    [switch] $DryRun
)

$ErrorActionPreference = 'Continue'
$ScriptDir = $PSScriptRoot

# ── 阶段定义 ──
# Phase 4 gate scripts:
# 1. asset 引用完整性检查 (check_assets)
# 2. 场景覆盖检查 (validate_scenes)
# 3. TTS 配音验证 (verify_voices)
# 4. 版本一致性检查 (sync_version_tracking)
# 5. 缺口检测 (gap_detect — M9)
$PhaseGroups = [ordered]@{
    assets = @('gen_figures.py', 'gen_backgrounds.py', 'gen_title.py', 'gen_audio.py', 'gen_voice.py')
    gate   = @('check_assets.py', 'validate_scenes.py', 'verify_voices.py', 'sync_version_tracking.py', 'gap_detect.py')
    proof  = @('gen_voice_vas.py', 'inject_vocal.py')
}

# ── 全局汇总 ──
$GlobalTotal   = 0
$GlobalSuccess = 0
$GlobalFailed  = 0
$GlobalSkipped = 0
$GlobalFailedList = [System.Collections.Generic.List[string]]::new()

# ── 工具函数 ──
function Write-Banner([string] $Text) {
    $sep = '─' * 60
    Write-Host "`n$sep" -ForegroundColor Cyan
    Write-Host "  $Text" -ForegroundColor Cyan
    Write-Host "$sep" -ForegroundColor Cyan
}

function Run-Phase([string] $PhaseName, [string[]] $Scripts) {
    $phaseWatch = [System.Diagnostics.Stopwatch]::StartNew()
    $success = 0
    $failed  = 0
    $skipped = 0
    $failedList = [System.Collections.Generic.List[string]]::new()

    Write-Banner "Phase: $PhaseName"

    foreach ($script in $Scripts) {
        $pyPath = Join-Path $ScriptDir $script

        if (-not (Test-Path $pyPath)) {
            Write-Host "  [SKIP] $script — 文件不存在: $pyPath" -ForegroundColor Yellow
            $skipped++
            $GlobalSkipped++
            $GlobalTotal++
            continue
        }

        $cmd = "python `"$pyPath`""
        Write-Host "  [RUN ] $script" -ForegroundColor White

        if ($DryRun) {
            Write-Host "         (DryRun) 将执行: $cmd" -ForegroundColor DarkGray
            continue
        }

        # 执行
        $scriptWatch = [System.Diagnostics.Stopwatch]::StartNew()

        if ($VerboseOutput) {
            # 捕获 stdout + stderr
            $output = & python $pyPath 2>&1
        } else {
            $output = & python $pyPath 2>$null
        }

        $scriptWatch.Stop()
        $elapsed = $scriptWatch.Elapsed.TotalSeconds.ToString('F1')
        $GlobalTotal++

        if ($LASTEXITCODE -ne 0) {
            Write-Host "  [FAIL] $script (exit=$LASTEXITCODE, ${elapsed}s)" -ForegroundColor Red
            $failed++
            $GlobalFailed++
            $failedList.Add($script)
            $GlobalFailedList.Add($script)

            if ($VerboseOutput -and $output) {
                # 过滤出错误行
                $errLines = $output | Where-Object { $_ -is [System.Management.Automation.ErrorRecord] -or $_ -match 'error|Error|ERROR|Traceback|exception' }
                if ($errLines) {
                    Write-Host "         ── stderr ──" -ForegroundColor DarkRed
                    $errLines | ForEach-Object { Write-Host "         $_" -ForegroundColor DarkRed }
                    Write-Host "         ────────────" -ForegroundColor DarkRed
                }
            }
        } else {
            Write-Host "  [PASS] $script (${elapsed}s)" -ForegroundColor Green
            $success++
            $GlobalSuccess++
        }
    }

    $phaseWatch.Stop()
    $phaseTotal = $success + $failed + $skipped
    $phaseElapsed = $phaseWatch.Elapsed.TotalSeconds.ToString('F1')

    Write-Host ""
    Write-Host "  ── [$PhaseName] 汇总: 共 $phaseTotal 个 | 成功 $success | 失败 $failed | 跳过 $skipped | 耗时 ${phaseElapsed}s ──" -ForegroundColor $(if ($failed -gt 0) { 'Yellow' } else { 'Green' })

    if ($failedList.Count -gt 0) {
        Write-Host "  失败脚本:" -ForegroundColor Red
        $failedList | ForEach-Object { Write-Host "    ✗ $_" -ForegroundColor Red }
    }
}

# ── 主流程 ──
$overallWatch = [System.Diagnostics.Stopwatch]::StartNew()

Write-Host "Makefile.ps1 — game-production-kit 脚本串联" -ForegroundColor Magenta
Write-Host "脚本目录: $ScriptDir" -ForegroundColor DarkGray
if ($DryRun) { Write-Host "模式: DRY RUN（仅预览，不执行）" -ForegroundColor Yellow }
Write-Host ""

if ($Phase -eq 'all') {
    foreach ($phaseName in $PhaseGroups.Keys) {
        Run-Phase $phaseName $PhaseGroups[$phaseName]
    }
} else {
    Run-Phase $Phase $PhaseGroups[$Phase]
}

$overallWatch.Stop()
$overallElapsed = $overallWatch.Elapsed.TotalSeconds.ToString('F1')

# ── 全局汇总 ──
Write-Banner "全阶段汇总"
Write-Host "  总脚本数: $GlobalTotal | 成功: $GlobalSuccess | 失败: $GlobalFailed | 跳过: $GlobalSkipped | 总耗时: ${overallElapsed}s" -ForegroundColor $(if ($GlobalFailed -gt 0) { 'Red' } else { 'Green' })

if ($GlobalFailedList.Count -gt 0) {
    Write-Host ""
    Write-Host "  ====== FAIL 列表 ======" -ForegroundColor Red
    $GlobalFailedList | ForEach-Object { Write-Host "    ✗ $_" -ForegroundColor Red }
    Write-Host "  ========================" -ForegroundColor Red
    Write-Host ""
    Write-Host "共 $($GlobalFailedList.Count) 个脚本失败，请检查以上 FAIL 列表。" -ForegroundColor Red
    exit 1
} else {
    Write-Host ""
    Write-Host "全部通过 ✓" -ForegroundColor Green
    exit 0
}
