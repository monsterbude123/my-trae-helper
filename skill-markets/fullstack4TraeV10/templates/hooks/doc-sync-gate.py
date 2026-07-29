#!/usr/bin/env python3
"""doc-sync-gate.py — V10.1 文档同步门禁
PreToolUse Hook: 编码前检查 DOC SYNC 是否完成 + spec-purge 历史是否已迁移。

V10.1 变更:
  - _invalidated_ 机制已废止，改用 archive/out/spec-purge/ 路径
"""

import sys
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent.parent
state_card = project_root / "docs" / "specs" / ".state-card.md"

# ── spec-purge 历史检测（V10.1 取代 V9.2 _invalidated/）──
spec_purge_dir = project_root / "docs" / "archive" / "out" / "spec-purge"
if spec_purge_dir.exists():
    print("[Doc-Sync Gate] ℹ️ spec-purge history 已迁移到 archive/out/spec-purge/")
    print("    → 旧 DOC SYNC 状态已被 spec-purge.py 归档")
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
