#!/usr/bin/env python3
"""test-coverage-guard.py — run pytest with coverage and enforce >= threshold."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path.cwd()
CONFIG_PATH = ROOT / "guards" / "guard-config.json"
DEFAULT_THRESHOLD = 80


def load_threshold() -> int:
    if not CONFIG_PATH.exists():
        return DEFAULT_THRESHOLD
    try:
        cfg = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
        for g in cfg.get("guards", []):
            if g.get("id") == "test-coverage":
                return int(g.get("threshold", DEFAULT_THRESHOLD))
    except (OSError, json.JSONDecodeError):
        pass
    return DEFAULT_THRESHOLD


def main() -> int:
    threshold = load_threshold()
    print(f"[test-coverage-guard] threshold = {threshold}%")
    result = subprocess.run(
        ["pytest", "--cov=src", "--cov-report=term", "--cov-fail-under", str(threshold)],
        cwd=ROOT,
    )
    if result.returncode != 0:
        print(f"[test-coverage-guard] FAILED (exit={result.returncode})")
        return result.returncode
    print("[test-coverage-guard] PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())