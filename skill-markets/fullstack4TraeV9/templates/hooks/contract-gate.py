#!/usr/bin/env python3
"""contract-gate.py — V9.2 契约门禁
PreToolUse Hook: 编码前检查契约是否就绪 + 方向是否已变。
"""

import sys
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent.parent

# ── _invalidated_ 检测 ──
specs_dir = project_root / "docs" / "specs"
if specs_dir.exists():
    for feat_dir in specs_dir.iterdir():
        if not feat_dir.is_dir():
            continue
        invalidated = feat_dir / "_invalidated"
        if invalidated.exists():
            contracts = feat_dir / "contracts"
            if not contracts.exists() or not list(contracts.iterdir()):
                print(f"[Contract Gate] ⚠️ {feat_dir.name}: _invalidated_ detected but contracts/ missing")
                print(f"    → 方向已变（铁律 11），contracts/ 需要重新生成")
                # 不阻断，但警告
                continue

# ── 契约检查 ──
project_contracts = project_root / "contracts"
has_contracts = project_contracts.exists() and bool(list(project_contracts.iterdir()))
has_spec_contracts = False
if specs_dir.exists():
    for feat_dir in specs_dir.iterdir():
        if feat_dir.is_dir() and (feat_dir / "contracts").exists():
            has_spec_contracts = True
            break

if not has_contracts and not has_spec_contracts:
    print("[Contract Gate] ⚠️ No contracts/ found in project or specs/")
    print("    → 对于纯后端变更，建议先定义 contracts/")
    # 不阻断，仅提示

sys.exit(0)
