#!/usr/bin/env bash
# V11 Pre-accept Gate (HARDENED) — Stage 5 Accept Validation
# HARDENING POINTS:
#   1. set -euo pipefail (fail-fast + pipe error propagation)
#   2. Mandatory environment variable validation (V11_GATE_ENFORCED)
#   3. Missing env vars = gate FAIL (exit 1) — cannot bypass
#   4. FORCED Stage 4.5 rot-scan verification
#   5. fix-list.json existence check
#   6. Real execution of phase-gate.py — no mock/stub PASS

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
GATE_ID="pre-accept-$(date +%Y%m%d%H%M%S)"
FAILURES=0

echo "==> [V11 Gate] Pre-accept hardened gate (Stage 5 Accept)"
echo "    Gate ID: $GATE_ID"

cd "$PROJECT_ROOT"

# ---- Step 0: MANDATORY environment variable validation ----
echo ""
echo "    [0/5] Environment variable validation (HARDENED):"

VALIDATION_FAILED=0

if [ -z "${V11_GATE_ENFORCED:-}" ]; then
    echo "          ✗ V11_GATE_ENFORCED is NOT SET — gate FAILS"
    echo "          Required: V11_GATE_ENFORCED=true (set by V11 orchestrator)"
    VALIDATION_FAILED=1
else
    echo "          ✓ V11_GATE_ENFORCED=${V11_GATE_ENFORCED}"
fi

if [ -z "${V11_GATE_STAGE:-}" ]; then
    echo "          ✗ V11_GATE_STAGE is NOT SET — gate FAILS"
    echo "          Required: V11_GATE_STAGE=5/accept (for Stage 5 accept)"
    VALIDATION_FAILED=1
else
    echo "          ✓ V11_GATE_STAGE=${V11_GATE_STAGE}"
fi

if [ -z "${V11_GATE_CALLER:-}" ]; then
    echo "          ✗ V11_GATE_CALLER is NOT SET — gate FAILS"
    echo "          Required: V11_GATE_CALLER=<caller-name> (e.g., stage-5-agent)"
    VALIDATION_FAILED=1
else
    echo "          ✓ V11_GATE_CALLER=${V11_GATE_CALLER}"
fi

if [ $VALIDATION_FAILED -ne 0 ]; then
    echo ""
    echo "    🛑 Gate FAIL: Missing mandatory environment variables"
    echo "    Agent cannot bypass this gate without proper V11 orchestrator context."
    echo "    To fix: Ensure V11 orchestrator sets V11_GATE_ENFORCED/STAGE/CALLER."
    exit 1
fi

# ---- Step 1: Change ID validation ----
echo ""
echo "    [1/5] Change ID validation:"

CHANGE_ID="${CHANGE_ID:-}"

if [ -z "$CHANGE_ID" ]; then
    echo "          ✗ CHANGE_ID is NOT SET — gate FAILS"
    echo "          Required: CHANGE_ID=<change-id> (for state card path)"
    exit 1
else
    echo "          ✓ CHANGE_ID: $CHANGE_ID"
fi

# ---- Step 2: State card existence check ----
echo ""
echo "    [2/5] State card existence check:"

STATE_CARD="$PROJECT_ROOT/docs/specs/changes/${CHANGE_ID}/.state-card.md"

if [ ! -f "$STATE_CARD" ]; then
    echo "          ✗ State card NOT FOUND: $STATE_CARD"
    echo "          Required for Stage 5 accept validation."
    exit 1
else
    echo "          ✓ State card exists: $STATE_CARD"
fi

# ---- Step 3: FORCED Stage 4.5 rot-scan verification ----
echo ""
echo "    [3/5] FORCED Stage 4.5 rot-scan verification:"

V11_SCRIPTS="${V11_SCRIPTS:-$HOME/.trae-cn/skills/fullstack4TraeV11/scripts}"
PHASE_GATE_SCRIPT="$V11_SCRIPTS/phase-gate.py"

if [ ! -f "$PHASE_GATE_SCRIPT" ]; then
    echo "          ✗ phase-gate.py NOT FOUND: $PHASE_GATE_SCRIPT"
    echo "          Required for Stage 4.5 rot-scan verification."
    exit 1
else
    echo "          ✓ phase-gate.py exists: $PHASE_GATE_SCRIPT"
fi

echo "          Running: python $PHASE_GATE_SCRIPT --verify-rot-scan --change-id $CHANGE_ID"

if python "$PHASE_GATE_SCRIPT" \
    --state-card "$STATE_CARD" \
    --verify-rot-scan \
    --change-id "$CHANGE_ID" 2>&1; then
    echo "          ✓ Stage 4.5 rot-scan PASSED"
else
    EXIT_CODE=$?
    echo "          ✗ Stage 4.5 rot-scan FAILED (exit code: $EXIT_CODE)"
    echo "    🛑 Gate FAIL: Stage 4.5 rot-scan MUST PASS before accept"
    echo "    Fix: Run rot-scan stage and resolve all issues."
    exit $EXIT_CODE
fi

# ---- Step 4: fix-list.json existence check ----
echo ""
echo "    [4/5] fix-list.json existence check:"

FIX_LIST="$PROJECT_ROOT/docs/specs/changes/${CHANGE_ID}/fix-list.json"

if [ ! -f "$FIX_LIST" ]; then
    echo "          ✗ fix-list.json NOT FOUND: $FIX_LIST"
    echo "          Required for Stage 5 accept (must track fixes)."
    echo "    🛑 Gate FAIL: fix-list.json MUST exist"
    exit 1
else
    echo "          ✓ fix-list.json exists: $FIX_LIST"
fi

# ---- Step 5: Gate signature (SHA-256 hash) ----
echo ""
echo "    [5/5] Gate signature generation:"

GATE_RESULT="status=PASS,gate_id=$GATE_ID,stage=5/accept,caller=${V11_GATE_CALLER},change_id=${CHANGE_ID}"
SIGNATURE=$(echo -n "$GATE_RESULT" | sha256sum | cut -d' ' -f1)
echo "          Signature: $SIGNATURE"
echo "          Gate result: $GATE_RESULT"

echo ""
echo "==> [V11 Gate] Pre-accept PASSED"
echo "    Gate ID: $GATE_ID"
echo "    Change ID: $CHANGE_ID"
echo "    Signature: $SIGNATURE"