#!/usr/bin/env bash
# Pre-push gate for Node.js preset (Level L2)
# Runs integration tests + coverage + build.

set -euo pipefail

echo "==> [L2] Running pre-push gate (nodejs preset)..."

echo "    [1/3] Integration tests..."
npm run test:integration

echo "    [2/3] Coverage..."
npm run test:coverage

echo "    [3/3] Build..."
npm run build

echo "==> [L2] PASSED"