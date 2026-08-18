#!/usr/bin/env bash
# V12 Pre-push Gate (HARDENED) — Stage 3 implement + 3.5 real-verify
# HARDENING POINTS:
#   1. set -euo pipefail (fail-fast + pipe error propagation)
#   2. All required files/scripts MUST exist — no assumptions
#   3. Detect echo-skip anti-pattern (placeholder scripts)
#   4. Real execution — no mock/stub PASS allowed
#   5. V12 物理布局: push 前 stage/3/implement + stage/3.5/real-verify 状态卡必存

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
GATE_ID="L2-pre-push-$(date +%Y%m%d%H%M%S)"
FAILURES=0

echo "==> [V12 Gate L2] Pre-push hardened gate (Stage 3 implement + 3.5 real-verify)"
echo "    Gate ID: $GATE_ID"

cd "$PROJECT_ROOT"

# ---- Step 0: Environment validation (V12_GATE_ENFORCED) ----
if [ -z "${V12_GATE_ENFORCED:-}" ]; then
    export V12_GATE_ENFORCED="true"
    export V12_GATE_STAGE="3.5/real-verify"
    export V12_GATE_CALLER="pre-push-hardened.sh"
    echo "    [0/6] Environment: V12_GATE_ENFORCED=true (auto-set)"
else
    echo "    [0/6] Environment: V12_GATE_ENFORCED=${V12_GATE_ENFORCED}"
fi

# ---- Step 1: Required files existence check ----
echo ""
echo "    [1/6] Required files existence check:"

REQUIRED_FILES=("AGENTS.md" "package.json")
MISSING_FILES=()

for file in "${REQUIRED_FILES[@]}"; do
    if [ ! -f "$PROJECT_ROOT/$file" ]; then
        echo "          [$file] ✗ MISSING — gate fails"
        MISSING_FILES+=("$file")
        FAILURES=$((FAILURES + 1))
    else
        echo "          [$file] ✓ exists"
    fi
done

if [ $FAILURES -gt 0 ]; then
    echo ""
    echo "    🛑 Gate FAIL: ${FAILURES} required file(s) missing"
    exit $FAILURES
fi

# ---- Step 2: Required scripts existence + echo-skip detection ----
echo ""
echo "    [2/6] Required scripts existence + echo-skip detection:"

REQUIRED_SCRIPTS=("test:integration" "build")
MISSING_SCRIPTS=()

has_script() {
    local name="$1"
    python3 - "$name" <<'PYEOF' 2>/dev/null
import json, sys
try:
    with open('package.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    scripts = (data.get('scripts') or {})
    name = sys.argv[1]
    sys.exit(0 if name in scripts else 1)
except Exception:
    sys.exit(1)
PYEOF
}

for script in "${REQUIRED_SCRIPTS[@]}"; do
    if has_script "$script"; then
        body=$(python3 -c "import json; print(json.load(open('package.json')).get('scripts',{}).get('$script',''))" 2>/dev/null)
        if echo "$body" | grep -qiE '^[[:space:]]*echo[[:space:]]+["'"'"']?(skip|not|skipp)'; then
            echo "          [$script] ✗ ECHO-SKIP DETECTED — gate rejects placeholder"
            MISSING_SCRIPTS+=("$script")
            FAILURES=$((FAILURES + 1))
        else
            echo "          [$script] ✓ script exists (no echo-skip)"
        fi
    else
        echo "          [$script] ✗ MISSING — gate fails"
        MISSING_SCRIPTS+=("$script")
        FAILURES=$((FAILURES + 1))
    fi
done

if [ $FAILURES -gt 0 ]; then
    echo ""
    echo "    🛑 Gate FAIL: ${FAILURES} required script(s) missing or invalid"
    echo ""
    echo "    Fix: add real implementation to package.json 'scripts'."
    echo "    Forbidden: 'echo \"skipping ...\"' placeholders."
    exit $FAILURES
fi

# ---- Step 3: V12 stage 3 + 3.5 state card 强制存在性校验 ----
echo ""
echo "    [3/6] V12 stage 3 + 3.5 state card 强制校验:"

# V12 唯一布局: push 前 stage/3/implement + stage/3.5/real-verify 状态卡必存
IMPLEMENT_CARD="$PROJECT_ROOT/stage/3/implement/.state-card.md"
REAL_VERIFY_CARD="$PROJECT_ROOT/stage/3.5/real-verify/.state-card.md"

if [ ! -f "$IMPLEMENT_CARD" ]; then
    echo "          ✗ V12 stage 3 implement card NOT FOUND: $IMPLEMENT_CARD"
    echo "          Push 前 stage/3/implement/.state-card.md 必须存在"
    FAILURES=$((FAILURES + 1))
else
    echo "          ✓ stage/3/implement/.state-card.md exists"
fi

if [ ! -f "$REAL_VERIFY_CARD" ]; then
    echo "          ✗ V12 stage 3.5 real-verify card NOT FOUND: $REAL_VERIFY_CARD"
    echo "          Push 前 stage/3.5/real-verify/.state-card.md 必须存在"
    FAILURES=$((FAILURES + 1))
else
    echo "          ✓ stage/3.5/real-verify/.state-card.md exists"
fi

# ---- Step 4: Test coverage check ----
echo ""
echo "    [4/6] Test coverage check:"

if has_script "test:coverage"; then
    echo "        [test:coverage] npm run test:coverage"
    if npm run test:coverage 2>&1; then
        echo "        [test:coverage] ✓ PASS"
    else
        echo "        [test:coverage] ⚠ FAIL (non-blocking for L2)"
    fi
else
    echo "        [test:coverage] ⚠ not found — skip"
fi

# ---- Step 5: Real execution (integration + build) ----
echo ""
echo "    [5/6] Real execution (no mock/stub PASS):"

run_step() {
    local label="$1"
    local script="$2"
    echo ""
    echo "        [$label] npm run $script"
    if npm run "$script" 2>&1; then
        echo "        [$label] ✓ PASS"
    else
        echo "        [$label] ✗ FAIL"
        FAILURES=$((FAILURES + 1))
    fi
}

run_step "integration" "test:integration"
run_step "build" "build"

# ---- Step 6: Gate signature (SHA-256 hash) ----
echo ""
echo "    [6/6] Gate signature generation:"

GATE_RESULT="status=PASS,failures=$FAILURES,gate_id=$GATE_ID,stage=3.5/real-verify"
SIGNATURE=$(echo -n "$GATE_RESULT" | sha256sum | cut -d' ' -f1)
echo "          Signature: $SIGNATURE"
echo "          Gate result: $GATE_RESULT"

if [ $FAILURES -gt 0 ]; then
    echo ""
    echo "==> [V12 Gate L2] FAILED ($FAILURES check(s) failed)"
    echo "    Gate ID: $GATE_ID"
    exit $FAILURES
fi

echo ""
echo "==> [V12 Gate L2] PASSED"
echo "    Gate ID: $GATE_ID"
echo "    Signature: $SIGNATURE"