#!/usr/bin/env python3
"""scan-templates.py — 扫描模板解析结果（回归扫描 / 审计）

借鉴 spec-kit resolve_template 设计，扫描 V10 项目实际使用的模板路径，
确保项目级 overrides 真正生效，未被静默回退到 V10 内置。

支持扫描的模板名（与 templates/ 下文件名对齐）:
  - spec-template          （setup-feature.py 用）
  - constitution-template  （项目初始化 constitution 用）
  - checklist-template     （checklist 生成用）

特性:
  - --json 机械可解析
  - --strict 严格模式：任一模板无匹配 = 退出码 1
  - 不创建任何文件，纯只读扫描

用法:
  python scripts/scan-templates.py
  python scripts/scan-templates.py --project-root /path/to/project
  python scripts/scan-templates.py --json
  python scripts/scan-templates.py --strict

环境变量:
  V10_FEATURE   feature 名（仅用于路径检测，不影响模板解析）
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import List

# 允许直接执行或 import
try:
    from common import emit_json, get_project_root, resolve_template
except ImportError:  # pragma: no cover
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from common import emit_json, get_project_root, resolve_template


# V10 技能包根（用于解析 L3 内置模板）
V10_PACKAGE_ROOT = Path(__file__).resolve().parent.parent

# 扫描的模板清单（与 templates/ 下文件名对齐）
SCAN_TEMPLATES: List[str] = [
    "spec-template",
    "constitution-template",
    "checklist-template",
]


def _classify_source(
    resolved: Path,
    project_root: Path,
    template_name: str,
) -> str:
    """分类模板来源（project-overrides / v10-core / unknown）

    Args:
        resolved: 解析到的模板路径
        project_root: V10 项目根
        template_name: 模板名（不含 .md）

    Returns:
        来源标签
    """
    override_path = (
        project_root / "docs" / "templates" / "overrides" / f"{template_name}.md"
    )
    try:
        if resolved.resolve() == override_path.resolve():
            return "project-overrides"
    except OSError:
        pass
    return "v10-core"


def scan(project_root: Path) -> dict:
    """扫描所有模板的解析结果

    Returns:
        {
            "project_root": str,
            "v10_package_root": str,
            "templates": [
                {
                    "name": "spec-template",
                    "resolved_path": str | None,
                    "source": "project-overrides" | "v10-core" | "missing",
                },
                ...
            ],
            "missing_count": int,
        }
    """
    results = []
    missing_count = 0
    for name in SCAN_TEMPLATES:
        resolved = resolve_template(project_root, name, V10_PACKAGE_ROOT)
        if resolved is None:
            results.append(
                {"name": name, "resolved_path": None, "source": "missing"}
            )
            missing_count += 1
        else:
            source = _classify_source(resolved, project_root, name)
            results.append(
                {
                    "name": name,
                    "resolved_path": str(resolved),
                    "source": source,
                }
            )
    return {
        "project_root": str(project_root),
        "v10_package_root": str(V10_PACKAGE_ROOT),
        "templates": results,
        "missing_count": missing_count,
    }


def _print_text(result: dict) -> None:
    """文本模式输出"""
    print(f"Project: {result['project_root']}")
    print(f"V10 pkg: {result['v10_package_root']}")
    print()
    print("Templates:")
    for t in result["templates"]:
        if t["source"] == "project-overrides":
            icon = "🎯"
        elif t["source"] == "v10-core":
            icon = "📦"
        else:
            icon = "❌"
        print(f"  {icon} {t['name']:<24} [{t['source']}]")
        if t["resolved_path"]:
            print(f"     → {t['resolved_path']}")
        else:
            print(f"     → (无匹配)")
    print()
    if result["missing_count"] > 0:
        print(f"⚠️ {result['missing_count']} 个模板无匹配（将走最小骨架或失败）")
    else:
        print("✅ 全部模板均可解析")


def main(argv: List[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="V10 模板解析回归扫描",
        add_help=False,
    )
    parser.add_argument("--project-root", type=str, help="项目根路径")
    parser.add_argument("--json", action="store_true", help="JSON 格式输出")
    parser.add_argument(
        "--strict",
        action="store_true",
        help="严格模式：任一模板无匹配 = 退出码 1",
    )
    parser.add_argument("--help", "-h", action="store_true", help="显示帮助")

    args = parser.parse_args(argv)

    if args.help:
        print(__doc__)
        return 0

    project_root = (
        Path(args.project_root).resolve() if args.project_root else get_project_root()
    )
    result = scan(project_root)

    if args.json:
        emit_json(result)
    else:
        _print_text(result)

    if args.strict and result["missing_count"] > 0:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
