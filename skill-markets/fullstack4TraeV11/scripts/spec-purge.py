#!/usr/bin/env python3
"""
V11 spec-purge.py — 归档隔离（Stage 5 Accept 必走）

Usage:
    python spec-purge.py --change-id <id> [--dry-run]

流程:
  1. 检查 change 必含 4 工件
  2. 隔离至 _invalidated/{timestamp}-{change-id}/
  3. 归档至 archive/done/{change-id}/

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


REQUIRED_ARTIFACTS = [
    "spec.md",
    "plan.md",
    "contracts/domain-models.md",
    "contracts/api-contracts.md",
    "review-report.md",
    "rot-scan-{date}.md",
]


def check_artifacts(change_dir: pathlib.Path) -> tuple:
    """检查 change 必含 4 工件"""
    if not change_dir.exists():
        return False, f"change 目录不存在: {change_dir}"

    missing = []
    today = datetime.now().strftime("%Y-%m-%d")
    required = [a.format(date=today) if "{" in a else a for a in REQUIRED_ARTIFACTS]

    for art in required:
        if not (change_dir / art).exists():
            missing.append(art)

    if missing:
        return False, f"缺失工件: {missing}"

    return True, "4 工件齐全"


def purge_change(project_root: pathlib.Path, change_id: str, dry_run: bool = False) -> tuple:
    """归档 change 至 archive/done/{change-id}"""

    change_dir = project_root / f"docs/specs/changes/{change_id}"
    if not change_dir.exists():
        return False, f"change 目录不存在: {change_dir}"

    # 检查工件
    is_ready, msg = check_artifacts(change_dir)
    if not is_ready:
        return False, msg

    # 隔离 + 归档
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    invalidated_dir = project_root / f"docs/specs/_invalidated/{timestamp}-{change_id}"
    archive_dir = project_root / f"docs/archive/done/{change_id}"

    if dry_run:
        return True, f"DRY-RUN: 将隔离至 {invalidated_dir}, 归档至 {archive_dir}"

    # 隔离原 change
    if change_dir.exists():
        invalidated_dir.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(change_dir), str(invalidated_dir))

    # 归档
    archive_dir.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(str(invalidated_dir), str(archive_dir))

    return True, f"已归档: {archive_dir}"


def main():
    parser = argparse.ArgumentParser(description="V11 spec-purge 归档")
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
        "message": msg,
    }

    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        icon = {"PASS": "✅", "FAIL": "❌", "DRY-RUN": "🔍"}[result["status"]]
        print(f"{icon} {result['status']} — {msg}")

    return 0 if is_pass else (2 if args.dry_run else 1)


if __name__ == "__main__":
    sys.exit(main())