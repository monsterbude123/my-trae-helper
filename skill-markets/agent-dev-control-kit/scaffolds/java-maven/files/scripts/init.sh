#!/usr/bin/env bash
# init.sh — initialize a Java/Maven project from this preset.

set -euo pipefail

echo "==> Initializing Java/Maven project..."

if [ ! -f pom.xml ]; then
  echo "    ERROR: pom.xml not found. Did the preset materialize correctly?"
  exit 1
fi

echo "    [1/3] mvn validate..."
mvn -B -q validate

echo "    [2/3] mvn compile..."
mvn -B -q compile

echo "    [3/3] mvn test (sanity)..."
mvn -B -q test

echo "==> Initialization complete. Next steps:"
echo "    - Edit pom.xml (groupId, artifactId, version)"
echo "    - Run gates: ./gates/pre-commit.sh"
echo "    - Run guards: ./guards/api-contract-guard.sh"