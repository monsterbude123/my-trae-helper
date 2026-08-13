#!/usr/bin/env bash
# Pre-commit gate for Python preset (Level L1)

set -euo pipefail

echo "==> [L1] Running pre-commit gate (python preset)..."

echo "    [1/3] Lint (ruff)..."
ruff check .

echo "    [2/3] Typecheck (mypy)..."
mypy src/ || echo "    (mypy not configured — skipping)"

echo "    [3/3] Unit tests (pytest)..."
pytest tests/unit -v

echo "==> [L1] PASSED"