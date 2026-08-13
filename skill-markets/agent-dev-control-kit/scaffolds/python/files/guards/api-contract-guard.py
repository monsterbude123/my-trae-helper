#!/usr/bin/env python3
"""api-contract-guard.py — verify that every service module exposes callable symbols.

Exit 0 on pass, 1 on fail.
"""

from __future__ import annotations

import ast
import sys
from pathlib import Path

ROOT = Path.cwd()
SERVICES_DIR = ROOT / "src" / "services"
SCHEMAS_DIR = ROOT / "schemas" / "api"


def list_modules(d: Path) -> list[Path]:
    if not d.exists():
        return []
    return [p for p in d.glob("*.py") if not p.name.startswith("_")]


def extract_top_level_funcs(path: Path) -> list[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    return [n.name for n in tree.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]


def main() -> int:
    modules = list_modules(SERVICES_DIR)
    if not modules:
        print("[api-contract-guard] No src/services/ — skipped.")
        return 0

    failures = 0
    for m in modules:
        funcs = extract_top_level_funcs(m)
        print(f"[api-contract-guard] {m.name}: funcs = [{', '.join(funcs) or 'none'}]")
        if not funcs:
            print(f"[api-contract-guard] FAIL: {m.name} has no top-level functions")
            failures += 1

    schemas = list(SCHEMAS_DIR.glob("*.json")) if SCHEMAS_DIR.exists() else []
    print(f"[api-contract-guard] schemas: {len(schemas)} found")

    if failures:
        print(f"[api-contract-guard] {failures} failure(s)")
        return 1
    print("[api-contract-guard] PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())