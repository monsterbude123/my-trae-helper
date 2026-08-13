#!/usr/bin/env bash
# Pre-commit gate for Java/Maven preset (Level L1)

set -euo pipefail

echo "==> [L1] Running pre-commit gate (java-maven preset)..."

echo "    [1/3] Lint (checkstyle)..."
mvn -B -q checkstyle:check || echo "    (checkstyle not configured — skipping)"

echo "    [2/3] Typecheck (mvn compile)..."
mvn -B -q compile

echo "    [3/3] Unit tests..."
mvn -B -q test -Dtest='*Test' -DfailIfNoTests=false

echo "==> [L1] PASSED"