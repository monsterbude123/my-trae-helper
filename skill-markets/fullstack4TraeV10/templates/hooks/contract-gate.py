#!/usr/bin/env python3
"""contract-gate.py — V10.1 契约门禁
PreToolUse Hook: 编码前检查契约是否就绪 + spec-purge 历史是否已迁移。

V10.1 变更:
  - _invalidated_ 机制已废止，改用 archive/out/spec-purge/ 路径
"""

import sys
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent.parent

# ── spec-purge 历史检测（V10.1 取代 V9.2 _invalidated/）──
spec_purge_dir = project_root / "docs" / "archive" / "out" / "spec-purge"
specs_dir = project_root / "docs" / "specs"

if spec_purge_dir.exists():
    # spec-purge 存在时，检查对应 feature 是否还缺新契约
    if specs_dir.exists():
        for feat_dir in specs_dir.iterdir():
            if not feat_dir.is_dir():
                continue
            contracts = feat_dir / "contracts"
            if not contracts.exists() or not list(contracts.iterdir()):
                print(f"[Contract Gate] ⚠️ {feat_dir.name}: spec-purge 历史存在但 contracts/ 缺失")
                print(f"    → V10 spec-purge.py 已归档旧契约，contracts/ 需重新生成")
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
