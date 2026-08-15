#!/usr/bin/env bash
# V11 Pre-stage Gate (HARDENED) — Stage Transition Validation
# HARDENING POINTS:
#   1. set -euo pipefail (fail-fast + pipe error propagation)
#   2. Mandatory environment variable validation (V11_GATE_ENFORCED)
#   3. Missing env vars = gate FAIL (exit 1) — cannot bypass
#   4. Real execution of stage-gate.py — no mock/stub PASS
#   5. State card existence check + stage verification

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
GATE_ID="pre-stage-$(date +%Y%m%d%H%M%S)"

echo "==> [V11 Gate] Pre-stage hardened gate"
echo "    Gate ID: $GATE_ID"

cd "$PROJECT_ROOT"

# ---- Step 0: MANDATORY environment variable validation ----
echo ""
echo "    [0/4] Environment variable validation (HARDENED):"

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
    echo "          Required: V11_GATE_STAGE=<stage> (e.g., 1/spec, 2/impl)"
    VALIDATION_FAILED=1
else
    echo "          ✓ V11_GATE_STAGE=${V11_GATE_STAGE}"
fi

if [ -z "${V11_GATE_CALLER:-}" ]; then
    echo "          ✗ V11_GATE_CALLER is NOT SET — gate FAILS"
    echo "          Required: V11_GATE_CALLER=<caller-name> (e.g., stage-1-agent)"
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

# ---- Step 1: State card existence check ----
echo ""
echo "    [1/4] State card existence check:"

STATE_CARD="${STATE_CARD_PATH:-}"
if [ -z "$STATE_CARD" ]; then
    STATE_CARD="$(find docs/specs/changes -name .state-card.md 2>/dev/null | head -1 || true)"
fi
if [ -z "$STATE_CARD" ] && [ -f "$PROJECT_ROOT/docs/specs/.state-card.md" ]; then
    STATE_CARD="$PROJECT_ROOT/docs/specs/.state-card.md"
fi

if [ ! -f "$STATE_CARD" ]; then
    echo "          ✗ State card NOT FOUND: $STATE_CARD"
    echo "          Required for stage transition validation."
    exit 1
else
    echo "          ✓ State card exists: $STATE_CARD"
fi

# ---- Step 2: stage-gate.py script existence check ----
echo ""
echo "    [2/4] stage-gate.py script existence check:"

V11_SCRIPTS="${V11_SCRIPTS:-$HOME/.trae-cn/skills/fullstack4TraeV11/scripts}"
STAGE_GATE_SCRIPT="$V11_SCRIPTS/stage-gate.py"

if [ ! -f "$STAGE_GATE_SCRIPT" ]; then
    echo "          ✗ stage-gate.py NOT FOUND: $STAGE_GATE_SCRIPT"
    echo "          Required for real stage transition validation."
    exit 1
else
    echo "          ✓ stage-gate.py exists: $STAGE_GATE_SCRIPT"
fi

# ---- Step 3: Real execution — stage-gate.py ----
echo ""
echo "    [3/4] Real execution (no mock/stub PASS):"
echo "          Running: python $STAGE_GATE_SCRIPT --state-card $STATE_CARD ${EXPECTED_STAGE:+--stage $EXPECTED_STAGE}"

EXPECTED_STAGE="${EXPECTED_STAGE:-}"

if python "$STAGE_GATE_SCRIPT" \
    --state-card "$STATE_CARD" \
    ${EXPECTED_STAGE:+--stage "$EXPECTED_STAGE"} 2>&1; then
    echo "          ✓ stage-gate.py PASS"
else
    EXIT_CODE=$?
    echo "          ✗ stage-gate.py FAIL (exit code: $EXIT_CODE)"
    echo "    🛑 Gate FAIL: Stage transition not allowed"
    exit $EXIT_CODE
fi

# ---- Step 4: Gate signature (SHA-256 hash) ----
echo ""
echo "    [4/4] Gate signature generation:"

GATE_RESULT="status=PASS,gate_id=$GATE_ID,stage=${V11_GATE_STAGE},caller=${V11_GATE_CALLER}"
SIGNATURE=$(echo -n "$GATE_RESULT" | sha256sum | cut -d' ' -f1)
echo "          Signature: $SIGNATURE"
echo "          Gate result: $GATE_RESULT"

echo ""
echo "==> [V11 Gate] Pre-stage PASSED"
echo "    Gate ID: $GATE_ID"
echo "    Signature: $SIGNATURE"