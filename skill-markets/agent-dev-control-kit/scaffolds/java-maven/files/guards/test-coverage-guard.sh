#!/usr/bin/env bash
# test-coverage-guard.sh — run jacoco and enforce >= threshold (default 80%).

set -euo pipefail

ROOT="$(pwd)"
THRESHOLD="${COVERAGE_THRESHOLD:-80}"

echo "[test-coverage-guard] threshold = ${THRESHOLD}%"

cd "$ROOT"
mvn -B -q jacoco:report

REPORT="$ROOT/target/site/jacoco/jacoco.csv"
if [ ! -f "$REPORT" ]; then
  echo "[test-coverage-guard] jacoco report not found at $REPORT"
  exit 1
fi

# Compute total line coverage from jacoco.csv:
#   covered / (covered + missed) for INSTRUCTION or LINE
covered=$(awk -F, 'NR>1 {c += $5} END {print c}' "$REPORT")
missed=$(awk -F, 'NR>1 {m += $4} END {print m}' "$REPORT")
total=$((covered + missed))
if [ "$total" -eq 0 ]; then
  pct=0
else
  pct=$(( (covered * 100) / total ))
fi

echo "[test-coverage-guard] covered=$covered missed=$missed pct=${pct}%"

if [ "$pct" -lt "$THRESHOLD" ]; then
  echo "[test-coverage-guard] FAILED: ${pct}% < ${THRESHOLD}%"
  exit 1
fi
echo "[test-coverage-guard] PASSED"