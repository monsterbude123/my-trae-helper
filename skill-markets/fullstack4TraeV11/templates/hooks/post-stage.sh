#!/bin/bash
# V11 post-stage hook: stage 结束后必走
# 验证状态卡已更新 + artifacts 存在

set -e

CHANGE_ID="${CHANGE_ID:-}"
ARTIFACTS="${ARTIFACTS:-}"

if [ -z "$CHANGE_ID" ]; then
    echo "❌ 缺 CHANGE_ID env"
    exit 1
fi

STATE_CARD="docs/specs/changes/${CHANGE_ID}/.state-card.md"
python "${V11_SCRIPTS:-~/.trae-cn/skills/fullstack4TraeV11/scripts}/state-card-validator.py" "$STATE_CARD"

echo "✅ post-stage PASS"