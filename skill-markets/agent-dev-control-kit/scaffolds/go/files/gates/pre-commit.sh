#!/usr/bin/env bash
# Pre-commit gate for Go preset (Level L1)
# Runs lint + typecheck (build) + unit tests.
# HARD REQUIREMENT: required tools MUST exist; go.mod MUST be present — no silent skipping allowed.

set -euo pipefail

REQUIRED_TOOLS=("go")
REQUIRED_FILES=("go.mod")
FAILURES=0

cd "$(git rev-parse --show-toplevel 2>/dev/null || pwd)"

echo "==> [L1] Running pre-commit gate (go preset)..."

# ---- Step 1: required file existence ----
echo "    [1/?] Required file existence check:"
MISSING=()
for f in "${REQUIRED_FILES[@]}"; do
  if [ -f "$f" ]; then
    echo "          [$f] ✓ exists"
  else
    echo "          [$f] ✗ MISSING — gate fails"
    MISSING+=("$f")
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

# ---- Step 3: linter decision (must have at least one real linter) ----
echo ""
echo "    [3/?] Linter decision:"
LINTER=""
if command -v golangci-lint >/dev/null 2>&1; then
  LINTER="golangci-lint"
  echo "          ✓ golangci-lint available ($(command -v golangci-lint))"
elif go vet ./... >/dev/null 2>&1 & HELP_PID=$!; sleep 0.05; kill $HELP_PID 2>/dev/null; then
  LINTER="go-vet"
  echo "          ✓ go vet available (via go toolchain)"
else
  echo "          ✗ MISSING — neither golangci-lint nor usable go vet found"
  FAILURES=$((FAILURES + 1))
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
  echo "    Install Go: https://go.dev/dl/"
  echo "    Install golangci-lint: https://golangci-lint.run/welcome/install/"
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

if [ "$LINTER" = "golangci-lint" ]; then
  run_step "2/4" "golangci-lint" run
else
  run_step "2/4" "go" vet ./...
fi
run_step "3/4" "go" build ./...
run_step "4/4" "go" test ./internal/... -short

if [ $FAILURES -gt 0 ]; then
  echo ""
  echo "==> [L1] FAILED ($FAILURES check(s) failed)"
  exit "$FAILURES"
fi

echo ""
echo "==> [L1] PASSED"