#!/usr/bin/env python3
"""setup-feature.py — 初始化新 feature 目录结构（借鉴 spec-kit setup-plan.sh）

借鉴来源:
  - spec-kit scripts/bash/setup-plan.sh（按需创建 + 模板复制模式）
  - V10 SKILL.md §0（5 阶段流水线）

创建目录结构:
  docs/specs/{feature}/
  ├── spec.md              （从 templates/spec-template.md 复制或空白骨架）
  ├── prototypes/          （空目录）
  └── contracts/           （空目录）

特性:
  - 校验 feature 名格式（NN-NN-name）
  - 防覆盖（feature 目录已存在 → 🛑）
  - 模板可选（找不到 spec-template.md → 用最小骨架）
  - 输出 feature.json 元数据（可被 check_prerequisites 消费）
  - --json 输出（机械验证可解析）
  - 幂等：--force 允许在已有空目录上补全缺失文件

用法:
  python scripts/setup-feature.py --name 00-05-task-queue
  python scripts/setup-feature.py --name 00-05-task-queue --json
  python scripts/setup-feature.py --name 00-05-task-queue --dry-run
  python scripts/setup-feature.py --name 00-05-task-queue --force
  python scripts/setup-feature.py --name 00-05-task-queue --template /path/to/spec-template.md

环境变量:
  V10_FEATURE   feature 名（可用 --name 覆盖）
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Tuple

# 允许直接执行或 import
try:
    from common import (
        FeaturePaths,
        detect_feature_dir,
        emit_json,
        get_project_root,
        resolve_template,
        validate_feature_name,
    )
except ImportError:  # pragma: no cover
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from common import (
        FeaturePaths,
        detect_feature_dir,
        emit_json,
        get_project_root,
        resolve_template,
        validate_feature_name,
    )


# V10 模板默认路径（相对 V10 包根）
V10_PACKAGE_ROOT = Path(__file__).resolve().parent.parent

# feature.json 元数据结构
FEATURE_JSON_VERSION = "1.0"


HELP_TEXT = """用法: setup-feature.py --name FEATURE [OPTIONS]

初始化 V10 feature 目录结构。

选项:
  --name NAME            feature 名（必填，格式: NN-NN-name）
  --project-root PATH    项目根（默认自动查找）
  --template PATH        spec.md 模板路径（一次性覆盖，默认走 2 层栈解析）
  --print-template-path  只输出实际解析到的模板路径，不创建任何文件
  --dry-run              预览，不实际创建
  --force                已存在时补全缺失文件（不覆盖已有文件）
  --json                 JSON 格式输出
  --help, -h             显示此帮助

模板解析优先级（借鉴 spec-kit，简化为 2 层）:
  1. --template PATH                       （命令行一次性覆盖，最高）
  2. docs/templates/overrides/spec-template.md  （项目级长期覆盖）
  3. {V10 包}/templates/spec-template.md        （V10 内置默认）

示例:
  # 创建标准 feature
  python scripts/setup-feature.py --name 00-05-task-queue

  # 预览模式
  python scripts/setup-feature.py --name 00-05-task-queue --dry-run

  # 强制补全（已存在但缺文件时）
  python scripts/setup-feature.py --name 00-05-task-queue --force

  # 回归扫描：查看当前项目实际会用到哪个模板
  python scripts/setup-feature.py --name 00-05-task-queue --print-template-path

创建结构（自动适配布局）:
  - V10 标准:   docs/specs/{feature}/
  - 嵌套布局:   docs/specs/changes/{feature}/  （当 changes/ 已存在）

  {feature}/
  ├── spec.md
  ├── .feature.json     （元数据）
  ├── prototypes/       （空目录）
  └── contracts/        （空目录）
"""


# === 模板处理 ===

MINIMAL_SPEC_SKELETON = """---
feature_name: {feature}
branch: {feature}
created: {date}
status: draft
spec_version: "10.1"
source: (待填)
---

# {feature}

> 编号: (待填)
> 状态: draft
> 创建: {date}

{1-2 句说明这个功能做什么 + 解决什么用户问题}

---

## Why *(mandatory)*

**问题陈述**:

**价值主张**:

**不做会怎样**:

---

## What Changes *(mandatory)*

### 必改项 (MUST)
- **WCH-001**: (待填)

