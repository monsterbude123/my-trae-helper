#!/usr/bin/env bash
# api-contract-guard.sh — verify internal/services/*.go have exported funcs.

set -euo pipefail

ROOT="$(pwd)"
SERVICES_DIR="$ROOT/internal/services"

if [ ! -d "$SERVICES_DIR" ]; then
  echo "[api-contract-guard] No internal/services/ — skipped."
  exit 0
fi

failures=0
for f in "$SERVICES_DIR"/*.go; do
  [ -f "$f" ] || continue
  base="$(basename "$f")"
  case "$base" in
    *_test.go) continue ;;
  esac
  funcs=$(grep -E '^func [A-Z]' "$f" | awk '{print $2}' | cut -d '(' -f1 || true)
  if [ -z "$funcs" ]; then
    echo "[api-contract-guard] FAIL: $base has no exported top-level funcs"
    failures=$((failures + 1))
  else
    echo "[api-contract-guard] $base: funcs = [$funcs]"
  fi
done

if [ "$failures" -gt 0 ]; then
  echo "[api-contract-guard] $failures failure(s)"
  exit 1
fi
echo "[api-contract-guard] PASSED"