<#
pre-release.ps1 — skill-acceptance pre-release hook (PowerShell 5.1+)
#
# 触发时机：git tag 推送 / release 创建 / GitHub Actions workflow_dispatch
# 调 verify.py 逐个跑 skill-markets/ 下每个 skill 的 6 项检查
#
# 用法:
#   pre-release.ps1 [-Skill <name>]... [-Force] [-Help]
#
# 环境变量:
#   SKIP_SKILL_ACCEPTANCE=1  跳过校验（CI 调试用）
#   NO_COLOR=1              关闭 ANSI 颜色
#
# 退出码（与 sh 镜像）:
#   0  全部 PASS
#   1  任意 BLOCK（阻断 release）
#   2  >=3 WARN（可用 -Force 忽略）
#   3  参数错误 / verify.py 缺失
#
# 兼容性：PowerShell 5.1+（不用 ?:, 不用 null-coalescing ??）
#>

[CmdletBinding()]
param(
    [Parameter(ValueFromRemainingArguments=$false)]
    [string[]]$Skill,
    [switch]$Force,
    [switch]$Help
)

$ErrorActionPreference = 'Stop'

# ---------- 帮助 ----------
function Print-Help {
@'
pre-release.ps1 - skill-acceptance pre-release hook (Windows)

用法:
    pre-release.ps1 [-Skill <name>]... [-Force] [-Help]

参数:
    -Skill <name>   指定要验收的 skill 名（可重复；默认扫描 skill-markets/ 全量）
    -Force          强制忽略 WARN 阈值（不忽略 BLOCK）
    -Help           显示本帮助

退出码:
    0  全部 PASS
    1  任意 BLOCK（阻断 release）
    2  >=3 WARN（可用 -Force 忽略）
    3  参数错误 / verify.py 缺失
'@
}

if ($Help) {
    Print-Help
    exit 0
}

# ---------- 颜色（NO_COLOR 兜底） ----------
if ($env:NO_COLOR) {
    $script:C_RED = ""
    $script:C_GREEN = ""
    $script:C_YELLOW = ""
    $script:C_RESET = ""
} else {
    $script:C_RED = [char]27 + "[31m"
    $script:C_GREEN = [char]27 + "[32m"
    $script:C_YELLOW = [char]27 + "[33m"
    $script:C_RESET = [char]27 + "[0m"
}

# ---------- SKIP 快速通道 ----------
if ($env:SKIP_SKILL_ACCEPTANCE -eq "1") {
    Write-Host "${C_YELLOW}⏭ SKIP_SKILL_ACCEPTANCE=1,跳过 skill 验收${C_RESET}"
    exit 0
}

# ---------- 路径定位 ----------
# 钩子位于 <skill-acceptance>/hooks/pre-release.ps1
$HookPath = Split-Path -Parent $MyInvocation.MyCommand.Path
$SkillRoot = Split-Path -Parent $HookPath
$ProjectRoot = Split-Path -Parent $SkillRoot

$VerifyPy = Join-Path $SkillRoot "scripts/verify.py"
if (-not (Test-Path $VerifyPy)) {
    Write-Host "${C_RED}🛑 verify.py 不存在: $VerifyPy${C_RESET}" -ForegroundColor Red 2>$null
    Write-Host "${C_RED}   请先实施 scripts/verify.py(本钩子不创建该文件)${C_RESET}" 2>$null
    exit 3
}

# ---------- 收集 skill 列表 ----------
if (-not $Skill -or $Skill.Count -eq 0) {
    $SkillsDir = Join-Path $ProjectRoot "skill-markets"
    if (-not (Test-Path $SkillsDir)) {
        Write-Host "${C_RED}🛑 skill-markets/ 目录不存在: $SkillsDir${C_RESET}" 2>$null
        exit 3
    }
    $script:Skills = @()
    Get-ChildItem -Path $SkillsDir -Directory | ForEach-Object {
        $script:Skills += $_.Name
    }
} else {
    $script:Skills = $Skill
}

$Total = 0
$PassCount = 0
$WarnCount = 0
$BlockCount = 0
$ExitCode = 0

