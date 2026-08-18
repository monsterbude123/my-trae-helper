#!/usr/bin/env bash
# close-bug.sh — bug-hunt 三文件状态同步回写（V12.0.0 UPDATE Stage 6 Phase B Step 7）
#
# 用法: bash scripts/bug-hunt/close-bug.sh BUG-017 <agent-id>
# 三文件同步(V12 多卡):
#   1. docs/bugs/<YYYY-MM-DD>/<BUG-NNN>-<module>.md  status: OPEN → FIXED
#   2. docs/bugs/index.md                            BUG-NNN | OPEN → | FIXED (timestamp)
#   3. stage/6/bug-fix/.state-card.md(V12 多卡)     BUG-NNN: OPEN → BUG-NNN: FIXED
#
# V12.0.0 UPDATE: 旧 V11 扁平路径(V12 永久废弃) → stage/6/bug-fix/.state-card.md(V12 物理布局)
# 反 V11-BH4 反例: 修复后 status 未回写 → 主代理二次误判。
#
# 校验命令（必 0 命中）:
#   grep -l "^| status | OPEN" docs/bugs/<date>/BUG-*.md
#   grep -lE "^\s*-\s*\[" docs/bugs/index.md | xargs grep -L "FIXED"

set -euo pipefail

if [[ $# -lt 1 ]]; then
    echo "[FATAL] 用法: bash $0 <bug_id> [agent_id]" >&2
    echo "  示例: bash $0 BUG-017 sub-agent-bug-fix-01" >&2
    exit 1
fi

BUG_ID="$1"
AGENT_ID="${2:-unknown-agent}"
TIMESTAMP=$(TZ=Asia/Shanghai date +"%Y-%m-%dT%H:%M:%S+08:00")

# 查找 bug 单文件
BUG_FILE=$(ls docs/bugs/*/${BUG_ID}-*.md 2>/dev/null | head -n 1 || true)

if [[ -z "$BUG_FILE" ]]; then
    echo "[FATAL] bug 单文件未找到: ${BUG_ID}-*.md" >&2
    exit 1
fi

echo "[INFO] 操作文件: $BUG_FILE"

# 1. bug 单 .md status: OPEN → FIXED
if grep -q "^| status | OPEN" "$BUG_FILE"; then
    sed -i.bak "s/^| status | OPEN|/| status | FIXED (${TIMESTAMP} by ${AGENT_ID}) |/" "$BUG_FILE"
    rm -f "${BUG_FILE}.bak"
    echo "[OK] bug 单 status → FIXED"
else
    echo "[WARN] bug 单 status 不是 OPEN（可能已回写或未对齐）, 跳过"
fi

# 2. docs/bugs/index.md 同步
INDEX_FILE="docs/bugs/index.md"
if [[ -f "$INDEX_FILE" ]]; then
    if grep -qE "^\|?\s*${BUG_ID}\s*\|\s*OPEN" "$INDEX_FILE"; then
        sed -i.bak "s/^| ${BUG_ID} | OPEN/| ${BUG_ID} | FIXED (${TIMESTAMP}) |/" "$INDEX_FILE"
        rm -f "${INDEX_FILE}.bak"
        echo "[OK] docs/bugs/index.md 同步"
    fi
fi

# 3. stage/6/bug-fix/.state-card.md 同步(V12 多卡)
STATE_FILE="stage/6/bug-fix/.state-card.md"
if [[ -f "$STATE_FILE" ]]; then
    if grep -qE "^${BUG_ID}: OPEN" "$STATE_FILE"; then
        sed -i.bak "s/^${BUG_ID}: OPEN/${BUG_ID}: FIXED (${TIMESTAMP})/" "$STATE_FILE"
        rm -f "${STATE_FILE}.bak"
        echo "[OK] stage/6/bug-fix/.state-card.md 同步"
    fi
fi

# 4. 反向校验（自验收）
echo ""
echo "[VERIFY] 反向校验（应 0 命中）:"
if grep -l "^| status | OPEN" "$BUG_FILE" > /dev/null 2>&1; then
    echo "  [FAIL] bug 单仍含 status: OPEN"
    exit 1
fi
if [[ -f "$INDEX_FILE" ]]; then
    if grep -E "^\|?\s*${BUG_ID}\s*\|\s*OPEN" "$INDEX_FILE" > /dev/null 2>&1; then
        echo "  [FAIL] docs/bugs/index.md 仍含 OPEN"
        exit 1
    fi
fi

echo "  [PASS] 三文件状态同步成功"
echo ""
echo "[DONE] ${BUG_ID} → FIXED (${TIMESTAMP} by ${AGENT_ID})"