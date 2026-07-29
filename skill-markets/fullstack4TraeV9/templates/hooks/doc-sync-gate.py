#!/usr/bin/env python3
"""doc-sync-gate.py — V9.2 文档同步门禁
PreToolUse Hook: 编码前检查 DOC SYNC 是否完成 + 方向是否已变。
"""

import sys
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent.parent
state_card = project_root / "docs" / "specs" / ".state-card.md"

# ── _invalidated_ 检测 ──
specs_dir = project_root / "docs" / "specs"
reset_detected = False
if specs_dir.exists():
    for feat_dir in specs_dir.iterdir():
        if feat_dir.is_dir() and (feat_dir / "_invalidated").exists():
            reset_detected = True
            break

if reset_detected:
    print("[Doc-Sync Gate] ⚠️ Clean reset detected — _invalidated/ exists")
    print("    → 旧 DOC SYNC 状态已废弃，按新方向工作")
    print("    → 实现前确保新 contracts/ + define.md 已就绪")

# ── DOC SYNC 检查 ──
if not state_card.exists():
    print("[Doc-Sync Gate] ⚠️ .state-card.md missing — run intake first")
    sys.exit(0)

# 检查 modules/ 是否存在（DOC SYNC 产出）
modules_dir = project_root / "docs" / "modules"
if not modules_dir.exists() or not list(modules_dir.iterdir()):
    print("[Doc-Sync Gate] ℹ️ docs/modules/ empty — DOC SYNC not yet executed")

sys.exit(0)
