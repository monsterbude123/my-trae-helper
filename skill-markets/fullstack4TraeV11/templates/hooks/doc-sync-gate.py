#!/usr/bin/env python3
"""V11 doc-sync-gate.py — PreToolUse Hook（蒸馏自 V10）

编码前检查 DOC SYNC + spec-purge 历史是否已迁移。
"""

import sys
import json
from pathlib import Path


def resolve_project_root() -> Path:
    cursor = Path(__file__).resolve().parent
    while cursor != cursor.parent:
        if (cursor / ".trae").exists() or (cursor / "docs").exists():
            return cursor
        cursor = cursor.parent
    return Path(__file__).resolve().parent.parent.parent


def resolve_state_card(project_root: Path) -> Path | None:
    # 优先新路径 docs/specs/changes/*/.state-card.md
    for p in (project_root / "docs" / "specs" / "changes").glob("*/**/.state-card.md"):
        return p
    # 再试顶层旧路径
    top = project_root / "docs" / "specs" / ".state-card.md"
    return top if top.exists() else None


project_root = resolve_project_root()
state_card = resolve_state_card(project_root)

# ── spec-purge 历史检测 ──
spec_purge_dir = project_root / "docs" / "archive" / "out" / "spec-purge"
if spec_purge_dir.exists():
    print("[V11 Doc-Sync Gate] ℹ️ spec-purge history 已迁移到 archive/out/spec-purge/")
    print("    → 旧 DOC SYNC 状态已被 spec-purge.py 归档")
    print("    → 实现前确保新 contracts/ + define.md 已就绪")

# ── DOC SYNC 检查 ──
if state_card is None or not state_card.exists():
    print("[V11 Doc-Sync Gate] 🛑 BLOCKED: state card missing (docs/specs/changes/*/ or docs/specs/)")
    print("    → DOC SYNC 未完成，禁止写代码")
    print("    → 修复: 运行 intake 或 stage-1-intake 生成 .state-card.md")
    # Trae 官方 schema: PreToolUse 阻断必须 exit=2 + permissionDecision: "deny" JSON
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": "DOC SYNC 未完成，state card 缺失"
        }
    }))
    sys.exit(2)

# 检查 modules/ 是否存在（DOC SYNC 产出）
modules_dir = project_root / "docs" / "modules"
if not modules_dir.exists() or not any(modules_dir.iterdir()):
    print("[V11 Doc-Sync Gate] 🛑 BLOCKED: docs/modules/ empty or missing")
    print("    → DOC SYNC 未完成，禁止写代码")
    print("    → 修复: 运行 stage-2-doc-sync 生成 docs/modules/")
    # Trae 官方 schema: PreToolUse 阻断必须 exit=2 + permissionDecision: "deny" JSON
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": "DOC SYNC 未完成，docs/modules/ 缺失或为空"
        }
    }))
    sys.exit(2)

print("[V11 Doc-Sync Gate] ✅ DOC SYNC 状态 OK")
sys.exit(0)