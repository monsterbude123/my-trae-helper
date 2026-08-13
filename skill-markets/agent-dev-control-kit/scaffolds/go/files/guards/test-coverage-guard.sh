#!/usr/bin/env bash
# test-coverage-guard.sh — run coverage check on internal/.

set -euo pipefail

ROOT="$(pwd)"
THRESHOLD="${COVERAGE_THRESHOLD:-80}"

echo "[test-coverage-guard] threshold = ${THRESHOLD}%"

cd "$ROOT"
go test ./internal/... -coverprofile=coverage.out -covermode=atomic

# Extract total coverage
if command -v go >/dev/null 2>&1; then
  pct=$(go tool cover -func=coverage.out | awk '/^total:/ {print substr($3, 1, length($3)-1)}')
  echo "[test-coverage-guard] total coverage = ${pct}%"
  # awk comparison on integer percentage (no decimals)
  pass=$(awk -v p="$pct" -v t="$THRESHOLD" 'BEGIN { print (p+0 >= t+0) ? 1 : 0 }')
  if [ "$pass" != "1" ]; then
    echo "[test-coverage-guard] FAILED: ${pct}% < ${THRESHOLD}%"
    exit 1
  fi
fi

echo "[test-coverage-guard] PASSED"