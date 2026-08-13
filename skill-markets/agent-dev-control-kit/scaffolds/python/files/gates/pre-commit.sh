#!/usr/bin/env bash
# Pre-commit gate for Python preset (Level L1)
# Runs lint + typecheck + unit tests.
# HARD REQUIREMENT: required tools/scripts MUST exist or be declared — no silent skipping allowed.

set -euo pipefail

REQUIRED_TOOLS=("ruff" "mypy" "pytest")
REQUIRED_PROJECTS=("pyproject.toml")
FAILURES=0

cd "$(git rev-parse --show-toplevel 2>/dev/null || pwd)"

echo "==> [L1] Running pre-commit gate (python preset)..."

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

# ---- Step 3: pyproject.toml no placeholder check ----
if [ -f pyproject.toml ]; then
  echo ""
  echo "    [3/?] pyproject.toml placeholder scan:"
  if grep -qiE 'skip[[:space:]]*[:=][[:space:]]*true|^[[:space:]]*#[[:space:]]*noqa[[:space:]]*$' pyproject.toml; then
    echo "          ⚠️  Found suspicious skip markers in pyproject.toml"
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
    echo ""
    echo "    Install all required tools:"
    echo "        pip install -e '.[dev]'"
    echo "    Or:  pip install ruff mypy pytest pytest-cov"
  fi
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

run_step "2/4" "ruff" check .
run_step "3/4" "mypy" src/
run_step "4/4" "pytest" tests/unit -v

if [ $FAILURES -gt 0 ]; then
  echo ""
  echo "==> [L1] FAILED ($FAILURES check(s) failed)"
  exit "$FAILURES"
fi

echo ""
echo "==> [L1] PASSED"