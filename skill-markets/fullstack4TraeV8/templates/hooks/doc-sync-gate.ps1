# fullstack DOC SYNC GATE Hook
# 写代码前检查模块文档是否同步（DOC FIRST 铁律 3 的自动化执行）
# V9 NEW: 扩展匹配器覆盖 docs/ 路径 + 产出日志（P2-4 教训：盲区修复）

param(
    [string]$tool_name = $env:TRAE_TOOL_NAME,
    [string]$file_path = $env:TRAE_FILE_PATH
)

# 仅拦截 src/ 源文件写入（编码操作），不拦截 docs/ 文档写入
# DOC SYNC 是编码前置门禁（Phase 6），不是文档写作前置门禁
$isCodeFile = $file_path -match 'src/.*\.(py|ts|tsx|js|jsx|java|go|rs|rb)$'
$isDocFile  = $file_path -match 'docs/.*\.(md)$'

if ($isDocFile -and -not $isCodeFile) {
    exit 0  # 文档写入放行（spec/contract/design 写作不应被 DOC SYNC 门禁拦截）
}

if (-not $isCodeFile) {
    exit 0
}

# 检查是否有活跃变更目录
$changesDir = "docs/specs/changes"
if (-not (Test-Path $changesDir)) {
    exit 0  # 没有活跃变更，放行
}

# V10 NEW: 检查当前相位，仅 Phase 6 (Implement) 触发 DOC SYNC GATE
# 其他相位写代码（如 debugger）放行
$stateCards = Get-ChildItem -Path $changesDir -Directory -ErrorAction SilentlyContinue | ForEach-Object {
    $cardPath = Join-Path $_.FullName ".state-card.md"
    if (Test-Path $cardPath) { $cardPath }
}
$inImplementPhase = $false
foreach ($card in $stateCards) {
    $cardContent = Get-Content $card -Raw -ErrorAction SilentlyContinue
    if ($cardContent -match '当前阶段.*\b(?:6|Implement)\b') {
        $inImplementPhase = $true
        break
    }
}
if (-not $inImplementPhase) {
    exit 0  # 不在 Implement 相位，放行
}

# 检查变更的 tasks.md 状态
$activeChanges = Get-ChildItem -Directory $changesDir -ErrorAction SilentlyContinue
$inProgress = $false
foreach ($change in $activeChanges) {
    $tasksFile = Join-Path $change.FullName "tasks.md"
    if (Test-Path $tasksFile) {
        $content = Get-Content $tasksFile -Raw
        $pending = ([regex]::Matches($content, '- \[ \]')).Count
        if ($pending -eq 0) {
            continue  # 所有任务已完成
        }
        $inProgress = $true
        
        # 检查第一条未完成任务是否标注了 DOC SYNC
        $lines = Get-Content $tasksFile
        $firstPending = $null
        foreach ($line in $lines) {
            if ($line -match '- \[ \] (.+)') {
                $firstPending = $matches[1]
                break
            }
        }
        if ($firstPending -and $firstPending -notmatch 'DOC SYNC|文档同步|CODEMAP') {
            Write-Output "[Fullstack DOC SYNC GATE] 🛑 FAILED: 第一条未完成任务 '$firstPending' 不是 DOC SYNC 步骤"
            Write-Output "DOC FIRST 铁律: 编码前必须先同步模块文档。请先完成 DOC SYNC 任务。"
            Write-Output "参考: references/doc-sync-protocol.md"
            exit 1
        }
    }
}

exit 0
