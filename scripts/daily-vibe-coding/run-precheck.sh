#!/usr/bin/env bash
# run-precheck.sh — 跑 daily-vibe-coding 前的一键基线采集
#
# 用法:
#   bash scripts/daily-vibe-coding/run-precheck.sh
#   bash scripts/daily-vibe-coding/run-precheck.sh --no-scan --history 2026-08-13
#
# 输出: logs/daily-vibe-coding/<today>/_baseline.json
# 下一步: agent 直接读 _baseline.json, 不再重复跑命令

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# 探测 Python(Windows + Git Bash 兼容)
PY=""
for cand in /c/ProgramData/miniconda3/python.exe \
            /mnt/c/ProgramData/miniconda3/python.exe \
            python3 py python; do
  if command -v "$cand" >/dev/null 2>&1; then
    PY="$cand"
    break
  fi
done

if [ -z "$PY" ]; then
  echo "[run-precheck] FATAL: python not found"
  exit 1
fi

echo "[run-precheck] python=$PY root=$ROOT"
cd "$ROOT"
exec "$PY" "$SCRIPT_DIR/collect-baseline.py" "$@"