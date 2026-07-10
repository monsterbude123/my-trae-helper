# gitnexus Stop Hook: 会话结束前变更验证
# 在智能体完成任务后自动触发
# 检查当前 git 变更的影响范围，确保没有意外破坏

$projectRoot = Get-Location
$gitnexusDir = Join-Path $projectRoot ".gitnexus"

Write-Output "[GitNexus Changes Verify]"

# 1. 检查是否有 git 变更
try {
    $gitStatus = git status --porcelain 2>&1
    if (-not $gitStatus) {
        Write-Output "OK: 无代码变更。"
        exit 0
    }

    $changedFiles = ($gitStatus | Where-Object { $_ -match '^\s*[MADRC]' }).Count
    Write-Output "检测到 $changedFiles 个文件变更。"
} catch {
    Write-Output "NOTE: 无法检查 git 状态。"
    exit 0
}

# 2. 如果有 GitNexus 索引，运行 detect_changes
if (-not (Test-Path $gitnexusDir)) {
    Write-Output "NOTE: GitNexus 索引不存在，跳过影响分析。"
    exit 0
}

# 提醒 AI 运行 detect_changes 验证影响范围
Write-Output "建议运行变更验证:"
Write-Output "  run_mcp({server_name: 'gitnexus', tool_name: 'detect_changes', args: {scope: 'all'}})"
Write-Output "验证受影响的执行流和风险等级，确保改动在预期范围内。"

exit 0
