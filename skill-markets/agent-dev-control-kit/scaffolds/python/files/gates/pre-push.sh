#!/usr/bin/env bash
# Pre-push gate for Python preset (Level L2)
# Runs integration tests + coverage + build.
# HARD REQUIREMENT: required tools MUST exist or be declared — no silent skipping allowed.

set -euo pipefail

REQUIRED_TOOLS=("pytest" "build")
REQUIRED_PROJECTS=("pyproject.toml")
FAILURES=0

cd "$(git rev-parse --show-toplevel 2>/dev/null || pwd)"

echo "==> [L2] Running pre-push gate (python preset)..."

# ---- Step 1: project file existence check ----
echo "    [1/?] Project manifest existence check:"
MISSING=()
for f in "${REQUIRED_PROJECTS[@]}"; do
  if [ -f "$f" ]; then
    echo "          [$f] ✓ exists"
  else
    echo "          [$f] ✗ MISSING — gate fails"
    MISSING+=("$f")
    FAILURES=$((FAILURES + 1))
  fi
done

# ---- Step 2: tool existence check ----
echo ""
echo "    [2/?] Required tool existence check:"
MISSING_TOOLS=()
for tool in "${REQUIRED_TOOLS[@]}"; do
  if command -v "$tool" >/dev/null 2>&1; then
    echo "          [$tool] ✓ installed ($(command -v "$tool"))"
  else
    echo "          [$tool] ✗ NOT INSTALLED — gate fails"
    MISSING_TOOLS+=("$tool")
    FAILURES=$((FAILURES + 1))
  fi
done

# ---- Step 3: build-backend declared check ----
if [ -f pyproject.toml ]; then
  echo ""
  echo "    [3/?] Build backend declaration:"
  if grep -qE 'build-backend[[:space:]]*=' pyproject.toml; then
    backend=$(grep -E 'build-backend[[:space:]]*=' pyproject.toml | head -1 | sed -E 's/.*=[[:space:]]*"([^"]+)".*/\1/')
    echo "          ✓ build backend declared: $backend"
  else
    echo "          ✗ MISSING — build-backend not declared"
    FAILURES=$((FAILURES + 1))
  fi
fi

if [ $FAILURES -gt 0 ]; then
  echo ""
  echo "    🛑 Gate FAIL: ${FAILURES} required item(s) missing"
  if [ ${#MISSING[@]} -gt 0 ]; then
    echo "        Missing files:"
    for s in "${MISSING[@]}"; do echo "          - $s"; done
  fi
  if [ ${#MISSING_TOOLS[@]} -gt 0 ]; then
    echo "        Missing tools:"
    for s in "${MISSING_TOOLS[@]}"; do echo "          - $s"; done
  fi
  echo ""
  echo "    Install all required tools: pip install -e '.[dev]'"
  exit "$FAILURES"
fi

# ---- Step 4: real execution ----
run_step() {
  local label="$1"
  shift
  echo ""
  echo "    [$label] $*"
  if "$@"; then
    echo "    [$label] ✓ PASS"
  else
    echo "    [$label] ✗ FAIL"
    FAILURES=$((FAILURES + 1))
  fi
}

run_step "2/4" "pytest" tests/integration -v
run_step "3/4" "pytest" --cov=src --cov-report=term-missing
run_step "4/4" "python" -m build

if [ $FAILURES -gt 0 ]; then
  echo ""
  echo "==> [L2] FAILED ($FAILURES check(s) failed)"
  exit "$FAILURES"
fi

echo ""
echo "==> [L2] PASSED"