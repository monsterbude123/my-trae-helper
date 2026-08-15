#!/usr/bin/env bash
# V11 Launch Guard — 运行 stage 前必跑的自校验兜底
# 检测 Git 钩子层是否就绪，未就绪即阻断，防止在门禁失效时干活
set -u

PROJECT_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
cd "$PROJECT_ROOT"
FAILURES=0

echo "==> [V11 Launch Guard] Pre-stage self-check (cannot be bypassed)"

# 1. Git 钩子层就绪性（Gate 唯一宿主）
echo "  [1/3] Git hook layer readiness:"
if [ -d .husky ] && [ -f .husky/pre-commit ] && [ -f .husky/pre-push ]; then
    echo "      ✓ .husky/pre-commit + pre-push present"
else
    echo "      ✗ Gate layer NOT ready — .husky 缺失"
    echo "        Fix: bash scripts/install-hooks.py --project-root .  (或参照 scaffolds)"
    FAILURES=$((FAILURES + 1))
fi

# 2. 状态卡定位（新路径优先）
echo "  [2/3] State card resolution:"
STATE_CARD="${STATE_CARD_PATH:-}"
if [ -z "$STATE_CARD" ]; then
    STATE_CARD="$(find docs/specs/changes -name .state-card.md 2>/dev/null | head -1)"
fi
if [ -z "$STATE_CARD" ] && [ -f docs/specs/.state-card.md ]; then
    STATE_CARD="docs/specs/.state-card.md"
fi
if [ -n "$STATE_CARD" ]; then
    echo "      ✓ state card: $STATE_CARD"
else
    echo "      ✗ state card NOT found — 先跑 intake 初始化"
    FAILURES=$((FAILURES + 1))
fi

# 3. 关键脚本可达性
echo "  [3/3] Required scripts reachability:"
for s in stage-gate.py phase-gate.py; do
    if python3 -c "import pathlib,sys; sys.exit(0 if pathlib.Path('$s').exists() or pathlib.Path('scripts/$s').exists() else 1)" 2>/dev/null; then
        echo "      ✓ $s reachable"
    else
        echo "      ✗ $s missing (scripts/ 需包含)"
        FAILURES=$((FAILURES + 1))
    fi
done

if [ $FAILURES -gt 0 ]; then
    echo ""
    echo "==> [V11 Launch Guard] BLOCKED ($FAILURES check(s) failed)"
    echo "    Gate layer not ready — 禁止继续 stage"
    exit 1
fi
echo ""
echo "==> [V11 Launch Guard] PASSED"
exit 0