#!/usr/bin/env bash
# Pre-commit gate for Node.js preset (Level L1)
# Runs lint + typecheck + unit tests. Exits non-zero on failure.

set -euo pipefail

echo "==> [L1] Running pre-commit gate (nodejs preset)..."

echo "    [1/3] Lint..."
npm run lint

echo "    [2/3] Typecheck..."
npm run typecheck

echo "    [3/3] Unit tests..."
npm run test:unit

echo "==> [L1] PASSED"