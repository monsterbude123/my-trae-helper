#!/usr/bin/env python3
"""
V11 orphan-detector.py — 孤儿契约测试扫描（rot #12 修复）

Usage:
    python orphan-detector.py [--type contract|test] [--output <path>]

Exit codes:
    0 = PASS（无孤儿）
    1 = FAIL（发现孤儿测试，输出 orphans.json）
"""
import sys
import argparse
import pathlib
import json
import re
from datetime import datetime, timezone


def scan_orphan_contract_tests(project_root: pathlib.Path) -> list:
    """扫描 __tests__/contracts/ 中引用已不存在的 contract"""
    orphans = []

    test_dirs = [
        project_root / "__tests__/contracts",
        project_root / "tests/contracts",
        project_root / "src/**/__tests__/contracts",
    ]

    # V12 物理布局:contracts 位于 change_dir/fact/contracts/ 下
    contracts_dir = project_root / "docs" / "specs" / "changes" / "*" / "fact" / "contracts"

    test_files = []
    for td in test_dirs:
        if "*" in str(td):
            test_files.extend(td.parent.rglob("*.test.*"))
        elif td.exists():
            test_files.extend(td.rglob("*.test.*"))

    if not test_files:
        return orphans

    # 收集所有 contract 接口(V12:走 fact/contracts/ 路径)
    contract_interfaces = set()
    for contracts_root in [project_root / "docs" / "specs" / "changes"]:
        if not contracts_root.exists():
            continue
        for contracts_dir in contracts_root.rglob("api-contracts.md"):
            try:
                content = contracts_dir.read_text(encoding="utf-8")
                # 提取 - path: /api/v1/... 或 method + path
                for m in re.finditer(r"path:\s*([/\w\-]+)", content):
                    contract_interfaces.add(m.group(1))
            except Exception:
                pass

    # 检测每个测试文件引用的接口是否在 contract 中存在
    for tf in test_files:
        try:
            content = tf.read_text(encoding="utf-8")
        except Exception:
            continue

        # 提取测试中引用的 API 路径
        referenced = set()
        for m in re.finditer(r"['\"](/api/v1[^'\"]+)['\"]", content):
            referenced.add(m.group(1))

        for ref in referenced:
            if ref not in contract_interfaces:
                orphans.append({
                    "test_file": str(tf.relative_to(project_root)),
                    "references": [ref],
                    "exists_in_contracts": False,
                    "action": "delete_or_update",
                })

    return orphans


def main():
    parser = argparse.ArgumentParser(description="V11 孤儿契约测试扫描")
    parser.add_argument("--type", default="contract", choices=["contract", "test"], help="扫描类型")
    parser.add_argument("--project-root", default=".", help="项目根路径")
    parser.add_argument("--output", default="orphans.json", help="orphans.json 输出路径")
    parser.add_argument("--json", action="store_true", help="JSON 输出")
    args = parser.parse_args()

    project_root = pathlib.Path(args.project_root).resolve()

    orphans = scan_orphan_contract_tests(project_root)

    output = {
        "scan_at": datetime.now(timezone.utc).isoformat(),
        "scan_type": args.type,
        "stats": {"total_orphans": len(orphans)},
        "orphans": orphans,
        "status": "PASS" if not orphans else "FAIL",
    }

    pathlib.Path(args.output).write_text(
        json.dumps(output, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    if args.json:
        print(json.dumps(output, indent=2, ensure_ascii=False))
    else:
        if orphans:
            print(f"❌ FAIL — 发现 {len(orphans)} 个孤儿")
            for o in orphans:
                print(f"   - {o['test_file']}: {o['references']}")
        else:
            print(f"✅ PASS — 无孤儿测试")

    return 0 if not orphans else 1


if __name__ == "__main__":
    sys.exit(main())