#!/usr/bin/env python3
"""drift-detect.py — V9.2 契约漂移检测
PostToolUse Hook: 编码后检测契约与代码不一致。

V9.2 变更:
  - _invalidated_ 上下文检测: 若方向已变，跳过旧端点比对（已移除的端点是正常重构）
"""

import re
import sys
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent.parent
contracts_dir = project_root / "docs" / "specs"

# ── _invalidated_ 检测 ──
reset_features = set()
if contracts_dir.exists():
    for feat_dir in contracts_dir.iterdir():
        if feat_dir.is_dir() and (feat_dir / "_invalidated").exists():
            reset_features.add(feat_dir.name)

drift_found = False
drift_report = []

if contracts_dir.exists():
    for api_file in contracts_dir.rglob("api-contracts.md"):
        # 跳过 _invalidated/ 内的文件
        if "_invalidated" in str(api_file):
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
                    # 方向已变 — 旧端点被移除是正常的
                    drift_report.append(
                        f"ℹ️  {method} {route} not found (clean reset — expected)"
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
