#!/usr/bin/env bash
# validate-config.sh — sanity-check the gate/guard configs for the Java/Maven preset.

set -euo pipefail

ROOT="$(pwd)"

check() {
  local label="$1"
  local ok="$2"
  if [ "$ok" = "true" ]; then
    echo "✅ $label"
  else
    echo "❌ $label"
    return 1
  fi
}

fail=0

[ -f "$ROOT/pom.xml" ] && ok=true || ok=false
check "pom.xml exists" "$ok" || fail=1

[ -f "$ROOT/gates/gate-config.json" ] && ok=true || ok=false
check "gates/gate-config.json exists" "$ok" || fail=1

[ -f "$ROOT/guards/guard-config.json" ] && ok=true || ok=false
check "guards/guard-config.json exists" "$ok" || fail=1

if command -v jq >/dev/null 2>&1; then
  jq -e '.levels.L1' "$ROOT/gates/gate-config.json" >/dev/null && ok=true || ok=false
  check "gate-config has L1" "$ok" || fail=1
  jq -e '.levels.L2' "$ROOT/gates/gate-config.json" >/dev/null && ok=true || ok=false
  check "gate-config has L2" "$ok" || fail=1
fi

if [ "$fail" -ne 0 ]; then
  echo "Validation FAILED"
  exit 1
fi
echo "Validation PASSED"