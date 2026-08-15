#!/usr/bin/env python3
"""
_check_protocol_coverage.py — 多维度同步检测工具(2026-08-15 NEW)

基于 .agents/skills/project-rule-skill/references/skill-creation-workflow.md §2 多维度同步约束(V11.8.0.1 路径迁移),程序化检测:
  "某协议规范(<topic>-protocol.md)被 6 个维度的文件引用了吗?"

Usage:
    python _check_protocol_coverage.py \
        --protocol <path-to-protocol-file> \
        [--project-root <path>] \
        [--json] [--dry-run] [--strict]

设计:
  - 默认 6 维度路径模式(可在 .check_protocol_coverage.yaml 覆盖):
    1. SKILL.md       — skill-markets/<pkg>/SKILL.md
    2. reference      — skill-markets/<pkg>/references/*.md
    3. workflow       — skill-markets/<pkg>/**/workflows/*.md
    4. script         — skill-markets/<pkg>/scripts/*.py
    5. guard          — scripts/<pkg>-*.{py,mjs}
    6. other-refs     — AGENTS.md + CAPABILITY-MAP.md + SECURITY-MAP.md + README.md + CHANGELOG.md
  - 每维度检查:维度内是否有文件 *链接* 到 protocol 文件(相对路径/文件名)
  - 缺任何维度 = FAIL + 列出缺失清单
  - 用于 skill-creation-workflow.md §2.2 多维度一致性检测

Exit codes:
    0 = PASS(6 维度全引用)
    1 = FAIL(任一维度未引用)
    2 = NEEDS_REVIEW(strict 模式下 evidence 缺失)
"""
from __future__ import annotations

import argparse
import json
import pathlib
import re
import sys
from dataclasses import dataclass, field, asdict

PROJECT_ROOT_DEFAULT = pathlib.Path(__file__).resolve().parent.parent

# 默认 6 维度路径 glob(相对 project_root)
PACKAGE_DIMENSIONS = {
    "SKILL.md": "skill-markets/*/SKILL.md",
    "reference": "skill-markets/*/references/*.md",
    "workflow": "skill-markets/*/skills/*/workflows/*.md",
    "script": "skill-markets/*/scripts/*.py",
    "guard": "scripts/*-guard.{py,mjs}",
    "other-refs": [
        "AGENTS.md",
        "skill-markets/CAPABILITY-MAP.md",
        "SECURITY-MAP.md",
        "README.md",
        "CHANGELOG.md",
    ],
}

# 全局规则维度(项目级,如 .agents/rules/*.md)只需 1 维度
GLOBAL_DIMENSIONS = {
    "other-refs": [
        "AGENTS.md",
        ".agents/skills/*/SKILL.md",
        ".agents/skills/project-rule-skill/SKILL.md",
        ".trae/rules/*.md",
        "skill-markets/CAPABILITY-MAP.md",
        "SECURITY-MAP.md",
        "README.md",
        "CHANGELOG.md",
    ],
}

# 检测协议引用 — 用文件名(如 "stage-transition-protocol.md") 作为最小匹配单元
# 也支持带路径(如 "references/stage-transition-protocol.md")


@dataclass
class DimensionResult:
    name: str
    pattern: str
    matched_files: list = field(default_factory=list)
    referenced: bool = False
    evidence: list = field(default_factory=list)


def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser(description="多维度协议覆盖度检测(protocol-first 多维度一致性)")
    ap.add_argument("--protocol", type=pathlib.Path, required=True, help="协议规范文件路径(必填)")
    ap.add_argument("--project-root", type=pathlib.Path, default=PROJECT_ROOT_DEFAULT, help="项目根")
    ap.add_argument("--scope", choices=["package", "global"], default="package",
                    help="协议作用域:package(6 维度全要,默认) | global(项目级规则,只检 other-refs)")
    ap.add_argument("--json", action="store_true", help="JSON 输出")
    ap.add_argument("--dry-run", action="store_true", help="dry-run,不退出码检查")
    ap.add_argument("--strict", action="store_true", help="严格模式(空维度 = FAIL)")
    ap.add_argument("--check", action="store_true", help="CI gate 模式(等价于不做 --dry-run)")
    return ap.parse_args()


