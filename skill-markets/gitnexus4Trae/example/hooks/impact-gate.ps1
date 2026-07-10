# gitnexus PreToolUse Hook: 代码修改影响分析门禁
# 在 Write/Edit 工具调用前自动触发
# 检查即将修改的文件是否在索引中，如果是则提醒 AI 先做影响分析
# 不会阻断执行（exit 0），仅输出提醒信息

param(
    [string]$tool_name = $env:TRAE_TOOL_NAME,
    [string]$file_path = $env:TRAE_FILE_PATH
)

# 只检查源代码文件
if ($file_path -notmatch '\.(py|ts|tsx|js|jsx|java|go|rs|rb|c|cpp|h|hpp|cs|swift|kt)$') {
    exit 0
}

# 跳过测试文件和配置文件（低风险修改）
if ($file_path -match '(test|spec|__tests__|\.test\.|\.spec\.)' -or
    $file_path -match '(config|\.config|\.rc|setup)\.(py|ts|js|json|yaml|yml)$') {
    exit 0
}

# 跳过新增文件（不影响已有代码）
if ($tool_name -eq "Write" -and -not (Test-Path $file_path)) {
    exit 0
}

# 检查 GitNexus 索引是否存在
$gitnexusDir = Join-Path (Get-Location) ".gitnexus"
if (-not (Test-Path $gitnexusDir)) {
    exit 0  # 没有索引，不干预
}

Write-Output "[GitNexus Impact Gate] 修改源代码文件: $file_path"
Write-Output "提醒: 修改前建议先做影响分析。"
Write-Output "  run_mcp({server_name: 'gitnexus', tool_name: 'impact', args: {target: '<symbol>', direction: 'upstream'}})"
Write-Output "  或: run_mcp({server_name: 'gitnexus', tool_name: 'detect_changes', args: {}})"

exit 0
