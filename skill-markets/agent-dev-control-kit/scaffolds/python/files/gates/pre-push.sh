#!/usr/bin/env bash
# Pre-push gate for Python preset (Level L2)

set -euo pipefail

echo "==> [L2] Running pre-push gate (python preset)..."

echo "    [1/3] Integration tests..."
pytest tests/integration -v

echo "    [2/3] Coverage..."
pytest --cov=src --cov-report=term-missing

echo "    [3/3] Build..."
python -m build

echo "==> [L2] PASSED"