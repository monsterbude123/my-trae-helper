#!/usr/bin/env bash
# module-boundary-guard.sh — ensure no imports from outside the module enter internal/.
#
# Strategy: any Go file under cmd/ or pkg/ or tests/ may import internal/. Files under
# internal/ must NOT be imported by anything outside this module path.
#
# Heuristic check: grep for "<module>/internal/" references outside internal/.

set -euo pipefail

ROOT="$(pwd)"
MODULE=$(grep -E '^module ' go.mod | awk '{print $2}')

if [ -z "$MODULE" ]; then
  echo "[module-boundary-guard] no module path in go.mod — skipped."
  exit 0
fi

echo "[module-boundary-guard] module = $MODULE"

# Find any non-internal Go file that imports $MODULE/internal/.
violations=$(grep -rEn "$MODULE/internal/" \
  --include='*.go' \
  --exclude-dir=internal \
  . 2>/dev/null || true)

if [ -n "$violations" ]; then
  echo "[module-boundary-guard] VIOLATIONS:"
  echo "$violations"
  exit 1
fi

echo "[module-boundary-guard] PASSED"