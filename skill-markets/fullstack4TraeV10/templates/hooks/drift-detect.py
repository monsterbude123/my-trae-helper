#!/usr/bin/env python3
"""drift-detect.py — V10.1 契约漂移检测
PostToolUse Hook: 编码后检测契约与代码不一致。

V10.1 变更:
  - spec-purge 历史感知: 若方向已变（旧契约已归档到 archive/out/spec-purge/），跳过旧端点比对
"""

import re
import sys
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent.parent
contracts_dir = project_root / "docs" / "specs"

# ── spec-purge 历史检测（V10.1 取代 V9.2 _invalidated/）──
spec_purge_dir = project_root / "docs" / "archive" / "out" / "spec-purge"
reset_features = set()
if spec_purge_dir.exists():
    for purged in spec_purge_dir.iterdir():
        if purged.is_dir():
            reset_features.add(purged.name)

drift_found = False
drift_report = []

if contracts_dir.exists():
    for api_file in contracts_dir.rglob("api-contracts.md"):
        # 跳过 archive/out/ 下的旧契约
        if "archive" in api_file.parts:
            continue

        feature = api_file.parent.parent.name
        is_reset = feature in reset_features

        try:
            content = api_file.read_text(encoding="utf-8")
        except Exception:
            continue

        matches = re.findall(r'##\s+(GET|POST|PUT|PATCH|DELETE)\s+(/\S+)', content)
        for method, route in matches:
            # 在代码中搜索对应路由
            route_pattern = re.sub(r':\w+', r'[^/]+', route)
            code_match = False
            for src_dir in ("src", "app", "lib"):
                src_path = project_root / src_dir
                if not src_path.exists():
                    continue
                for ext in ("*.ts", "*.tsx", "*.py", "*.js", "*.jsx"):
                    for src_file in src_path.rglob(ext):
                        try:
                            text = src_file.read_text(encoding="utf-8")
                        except Exception:
                            continue
                        for line in text.splitlines():
                            if re.search(route_pattern, line):
                                code_match = True
                                break
                        if code_match:
                            break
                    if code_match:
                        break
                if code_match:
                    break

            if not code_match:
                if is_reset:
                    # 方向已变 — 旧端点被归档是正常的
                    drift_report.append(
                        f"ℹ️  {method} {route} not found (spec-purged — expected)"
                    )
                else:
                    drift_found = True
                    drift_report.append(f"🔴 {method} {route} not found in source")

if drift_report:
    print("[Drift Detect] Result:")
    for r in drift_report:
        print(f"   {r}")
    if drift_found:
        print("   🛑 Contract drift detected — re-validate")
else:
    print("[Drift Detect] ✅ No contract drift")

sys.exit(0)
