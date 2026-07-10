# gitnexus SessionStart Hook: 索引状态检查
# 会话创建后自动执行，检查 GitNexus 索引是否存在且新鲜
# 如果索引不存在或过时，提示 AI 先运行 npx gitnexus analyze

$projectRoot = Get-Location
$gitnexusDir = Join-Path $projectRoot ".gitnexus"

Write-Output "[GitNexus Index Check]"

# 1. 检查索引是否存在
if (-not (Test-Path $gitnexusDir)) {
    Write-Output "WARNING: GitNexus 索引不存在。请先运行: npx gitnexus analyze"
    Write-Output "提示: GitNexus 技能（exploring/debugging/impact/refactoring）依赖索引才能工作。"
    exit 0
}

# 2. 检查索引新鲜度（通过 gitnexus status）
try {
    $status = npx gitnexus status 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Output "WARNING: GitNexus 索引检查失败。可能需要重新构建: npx gitnexus analyze"
        exit 0
    }

    # 检查是否有过时提示
    if ($status -match 'stale|outdated|过时') {
        Write-Output "WARNING: GitNexus 索引已过时。建议运行: npx gitnexus analyze"
        Write-Output "过时的索引可能导致影响分析和重构结果不准确。"
    } else {
        Write-Output "OK: GitNexus 索引可用。"
    }
} catch {
    Write-Output "WARNING: 无法运行 gitnexus status。请确认 GitNexus MCP Server 已安装。"
}

# 3. 检查是否在 git 仓库中
if (-not (Test-Path (Join-Path $projectRoot ".git"))) {
    Write-Output "NOTE: 当前目录不是 git 仓库。GitNexus 需要 git 仓库才能索引。"
}

exit 0