Write-Host "${C_GREEN}==================================================${C_RESET}"
Write-Host "${C_GREEN} skill-acceptance pre-release (PowerShell)${C_RESET}"
Write-Host "${C_GREEN} target skills:${C_RESET} $($script:Skills -join ', ')"
Write-Host "${C_GREEN}==================================================${C_RESET}"

# ---------- 报告暂存 ----------
$ReportDir = Join-Path $SkillRoot ".reports"
if (-not (Test-Path $ReportDir)) {
    New-Item -ItemType Directory -Path $ReportDir | Out-Null
}
$Ts = Get-Date -AsUTC -Format "yyyyMMddTHHmmssZ"
$ReportFile = Join-Path $ReportDir "pre-release-${Ts}.json"

# ---------- 逐 skill 调 verify.py ----------
foreach ($skill in $script:Skills) {
    $Total++
    $Target = Join-Path $ProjectRoot "skill-markets/$skill"
    Write-Host ""
    Write-Host "${C_GREEN}▶ [$Total] $skill${C_RESET}"

    if (-not (Test-Path $Target)) {
        Write-Host "${C_RED}  ✗ 目录不存在: $Target${C_RESET}"
        $BlockCount++
        $ExitCode = 1
        continue
    }

    # 调 verify.py 单一 skill
    $stdoutFile = [System.IO.Path]::GetTempFileName()
    $stderrFile = [System.IO.Path]::GetTempFileName()
    try {
        # PowerShell 5.1 不支持 null-coalescing ??；用 -ne 判断
        $proc = Start-Process -FilePath "python" `
            -ArgumentList @($VerifyPy, "--target", $skill, "--json", "--report", $ReportFile, "--project-root", $ProjectRoot) `
            -NoNewWindow -Wait -PassThru `
            -RedirectStandardOutput $stdoutFile `
            -RedirectStandardError $stderrFile
        $rc = $proc.ExitCode
        $out = (Get-Content $stdoutFile -Raw -ErrorAction SilentlyContinue)
        $err = (Get-Content $stderrFile -Raw -ErrorAction SilentlyContinue)
    } catch {
        Write-Host "${C_RED}  ✗ python 调用失败: $($_.Exception.Message)${C_RESET}"
        $BlockCount++
        $ExitCode = 1
        continue
    } finally {
        Remove-Item -Force $stdoutFile, $stderrFile -ErrorAction SilentlyContinue
    }

    # 解析退出码语义
    switch ($rc) {
        0 {
            Write-Host "${C_GREEN}  ✓ PASS${C_RESET}"
            $PassCount++
        }
        { $_ -eq 1 -or $_ -eq 2 } {
            $WarnCount++
            Write-Host "${C_YELLOW}  ⚠ WARN (exit=$rc)${C_RESET}"
            if ($out) { Write-Host ("    " + ($out -replace "`r?`n", "`n    ")) }
        }
        default {
            $BlockCount++
            $ExitCode = 1
            Write-Host "${C_RED}  ✗ BLOCK (exit=$rc)${C_RESET}"
            if ($out) { Write-Host ("    " + ($out -replace "`r?`n", "`n    ")) }
            if ($err) { Write-Host ("    [stderr] " + ($err -replace "`r?`n", "`n    [stderr] ")) }
        }
    }
}

# ---------- 阈值判断 ----------
if ($WarnCount -ge 3 -and -not $Force.IsPresent) {
    if ($ExitCode -eq 0) {
        $ExitCode = 2
    }
}
if ($Force.IsPresent -and $ExitCode -eq 2) {
    Write-Host ""
    Write-Host "${C_YELLOW}⚠ -Force:忽略 WARN 阈值警告${C_RESET}"
    $ExitCode = 0
}

# ---------- 报告 ----------
Write-Host ""
Write-Host "${C_GREEN}==================================================${C_RESET}"
Write-Host "${C_GREEN} 验收报告${C_RESET}"
Write-Host "  total : $Total"
Write-Host "  ${C_GREEN}PASS${C_RESET}  : $PassCount"
Write-Host "  ${C_YELLOW}WARN${C_RESET}  : $WarnCount"
Write-Host "  ${C_RED}BLOCK${C_RESET} : $BlockCount"
Write-Host "  report: $ReportFile"
Write-Host "${C_GREEN}==================================================${C_RESET}"

exit $ExitCode
