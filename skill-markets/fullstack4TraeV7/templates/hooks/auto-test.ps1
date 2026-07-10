# fullstack Auto Test Hook（默认启用）
# 编码后自动运行相关测试
# V5.1: 默认 enabled=true（P2-4 教训：关键 hook 不应默认关闭）
# V9 NEW: 产出 Hook 执行日志（自证生效）

param(
    [string]$file_path = $env:TRAE_FILE_PATH
)

# 只处理代码文件
if ($file_path -notmatch 'src/.*\.(py|ts|tsx|js|jsx)$') {
    exit 0
}

# 确定测试命令
$testCmd = $null
if (Test-Path "jest.config.js") { $testCmd = "npx jest --passWithNoTests" }
elseif (Test-Path "vitest.config.ts") { $testCmd = "npx vitest run" }
elseif (Test-Path "pytest.ini" -or (Test-Path "pyproject.toml")) { $testCmd = "pytest --tb=short" }

if (-not $testCmd) {
    exit 0  # 未检测到测试框架
}

Write-Output "[Fullstack Auto Test] Running: $testCmd"
$result = Invoke-Expression $testCmd 2>&1
$exitCode = $LASTEXITCODE

if ($exitCode -ne 0) {
    Write-Output "[Fullstack Auto Test] FAILED (exit code: $exitCode)"
    Write-Output $result
    exit 1
}

Write-Output "[Fullstack Auto Test] PASSED"

# === V5.0 新增：TDD RED/GREEN 标记会话输出检查（警告级）===
# 本 Hook 作为 PostToolUse 在编码后触发，但无法访问 AI 会话历史，
# 无法直接验证"先 RED 后 GREEN"的 TDD 节奏是否被遵守。
# 以下为检查逻辑说明，由 agent 在会话内自检或由 reviewer 在验收时核验：
#
# 检查点 1 (RED 标记): 本次编辑对应的测试文件，是否在会话中先以失败状态输出过
#   - 期望会话中出现类似 "FAIL tests/xxx.test.ts" 或 "AssertionError" 的 RED 信号
#   - 若会话中从未出现该测试的失败输出，判定为"跳过 RED"，发警告
#
# 检查点 2 (GREEN 标记): 本次编辑后测试通过，是否在会话中输出过 GREEN 信号
#   - 期望会话中出现类似 "PASS tests/xxx.test.ts" 或 "✓ ..." 的 GREEN 信号
#   - 若本次测试结果为 PASS 但会话历史中无对应 GREEN 输出，判定为"GREEN 缺失"，发警告
#
# 检查点 3 (RED→GREEN 顺序): RED 必须出现在 GREEN 之前
#   - 若 GREEN 输出时间戳早于 RED，判定为"顺序倒置"，发警告
#
# 实现约束：PowerShell 无法读取会话历史，上述检查由 agent 自检完成。
# 本 Hook 仅在测试通过后输出以下提醒，触发 agent 自检：
Write-Output "[Fullstack Auto Test] ⚠️ TDD 自检提醒: 请确认本次编辑遵循 RED→GREEN 节奏"
Write-Output "   - 会话中是否先输出过测试失败 (RED)？"
Write-Output "   - 本次 PASS 是否为 GREEN 信号？"
Write-Output "   - 若跳过 RED 直接 GREEN，违反 TDD 铁律，请补 RED 证据"
# =========================================================

exit 0
