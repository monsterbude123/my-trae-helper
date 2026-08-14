#!/usr/bin/env bash
# skills-security-scan install.sh — DEPRECATED 2026-08-14
# 已并入 trae-security-review。改用：
#   node ${MY_TRAE_HELPER}/bin/cli.mjs add trae-security-review -a trae-cn
set -euo pipefail

echo "[DEPRECATED] skills-security-scan 已并入 trae-security-review。" >&2
echo "请改用：" >&2
echo "  node \${MY_TRAE_HELPER}/bin/cli.mjs add trae-security-review -a trae-cn" >&2
exit 64  # EX_USAGE
