#!/usr/bin/env bash
# init.sh — initialize a Go project from this preset.

set -euo pipefail

echo "==> Initializing Go project..."

if [ ! -f go.mod ]; then
  echo "    ERROR: go.mod not found. Did the preset materialize correctly?"
  exit 1
fi

echo "    [1/3] go mod tidy..."
go mod tidy

echo "    [2/3] go build (sanity)..."
go build ./...

echo "    [3/3] go test (sanity)..."
go test ./internal/... -short

echo "==> Initialization complete. Next steps:"
echo "    - Edit go.mod (module path, dependencies)"
echo "    - Run gates: ./gates/pre-commit.sh"
echo "    - Run guards: ./guards/api-contract-guard.sh"