#!/usr/bin/env python3
"""check_prerequisites.py — V10 前置校验（借鉴 spec-kit）

检查当前 feature 在指定阶段的前置条件是否满足。

借鉴来源:
  - spec-kit scripts/python/check_prerequisites.py
  - V10 SKILL.md §0 五阶段门禁链

V10 阶段前置表（V10_PHASE_PREREQS 定义于 common.py）:
  plan:                无前置（全新起点）
  spec:                需要 plan.md
  contract:            需要 spec.md
  implement:           需要 spec.md + contracts/api-contracts.md
  review:              需要 spec.md + contracts/api-contracts.md + tasks.md（全部 [x]）
  acceptance-precheck: 需要 spec.md ## E2E 段勾选 ≥ 50%（V10 腐烂点 #B 修复）

用法:
  python scripts/check_prerequisites.py --phase plan
  python scripts/check_prerequisites.py --phase spec
  python scripts/check_prerequisites.py --phase contract
  python scripts/check_prerequisites.py --phase implement
  python scripts/check_prerequisites.py --phase review
  python scripts/check_prerequisites.py --phase review --json
  python scripts/check_prerequisites.py --phase review --paths-only
  python scripts/check_prerequisites.py --feature 00-05-task-queue --phase spec
  python scripts/check_prerequisites.py --phase acceptance-precheck --feature 00-01-foundation

环境变量:
  V10_FEATURE  当前 feature 名（可用 --feature 覆盖）
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import List, Tuple

# 允许直接执行或 import
try:
    from common import (
        FeaturePaths,
        V10_PHASE_PREREQS,
        V10_PHASES,
        dir_has_entries,
        emit_json,
        error_exit,
        get_current_feature,
        get_project_root,
        has_unfinished_tasks,
        validate_feature_name,
    )
except ImportError:  # pragma: no cover
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from common import (
        FeaturePaths,
        V10_PHASE_PREREQS,
        V10_PHASES,
        dir_has_entries,
        emit_json,
        error_exit,
        get_current_feature,
        get_project_root,
        has_unfinished_tasks,
        validate_feature_name,
    )

# V10 扩展 phase: acceptance-precheck（腐烂点 #B 修复）
# 不入 V10_PHASES 避免影响原有流程，但需在 choices 中可见
EXTENDED_PHASES: List[str] = V10_PHASES + ["acceptance-precheck", "orphan-precheck"]


HELP_TEXT = f"""用法: check_prerequisites.py [OPTIONS]

V10 前置校验 — 检查当前 feature 在指定阶段的前置条件是否满足。

选项:
  --phase {{{'|'.join(EXTENDED_PHASES)}}}
                          要检查的阶段（必填；EXTENDED 含 acceptance-precheck）
  --feature NAME          feature 名（覆盖 V10_FEATURE 环境变量）
  --project-root PATH     项目根（默认自动查找）
  --json                  JSON 格式输出
  --paths-only            只输出路径变量（不做前置校验）
  --help, -h              显示此帮助

示例:
  # 检查 Spec 阶段前置
  python scripts/check_prerequisites.py --phase spec

  # 检查 Review 阶段前置（JSON 输出）
  python scripts/check_prerequisites.py --phase review --json

  # 仅输出路径
  python scripts/check_prerequisites.py --feature 00-05-task-queue --paths-only

阶段前置:
  plan      — 无前置
  spec      — plan.md 存在
  contract  — spec.md 存在
  implement — spec.md + contracts/api-contracts.md 存在
  review    — spec.md + contracts/api-contracts.md + tasks.md 全 [x]
