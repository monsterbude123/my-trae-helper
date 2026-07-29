#!/usr/bin/env python3
"""tasks-integrity.py — V9.2 任务完整性检查
Stop Hook: 确认任务结束前 tasks.md 完整性 + 干净重置上下文。

V9.2 变更:
  - 检测 _invalidated/ 上下文 → 区分 clean reset 和正常完成
"""

import sys
import re
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent.parent
specs_dir = project_root / "docs" / "specs"

issues = []

if not specs_dir.exists():
    sys.exit(0)

for feat_dir in specs_dir.iterdir():
    if not feat_dir.is_dir() or feat_dir.name.startswith('.'):
        continue
    if feat_dir.name in ("archive", "changes"):
        continue

    tasks_file = feat_dir / "tasks.md"
    invalidated = feat_dir / "_invalidated"
    is_clean_reset = invalidated.exists()

    if not tasks_file.exists():
        continue

    try:
        content = tasks_file.read_text(encoding="utf-8")
    except Exception:
        continue

    unchecked = re.findall(r'^-\s*\[\s\]\s+.+$', content, re.MULTILINE)
    checked = re.findall(r'^-\s*\[x\]\s+.+$', content, re.MULTILINE)

    total = len(unchecked) + len(checked)

    if is_clean_reset and total == 0:
        issues.append(f"{feat_dir.name}: _invalidated_ exists but no new tasks — 需要重新生成 tasks.md")

    if total == 0:
        continue

    ratio = len(checked) / total if total else 0

    if is_clean_reset and len(checked) > 0 and ratio < 0.5:
        # 干净重置场景：有部分 [x] 但多数 [ ] — 这是正常的（agent 在实现中）
        pass
    elif is_clean_reset and ratio > 0.9:
        # 干净重置场景全完成 — 正常
        print(f"[Tasks Integrity] {feat_dir.name}: {len(checked)}/{total} done (clean reset, {len(subdirs) if invalidated else 0} resets)")
    elif not is_clean_reset and ratio < 0.5:
        issues.append(f"{feat_dir.name}: {len(unchecked)}/{total} unchecked — 任务未完成，确认是否继续？")

if issues:
    print("[Tasks Integrity] ⚠️ 警告:")
    for issue in issues:
        print(f"  - {issue}")
else:
    print("[Tasks Integrity] ✅ 所有活跃 tasks.md 已检查")

sys.exit(0)
