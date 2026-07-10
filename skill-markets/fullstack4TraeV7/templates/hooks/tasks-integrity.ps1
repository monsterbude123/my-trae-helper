# fullstack Tasks Integrity Hook
# 任务结束时检查 tasks.md 所有任务是否已完成 ([x])
# 触发时机: Stop 事件
#
# === V5.0 升级（2026-06）===
# 新增：证据强制检查
# tasks.md 里的 [x] 项必须能匹配到证据标注（commit hash 或 test output），
# 否则发出警告。证据标注格式：
#   - commit hash: 7-40 位十六进制（如 abc1234）
#   - test output: tests/xxx.test.ts 路径引用 或 [test:passed] 标记
# ===========================

$projectRoot = Get-Location
$changesDir = Join-Path $projectRoot "docs/specs/changes"

if (-not (Test-Path $changesDir)) {
    exit 0
}

$allOk = $true
$activeChanges = Get-ChildItem -Directory $changesDir -ErrorAction SilentlyContinue

foreach ($change in $activeChanges) {
    $tasksFile = Join-Path $change.FullName "tasks.md"
    if (-not (Test-Path $tasksFile)) { continue }
    
    $content = Get-Content $tasksFile -Raw
    $pending = ([regex]::Matches($content, '- \[ \]')).Count
    $completed = ([regex]::Matches($content, '- \[x\]')).Count
    $total = $pending + $completed
    
    if ($pending -gt 0) {
        $allOk = $false
        Write-Output "[Fullstack Tasks Integrity] $($change.Name): $completed/$total done ($pending pending)"
        
        # 列出未完成任务
        $lines = Get-Content $tasksFile
        $count = 0
        foreach ($line in $lines) {
            if ($line -match '- \[ \] (.+)') {
                $count++
                Write-Output "  - [ ] $($matches[1])"
            }
        }
    } else {
        Write-Output "[Fullstack Tasks Integrity] $($change.Name): ALL DONE ($completed/$total)"
    }

    # === V5.0 新增：证据强制检查 ===
    # 检查每个 [x] 项是否带有证据标注（commit hash 或 test output）
    # 证据模式：
    #   1. commit hash: 7-40 位十六进制字符（git short/long hash）
    #   2. test output: tests/xxx.test.{ts,js,py} 路径引用
    #   3. 显式标记: [test:passed] / [evidence:...] / <!-- evidence -->
    $evidencePattern = '(?:\b[0-9a-f]{7,40}\b|tests/\S+\.test\.\w+|\[test:passed\]|\[evidence:[^\]]*\]|<!--\s*evidence)'
    $lines = Get-Content $tasksFile
    $missingEvidence = @()
    foreach ($line in $lines) {
        if ($line -match '- \[x\]') {
            if ($line -notmatch $evidencePattern) {
                # 提取任务描述（去掉 [x] 前缀，截断过长内容）
                $desc = ($line -replace '- \[x\]\s*', '').Trim()
                if ($desc.Length -gt 60) { $desc = $desc.Substring(0, 60) + "..." }
                $missingEvidence += $desc
            }
        }
    }
    if ($missingEvidence.Count -gt 0) {
        Write-Output "[Fullstack Tasks Integrity] ⚠️ $($change.Name): $($missingEvidence.Count) 个已完成任务缺少证据标注"
        foreach ($desc in $missingEvidence) {
            Write-Output "   - [x] $desc  ← 需补 commit hash 或 test output 引用"
        }
        Write-Output "   证据格式示例: '- [x] 实现 X <!-- abc1234 -->' 或 '- [x] 实现 X [test:passed]'"
    }
    # ==============================
}

if (-not $allOk) {
    Write-Output ""
    Write-Output "[Fullstack] 提醒: 有未完成的任务。铁律 5: 验收不通过不算完成。"
}

exit 0  # 不阻断，仅提醒
