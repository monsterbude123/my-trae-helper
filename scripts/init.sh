#!/usr/bin/env bash
# init.sh — initialize a Node.js project from this preset.
# Run from the project root after template files have been materialized.

set -euo pipefail

echo "==> Initializing Node.js project..."

if [ ! -f package.json ]; then
  echo "    ERROR: package.json not found. Did the preset materialize correctly?"
  exit 1
fi

echo "    [1/2] Installing dependencies..."
npm install

echo "    [2/2] Running sanity check..."
npm run test:unit

echo "==> Initialization complete. Next steps:"
echo "    - Edit package.json (name, description, author)"
echo "    - Run gates: ./gates/pre-commit.sh"
echo "    - Run guards: node guards/api-contract-guard.mjs"