### 可选项 (MAY)
- (待填)

### 不改项 (WON'T)
- (待填)

---

## Acceptance Criteria *(mandatory)*

### AC-1 (testable)
- Given (前提)
- When (动作)
- Then (结果)

### AC-2 (testable)
- ...

---

## Invariants *(mandatory, ≥1)*

- **INV-1**: (不可违反的系统级约束)

---

## E2E Scenarios *(mandatory, ≥2)*

### E2E-1: (场景名)
- 步骤 1
- 步骤 2
- 预期结果

### E2E-2: (场景名)
- ...
"""


def _load_template(template_path: Path) -> Optional[str]:
    """加载 spec.md 模板（找不到返回 None → 走最小骨架）"""
    if not template_path.is_file():
        return None
    try:
        return template_path.read_text(encoding="utf-8")
    except OSError:
        return None


def _resolve_actual_template(
    cli_template: Optional[Path],
    project_root: Path,
    package_root: Path,
) -> Optional[Path]:
    """3 层栈解析实际使用的模板路径

    优先级（借鉴 spec-kit 4 层栈，简化为 3 层）:
      1. --template PATH                       （命令行一次性覆盖）
      2. docs/templates/overrides/spec-template.md  （项目级长期覆盖）
      3. {package_root}/templates/spec-template.md  （V10 内置默认）

    Args:
        cli_template: --template 参数（None 表示未指定）
        project_root: V10 项目根
        package_root: V10 技能包根

    Returns:
        实际使用的模板路径（找不到返回 None → 走最小骨架）
    """
    # L1: 命令行一次性覆盖
    if cli_template is not None:
        return cli_template
    # L2 + L3: 走 common.resolve_template 2 层栈
    return resolve_template(project_root, "spec-template", package_root)


def _render_spec_content(feature: str, template_text: Optional[str], today: str) -> str:
    """渲染 spec.md 内容

    优先级: 模板文件 > 最小骨架
    占位符替换: {feature} {date}
    """
    if template_text:
        text = template_text
    else:
        text = MINIMAL_SPEC_SKELETON

    # 占位符替换（保守策略：只替换已知占位符）
    placeholders = {
        "{功能名称}": feature,
        "{feature_name}": feature,
        "{YYYY-MM-DD}": today,
        "{created}": today,
        "{proposal/issue 链接}": "(待填)",
        "{1-2 句说明这个功能做什么 + 解决什么用户问题}": f"待补: {feature} 的功能说明",
        "{具体的决策/契约改动,引用 contracts/ 路径}": "(待填)",
        "{模块/接口的增删改}": "(待填)",
        "{前提}": "(待填)",
        "{动作}": "(待填)",
        "{结果}": "(待填)",
        "{不可违反的系统级约束}": "(待填)",
        "{场景名}": "(待填)",
        "{层次}": "?",
        "{序号}": "?",
    }
    for placeholder, value in placeholders.items():
        text = text.replace(placeholder, value)

    return text


def _build_feature_json(feature: str, today: str) -> str:
    """构建 .feature.json 元数据"""
    meta = {
        "version": FEATURE_JSON_VERSION,
        "feature": feature,
        "created": today,
        "phase": "plan",
        "phases_completed": [],
    }
    return json.dumps(meta, ensure_ascii=False, indent=2) + "\n"


# === 目录创建 ===

def _pick_feature_dir(project_root: Path, feature: str) -> Path:
    """决定 feature 目录应该创建在哪个位置

    规则：
      - 如果 docs/specs/{feature}/ 已存在 → 用它（V10 标准）
      - 如果 docs/specs/changes/{feature}/ 已存在 → 用它（嵌套布局已有）
      - 如果 docs/specs/changes/ 存在但目标 feature 不存在 → 用嵌套布局（AIGCMediaDesktop 风格）
      - 否则 → 用 V10 标准布局（my-trae-helper 风格）
    """
    specs = project_root / "docs" / "specs"
    standard = specs / feature
    nested = specs / "changes" / feature

    if standard.is_dir():
        return standard
    if nested.is_dir():
        return nested
    if (specs / "changes").is_dir():
        return nested
    return standard


def _create_directory(
    path: Path,
    dry_run: bool,
) -> Tuple[bool, str]:
    """创建目录（存在则跳过）

    Returns:
        (created, status_line)
    """
    if path.is_dir():
        return False, f"  ⏭️ 已存在: {path}"
    if dry_run:
        return True, f"  [DRY RUN] 将创建: {path}"
    try:
        path.mkdir(parents=True, exist_ok=True)
        return True, f"  ✅ 创建: {path}"
    except OSError as e:
        return False, f"  ❌ 创建失败: {path} — {e}"


def _write_file(
    path: Path,
    content: str,
    force: bool,
    dry_run: bool,
) -> Tuple[bool, str]:
    """写入文件（force=False 时已存在跳过）

    Returns:
        (written, status_line)
    """
    if path.is_file() and not force:
        return False, f"  ⏭️ 已存在: {path}"
    if dry_run:
        return True, f"  [DRY RUN] 将写入: {path}"
    try:
        path.write_text(content, encoding="utf-8")
        return True, f"  ✅ 写入: {path}"
    except OSError as e:
        return False, f"  ❌ 写入失败: {path} — {e}"


# === 主流程 ===

def setup_feature(
    project_root: Path,
    feature: str,
    template_path: Optional[Path],
    dry_run: bool,
    force: bool,
) -> dict:
    """执行 feature 初始化

    Returns:
        结果 dict（含 status / actions / paths）
    """
    today = datetime.now().strftime("%Y-%m-%d")
    # 布局自动检测：如果项目使用 docs/specs/changes/ 嵌套布局（AIGCMediaDesktop），
    # 且 docs/specs/{feature}/ 不存在，则在 changes/ 下创建。
    feature_dir = _pick_feature_dir(project_root, feature)
    # FeaturePaths 现在已通过 detect_feature_dir 自动适配；但创建阶段我们需要
    # 显式选位置，所以直接构造一次 FeaturePaths 即可。
    paths = FeaturePaths.from_root(project_root, feature)
    if feature_dir != paths.feature_dir:
        # 两者不一致 = 项目用嵌套布局但本次是新建 → 让 FeaturePaths 也指向 nested
        paths = FeaturePaths(
            project_root=paths.project_root,
            feature=paths.feature,
            feature_dir=feature_dir,
            plan=feature_dir / "plan.md",
            spec=feature_dir / "spec.md",
            tasks=feature_dir / "tasks.md",
            define=feature_dir / "define.md",
            contracts_dir=feature_dir / "contracts",
            prototypes_dir=feature_dir / "prototypes",
            state_card=feature_dir / ".state-card.md",
        )

    # 防覆盖检查
    if paths.feature_dir.is_dir() and not force:
        return {
            "status": "skip",
            "feature": feature,
            "feature_dir": str(paths.feature_dir),
            "reason": "feature 目录已存在。用 --force 强制补全缺失文件。",
        }

    actions: List[str] = []

    # 1. 创建 feature 根目录
    created, line = _create_directory(paths.feature_dir, dry_run)
    actions.append(line)
    if not created and not force:
        return {
            "status": "error",
            "feature": feature,
            "errors": [line],
        }

    # 2. 创建子目录
    for sub_dir in [paths.prototypes_dir, paths.contracts_dir]:
        created, line = _create_directory(sub_dir, dry_run)
        actions.append(line)

    # 3. 加载模板并写 spec.md（2 层栈：--template > overrides > V10 内置）
    resolved_template = _resolve_actual_template(
        template_path, project_root, V10_PACKAGE_ROOT
    )
    template_text = _load_template(resolved_template) if resolved_template else None
    if template_text is None:
        actions.append(
            f"  ⚠️ 模板未找到: {resolved_template or '(全部层级均无匹配)'}，使用最小骨架"
        )

    spec_content = _render_spec_content(feature, template_text, today)
    written, line = _write_file(paths.spec, spec_content, force, dry_run)
    actions.append(line)

    # 4. 写 .feature.json 元数据
    feature_json_path = paths.feature_dir / ".feature.json"
    feature_json_content = _build_feature_json(feature, today)
    written, line = _write_file(feature_json_path, feature_json_content, force, dry_run)
    actions.append(line)

    return {
        "status": "ok" if not dry_run else "dry-run",
        "feature": feature,
        "feature_dir": str(paths.feature_dir),
        "resolved_template": str(resolved_template) if resolved_template else None,
        "created_paths": {
            "feature_dir": str(paths.feature_dir),
            "spec": str(paths.spec),
            "prototypes": str(paths.prototypes_dir),
            "contracts": str(paths.contracts_dir),
            "feature_json": str(feature_json_path),
        },
        "actions": actions,
    }


def _print_text_results(result: dict, dry_run: bool) -> None:
    """文本模式输出"""
    status = result["status"]
    icon = {
        "ok": "✅",
        "dry-run": "🔍",
        "skip": "⏭️",
        "error": "❌",
    }.get(status, "•")

    print(f"{icon} {result['feature']} ({status})")
    if "feature_dir" in result:
        print(f"  目录: {result['feature_dir']}")

    if status == "skip":
        print(f"  原因: {result.get('reason', 'N/A')}")
        return

    if status == "error":
        for err in result.get("errors", []):
            print(err)
        return

    print(f"  操作:")
    for action in result.get("actions", []):
        print(action)

    if status == "ok":
        print(f"\n下一步:")
        # 自动判断 layout 路径显示
        fd = result.get("feature_dir", "")
        rel = fd.replace("\\", "/").split("docs/specs/")[-1] if "docs/specs/" in fd else f"{result['feature']}"
        print(f"  1. 编辑 docs/specs/{rel}/spec.md")
        print(f"  2. 运行: python scripts/check_prerequisites.py --phase spec")


def main(argv: List[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="V10 feature 初始化",
        add_help=False,
    )
    parser.add_argument("--name", type=str, help="feature 名（必填，NN-NN-name）")
    parser.add_argument("--project-root", type=str, help="项目根路径")
    parser.add_argument("--template", type=str, help="spec.md 模板路径（一次性覆盖）")
    parser.add_argument(
        "--print-template-path",
        action="store_true",
        help="只输出实际解析到的模板路径，不创建任何文件（回归扫描用）",
    )
    parser.add_argument("--dry-run", action="store_true", help="预览模式")
    parser.add_argument("--force", action="store_true", help="已存在时补全缺失文件")
    parser.add_argument("--json", action="store_true", help="JSON 格式输出")
    parser.add_argument("--help", "-h", action="store_true", help="显示帮助")

    args = parser.parse_args(argv)

    if args.help:
        print(HELP_TEXT)
        return 0

    if not args.name:
        print("ERROR: 必须指定 --name FEATURE", file=sys.stderr)
        print(HELP_TEXT, file=sys.stderr)
        return 1

    # 校验 feature 名格式
    if not validate_feature_name(args.name):
        print(
            f"ERROR: feature 名 '{args.name}' 不符合 NN-NN-name 格式",
            file=sys.stderr,
        )
        return 1

    # 解析项目根
    if args.project_root:
        project_root = Path(args.project_root).resolve()
    else:
        project_root = get_project_root()

    # 解析模板路径
    template_path: Optional[Path] = None
    if args.template:
        template_path = Path(args.template).resolve()
        if not template_path.is_file():
            print(
                f"WARN: 自定义模板不存在: {template_path}，将用 V10 内置模板",
                file=sys.stderr,
            )
            template_path = None

    # --print-template-path: 只输出实际解析到的模板路径，不创建任何文件
    if args.print_template_path:
        resolved = _resolve_actual_template(
            template_path, project_root, V10_PACKAGE_ROOT
        )
        if args.json:
            emit_json(
                {
                    "template_name": "spec-template",
                    "resolved_path": str(resolved) if resolved else None,
                    "source": (
                        "cli"
                        if template_path is not None
                        else (
                            "project-overrides"
                            if resolved
                            and str(resolved).replace("\\", "/").endswith(
                                "docs/templates/overrides/spec-template.md"
                            )
                            else "v10-core"
                        )
                    ),
                }
            )
        else:
            if resolved:
                print(str(resolved))
            else:
                print("(无匹配模板，将走最小骨架)")
        return 0

    # 执行
    result = setup_feature(
        project_root=project_root,
        feature=args.name,
        template_path=template_path,
        dry_run=args.dry_run,
        force=args.force,
    )

    # 输出
    if args.json:
        emit_json(result)
    else:
        _print_text_results(result, args.dry_run)

    # 退出码
    status = result["status"]
    if status == "error":
        return 1
    if status == "skip" and not args.force:
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
