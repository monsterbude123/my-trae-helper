#!/usr/bin/env bash
# V11 Pre-commit Gate (HARDENED) — Stage 1 Spec Validation
# HARDENING POINTS:
#   1. set -euo pipefail (fail-fast + pipe error propagation)
#   2. All required files/scripts MUST exist — no assumptions
#   3. Detect echo-skip anti-pattern (placeholder scripts)
#   4. Real execution — no mock/stub PASS allowed
#   5. Mandatory Stage 1 Spec verification (V11 §0 required stage)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
GATE_ID="L1-pre-commit-$(date +%Y%m%d%H%M%S)"
FAILURES=0

echo "==> [V11 Gate L1] Pre-commit hardened gate (Stage 1 Spec Validation)"
echo "    Gate ID: $GATE_ID"

cd "$PROJECT_ROOT"

# ---- Step 0: Environment validation (V11_GATE_ENFORCED) ----
if [ -z "${V11_GATE_ENFORCED:-}" ]; then
    export V11_GATE_ENFORCED="true"
    export V11_GATE_STAGE="1/spec"
    export V11_GATE_CALLER="pre-commit-hardened.sh"
    echo "    [0/5] Environment: V11_GATE_ENFORCED=true (auto-set)"
else
    echo "    [0/5] Environment: V11_GATE_ENFORCED=${V11_GATE_ENFORCED}"
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

# ---- Step 3: Stage 1 Spec verification (V11 required stage) ----
echo ""
echo "    [3/5] Stage 1 Spec verification (V11 required stage):"

STATE_CARD="$PROJECT_ROOT/docs/specs/.state-card.md"

if [ -f "$STATE_CARD" ]; then
    if python3 - "$STATE_CARD" <<'PYEOF' 2>&1; then
import sys, pathlib, yaml
path = pathlib.Path(sys.argv[1])
content = path.read_text(encoding="utf-8")
if not content.startswith("---"):
    sys.exit(1)
end = content.index("\n---", 3)
fm = yaml.safe_load(content[3:end]) or {}
stage = fm.get("current_stage", "")
sys.exit(0 if stage == "1/spec" else 1)
PYEOF
        echo "          [state-card] ✓ current_stage == 1/spec"
    else
        echo "          [state-card] ✗ current_stage != 1/spec — gate fails"
        FAILURES=$((FAILURES + 1))
    fi
else
    echo "          [state-card] ⚠ not found — skip (not mandatory for pre-commit)"
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

GATE_RESULT="status=PASS,failures=$FAILURES,gate_id=$GATE_ID,stage=1/spec"
SIGNATURE=$(echo -n "$GATE_RESULT" | sha256sum | cut -d' ' -f1)
echo "          Signature: $SIGNATURE"
echo "          Gate result: $GATE_RESULT"

if [ $FAILURES -gt 0 ]; then
    echo ""
    echo "==> [V11 Gate L1] FAILED ($FAILURES check(s) failed)"
    echo "    Gate ID: $GATE_ID"
    exit $FAILURES
fi

echo ""
echo "==> [V11 Gate L1] PASSED"
echo "    Gate ID: $GATE_ID"
echo "    Signature: $SIGNATURE"