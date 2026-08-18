#!/usr/bin/env python3
"""
V11 change-status.py — 读取 change 状态

Usage:
    python change-status.py --change-id <id> [--project-root <path>]

输出:
  - 当前 stage
  - health
  - 必走工件状态
  - 阻塞报告（如有）

Exit codes:
    0 = PASS
    1 = FAIL
"""
import sys
import argparse
import pathlib
import json
import re
import yaml
from datetime import datetime, timezone


# V12 物理布局唯一:fact/ + stage/{N}/{name}/
REQUIRED_ARTIFACTS = [
    "fact/spec.md",
    "fact/plan.md",
    "fact/ac_list.md",
    "fact/edge_cases.md",
    "fact/contracts/domain-models.md",
    "fact/contracts/api-contracts.md",
    "stage/4/review/review-notes.md",
]


def read_state_card(state_card_path: pathlib.Path) -> dict:
    """读取状态卡（委托 _lib_state_card 共用库）"""
    import sys
    sys.path.insert(0, str(pathlib.Path(__file__).parent))
    from _lib_state_card import parse_state_card as _parse
    return _parse(state_card_path)


def audit_read_operation(
    state_card_path: pathlib.Path,
    project_root: pathlib.Path,
    actor: str = "change-status.py",
) -> dict:
    """P3-6 NEW: 读取状态卡时记录审计(防止 ghost read → ghost write)。

    失败不阻断主流程(best-effort)。
    """
    try:
        sys.path.insert(0, str(pathlib.Path(__file__).parent))
        from _lib_state_card import audit_state_card_change

        content_after = state_card_path.read_text(encoding="utf-8") if state_card_path.exists() else ""
        return audit_state_card_change(
            path=state_card_path,
            operation="read-via-change-status",
            actor=actor,
            content_after=content_after,
            project_root=project_root,
        )
    except Exception as e:
        sys.stderr.write(f"[change-status] WARN: audit_state_card_change 失败(不阻断): {e}\n")
        return {"error": str(e)}


def check_artifacts(change_dir: pathlib.Path) -> dict:
    """检查必走工件状态"""
    today = datetime.now().strftime("%Y-%m-%d")
    artifacts = {}

    # 替换 {date}
    resolved_required = [a.replace("{date}", today) if "{" in a else a for a in REQUIRED_ARTIFACTS]

    for art in REQUIRED_ARTIFACTS:
        path = change_dir / art
        artifacts[art] = {
            "exists": path.exists(),
            "size_bytes": path.stat().st_size if path.exists() else 0,
        }

    return artifacts


def main():
    parser = argparse.ArgumentParser(description="V11 change-status")
    parser.add_argument("--change-id", required=True, help="change ID")
    parser.add_argument("--project-root", default=".", help="项目根路径")
    parser.add_argument("--json", action="store_true", help="JSON 输出")
    args = parser.parse_args()

    project_root = pathlib.Path(args.project_root).resolve()
    change_dir = project_root / "docs" / "specs" / "changes" / args.change_id

    if not change_dir.exists():
        result = {"status": "FAIL", "message": f"change 不存在: {change_dir}"}
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print(f"❌ {result['message']}")
        return 1

    # V12 物理布局:状态卡由当前 stage 子目录持有
    # V12 唯一布局:从 -1/intake 到 7/health 任一 stage 子目录读取最新 .state-card.md
    state_card_candidates = sorted(
        change_dir.glob("stage/*/*/.state-card.md"),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )
    state_card_path = state_card_candidates[0] if state_card_candidates else None

    if state_card_path:
        state_card = read_state_card(state_card_path)
    else:
        state_card = {"current_stage": "unknown", "stage_status": "unknown", "health": "unknown"}

    # P3-6 NEW: 记录 read-via-change-status 审计,防止 ghost read 绕过审计链
    if state_card_path:
        audit_read_operation(
            state_card_path=state_card_path,
            project_root=project_root,
        )

    artifacts = check_artifacts(change_dir)

    missing = [art for art, status in artifacts.items() if not status["exists"]]

    output = {
        "change_id": args.change_id,
        "path": str(change_dir),
        "current_stage": state_card.get("current_stage"),
        "stage_status": state_card.get("stage_status"),
        "health": state_card.get("health"),
        "artifacts": artifacts,
        "missing": missing,
        "status": "PASS" if not missing else "WARN",
    }

    if args.json:
        print(json.dumps(output, indent=2, ensure_ascii=False, default=str))
    else:
        icon = "✅" if not missing else "⚠️"
        print(f"{icon} {output['current_stage']} / {output['stage_status']} / {output['health']}")
        print(f"   Change: {output['change_id']}")
        for art, status in artifacts.items():
            mark = "✓" if status["exists"] else "✗"
            print(f"   [{mark}] {art}: {status['size_bytes']}B")

    return 0  # WARN 不阻断（missing 是信息性，非阻塞）


if __name__ == "__main__":
    sys.exit(main())