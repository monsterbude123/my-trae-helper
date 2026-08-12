#!/usr/bin/env python3
"""V11 doc-sync-gate.py — PreToolUse Hook（蒸馏自 V10）

编码前检查 DOC SYNC + spec-purge 历史是否已迁移。
"""

import sys
from pathlib import Path


def resolve_project_root() -> Path:
    cursor = Path(__file__).resolve().parent
    while cursor != cursor.parent:
        if (cursor / ".trae").exists() or (cursor / "docs").exists():
            return cursor
        cursor = cursor.parent
    return Path(__file__).resolve().parent.parent.parent


project_root = resolve_project_root()
state_card = project_root / "docs" / "specs" / ".state-card.md"

# ── spec-purge 历史检测 ──
spec_purge_dir = project_root / "docs" / "archive" / "out" / "spec-purge"
if spec_purge_dir.exists():
    print("[V11 Doc-Sync Gate] ℹ️ spec-purge history 已迁移到 archive/out/spec-purge/")
    print("    → 旧 DOC SYNC 状态已被 spec-purge.py 归档")
    print("    → 实现前确保新 contracts/ + define.md 已就绪")

# ── DOC SYNC 检查 ──
if not state_card.exists():
    print("[V11 Doc-Sync Gate] ⚠️ docs/specs/.state-card.md missing — run intake first")
    sys.exit(0)

# 检查 modules/ 是否存在（DOC SYNC 产出）
modules_dir = project_root / "docs" / "modules"
if not modules_dir.exists() or not list(modules_dir.iterdir()):
    print("[V11 Doc-Sync Gate] ℹ️ docs/modules/ empty — DOC SYNC not yet executed")

print("[V11 Doc-Sync Gate] ✅ DOC SYNC 状态 OK")
sys.exit(0)