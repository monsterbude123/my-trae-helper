#!/usr/bin/env bash
# package-boundary-guard.sh — forbid cross-package imports in a layered architecture.
#
# Default rules (overridable via guard-config.json → forbidden_patterns):
#   - com.example.app.services.* must NOT import com.example.app.api.*
#   - com.example.app.services.* must NOT import com.example.app.db.*

set -euo pipefail

ROOT="$(pwd)"
SRC="$ROOT/src/main/java"

if [ ! -d "$SRC" ]; then
  echo "[package-boundary-guard] No src/main/java/ — skipped."
  exit 0
fi

# Parse forbidden_patterns from guard-config.json (fallback to defaults).
FORBIDDEN='["com.example.app.services -> com.example.app.api","com.example.app.services -> com.example.app.db"]'
if [ -f "$ROOT/guards/guard-config.json" ] && command -v jq >/dev/null 2>&1; then
  FORBIDDEN=$(jq -r '
    .guards[] | select(.id=="package-boundary") | .forbidden_patterns[]? | "\(.from) -> \(.to)"
  ' "$ROOT/guards/guard-config.json" 2>/dev/null | tr '\n' ',' | sed 's/,$//')
fi

IFS=',' read -ra RULES <<< "$FORBIDDEN"

failures=0
while IFS= read -r f; do
  rel="${f#$SRC/}"
  rel="${rel%.java}"
  rel="${rel//\//.}"
  for rule in "${RULES[@]}"; do
    [ -z "$rule" ] && continue
    from="${rule%% -> *}"
    to="${rule##* -> }"
    case "$rel" in
      ${from}.*)
        if grep -qE "^import\s+${to//./\\.}(\.|\*)" "$f"; then
          echo "[package-boundary-guard] FAIL: $rel imports ${to}.* (rule: $from → $to)"
          failures=$((failures + 1))
        fi
        ;;
    esac
  done
done < <(find "$SRC" -name '*.java')

if [ "$failures" -gt 0 ]; then
  echo "[package-boundary-guard] $failures violation(s)"
  exit 1
fi
echo "[package-boundary-guard] PASSED"