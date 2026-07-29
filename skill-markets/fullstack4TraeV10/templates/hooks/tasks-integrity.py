#!/usr/bin/env python3
"""tasks-integrity.py — V10.1 任务完整性检查
Stop Hook: 确认任务结束前 tasks.md 完整性 + spec-purge 历史上下文。

V10.1 变更:
  - _invalidated_ 机制已废止，改用 archive/out/spec-purge/ 路径
"""

import sys
import re
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent.parent
specs_dir = project_root / "docs" / "specs"
spec_purge_dir = project_root / "docs" / "archive" / "out" / "spec-purge"

issues = []

if not specs_dir.exists():
    sys.exit(0)

# 收集所有已 spec-purge 的 feature 名
purged_features = set()
if spec_purge_dir.exists():
    for purged in spec_purge_dir.iterdir():
        if purged.is_dir():
            purged_features.add(purged.name)

for feat_dir in specs_dir.iterdir():
    if not feat_dir.is_dir() or feat_dir.name.startswith('.'):
        continue
    if feat_dir.name in ("archive", "changes"):
        continue

    tasks_file = feat_dir / "tasks.md"
    is_purged = feat_dir.name in purged_features

    if not tasks_file.exists():
        if is_purged:
            issues.append(f"{feat_dir.name}: spec-purge 历史存在但无 tasks.md — 需要重新生成")
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
            issues.append(f"{feat_dir.name}: spec-purge 历史存在但 tasks.md 为空 — 需要重新生成")
        continue

    ratio = len(checked) / total if total else 0

    if is_purged and len(checked) > 0 and ratio < 0.5:
        # spec-purge 场景：有部分 [x] 但多数 [ ] — 这是正常的（agent 在实现中）
        pass
    elif is_purged and ratio > 0.9:
        # spec-purge 场景全完成 — 正常
        print(f"[Tasks Integrity] {feat_dir.name}: {len(checked)}/{total} done (spec-purged, ok)")
    elif not is_purged and ratio < 0.5:
        issues.append(f"{feat_dir.name}: {len(unchecked)}/{total} unchecked — 任务未完成，确认是否继续？")

if issues:
    print("[Tasks Integrity] ⚠️ 警告:")
    for issue in issues:
        print(f"  - {issue}")
else:
    print("[Tasks Integrity] ✅ 所有活跃 tasks.md 已检查")

sys.exit(0)
