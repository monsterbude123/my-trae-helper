#!/usr/bin/env bash
# Pre-commit gate for Java/Maven preset (Level L1)
# Runs lint (checkstyle) + typecheck (compile) + unit tests.
# HARD REQUIREMENT: required tools and project files MUST exist — no silent skipping allowed.

set -euo pipefail

REQUIRED_TOOLS=("mvn")
REQUIRED_FILES=("pom.xml")
FAILURES=0

cd "$(git rev-parse --show-toplevel 2>/dev/null || pwd)"

echo "==> [L1] Running pre-commit gate (java-maven preset)..."

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

# ---- Step 3: pom.xml sanity check ----
echo ""
echo "    [3/?] pom.xml sanity check:"
if [ -f pom.xml ]; then
  if grep -qE '<groupId>[[:space:]]*[^<]+[[:space:]]*</groupId>' pom.xml \
     && grep -qE '<artifactId>[[:space:]]*[^<]+[[:space:]]*</artifactId>' pom.xml; then
    echo "          ✓ pom.xml has groupId and artifactId"
  else
    echo "          ✗ pom.xml missing groupId/artifactId — gate fails"
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
  echo "    Install Maven: https://maven.apache.org/install.html"
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

# Checkstyle — fail if not configured (no silent skip)
echo ""
echo "    [2/4] checkstyle:check"
if grep -qE 'maven-checkstyle-plugin|<artifactId>maven-checkstyle' pom.xml; then
  run_step "" mvn -B -q checkstyle:check
else
  echo "          ✗ checkstyle plugin not configured in pom.xml — gate fails"
  FAILURES=$((FAILURES + 1))
fi

run_step "3/4" mvn -B -q compile
run_step "4/4" mvn -B -q test -Dtest='*Test' -DfailIfNoTests=false

if [ $FAILURES -gt 0 ]; then
  echo ""
  echo "==> [L1] FAILED ($FAILURES check(s) failed)"
  exit "$FAILURES"
fi

echo ""
echo "==> [L1] PASSED"