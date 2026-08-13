#!/usr/bin/env bash
# Pre-push gate for Go preset (Level L2)
# Runs integration tests + coverage + build.
# HARD REQUIREMENT: required tools and build target MUST exist — no silent skipping allowed.

set -euo pipefail

REQUIRED_TOOLS=("go")
REQUIRED_FILES=("go.mod")
REQUIRED_DIRS=("tests/integration")
FAILURES=0

cd "$(git rev-parse --show-toplevel 2>/dev/null || pwd)"

echo "==> [L2] Running pre-push gate (go preset)..."

# ---- Step 1: required file/dir existence ----
echo "    [1/?] Required file/dir existence check:"
MISSING=()
for f in "${REQUIRED_FILES[@]}"; do
  if [ -e "$f" ]; then
    echo "          [$f] ✓ exists"
  else
    echo "          [$f] ✗ MISSING — gate fails"
    MISSING+=("$f")
    FAILURES=$((FAILURES + 1))
  fi
done
for d in "${REQUIRED_DIRS[@]}"; do
  if [ -d "$d" ]; then
    echo "          [$d] ✓ directory exists"
  else
    echo "          [$d] ✗ MISSING — gate fails (create at least one *_test.go with build tag 'integration')"
    MISSING+=("$d")
    FAILURES=$((FAILURES + 1))
  fi
done

# ---- Step 2: required tool existence ----
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

# ---- Step 3: build target existence check ----
echo ""
echo "    [3/?] Build target existence:"
if [ -d cmd/app ]; then
  if ls cmd/app/*.go >/dev/null 2>&1; then
    echo "          ✓ cmd/app/*.go exists"
  else
    echo "          ✗ cmd/app exists but no .go files"
    FAILURES=$((FAILURES + 1))
  fi
else
  echo "          ⚠️  cmd/app not found — using root package"
fi

if [ $FAILURES -gt 0 ]; then
  echo ""
  echo "    🛑 Gate FAIL: ${FAILURES} required item(s) missing"
  if [ ${#MISSING[@]} -gt 0 ]; then
    echo "        Missing files/dirs:"
    for s in "${MISSING[@]}"; do echo "          - $s"; done
  fi
  if [ ${#MISSING_TOOLS[@]} -gt 0 ]; then
    echo "        Missing tools:"
    for s in "${MISSING_TOOLS[@]}"; do echo "          - $s"; done
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

run_step "2/4" "go" test ./tests/integration/... -tags=integration

mkdir -p bin
run_step "3/4" "go" test ./... -coverprofile=coverage.out -covermode=atomic

if [ -d cmd/app ] && ls cmd/app/*.go >/dev/null 2>&1; then
  run_step "4/4" "go" build -o bin/app ./cmd/app
else
  run_step "4/4" "go" build -o bin/app .
fi

if [ $FAILURES -gt 0 ]; then
  echo ""
  echo "==> [L2] FAILED ($FAILURES check(s) failed)"
  exit "$FAILURES"
fi

echo ""
echo "==> [L2] PASSED"