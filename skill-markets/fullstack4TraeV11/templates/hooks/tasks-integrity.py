#!/usr/bin/env python3
"""V11 tasks-integrity.py — Stop Hook（蒸馏自 V10）

任务完整性检查 + spec-purge 历史上下文。
"""

import sys
import re
from pathlib import Path


def resolve_project_root() -> Path:
    cursor = Path(__file__).resolve().parent
    while cursor != cursor.parent:
        if (cursor / ".trae").exists() or (cursor / "docs").exists():
            return cursor
        cursor = cursor.parent
    return Path(__file__).resolve().parent.parent.parent


project_root = resolve_project_root()
specs_changes_dir = project_root / "docs" / "specs" / "changes"
spec_purge_dir = project_root / "docs" / "archive" / "out" / "spec-purge"

issues = []

if not specs_changes_dir.exists():
    sys.exit(0)

# 收集所有已 spec-purge 的 change-id
purged_changes = set()
if spec_purge_dir.exists():
    for purged in spec_purge_dir.iterdir():
        if purged.is_dir():
            purged_changes.add(purged.name)

for change_dir in specs_changes_dir.iterdir():
    if not change_dir.is_dir() or change_dir.name.startswith('.'):
        continue

    tasks_file = change_dir / "tasks.md"
    is_purged = change_dir.name in purged_changes

    if not tasks_file.exists():
        if is_purged:
            issues.append(f"{change_dir.name}: spec-purge 历史存在但无 tasks.md — 需要重新生成")
        continue

    try:
        content = tasks_file.read_text(encoding="utf-8")
    except Exception:
        continue

    unchecked = re.findall(r'^-\s*\[\s\]\s+.+$', content, re.MULTILINE)
    checked = re.findall(r'^-\s*\[x\]\s+.+$', content, re.MULTILINE)

    total = len(unchecked) + len(checked)

    if total == 0:
        if is_purged:
            issues.append(f"{change_dir.name}: spec-purge 历史存在但 tasks.md 为空 — 需要重新生成")
        continue

    ratio = len(checked) / total if total else 0

    if is_purged and len(checked) > 0 and ratio < 0.5:
        # spec-purge 场景：有部分 [x] 但多数 [ ] — 这是正常的（agent 在实现中）
        pass
    elif is_purged and ratio > 0.9:
        print(f"[V11 Tasks Integrity] {change_dir.name}: {len(checked)}/{total} done (spec-purged, ok)")
    elif not is_purged and ratio < 0.5:
        issues.append(f"{change_dir.name}: {len(unchecked)}/{total} unchecked — 任务未完成，确认是否继续？")

if issues:
    print("[V11 Tasks Integrity] ⚠️ 警告:")
    for issue in issues:
        print(f"  - {issue}")
else:
    print("[V11 Tasks Integrity] ✅ 所有活跃 tasks.md 已检查")

sys.exit(0)