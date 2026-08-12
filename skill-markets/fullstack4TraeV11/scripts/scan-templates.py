#!/usr/bin/env python3
"""scan-templates.py — V11.1 模板解析回归扫描（蒸馏自 V10）

扫描 V11 项目实际使用的模板路径，确保项目级 overrides 真正生效，未被静默回退到 V11 内置。

支持扫描的模板名（与 V11 templates/ 下文件名对齐）:
  - spec-template          （setup-feature.py 用）
  - constitution-template  （项目初始化 constitution 用）
  - checklist-template     （Stage 1 Spec → Stage 2 Contract 门禁用）
  - state-card             （Intake 初始化用）
  - bug-template           （Bug Fix 录入用）

特性:
  - --json 机械可解析
  - --strict 严格模式：任一模板无匹配 = 退出码 1
  - 不创建任何文件，纯只读扫描

用法:
  python scripts/scan-templates.py
  python scripts/scan-templates.py --project-root /path/to/project
  python scripts/scan-templates.py --json
  python scripts/scan-templates.py --strict
"""
import argparse
import json
import sys
from pathlib import Path
from typing import List, Optional


V11_PACKAGE_ROOT = Path(__file__).resolve().parent.parent

# 扫描的模板清单（与 V11 templates/ 下文件名对齐）
SCAN_TEMPLATES: List[str] = [
    "spec-template",
    "constitution-template",
    "checklist-template",
    "state-card",
    "bug-template",
]


def resolve_template(project_root: Path, template_name: str, package_root: Path) -> Optional[Path]:
    """解析模板路径：项目 overrides > V11 内置

    Args:
        project_root: 项目根
        template_name: 模板名（不含 .md）
        package_root: V11 技能包根

    Returns:
        解析到的路径（None = 无匹配）
    """
    # 1. 项目级 overrides（最高优先级）
    override_path = project_root / "docs" / "templates" / "overrides" / f"{template_name}.md"
    if override_path.exists():
        return override_path

    # 2. 项目级 templates（次高优先级）
    project_templates = project_root / "docs" / "templates" / f"{template_name}.md"
    if project_templates.exists():
        return project_templates

    # 3. V11 内置（兜底）
    builtin_path = package_root / "templates" / f"{template_name}.md"
    if builtin_path.exists():
        return builtin_path

    return None


def _classify_source(resolved: Optional[Path], project_root: Path, template_name: str) -> str:
    """分类模板来源"""
    if resolved is None:
        return "missing"
    try:
        override_path = (
            project_root / "docs" / "templates" / "overrides" / f"{template_name}.md"
        )
        if resolved.resolve() == override_path.resolve():
            return "project-overrides"
    except OSError:
        pass
    # V11 内置
    builtin_path = V11_PACKAGE_ROOT / "templates" / f"{template_name}.md"
    try:
        if resolved.resolve() == builtin_path.resolve():
            return "v11-core"
    except OSError:
        pass
    return "project-templates"


def scan(project_root: Path) -> dict:
    """扫描所有模板的解析结果

    Returns:
        {
            "project_root": str,
            "v11_package_root": str,
            "templates": [...],
            "missing_count": int,
        }
    """
    results = []
    missing_count = 0
    for name in SCAN_TEMPLATES:
        resolved = resolve_template(project_root, name, V11_PACKAGE_ROOT)
        source = _classify_source(resolved, project_root, name)
        results.append({
            "name": name,
            "resolved_path": str(resolved) if resolved else None,
            "source": source,
        })
        if source == "missing":
            missing_count += 1
    return {
        "project_root": str(project_root),
        "v11_package_root": str(V11_PACKAGE_ROOT),
        "templates": results,
        "missing_count": missing_count,
    }


def _print_text(result: dict) -> None:
    """文本模式输出"""
    print(f"Project: {result['project_root']}")
    print(f"V11 pkg: {result['v11_package_root']}")
    print()
    print("Templates:")
    for t in result["templates"]:
        if t["source"] == "project-overrides":
            icon = "🎯"
        elif t["source"] == "project-templates":
            icon = "📝"
        elif t["source"] == "v11-core":
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


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        description="V11.1 模板解析回归扫描",
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

    if args.project_root:
        project_root = Path(args.project_root).resolve()
    else:
        project_root = Path.cwd()

    result = scan(project_root)

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        _print_text(result)

    if args.strict and result["missing_count"] > 0:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())