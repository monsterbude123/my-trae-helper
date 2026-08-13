#!/usr/bin/env bash
# init.sh — initialize a Python project from this preset.

set -euo pipefail

echo "==> Initializing Python project..."

if [ ! -f pyproject.toml ]; then
  echo "    ERROR: pyproject.toml not found. Did the preset materialize correctly?"
  exit 1
fi

echo "    [1/3] Creating virtualenv (uv)..."
if command -v uv >/dev/null 2>&1; then
  uv venv
  uv pip install -e ".[dev]"
else
  echo "    (uv not found — falling back to python -m venv)"
  python -m venv .venv
  . .venv/bin/activate
  pip install -e ".[dev]"
fi

echo "    [2/3] Running sanity check..."
pytest tests/unit -v

echo "    [3/3] Validating configs..."
python scripts/validate_config.py

echo "==> Initialization complete. Next steps:"
echo "    - Edit pyproject.toml (project name, author)"
echo "    - Run gates: ./gates/pre-commit.sh"