# fullstack Complexity Guard Hook（可选启用）
# 用户提交 prompt 时，评估需求复杂度，建议是否需要走 fullstack 流程
# 默认 disabled，用户按需开启

# 简单关键词检测（可扩展为更复杂的分析）
$userPrompt = Get-Content $env:TRAE_USER_PROMPT -Raw -ErrorAction SilentlyContinue
if (-not $userPrompt) { exit 0 }

Write-Output "[Fullstack Complexity Guard] Evaluating prompt complexity..."

$score = 0
$signals = @()

# 检测复杂度信号
if ($userPrompt -match '(?i)refactor|重构|重写|rewrite') {
    $score += 3
    $signals += "重构"
}
if ($userPrompt -match '(?i)architecture|架构|database.*schema|数据.*迁移') {
    $score += 3
    $signals += "架构级变更"
}
if ($userPrompt -match '(?i)new.*feature|新功能|add.*support|integrate|集成') {
    $score += 2
    $signals += "新功能"
}
if ($userPrompt -match '(?i)multiple.*module|跨.*模块|several.*file|多.*文件') {
    $score += 2
    $signals += "多模块涉及"
}
if ($userPrompt -match '(?i)security|auth|permission|安全|权限|认证') {
    $score += 2
    $signals += "安全相关"
}
if ($userPrompt -match '(?i)api.*change|breaking|接口.*变更|contract|契约') {
    $score += 2
    $signals += "接口变更"
}

if ($score -ge 3) {
    Write-Output "[Fullstack Complexity Guard] 复杂度评估: HIGH (score: $score)"
    Write-Output "  信号: $($signals -join ', ')"
    Write-Output "  建议: 走 fullstack 完整流程 (proposal → spec → design → tasks → tdd → review → accept)"
} elseif ($score -ge 1) {
    Write-Output "[Fullstack Complexity Guard] 复杂度评估: MEDIUM (score: $score)"
    Write-Output "  信号: $($signals -join ', ')"
    Write-Output "  建议: 至少写 proposal + spec"
} else {
    Write-Output "[Fullstack Complexity Guard] 复杂度评估: LOW"
    Write-Output "  建议: 用 ponytail 懒人模式（最简实现），不需要走完整 fullstack 流程"
}

exit 0
