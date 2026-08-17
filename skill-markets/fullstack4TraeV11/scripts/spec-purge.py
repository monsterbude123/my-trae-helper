#!/usr/bin/env python3
"""
V11 spec-purge.py — 归档隔离（Stage 5 Accept 必走）

Usage:
    python spec-purge.py --change-id <id> [--dry-run]

流程:
  1. 检查 change 必含 4 工件
  2. 隔离至 _invalidated/{timestamp}-{change-id}/
  3. 归档至 archive/done/{change-id}/  (路径由 .trae/fullstack4traev11.config.yaml 配置)

V11.8.7 NEW (case 2 蒸馏 fix V12 layout vs spec-purge 双源):
  - 自动探测 change 物理布局(V11 扁平 vs V12 fact/ + stage/{N}/)
  - V11 模式:读顶层 spec.md / plan.md / contracts/api-contracts.md 等
  - V12 模式:读 fact/spec.md / fact/plan.md / fact/contracts/... + stage/3-implement/... 流程文档
  - V12 模式下自动展平到 archive(归档目录仍用 V11 平铺布局便于 audit)
  - 跨模式互斥校验:同一 change 不能"顶层 6 文件 + V12 stage/ 同时存在",
    违反 → FAIL with explicit reason

Exit codes:
    0 = PASS
    1 = FAIL（缺工件）
    2 = DRY-RUN
"""
import sys
import argparse
import pathlib
import shutil
import json
from datetime import datetime, timezone

try:
    from _lib_paths import get_archive_dir
except ImportError:
    def get_archive_dir(project_root: pathlib.Path) -> pathlib.Path:
        return project_root / "docs" / "archive" / "done"


# V11 扁平 layout:6 个根级工件(legacy)
REQUIRED_ARTIFACTS_V11 = [
    "spec.md",
    "plan.md",
    "contracts/domain-models.md",
    "contracts/api-contracts.md",
    "review-report.md",
    "rot-scan-{date}.md",
]

# V12 物理布局(case 2 蒸馏 fix):fact/ + stage/N/*.md
# - fact/ = 跨 stage 共享真相源(spec / plan / contracts)
# - stage/N/*.md = 流程产物(stage 切换可重置)
V12_FACT_ARTIFACTS = [
    "fact/spec.md",
    "fact/plan.md",
    "fact/contracts/domain-models.md",
    "fact/contracts/api-contracts.md",
]
V12_STAGE_ARTIFACTS = [
    "stage/4-review/review-report.md",
    "stage/4.5-rot-scan/rot-scan-report.md",
]


def detect_layout(change_dir: pathlib.Path) -> str:
    """探测 change 物理布局:V11(扁平) / V12(fact/ + stage/)

    决策算法:
      - 同时存在 fact/ + stage/ → V12
      - 否则 → V11
      - 两者都不是 → UNKNOWN(后续 check_artifacts 抛 fail)
    """
    has_fact = (change_dir / "fact").is_dir()
    has_stage = (change_dir / "stage").is_dir()
    if has_fact and has_stage:
        return "v12"
    if has_fact or has_stage:
        # 只有一个 = 残留半成品状态,不算合法布局
        return "broken"
    return "v11"


def check_artifacts(change_dir: pathlib.Path) -> tuple:
    """根据探测到的布局检查必含工件

    V11.8.7:支持 V11(扁平 6 文件) + V12(fact/ + stage/N/) 双布局,自动适配。
    """
    if not change_dir.exists():
        return False, f"change 目录不存在: {change_dir}"

    layout = detect_layout(change_dir)
    if layout == "broken":
        return False, "BROKEN layout:仅含 fact/ 或仅含 stage/,缺一半。V11 扁平布局不需 fact/stage;V12 必须两者齐全"

    missing = []
    today = datetime.now().strftime("%Y-%m-%d")

    if layout == "v12":
        # V12:fact/ + stage/N/(任一 rot-scan-* 通配)
        required = list(V12_FACT_ARTIFACTS) + list(V12_STAGE_ARTIFACTS)
        # rot-scan 不限定文件名(可能 rot-scan-report.md / rot-scan-2026-XX.md)
        rot_alts = [
            "stage/4.5-rot-scan/rot-scan-report.md",
            "stage/4.5-rot-scan/rot-notes.md",
        ]
        has_rot = any((change_dir / r).is_file() for r in rot_alts)
        if not has_rot:
            # 也允许顶层 rot-scan-{date}.md 兼容
            for f in change_dir.glob("rot-scan-*.md"):
                has_rot = True
                break

        for art in required:
            if not (change_dir / art).exists():
                missing.append(art)
        # rot-scan 单独处理(任一即可)
        if not has_rot:
            missing.append("stage/4.5-rot-scan/rot-scan-report.md(任一 .md 通配)")
    else:
        # V11 legacy:6 顶层工件
        required = [a.format(date=today) if "{" in a else a for a in REQUIRED_ARTIFACTS_V11]
        for art in required:
            if not (change_dir / art).exists():
                missing.append(art)

    if missing:
        return False, f"[{layout}] 缺失工件: {missing}"

    return True, f"[{layout}] 4 工件齐全"


