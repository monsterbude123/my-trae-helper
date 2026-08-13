#!/usr/bin/env python3
"""validate_config.py — sanity-check the gate/guard configs for the Python preset."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path.cwd()


def check(label: str, ok: bool) -> bool:
    print(f"{'✅' if ok else '❌'} {label}")
    return ok


def main() -> int:
    ok = True
    ok &= check("pyproject.toml exists", (ROOT / "pyproject.toml").exists())
    ok &= check("gates/gate-config.json exists", (ROOT / "gates" / "gate-config.json").exists())
    ok &= check("guards/guard-config.json exists", (ROOT / "guards" / "guard-config.json").exists())

    try:
        gate = json.loads((ROOT / "gates" / "gate-config.json").read_text(encoding="utf-8"))
        ok &= check("gate-config has L1", bool(gate.get("levels", {}).get("L1")))
        ok &= check("gate-config has L2", bool(gate.get("levels", {}).get("L2")))
    except Exception as e:  # noqa: BLE001
        print(f"❌ gate-config.json invalid: {e}")
        ok = False

    try:
        guard = json.loads((ROOT / "guards" / "guard-config.json").read_text(encoding="utf-8"))
        ok &= check(
            f"guard-config has {len(guard.get('guards', []))} guard(s)",
            len(guard.get("guards", [])) > 0,
        )
    except Exception as e:  # noqa: BLE001
        print(f"❌ guard-config.json invalid: {e}")
        ok = False

    if not ok:
        print("Validation FAILED")
        return 1
    print("Validation PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())