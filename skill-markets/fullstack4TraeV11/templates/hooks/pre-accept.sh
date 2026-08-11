#!/bin/bash
# V11 pre-accept hook: Stage 5 Accept 前必跑 Stage 4.5 rot-scan
set -e

CHANGE_ID="${CHANGE_ID:-}"
if [ -z "$CHANGE_ID" ]; then
    echo "❌ 缺 CHANGE_ID env"
    exit 1
fi

python "${V11_SCRIPTS:-~/.trae-cn/skills/fullstack4TraeV11/scripts}/phase-gate.py" \
    --state-card "docs/specs/changes/${CHANGE_ID}/.state-card.md" \
    --verify-rot-scan \
    --change-id "$CHANGE_ID"

echo "✅ pre-accept PASS"