def flatten_v12_to_v11_layout(v12_dir: pathlib.Path, target_dir: pathlib.Path) -> list:
    """V11.8.7 NEW(case 2 蒸馏):V12 物理布局 → 展平到 V11 平铺布局
    (用于归档目录保持 V11 一致性,便于 audit)

    映射规则:
      fact/spec.md          → spec.md
      fact/plan.md          → plan.md
      fact/test-plan.md     → test-plan.md
      fact/prototype.md     → prototype.md
      fact/contracts/       → contracts/(整个目录移动)
      fact/.state-card.md   → .state-card.md
      stage/N/*.md          → {prefix}-{N}-{name}.md(prefix=stage)
      stage/N/handoff-out.md → handoff-{N}-out.md
    """
    moves = []
    fact_dir = v12_dir / "fact"
    if fact_dir.is_dir():
        for f in fact_dir.iterdir():
            if f.is_file():
                dst = target_dir / f.name
                if not dst.exists():
                    shutil.move(str(f), str(dst))
                    moves.append(f"fact/{f.name} → {f.name}")
            elif f.is_dir():
                dst = target_dir / f.name
                if not dst.exists():
                    shutil.move(str(f), str(dst))
                    moves.append(f"fact/{f.name}/ → {f.name}/")

    stage_dir = v12_dir / "stage"
    if stage_dir.is_dir():
        for sub in stage_dir.iterdir():
            if not sub.is_dir():
                continue
            for f in sub.iterdir():
                if not f.is_file():
                    continue
                # stage/N/X.md → flat {N}-{X}.md(去掉 sub 前缀)
                flat_name = f"{sub.name}-{f.name}"
                dst = target_dir / flat_name
                if not dst.exists():
                    shutil.move(str(f), str(dst))
                    moves.append(f"stage/{sub.name}/{f.name} → {flat_name}")
        # 删除空的 stage/
        try:
            shutil.rmtree(stage_dir)
        except OSError:
            pass
    # 删除空的 fact/(若还有就保留 README)
    try:
        if fact_dir.is_dir() and not any(fact_dir.iterdir()):
            fact_dir.rmdir()
    except OSError:
        pass
    return moves


def purge_change(project_root: pathlib.Path, change_id: str, dry_run: bool = False) -> tuple:
    """归档 change 至 archive/done/{change-id}

    V11.8.7 NEW:支持 V11 + V12 双布局,V12 先展平再归档(归档目录保持 V11 一致性)
    """
    change_dir = project_root / f"docs/specs/changes/{change_id}"
    if not change_dir.exists():
        return False, f"change 目录不存在: {change_dir}"

    layout = detect_layout(change_dir)

    # 检查工件
    is_ready, msg = check_artifacts(change_dir)
    if not is_ready:
        return False, msg

    # 隔离 + 归档
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    invalidated_dir = project_root / f"docs/specs/_invalidated/{timestamp}-{change_id}"
    archive_dir = get_archive_dir(project_root) / change_id

    if dry_run:
        extra = "(V12 → 展平到 V11 归档目录)" if layout == "v12" else ""
        return True, f"DRY-RUN ({layout}): 将隔离至 {invalidated_dir}, 归档至 {archive_dir} {extra}"

    # 隔离原 change
    if change_dir.exists():
        invalidated_dir.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(change_dir), str(invalidated_dir))

    # V11.8.7:V12 → 先展平到 archive,便于 audit
    if layout == "v12":
        archive_dir.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(str(invalidated_dir), str(archive_dir))
        # 在归档目录里展平
        flatten_moves = flatten_v12_to_v11_layout(archive_dir, archive_dir)
        extra_note = f" V12→V11 展平: {len(flatten_moves)} 个文件"
    else:
        archive_dir.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(str(invalidated_dir), str(archive_dir))
        extra_note = ""

    return True, f"已归档 ({layout}): {archive_dir}{extra_note}"


def main():
    parser = argparse.ArgumentParser(description="V11 spec-purge 归档")
    parser.add_argument("--change-id", required=True, help="change ID")
    parser.add_argument("--project-root", default=".", help="项目根路径")
    parser.add_argument("--dry-run", action="store_true", help="仅验证不执行")
    parser.add_argument("--json", action="store_true", help="JSON 输出")
    args = parser.parse_args()

    project_root = pathlib.Path(args.project_root).resolve()
    is_pass, msg = purge_change(project_root, args.change_id, args.dry_run)

    layout = detect_layout(pathlib.Path(args.project_root) / "docs" / "specs" / "changes" / args.change_id)
    result = {
        "status": "DRY-RUN" if args.dry_run else ("PASS" if is_pass else "FAIL"),
        "change_id": args.change_id,
        "layout": layout,
        "v11_8_7_layout_aware": True,
        "message": msg,
    }

    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        icon = {"PASS": "✅", "FAIL": "❌", "DRY-RUN": "🔍"}[result["status"]]
        print(f"{icon} {result['status']} [{layout}] — {msg}")

    return 0 if is_pass else (2 if args.dry_run else 1)


if __name__ == "__main__":
    sys.exit(main())