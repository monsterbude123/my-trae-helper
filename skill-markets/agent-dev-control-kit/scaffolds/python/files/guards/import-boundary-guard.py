#!/usr/bin/env python3
"""import-boundary-guard.py — forbid cross-layer imports in a layered architecture.

Default rules (overridable via guard-config.json → forbidden_patterns):
  - src/services/ must NOT import from src/api/ or src/db/

Exit 0 on pass, 1 on any violation.
"""

from __future__ import annotations

import ast
import json
import re
import sys
from pathlib import Path

ROOT = Path.cwd()
CONFIG_PATH = ROOT / "guards" / "guard-config.json"

DEFAULT_RULES = [
    {"from": "src/services/", "to": "src/api/"},
    {"from": "src/services/", "to": "src/db/"},
]


def load_rules() -> list[dict]:
    if not CONFIG_PATH.exists():
        return DEFAULT_RULES
    try:
        cfg = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
        for g in cfg.get("guards", []):
            if g.get("id") == "import-boundary":
                return g.get("forbidden_patterns", DEFAULT_RULES)
    except (OSError, json.JSONDecodeError):
        pass
    return DEFAULT_RULES


def iter_python_files(d: Path) -> list[Path]:
    if not d.exists():
        return []
    return [p for p in d.rglob("*.py") if not p.name.startswith("_")]


def extract_imports(path: Path) -> list[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    imports: list[str] = []
    for n in ast.walk(tree):
        if isinstance(n, ast.Import):
            for alias in n.names:
                imports.append(alias.name)
        elif isinstance(n, ast.ImportFrom):
            if n.module:
                imports.append(n.module)
    return imports


def main() -> int:
    rules = load_rules()
    src_dir = ROOT / "src"
    files = iter_python_files(src_dir)
    if not files:
        print("[import-boundary-guard] No src/ — skipped.")
        return 0

    rel_files = [f.relative_to(ROOT).as_posix() for f in files]
    violations: list[str] = []

    for f, rel in zip(files, rel_files):
        for imp in extract_imports(f):
            for rule in rules:
                if rel.startswith(rule["from"]) and imp.replace(".", "/").startswith(
                    rule["to"].rstrip("/")
                ):
                    violations.append(f"{rel}: forbidden import '{imp}' (rule {rule['from']} → {rule['to']})")

    if violations:
        print("[import-boundary-guard] VIOLATIONS:")
        for v in violations:
            print(f"  - {v}")
        return 1

    print("[import-boundary-guard] PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())