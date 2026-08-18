#!/usr/bin/env bash
# V12 Pre-commit Gate (HARDENED) — Stage current_stage Validation
# HARDENING POINTS:
#   1. set -euo pipefail (fail-fast + pipe error propagation)
#   2. All required files/scripts MUST exist — no assumptions
#   3. Detect echo-skip anti-pattern (placeholder scripts)
#   4. Real execution — no mock/stub PASS allowed
#   5. V12 物理布局: stage/{N}/.state-card.md 每 stage 独立(与 state-machine.yaml 对齐)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
GATE_ID="L1-pre-commit-$(date +%Y%m%d%H%M%S)"
FAILURES=0

# V12 13 stage 列表(斜杠命名,与 registry/state-machine.yaml 对齐)
VALID_STAGES=(
    "-1/intake"
    "0/plan"
    "0.5/test-plan"
    "1/spec"
    "1.5/prototype"
    "2/contract"
    "3/implement"
    "3.5/real-verify"
    "4/review"
    "4.5/rot-scan"
    "5/accept"
    "6/bug-fix"
    "7/health"
)

echo "==> [V12 Gate L1] Pre-commit hardened gate (current_stage Validation)"
echo "    Gate ID: $GATE_ID"

cd "$PROJECT_ROOT"

# ---- Step 0: Environment validation (V12_GATE_ENFORCED) ----
if [ -z "${V12_GATE_ENFORCED:-}" ]; then
    export V12_GATE_ENFORCED="true"
    export V12_GATE_STAGE="1/spec"
    export V12_GATE_CALLER="pre-commit-hardened.sh"
    echo "    [0/5] Environment: V12_GATE_ENFORCED=true (auto-set)"
else
    echo "    [0/5] Environment: V12_GATE_ENFORCED=${V12_GATE_ENFORCED}"
fi

# ---- Step 1: Required files existence check ----
echo ""
echo "    [1/5] Required files existence check:"

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
    echo "    Missing files:"
    for f in "${MISSING_FILES[@]}"; do
        echo "        - $f"
    done
    exit $FAILURES
fi

# ---- Step 2: Required scripts existence + echo-skip detection ----
echo ""
echo "    [2/5] Required scripts existence + echo-skip detection:"

REQUIRED_SCRIPTS=("lint" "typecheck" "test:unit")
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
    echo "    Missing/invalid scripts:"
    for s in "${MISSING_SCRIPTS[@]}"; do
        echo "        - $s"
    done
    echo ""
    echo "    Fix: add real implementation to package.json 'scripts'."
    echo "    Forbidden: 'echo \"skipping ...\"' placeholders."
    exit $FAILURES
fi

# ---- Step 3: V12 stage state card verification (V12 物理布局唯一路径) ----
echo ""
echo "    [3/5] V12 stage state card verification:"

# V12 唯一布局: stage/{current_stage}/.state-card.md(每 stage 独立卡)
CURRENT_STAGE="${V12_GATE_STAGE:-1/spec}"
STATE_CARD="$PROJECT_ROOT/stage/${CURRENT_STAGE}/.state-card.md"

if [ ! -f "$STATE_CARD" ]; then
    echo "          ✗ V12 stage state card NOT FOUND: $STATE_CARD"
    echo "          V12 物理布局要求: stage/${CURRENT_STAGE}/.state-card.md 必须存在"
    FAILURES=$((FAILURES + 1))
else
    # current_stage ∈ V12 13 stage 列表(硬编码,与 state-machine.yaml 对齐)
    STAGE_VALID=0
    for s in "${VALID_STAGES[@]}"; do
        if [ "$s" = "$CURRENT_STAGE" ]; then
            STAGE_VALID=1
            break
        fi
    done
    if [ $STAGE_VALID -ne 1 ]; then
        echo "          ✗ current_stage='$CURRENT_STAGE' NOT IN V12 13 stage 列表"
        echo "          Required: ${VALID_STAGES[*]}"
        FAILURES=$((FAILURES + 1))
    else
        echo "          ✓ V12 stage card exists: $STATE_CARD"
        echo "          ✓ current_stage='$CURRENT_STAGE' ∈ V12 stage 列表"
    fi
fi

# ---- Step 4: Real execution (lint + typecheck + test:unit) ----
echo ""
echo "    [4/5] Real execution (no mock/stub PASS):"

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

run_step "lint" "lint"
run_step "typecheck" "typecheck"
run_step "test:unit" "test:unit"

# ---- Step 5: Gate signature (SHA-256 hash) ----
echo ""
echo "    [5/5] Gate signature generation:"

GATE_RESULT="status=PASS,failures=$FAILURES,gate_id=$GATE_ID,stage=${CURRENT_STAGE}"
SIGNATURE=$(echo -n "$GATE_RESULT" | sha256sum | cut -d' ' -f1)
echo "          Signature: $SIGNATURE"
echo "          Gate result: $GATE_RESULT"

if [ $FAILURES -gt 0 ]; then
    echo ""
    echo "==> [V12 Gate L1] FAILED ($FAILURES check(s) failed)"
    echo "    Gate ID: $GATE_ID"
    exit $FAILURES
fi

echo ""
echo "==> [V12 Gate L1] PASSED"
echo "    Gate ID: $GATE_ID"
echo "    Signature: $SIGNATURE"