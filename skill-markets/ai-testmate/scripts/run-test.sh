#!/usr/bin/env bash
# ai-testmate 一键入口
# 跨平台:Bash(Git Bash / macOS / Linux)+ PowerShell 适配(Windows)
# 时间戳强制(AP-7)

set -euo pipefail

# === 跨平台 Python 探测 ===
SCRIPT_DIR="$(cd "$(dirname "${0}")" && pwd)"
if [ -f "$SCRIPT_DIR/detect-python.sh" ]; then
  # shellcheck disable=SC1091
  source "$SCRIPT_DIR/detect-python.sh"
else
  echo "[FATAL] detect-python.sh 不存在,违反 AP-6 跨平台铁律"
  exit 2
fi

# === 时间戳(AP-7)===
TIMESTAMP="$(date +%Y%m%d_%H%M%S)"

# === 工作空间探测(v1.2:自动从 cwd 向上找 .agents/.env)===
DETECT_JSON="$("$MY_TRAE_HELPER_PY" "$SCRIPT_DIR/workspace-detect.py" --start "$(pwd)" --json 2>/dev/null || true)"
if [ -z "$DETECT_JSON" ]; then
  # 探测失败:回退到 env 注入(AP-1)
  WORKSPACE_ROOT="${TESTMATE_WORKSPACE_ROOT:-$(pwd)}"
  DETECTED_MODE="env-fallback"
else
  WORKSPACE_ROOT="$(echo "$DETECT_JSON" | grep -oP '"workspace_root"\s*:\s*"\K[^"]+' || echo "$(pwd)")"
  DETECTED_MODE="$(echo "$DETECT_JSON" | grep -oP '"detected_mode"\s*:\s*"\K[^"]+' || echo 'unknown')"
fi
REPORT_DIR="${TESTMATE_REPORT_DIR:-$WORKSPACE_ROOT/reports/$TIMESTAMP}"

echo "=== ai-testmate run ==="
echo "  timestamp:    $TIMESTAMP"
echo "  workspace:    $WORKSPACE_ROOT"
echo "  detect_mode:  $DETECTED_MODE"
echo "  report:       $REPORT_DIR"

# === 守卫自检(AGENTS.md §2.4 Gate 自验收)===
"$MY_TRAE_HELPER_PY" "$SCRIPT_DIR/publish-protocol.py"
"$MY_TRAE_HELPER_PY" "$SCRIPT_DIR/ai-testmate-guard.py"

# === 准备报告目录 ===
mkdir -p "$REPORT_DIR/screenshots"

# === 占位实现 ===
# 实际流水线由主代理编排 5 个 agent:
#   planner → credential-keeper → [api-tester ∥ ui-tester] → reporter
# 本脚本仅作为入口与时间戳守护者

echo "[INFO] 5-agent 流水线由主代理编排,本脚本仅做守卫 + 时间戳守护"
echo "[INFO] 完整流水线请参见 references/workflow.md"
echo "✅ 入口成功"

exit 0
