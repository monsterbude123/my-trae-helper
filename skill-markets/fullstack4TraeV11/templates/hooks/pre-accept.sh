#!/usr/bin/env bash
# V12 Pre-accept Gate (HARDENED) — Stage 5 Accept Validation
# HARDENING POINTS (V12 ONLY):
#   1. set -euo pipefail (fail-fast + pipe error propagation)
#   2. Mandatory environment variable validation (V12_GATE_ENFORCED)
#   3. Missing env vars = gate FAIL (exit 1) — cannot bypass
#   4. FORCED Stage 4.5 rot-scan verification
#   5. fix-list.json existence check
#   6. Real execution of phase-gate.py — no mock/stub PASS
#   7. **V12**: stage/5/accept/.state-card.md 独立校验(不与其他 hook 共用逻辑)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
GATE_ID="pre-accept-$(date +%Y%m%d%H%M%S)"
FAILURES=0

echo "==> [V12 Gate] Pre-accept hardened gate (Stage 5 Accept)"
echo "    Gate ID: $GATE_ID"

cd "$PROJECT_ROOT"

# ---- Step 0: MANDATORY environment variable validation ----
echo ""
echo "    [0/5] Environment variable validation (HARDENED):"

VALIDATION_FAILED=0

if [ -z "${V12_GATE_ENFORCED:-}" ]; then
    echo "          ✗ V12_GATE_ENFORCED is NOT SET — gate FAILS"
    echo "          Required: V12_GATE_ENFORCED=true (set by V12 orchestrator)"
    VALIDATION_FAILED=1
else
    echo "          ✓ V12_GATE_ENFORCED=${V12_GATE_ENFORCED}"
fi

if [ -z "${V12_GATE_STAGE:-}" ]; then
    echo "          ✗ V12_GATE_STAGE is NOT SET — gate FAILS"
    echo "          Required: V12_GATE_STAGE=5/accept (for Stage 5 accept)"
    VALIDATION_FAILED=1
else
    echo "          ✓ V12_GATE_STAGE=${V12_GATE_STAGE}"
fi

if [ -z "${V12_GATE_CALLER:-}" ]; then
    echo "          ✗ V12_GATE_CALLER is NOT SET — gate FAILS"
    echo "          Required: V12_GATE_CALLER=<caller-name> (e.g., stage-5-agent)"
    VALIDATION_FAILED=1
else
    echo "          ✓ V12_GATE_CALLER=${V12_GATE_CALLER}"
fi

if [ $VALIDATION_FAILED -ne 0 ]; then
    echo ""
    echo "    🛑 Gate FAIL: Missing mandatory environment variables"
    echo "    Agent cannot bypass this gate without proper V12 orchestrator context."
    echo "    To fix: Ensure V12 orchestrator sets V12_GATE_ENFORCED/STAGE/CALLER."
    exit 1
fi

# ---- Step 1: V12 stage/5/accept/.state-card.md 独立校验 ----
# (INV 5: pre-accept.sh 必须独立校验 stage/5/accept/.state-card.md 存在,
#  不与其他 hook 共用逻辑 — V12 物理布局唯一)
echo ""
echo "    [1/5] V12 stage/5/accept/.state-card.md 独立校验:"

ACCEPT_CARD="$PROJECT_ROOT/stage/5/accept/.state-card.md"

if [ ! -f "$ACCEPT_CARD" ]; then
    echo "          ✗ V12 accept state card NOT FOUND: $ACCEPT_CARD"
    echo "          V12 物理布局: stage/5/accept/.state-card.md 必须存在"
    echo "    🛑 Gate FAIL: V12 Stage 5 accept card 不可缺失"
    exit 1
else
    echo "          ✓ V12 accept state card exists: $ACCEPT_CARD"
fi

# ---- Step 2: FORCED Stage 4.5 rot-scan verification ----
echo ""
echo "    [2/5] FORCED Stage 4.5 rot-scan verification:"

V12_SCRIPTS="${V12_SCRIPTS:-$HOME/.trae-cn/skills/fullstack4TraeV11/scripts}"
PHASE_GATE_SCRIPT="$V12_SCRIPTS/phase-gate.py"

if [ ! -f "$PHASE_GATE_SCRIPT" ]; then
    echo "          ✗ phase-gate.py NOT FOUND: $PHASE_GATE_SCRIPT"
    echo "          Required for Stage 4.5 rot-scan verification."
    exit 1
else
    echo "          ✓ phase-gate.py exists: $PHASE_GATE_SCRIPT"
fi

echo "          Running: python $PHASE_GATE_SCRIPT --verify-rot-scan --state-card $ACCEPT_CARD"

if python "$PHASE_GATE_SCRIPT" \
    --state-card "$ACCEPT_CARD" \
    --verify-rot-scan 2>&1; then
    echo "          ✓ Stage 4.5 rot-scan PASSED"
else
    EXIT_CODE=$?
    echo "          ✗ Stage 4.5 rot-scan FAILED (exit code: $EXIT_CODE)"
    echo "    🛑 Gate FAIL: Stage 4.5 rot-scan MUST PASS before accept"
    echo "    Fix: Run rot-scan stage and resolve all issues."
    exit $EXIT_CODE
fi

# ---- Step 3: fix-list.json existence check ----
echo ""
echo "    [3/5] fix-list.json existence check:"

FIX_LIST="$PROJECT_ROOT/docs/reports/fix-list.json"

if [ ! -f "$FIX_LIST" ]; then
    echo "          ✗ fix-list.json NOT FOUND: $FIX_LIST"
    echo "          Required for Stage 5 accept (must track fixes)."
    echo "    🛑 Gate FAIL: fix-list.json MUST exist"
    exit 1
else
    echo "          ✓ fix-list.json exists: $FIX_LIST"
fi

# ---- Step 4: stage/4.5/rot-scan/.state-card.md 存在性校验 ----
echo ""
echo "    [4/5] V12 stage/4.5/rot-scan/.state-card.md 校验:"

ROTSCAN_CARD="$PROJECT_ROOT/stage/4.5/rot-scan/.state-card.md"

if [ ! -f "$ROTSCAN_CARD" ]; then
    echo "          ✗ V12 rot-scan card NOT FOUND: $ROTSCAN_CARD"
    echo "          Accept 前 stage/4.5/rot-scan/.state-card.md 必须存在"
    FAILURES=$((FAILURES + 1))
else
    echo "          ✓ V12 rot-scan card exists: $ROTSCAN_CARD"
fi

# ---- Step 5: Gate signature (SHA-256 hash) ----
echo ""
echo "    [5/5] Gate signature generation:"

GATE_RESULT="status=PASS,gate_id=$GATE_ID,stage=5/accept,caller=${V12_GATE_CALLER}"
SIGNATURE=$(echo -n "$GATE_RESULT" | sha256sum | cut -d' ' -f1)
echo "          Signature: $SIGNATURE"
echo "          Gate result: $GATE_RESULT"

if [ $FAILURES -gt 0 ]; then
    echo ""
    echo "==> [V12 Gate] Pre-accept FAILED ($FAILURES check(s) failed)"
    echo "    Gate ID: $GATE_ID"
    exit $FAILURES
fi

echo ""
echo "==> [V12 Gate] Pre-accept PASSED"
echo "    Gate ID: $GATE_ID"
echo "    Signature: $SIGNATURE"