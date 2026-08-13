#!/usr/bin/env bash
# api-contract-guard.sh — verify services classes have public methods.

set -euo pipefail

ROOT="$(pwd)"
SRC="$ROOT/src/main/java"

if [ ! -d "$SRC" ]; then
  echo "[api-contract-guard] No src/main/java/ — skipped."
  exit 0
fi

failures=0
while IFS= read -r f; do
  rel="${f#$SRC/}"
  base="$(basename "$f" .java)"
  case "$base" in
    *Test) continue ;;
    App|Application|*Application) continue ;;
  esac
  methods=$(grep -E '^\s*public\s+(static\s+)?[A-Za-z<>]+\s+[a-zA-Z]+\s*\(' "$f" \
    | grep -v 'public\s\+\(final\s\+\)\?class\|public\s\+\(static\s\+\)\?interface\|public\s\+\(final\s\+\)\?enum' \
    | sed -E 's/^\s*public\s+(static\s+)?[A-Za-z<>]+\s+([a-zA-Z]+)\s*\(.*/\2/' \
    | sort -u || true)
  if [ -z "$methods" ]; then
    echo "[api-contract-guard] FAIL: $rel has no public methods"
    failures=$((failures + 1))
  else
    echo "[api-contract-guard] $rel: methods = [$methods]"
  fi
done < <(find "$SRC" -name '*.java')

if [ "$failures" -gt 0 ]; then
  echo "[api-contract-guard] $failures failure(s)"
  exit 1
fi
echo "[api-contract-guard] PASSED"