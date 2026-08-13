#!/bin/bash
# V11.3 stage-gate-pre-stage.sh - husky 式硬阻断门禁
# stage 切换前必跑 stage-gate.py + state-card-validator.py
# opt-in: 独立于 V11 pre-stage.sh, 作为 V11.3 增强门禁
# 用法: bash templates/hooks/stage-gate-pre-stage.sh
# 环境变量: STATE_CARD_PATH / EXPECTED_STAGE / V11_SCRIPTS
# chmod +x templates/hooks/stage-gate-pre-stage.sh

STATE_CARD="${STATE_CARD_PATH:-docs/specs/.state-card.md}"
EXPECTED_STAGE="${EXPECTED_STAGE:-}"
V11_SCRIPTS="${V11_SCRIPTS:-$(cd "$(dirname "$0")/../../scripts" && pwd)}"

# 1. stage-gate.py 阶段门禁校验
python "$V11_SCRIPTS/stage-gate.py" \
    --state-card "$STATE_CARD" \
    ${EXPECTED_STAGE:+--stage "$EXPECTED_STAGE"}
if [ $? -ne 0 ]; then
    echo "🛑 BLOCKED: stage-gate.py FAIL"
    exit 1
fi

# 2. state-card-validator.py 字段完整性校验
python "$V11_SCRIPTS/state-card-validator.py" "$STATE_CARD"
if [ $? -ne 0 ]; then
    echo "🛑 BLOCKED: state-card-validator.py FAIL"
    exit 1
fi

echo "✅ PASS"
exit 0