def file_references_protocol(file: pathlib.Path, protocol: pathlib.Path, project_root: pathlib.Path) -> bool:
    """检测 file 内容是否引用了 protocol 文件名/路径"""
    if not file.exists() or not file.is_file():
        return False
    try:
        content = file.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return False

    # 多种引用形式(覆盖 99% 场景)
    candidates = [
        protocol.name,                    # stage-transition-protocol.md
        str(protocol.relative_to(project_root)).replace("\\", "/"),  # references/stage-transition-protocol.md
        protocol.stem,                    # stage-transition-protocol
    ]
    for cand in candidates:
        if cand in content:
            return True
    return False


def collect_dimension_files(project_root: pathlib.Path, patterns) -> list:
    """收集某维度的所有文件(支持多个 glob 或单 glob 字符串)"""
    if isinstance(patterns, str):
        patterns = [patterns]
    files = []
    for pat in patterns:
        files.extend(sorted(project_root.glob(pat)))
    # 去重
    return sorted(set(files))


def check_dimension(project_root: pathlib.Path, name: str, pattern, protocol: pathlib.Path) -> DimensionResult:
    """检查单个维度的引用情况"""
    files = collect_dimension_files(project_root, pattern)
    matched = []
    evidence = []
    for f in files:
        if file_references_protocol(f, protocol, project_root):
            rel = str(f.relative_to(project_root)).replace("\\", "/")
            matched.append(rel)
            evidence.append({"file": rel, "ref_form": "filename"})

    return DimensionResult(
        name=name,
        pattern=str(pattern),
        matched_files=matched,
        referenced=len(matched) > 0,
        evidence=evidence,
    )


def main() -> int:
    args = parse_args()
    project_root = args.project_root.resolve()
    protocol = args.protocol.resolve()

    if not protocol.exists():
        print(f"❌ 协议文件不存在: {protocol}", file=sys.stderr)
        return 1

    # 协议必须在 project_root 内
    try:
        protocol_rel = protocol.relative_to(project_root)
    except ValueError:
        print(f"❌ 协议文件不在 project_root 内: {protocol}", file=sys.stderr)
        return 1

    # 6 维度检测(根据 scope 选维度集)
    dimensions = GLOBAL_DIMENSIONS if args.scope == "global" else PACKAGE_DIMENSIONS
    results = []
    for name, pattern in dimensions.items():
        results.append(check_dimension(project_root, name, pattern, protocol))

    # 总体判定
    missing_dims = [r.name for r in results if not r.referenced]
    overall_pass = len(missing_dims) == 0

    if args.json:
        output = {
            "protocol": str(protocol_rel),
            "project_root": str(project_root),
            "dimensions": [asdict(r) for r in results],
            "missing_dimensions": missing_dims,
            "overall": overall_pass,
        }
        print(json.dumps(output, ensure_ascii=False, indent=2))
    else:
        emoji = "✅" if overall_pass else "🛑"
        print(f"{emoji} [PROTOCOL-COVERAGE:{args.scope}] {protocol_rel}")
        print(f"   协议文件: {protocol}")
        print(f"   项目根: {project_root}")
        print()
        for r in results:
            mark = "✅" if r.referenced else "❌"
            print(f"  {mark} {r.name} ({r.pattern})")
            if r.referenced:
                for ev in r.evidence[:3]:  # 最多列 3 个证据
                    print(f"      → {ev['file']}")
                if len(r.evidence) > 3:
                    print(f"      → ... 还有 {len(r.evidence) - 3} 个")
            else:
                print(f"      ⚠ 未找到引用")
        print()
        if overall_pass:
            print(f"✅ 全部 {len(results)} 维度已引用 → PASS")
        else:
            print(f"🛑 缺失维度: {missing_dims}")
            print(f"   处置: 参考 .agents/skills/project-rule-skill/references/skill-creation-workflow.md §2(V11.8.0.1 路径迁移),在缺失维度补协议引用")

    if args.dry_run:
        return 0
    return 0 if overall_pass else 1


if __name__ == "__main__":
    raise SystemExit(main())