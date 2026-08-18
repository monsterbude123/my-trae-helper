#!/usr/bin/env python3
"""
V12 spec-purge.py — 归档隔离（Stage 5 Accept 必走）

Usage:
    python spec-purge.py --change-id <id> [--dry-run]

流程:
  1. 检查 change 必含 4 工件
  2. 隔离至 _invalidated/{timestamp}-{change-id}/
  3. 归档至 archive/done/{change-id}/  (路径由 .trae/fullstack4traev11.config.yaml 配置)

V12 物理布局(唯一):fact/ + stage/{N}/{name}/
  - fact/ = 跨 stage 共享真相源(spec / plan / contracts / intent / prototype / test-plan)
  - stage/{N}/{name}/ = 流程产物(每 stage 独立子目录,.state-card.md 也在内)

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


# V12 物理布局(唯一):fact/ + stage/{N}/{name}/
# - fact/ = 跨 stage 共享真相源(spec / plan / contracts)
V12_FACT_ARTIFACTS = [
    "fact/spec.md",
    "fact/plan.md",
    "fact/contracts/domain-models.md",
    "fact/contracts/api-contracts.md",
]
# - stage/{N}/{name}/ = 阶段产物(review-notes.md + rot-scan-*.md)
V12_STAGE_ARTIFACTS = [
    "stage/4/review/review-notes.md",
    "stage/4.5/rot-scan/rot-scan-report.md",
]

# 项目级模块声明文件名(归档时一并复制便于独立审计)
PROJECT_MODULE_FILENAME = "_module.md"


def check_artifacts(change_dir: pathlib.Path) -> tuple:
    """V12 唯一布局:检查 change 必含工件

    必须同时含:
      - fact/spec.md + fact/plan.md + fact/contracts/{domain-models,api-contracts}.md
      - stage/4/review/review-notes.md
      - stage/4.5/rot-scan/rot-scan-*.md(任一 .md 通配)
    """
    if not change_dir.exists():
        return False, f"change 目录不存在: {change_dir}"

    missing = []

    # fact/ 必含工件
    for art in V12_FACT_ARTIFACTS:
        if not (change_dir / art).is_file():
            missing.append(art)

    # stage/4/review/review-notes.md 必含
    if not (change_dir / "stage" / "4" / "review" / "review-notes.md").is_file():
        missing.append("stage/4/review/review-notes.md")

    # stage/4.5/rot-scan/rot-scan-*.md(任一 .md 通配)
    rot_dir = change_dir / "stage" / "4.5" / "rot-scan"
    has_rot = rot_dir.is_dir() and any(rot_dir.glob("*.md"))
    if not has_rot:
        missing.append("stage/4.5/rot-scan/rot-scan-*.md(任一 .md)")

    if missing:
        return False, f"[V12] 缺失工件: {missing}"

    return True, "[V12] 5 工件齐全"


def archive_keep_v12_layout(
    source_dir: pathlib.Path,
    archive_dir: pathlib.Path,
) -> list:
    """V12 归档:整目录 1:1 复制 fact/ + stage/ 物理布局(不展平、不重命名)

    额外:把项目级 `_module.md` 复制进 archive 顶层(便于独立审计)。
    返回:操作描述列表(供日志输出)
    """
    actions = []

    # 1. 整目录复制(保留 V12 物理布局)
    archive_dir.parent.mkdir(parents=True, exist_ok=True)
    if archive_dir.exists():
        shutil.rmtree(archive_dir)
    shutil.copytree(str(source_dir), str(archive_dir))
    actions.append(f"copytree 1:1 保留 V12 物理布局 → {archive_dir}")

    # 2. 注入项目级 _module.md(从项目根的 docs/specs/changes/_module.md 复制)
    project_module = source_dir.parent / PROJECT_MODULE_FILENAME
    if project_module.is_file():
        dst = archive_dir / PROJECT_MODULE_FILENAME
        shutil.copy2(str(project_module), str(dst))
        actions.append(f"复制项目级模块声明 → {dst}")
    else:
        actions.append(f"⚠️ 未发现项目级 {project_module}(可能未跑 init-from-zero.py Step 4.6)")

    return actions


def purge_change(project_root: pathlib.Path, change_id: str, dry_run: bool = False) -> tuple:
    """归档 change 至 archive/done/{change-id}(V12 物理布局 1:1 保留)"""
    change_dir = project_root / "docs" / "specs" / "changes" / change_id
    if not change_dir.exists():
        return False, f"change 目录不存在: {change_dir}"

    # 检查 V12 工件
    is_ready, msg = check_artifacts(change_dir)
    if not is_ready:
        return False, msg

    # 隔离 + 归档
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    invalidated_dir = project_root / f"docs/specs/_invalidated/{timestamp}-{change_id}"
    archive_dir = get_archive_dir(project_root) / change_id

    if dry_run:
        return True, f"DRY-RUN (V12): 将隔离至 {invalidated_dir}, 归档至 {archive_dir} (V12 保留物理布局 + 注入 _module.md)"

    # 隔离原 change
    if change_dir.exists():
        invalidated_dir.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(change_dir), str(invalidated_dir))

    # V12 保留物理布局 + 注入项目级 _module.md
    actions = archive_keep_v12_layout(invalidated_dir, archive_dir)
    extra_note = f" V12 保留布局({len(actions)} 步): " + "; ".join(actions)

    return True, f"已归档 (V12): {archive_dir}{extra_note}"


def main():
    parser = argparse.ArgumentParser(description="V12 spec-purge 归档(V12 物理布局唯一)")
    parser.add_argument("--change-id", required=True, help="change ID")
    parser.add_argument("--project-root", default=".", help="项目根路径")
    parser.add_argument("--dry-run", action="store_true", help="仅验证不执行")
    parser.add_argument("--json", action="store_true", help="JSON 输出")
    args = parser.parse_args()

    project_root = pathlib.Path(args.project_root).resolve()
    is_pass, msg = purge_change(project_root, args.change_id, args.dry_run)

    result = {
        "status": "DRY-RUN" if args.dry_run else ("PASS" if is_pass else "FAIL"),
        "change_id": args.change_id,
        "layout": "v12",
        "message": msg,
    }

    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        icon = {"PASS": "✅", "FAIL": "❌", "DRY-RUN": "🔍"}[result["status"]]
        print(f"{icon} {result['status']} [V12] — {msg}")

    return 0 if is_pass else (2 if args.dry_run else 1)


if __name__ == "__main__":
    sys.exit(main())
