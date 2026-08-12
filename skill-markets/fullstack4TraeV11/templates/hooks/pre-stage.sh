#!/bin/bash
# V11 pre-stage hook: stage 切换前必走
# 调用 stage-gate.py 验证当前状态卡

set -e
STATE_CARD="${STATE_CARD_PATH:-docs/specs/.state-card.md}"
EXPECTED_STAGE="${EXPECTED_STAGE:-}"
python "${V11_SCRIPTS:-~/.trae-cn/skills/fullstack4TraeV11/scripts}/stage-gate.py" \
    --state-card "$STATE_CARD" \
    ${EXPECTED_STAGE:+--stage "$EXPECTED_STAGE"}

echo "✅ pre-stage PASS"