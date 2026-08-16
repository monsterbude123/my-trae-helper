#!/usr/bin/env python3
"""V11 contract-gate.py — PreToolUse Hook（蒸馏自 V10）

编码前检查契约是否就绪 + spec-purge 历史是否已迁移。
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


project_root = resolve_project_root()
specs_changes_dir = project_root / "docs" / "specs" / "changes"
spec_purge_dir = project_root / "docs" / "archive" / "out" / "spec-purge"

# ── V11 spec-purge 历史检测 ──
if spec_purge_dir.exists():
    if specs_changes_dir.exists():
        for change_dir in specs_changes_dir.iterdir():
            if not change_dir.is_dir():
                continue
            contracts = change_dir / "contracts"
            if not contracts.exists() or not list(contracts.iterdir()):
                print(f"[V11 Contract Gate] ⚠️ {change_dir.name}: spec-purge 历史存在但 contracts/ 缺失")
                print(f"    → V11 spec-purge.py 已归档旧契约，contracts/ 需重新生成")

# ── 契约检查 ──
project_contracts = project_root / "contracts"
has_contracts = project_contracts.exists() and bool(list(project_contracts.iterdir()))
has_spec_contracts = False
if specs_changes_dir.exists():
    for change_dir in specs_changes_dir.iterdir():
        if change_dir.is_dir() and (change_dir / "contracts").exists():
            has_spec_contracts = True
            break

if not has_contracts and not has_spec_contracts:
    print("[V11 Contract Gate] 🛑 BLOCKED: No contracts/ found in project or specs/changes/")
    print("    → contracts/ 缺失，禁止写代码")
    print("    → 修复: 纯后端项目先定义 contracts/，前后端项目运行 stage-1-intake 生成 specs/changes/{id}/contracts/")
    # Trae 官方 schema: PreToolUse 阻断必须 exit=2 + permissionDecision: "deny" JSON
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": "contracts/ 缺失或为空，禁止写代码"
        }
    }))
    sys.exit(2)

print("[V11 Contract Gate] ✅ 检查完成")
sys.exit(0)