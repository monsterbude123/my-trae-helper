#!/usr/bin/env bash
# Pre-push gate for Go preset (Level L2)

set -euo pipefail

echo "==> [L2] Running pre-push gate (go preset)..."

echo "    [1/3] Integration tests..."
go test ./tests/integration/... -tags=integration

echo "    [2/3] Coverage..."
go test ./... -coverprofile=coverage.out -covermode=atomic

echo "    [3/3] Build (cmd/app)..."
mkdir -p bin
go build -o bin/app ./cmd/app

echo "==> [L2] PASSED"