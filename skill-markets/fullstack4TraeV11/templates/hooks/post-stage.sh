#!/usr/bin/env bash
# V11 Post-stage Audit Hook (NON-BLOCKING) — State Card Change Audit Log
# PURPOSE:
#   1. Record state card changes to audit log (NON-BLOCKING)
#   2. Call _lib_state_card.py audit_state_card_change()
#   3. Log operation type / actor / hash_before / hash_after
# HARDENING:
#   - set -euo pipefail (but catches errors for audit-only)
#   - Missing env vars → warn, NOT fail (audit-only mode)
#   - Missing state card → skip audit, NOT fail

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
AUDIT_ID="post-stage-$(date +%Y%m%d%H%M%S)"

echo "==> [V11 Audit] Post-stage audit hook"
echo "    Audit ID: $AUDIT_ID"

cd "$PROJECT_ROOT"

# ---- Step 0: Environment context (WARN only, non-blocking) ----
echo ""
echo "    [0/3] Environment context (audit-only, non-blocking):"

ACTOR="${V11_GATE_CALLER:-unknown-agent}"
GATE_STAGE="${V11_GATE_STAGE:-unknown-stage}"
GATE_ENFORCED="${V11_GATE_ENFORCED:-false}"

echo "          Actor: $ACTOR"
echo "          Stage: $GATE_STAGE"
echo "          Enforced: $GATE_ENFORCED"

# ---- Step 1: Change ID validation ----
echo ""
echo "    [1/3] Change ID validation:"

CHANGE_ID="${CHANGE_ID:-}"

if [ -z "$CHANGE_ID" ]; then
    echo "          ⚠ Missing CHANGE_ID env — skip audit (non-blocking)"
    echo "==> [V11 Audit] Post-stage SKIPPED (no CHANGE_ID)"
    exit 0
fi

echo "          ✓ CHANGE_ID: $CHANGE_ID"

# ---- Step 2: State card path resolution ----
echo ""
echo "    [2/3] State card path resolution:"

STATE_CARD="$PROJECT_ROOT/docs/specs/changes/${CHANGE_ID}/.state-card.md"

if [ ! -f "$STATE_CARD" ]; then
    echo "          ⚠ State card NOT FOUND: $STATE_CARD"
    echo "          Skip audit (non-blocking)"
    echo "==> [V11 Audit] Post-stage SKIPPED (no state card)"
    exit 0
fi

echo "          ✓ State card: $STATE_CARD"

# ---- Step 3: Audit log via _lib_state_card.py ----
echo ""
echo "    [3/3] Audit log recording:"

V11_SCRIPTS="${V11_SCRIPTS:-$HOME/.trae-cn/skills/fullstack4TraeV11/scripts}"
LIB_STATE_CARD="$V11_SCRIPTS/_lib_state_card.py"

if [ ! -f "$LIB_STATE_CARD" ]; then
    echo "          ⚠ _lib_state_card.py NOT FOUND: $LIB_STATE_CARD"
    echo "          Skip audit (non-blocking)"
    echo "==> [V11 Audit] Post-stage SKIPPED (missing lib)"
    exit 0
fi

# Read state card content for hash calculation
CONTENT_AFTER=$(cat "$STATE_CARD" 2>/dev/null || echo "")

# Call audit function via Python inline script
python3 - "$PROJECT_ROOT" "$STATE_CARD" "$ACTOR" "$CONTENT_AFTER" "$GATE_STAGE" "$GATE_ENFORCED" <<'PYEOF' 2>&1 || {
    echo "          ⚠ Audit logging failed (non-blocking)"
    echo "==> [V11 Audit] Post-stage COMPLETED (audit failed)"
    exit 0
}
import sys
import pathlib
import json
from datetime import datetime, timezone

try:
    # Add scripts dir to path for import
    scripts_dir = pathlib.Path(sys.argv[0]).parent / "skill-markets" / "fullstack4TraeV11" / "scripts"
    if not scripts_dir.exists():
        scripts_dir = pathlib.Path.home() / ".trae-cn" / "skills" / "fullstack4TraeV11" / "scripts"
    
    if scripts_dir.exists():
        sys.path.insert(0, str(scripts_dir))
        from _lib_state_card import audit_state_card_change, compute_hash
        
        project_root = pathlib.Path(sys.argv[1])
        state_card = pathlib.Path(sys.argv[2])
        actor = sys.argv[3]
        content_after = sys.argv[4]
        gate_stage = sys.argv[5]
        gate_enforced = sys.argv[6]
        
        entry = audit_state_card_change(
            path=state_card,
            operation="post-stage-update",
            actor=actor,
            content_after=content_after,
            project_root=project_root
        )
        
        print(f"          ✓ Audit logged: {entry['timestamp']}")
        print(f"            Hash: {entry['hash_after'][:16]}...")
        print(f"            Operation: {entry['operation']}")
    else:
        print("          ⚠ Scripts dir not found, skip audit")
except Exception as e:
    print(f"          ⚠ Audit error: {e}")
    pass
PYEOF

echo ""
echo "==> [V11 Audit] Post-stage COMPLETED"
echo "    Audit ID: $AUDIT_ID"