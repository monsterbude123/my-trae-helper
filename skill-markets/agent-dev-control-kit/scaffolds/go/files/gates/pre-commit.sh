#!/usr/bin/env bash
# Pre-commit gate for Go preset (Level L1)

set -euo pipefail

echo "==> [L1] Running pre-commit gate (go preset)..."

echo "    [1/3] Lint (golangci-lint / go vet)..."
if command -v golangci-lint >/dev/null 2>&1; then
  golangci-lint run
else
  echo "    (golangci-lint not found — falling back to go vet)"
  go vet ./...
fi

echo "    [2/3] Typecheck (go build)..."
go build ./...

echo "    [3/3] Unit tests (go test -short)..."
go test ./internal/... -short

echo "==> [L1] PASSED"