"""


def _print_paths_only(paths: FeaturePaths, json_mode: bool) -> None:
    """只输出路径变量"""
    if json_mode:
        emit_json(paths.to_dict())
    else:
        for key, value in paths.to_dict().items():
            print(f"{key.upper()}: {value}")


def _check_file(path: Path, label: str) -> Tuple[bool, str]:
    """检查文件存在性

    Returns:
        (exists, status_line)
    """
    exists = path.is_file()
    marker = "✓" if exists else "✗"
    return exists, f"  {marker} {label}: {path}"


def _check_dir_nonempty(path: Path, label: str) -> Tuple[bool, str]:
    """检查目录存在且非空"""
    exists = dir_has_entries(path)
    marker = "✓" if exists else "✗"
    return exists, f"  {marker} {label}/: {path}"


def _check_acceptance_precheck(paths: FeaturePaths) -> List[str]:
    """acceptance-precheck 校验（V10 腐烂点 #B 修复）

    检查 spec.md E2E 段:
      1. 含 ## E2E 段
      2. E2E 段每个场景前有 [x] 或 [ ]
      3. 至少 50% [x]（非零起步）

    Returns:
        error 列表（空 = 通过）
    """
    errors: List[str] = []
    spec = paths.spec

    # JSON 输出模式: e2e_total / e2e_checked / ratio 字段直接放 errors 之外的 kwargs
    # 但本函数仅返回 errors; 调用方在 main 里组装
    if not spec.is_file():
        errors.append(f"缺失: {spec}")
        return errors

    try:
        content = spec.read_text(encoding="utf-8")
    except OSError as e:
        return [f"无法读取 spec.md: {e}"]

    # 1. 含 ## E2E 段
    if not re.search(r"^## E2E", content, re.MULTILINE):
        errors.append("spec.md 缺 ## E2E 段")
        return errors

    # 2. 提取 E2E 段（到下一个 ## 标题或文件末尾）
    e2e_match = re.search(
        r"^## E2E.*?(?=^## |\Z)",
        content,
        re.MULTILINE | re.DOTALL,
    )
    if not e2e_match:
        errors.append("无法定位 E2E 段边界")
        return errors

    section = e2e_match.group(0)

    # 3. 计数 [x] / [ ] / [⏳]
    checked = len(re.findall(r"-\s*\[x\]", section, re.IGNORECASE))
    unchecked = len(re.findall(r"-\s*\[\s*\]", section))
    pending = len(re.findall(r"-\s*\[⏳\]", section))
    total = checked + unchecked + pending

    # 存到模块全局供 main 读取
    _check_acceptance_precheck.e2e_total = total  # type: ignore[attr-defined]
    _check_acceptance_precheck.e2e_checked = checked  # type: ignore[attr-defined]
    _check_acceptance_precheck.ratio = (checked / total) if total else 0.0  # type: ignore[attr-defined]

    if total == 0:
        errors.append("E2E 段无任何勾选项（[- [x]] / [- [ ]] / [- [⏳]]）")
        return errors

    ratio = checked / total
    if ratio < 0.5:
        errors.append(
            f"E2E 已勾选 {ratio*100:.0f}%（{checked}/{total}，含 {pending} ⏳）— 要求 ≥50%"
        )
        return errors

    # V10 硬门禁: ⏳ 必须为 0（v10_simplified 标记后遗留 ⏳ = 流水线漏水）
    if pending > 0:
        errors.append(
            f"E2E 勾选 {ratio*100:.0f}%（{checked}/{total}），但仍有 {pending} 项 ⏳ 未完成（要求 0 ⏳）"
        )

    return errors


def _check_prereqs(paths: FeaturePaths, phase: str) -> List[str]:
    """执行前置检查

    Returns:
        error 列表（空 = 通过）
    """
    errors: List[str] = []

    # acceptance-precheck 是独立校验（基于 E2E 段，非标准前置表）
    if phase == "acceptance-precheck":
        return _check_acceptance_precheck(paths)

    # V10.4 orphan-precheck: 委托给 orphan-detector.py (腐烂点 12 修复)
    if phase == "orphan-precheck":
        import subprocess
        script = Path(__file__).parent / "orphan-detector.py"
        if not script.exists():
            return [f"missing script: {script}"]
        cmd = ["python", str(script), "--project-root", str(project_root)]
        if feature:
            cmd += ["--feature", feature]
        result = subprocess.run(cmd, cwd=project_root, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout, end='')
        if result.returncode == 1:
            return ["orphan tests found (see output above)"]
        if result.returncode != 0:
            return [f"orphan-detector abnormal exit ({result.returncode}): {result.stderr.strip()}"]
        return []


    prereqs = V10_PHASE_PREREQS.get(phase, [])

    if not prereqs:
        return errors  # plan 阶段无前置

    for prereq in prereqs:
        if prereq.endswith("/"):
            # 目录检查
            dir_name = prereq.rstrip("/")
            target = paths.feature_dir / dir_name
            exists, _ = _check_dir_nonempty(target, dir_name)
            if not exists:
                errors.append(f"缺失目录: docs/specs/{paths.feature}/{dir_name}/")
        else:
            # 文件检查
            target = paths.feature_dir / prereq
            exists, _ = _check_file(target, prereq)
            if not exists:
                errors.append(f"缺失文件: docs/specs/{paths.feature}/{prereq}")

    # review 阶段额外检查：tasks.md 全部 [x]
    if phase == "review" and paths.tasks.is_file():
        if has_unfinished_tasks(paths.tasks):
            errors.append("tasks.md 还有未勾选任务（- [ ]）")

    return errors


def _print_text_results(paths: FeaturePaths, phase: str, errors: List[str]) -> None:
    """文本模式输出结果"""
    print(f"FEATURE_DIR: {paths.feature_dir}")
    print(f"PHASE: {phase}")
    print(f"PREREQUISITES:")

    prereqs = V10_PHASE_PREREQS.get(phase, [])
    if not prereqs:
        print("  (无前置)")
    else:
        for prereq in prereqs:
            if prereq.endswith("/"):
                dir_name = prereq.rstrip("/")
                _, line = _check_dir_nonempty(paths.feature_dir / dir_name, dir_name)
                print(line)
            else:
                _, line = _check_file(paths.feature_dir / prereq, prereq)
                print(line)

    if phase == "review" and paths.tasks.is_file():
        all_done = not has_unfinished_tasks(paths.tasks)
        marker = "✓" if all_done else "✗"
        print(f"  {marker} tasks.md 全部勾选: {paths.tasks}")

    print()
    if errors:
        print(f"🛑 {phase} 阶段前置未通过:")
        for err in errors:
            print(f"  - {err}")
        print(f"\n修复后再进入 {phase} 阶段。任一 FAIL = 🛑 REJECT")
    else:
        print(f"✅ {phase} 阶段前置通过")


def main(argv: List[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="V10 前置校验",
        add_help=False,
    )
    parser.add_argument("--phase", choices=EXTENDED_PHASES, help="要检查的阶段")
    parser.add_argument("--feature", type=str, help="feature 名（覆盖 V10_FEATURE）")
    parser.add_argument("--project-root", type=str, help="项目根路径")
    parser.add_argument("--json", action="store_true", help="JSON 格式输出")
    parser.add_argument("--paths-only", action="store_true", help="只输出路径")
    parser.add_argument("--help", "-h", action="store_true", help="显示帮助")

    args = parser.parse_args(argv)

    if args.help:
        print(HELP_TEXT)
        return 0

    if not args.phase and not args.paths_only:
        print("ERROR: 必须指定 --phase 或 --paths-only", file=sys.stderr)
        print(HELP_TEXT, file=sys.stderr)
        return 1

    # 解析项目根
    if args.project_root:
        project_root = Path(args.project_root).resolve()
    else:
        project_root = get_project_root()

    # 解析 feature 名
    feature = args.feature or get_current_feature()
    if not feature:
        print("ERROR: feature 名未指定（用 --feature 或设置 V10_FEATURE）", file=sys.stderr)
        return 1

    if not validate_feature_name(feature):
        print(f"WARN: feature 名 '{feature}' 不符合 NN-NN-name 格式", file=sys.stderr)

    # 构建路径
    paths = FeaturePaths.from_root(project_root, feature)

    # paths-only 模式
    if args.paths_only:
        _print_paths_only(paths, args.json)
        return 0

    # feature 目录不存在 → 🛑
    if not paths.feature_dir.is_dir():
        msg = f"feature 目录不存在: {paths.feature_dir}"
        if args.json:
            emit_json({
                "status": "error",
                "phase": args.phase,
                "feature": feature,
                "feature_dir": str(paths.feature_dir),
                "errors": [msg],
            })
        else:
            print(f"🛑 {msg}", file=sys.stderr)
            print(f"提示: 先运行 setup-feature.py 创建目录", file=sys.stderr)
        return 1

    # 执行前置检查
    errors = _check_prereqs(paths, args.phase)
    status = "pass" if not errors else "fail"

    if args.json:
        payload = {
            "status": status,
            "phase": args.phase,
            "feature": feature,
            "feature_dir": str(paths.feature_dir),
            "prerequisites": V10_PHASE_PREREQS.get(args.phase, []),
            "errors": errors,
        }
        # acceptance-precheck 附加 E2E 统计字段
        if args.phase == "acceptance-precheck":
            payload["e2e_total"] = getattr(_check_acceptance_precheck, "e2e_total", 0)
            payload["e2e_checked"] = getattr(_check_acceptance_precheck, "e2e_checked", 0)
            payload["ratio"] = getattr(_check_acceptance_precheck, "ratio", 0.0)
        emit_json(payload)
    else:
        _print_text_results(paths, args.phase, errors)

    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
