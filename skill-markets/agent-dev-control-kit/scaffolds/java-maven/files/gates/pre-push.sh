#!/usr/bin/env bash
# Pre-push gate for Java/Maven preset (Level L2)

set -euo pipefail

echo "==> [L2] Running pre-push gate (java-maven preset)..."

echo "    [1/3] Integration tests..."
mvn -B -q verify -DskipUnitTests

echo "    [2/3] Coverage (jacoco)..."
mvn -B -q jacoco:report

echo "    [3/3] Build (package)..."
mvn -B -q package -DskipTests

echo "==> [L2] PASSED"