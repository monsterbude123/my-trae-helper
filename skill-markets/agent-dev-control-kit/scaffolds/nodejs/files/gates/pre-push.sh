#!/usr/bin/env bash
# Pre-push gate for Node.js preset (Level L2)
# Runs integration tests + coverage + build.
# HARD REQUIREMENT: required scripts MUST exist in package.json — no echo-skipping allowed.

set -euo pipefail

REQUIRED_SCRIPTS=("test:integration" "test:coverage" "build")
FAILURES=0

cd "$(git rev-parse --show-toplevel 2>/dev/null || pwd)"

echo "==> [L2] Running pre-push gate (nodejs preset)..."

# ---- Step 1: existence check (fail-fast) ----
if [ ! -f package.json ]; then
  echo "    🛑 package.json not found at $(pwd)"
  echo "    gate fails: cannot verify required scripts without package.json"
  exit 1
fi

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

echo "    [1/?] Required script existence check:"
MISSING=()
for script in "${REQUIRED_SCRIPTS[@]}"; do
  if has_script "$script"; then
    body=$(python3 -c "import json; print(json.load(open('package.json')).get('scripts',{}).get('$script',''))" 2>/dev/null)
    if echo "$body" | grep -qiE '^[[:space:]]*echo[[:space:]]+["'"'"']?(skip|not|skipp)'; then
      echo "          [$script] ✗ ECHO-SKIP DETECTED — gate rejects placeholder"
      MISSING+=("$script")
      FAILURES=$((FAILURES + 1))
    else
      echo "          [$script] ✓ script exists"
    fi
  else
    echo "          [$script] ✗ MISSING — gate fails"
    MISSING+=("$script")
    FAILURES=$((FAILURES + 1))
  fi
done

if [ $FAILURES -gt 0 ]; then
  echo ""
  echo "    🛑 Gate FAIL: ${FAILURES} required script(s) missing or invalid:"
  for s in "${MISSING[@]}"; do
    echo "        - $s"
  done
  echo ""
  echo "    Fix: add real implementation to package.json 'scripts'."
  echo "    Forbidden: 'echo \"skipping ...\"' placeholders."
  exit "$FAILURES"
fi

# ---- Step 2: real execution ----
run_step() {
  local label="$1"
  local script="$2"
  echo ""
  echo "    [$label] npm run $script"
  if npm run "$script"; then
    echo "    [$label] ✓ PASS"
  else
    echo "    [$label] ✗ FAIL"
    FAILURES=$((FAILURES + 1))
  fi
}

run_step "2/4" "test:integration"
run_step "3/4" "test:coverage"
run_step "4/4" "build"

if [ $FAILURES -gt 0 ]; then
  echo ""
  echo "==> [L2] FAILED ($FAILURES check(s) failed)"
  exit "$FAILURES"
fi

echo ""
echo "==> [L2] PASSED"