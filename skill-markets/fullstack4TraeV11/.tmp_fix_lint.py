#!/usr/bin/env python3
"""Add pyflakes-import-not-found guard to check_lint_pre_existing."""
import sys
from pathlib import Path

path = Path("d:/workspace/my-trae-helper/skill-markets/fullstack4TraeV11/scripts/commit-minimum-check.py")
s = path.read_text(encoding="utf-8")

old = (
    "    rc, out, err = _run_cmd(PYFLAKES_CMD + [\"scripts/\"], cwd=project_root, timeout=60)\n"
    "    # pyflakes \\u8f93\\u51fa\\u683c\\u5f0f: <file>:<line>: <warning>\n"
    "    warnings_by_file: dict = {}"
)

new = (
    "    rc, out, err = _run_cmd(PYFLAKES_CMD + [\"scripts/\"], cwd=project_root, timeout=60)\n"
    "    # \\u5f02\\u5e38\\u963b\\u65ad:pyflakes \\u672a\\u88c5\n"
    "    if rc == 127 and \"No module named pyflakes\" in (err or \"\"):\n"
    "        return CheckResult(\n"
    "            name=\"lint-pre-existing\",\n"
    "            status=\"warn\",\n"
    "            detail=\"pyflakes \\u672a\\u5b89\\u88c5(\\u8df3\\u8fc7)\",\n"
    "            exit_code=0,\n"
    "            evidence={\"missing_module\": \"pyflakes\"},\n"
    "        )\n"
    "    # pyflakes \\u8f93\\u51fa\\u683c\\u5f0f: <file>:<line>: <warning>\n"
    "    warnings_by_file: dict = {}"
)

if old not in s:
    print("ERROR: old block not found")
    sys.exit(1)

s = s.replace(old, new)
path.write_text(s, encoding="utf-8")
print("OK replaced")
