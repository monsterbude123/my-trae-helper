#!/usr/bin/env python3
"""V11 drift-detect.py — PostToolUse Hook（蒸馏自 V10）

契约漂移检测 + spec-purge 历史感知。

V11 简化:
  - 改用 V11 docs/specs/changes/{id}/contracts/ 路径
  - 增加 V11 gitnexus 调用建议
"""

import re
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
specs_changes_dir = project_root / "docs" / "specs" / "changes"

# ── V11 spec-purge 历史检测 ──
spec_purge_dir = project_root / "docs" / "archive" / "out" / "spec-purge"
reset_features = set()
if spec_purge_dir.exists():
    for purged in spec_purge_dir.iterdir():
        if purged.is_dir():
            reset_features.add(purged.name)

drift_found = False
drift_report = []

if specs_changes_dir.exists():
    for change_dir in specs_changes_dir.iterdir():
        if not change_dir.is_dir():
            continue
        contracts_dir = change_dir / "contracts"
        if not contracts_dir.exists():
            continue

        api_file = contracts_dir / "api-contracts.md"
        if not api_file.exists():
            continue

        feature = change_dir.name
        is_reset = feature in reset_features

        try:
            content = api_file.read_text(encoding="utf-8")
        except Exception:
            continue

        matches = re.findall(r'##\s+(GET|POST|PUT|PATCH|DELETE)\s+(/\S+)', content)
        for method, route in matches:
            route_pattern = re.sub(r':\w+', r'[^/]+', route)
            code_match = False
            for src_dir in ("src", "app", "lib"):
                src_path = project_root / src_dir
                if not src_path.exists():
                    continue
                for ext in ("*.ts", "*.tsx", "*.py", "*.js", "*.jsx", "*.rs", "*.go"):
                    for code_file in src_path.rglob(ext):
                        try:
                            code = code_file.read_text(encoding="utf-8")
                            if re.search(route_pattern, code) and f'"{method}"' in code.upper() or f"'{method}'" in code.upper():
                                code_match = True
                                break
                        except Exception:
                            continue
                    if code_match:
                        break
                if code_match:
                    break

            if not code_match:
                if is_reset:
                    drift_report.append(f"ℹ️ {method} {route} — spec-purged (符合预期)")
                else:
                    drift_report.append(f"🔴 {method} {route} — 契约存在但代码无对应实现")
                    drift_found = True

if drift_report:
    print("[V11 Drift Detect] 契约漂移检测结果:")
    for line in drift_report:
        print(f"  {line}")
    if drift_found:
        print("\n🚨 存在契约漂移 — Stage 3 Implement 必先补实现")
        sys.exit(1)
    else:
        print("\n✅ 漂移均在 spec-purge 历史范围内")
else:
    print("[V11 Drift Detect] ✅ 无漂移")

sys.exit(0)