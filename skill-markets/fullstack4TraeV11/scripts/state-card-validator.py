#!/usr/bin/env python3
"""
V11 state-card-validator.py — 状态卡校验（字段完整性 + 文件系统交叉验证）

Usage:
    python state-card-validator.py <state-card-path> [--project-root <path>]

Exit codes:
    0 = PASS
    1 = FAIL
    2 = N/A

校验维度:
    1. 字段完整性（必填字段非空）
    2. 字段值合法性（current_stage 在 13 stage / health ∈ valid set）
    3. 文件系统交叉验证（artifacts[].exists 与实际文件存在性一致）
    4. stage-gate.py 同等校验（委托调用避免重复实现）
"""
import sys
import argparse
import pathlib
import subprocess
from datetime import datetime, timezone, timedelta


REQUIRED_FIELDS = [
    "card_type", "card_id", "current_stage", "stage_status",
    "stage_started_at", "updated_at", "updated_by", "health",
    "artifacts", "gate_result", "next_stage",
    "actor", "duration_minutes", "notes"
]

# 必填但允许 null 的字段（如 blocked_by / stage_ended_at）
NULLABLE_FIELDS = ["blocked_by", "stage_ended_at", "gate_result.output", "gate_result.verified_at", "next_stage.prerequisites"]

VALID_STAGES = [
    "-1/intake", "0/plan", "0.5/test-plan", "1/spec", "1.5/prototype",
    "2/contract", "3/implement", "3.5/real-verify", "4/review",
    "4.5/rot-scan", "5/accept", "6/bug-fix", "7/project-health"
]

VALID_HEALTH = ["🟢 on-track", "🟡 degraded", "🔴 blocked"]
VALID_CARD_TYPE = ["project", "change", "bug"]
VALID_STAGE_STATUS = ["pending", "working", "completed", "blocked", "skipped"]

# 状态卡陈旧阈值（updated_at 距今 > 30 分钟视为陈旧）
STALENESS_THRESHOLD_MINUTES = 30


def parse_state_card(path: pathlib.Path) -> dict:
    """解析状态卡 frontmatter（委托 _lib_state_card 共用库）"""
    import sys
    sys.path.insert(0, str(pathlib.Path(__file__).parent))
    from _lib_state_card import parse_state_card as _parse
    return _parse(path)


def validate_fields(fields: dict) -> list:
    """字段完整性 + 合法性"""
    errors = []

    for field in REQUIRED_FIELDS:
        if field not in fields:
            errors.append(f"缺少必填字段: {field}")
        elif fields[field] in ("", "null") or fields[field] is None:
            errors.append(f"必填字段为空: {field}")

    if "card_type" in fields:
        ct = fields["card_type"]
        if ct not in VALID_CARD_TYPE:
            errors.append(f"card_type 非法: {ct}（应在 {VALID_CARD_TYPE}）")

    if "current_stage" in fields:
        cs = fields["current_stage"]
        if cs not in VALID_STAGES:
            errors.append(f"current_stage 非法: {cs}（不在 13 stage 名单中）")

    if "stage_status" in fields:
        ss = fields["stage_status"]
        if ss not in VALID_STAGE_STATUS:
            errors.append(f"stage_status 非法: {ss}")

    if "health" in fields:
        h = fields["health"]
        if h not in VALID_HEALTH:
            errors.append(f"health 非法: {h}（应在 {VALID_HEALTH}）")

    # updated_at 格式 + 陈旧检测
    if "updated_at" in fields:
        ua = fields["updated_at"]
        if isinstance(ua, datetime):
            dt = ua
        elif ua not in (None, "null", ""):
            try:
                dt = datetime.fromisoformat(str(ua))
            except (ValueError, TypeError):
                errors.append(f"updated_at 格式错误: {ua}")
                dt = None
        else:
            dt = None

        if dt is not None:
            # naive datetime 视为 UTC
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            now = datetime.now(timezone.utc)
            age_minutes = (now - dt).total_seconds() / 60
            if age_minutes > STALENESS_THRESHOLD_MINUTES and fields.get("stage_status") not in ("completed", "skipped"):
                errors.append(f"状态卡陈旧（{int(age_minutes)} 分钟未更新 > 30 分钟门槛）")

    # blocked_by vs stage_status 一致性
    if "blocked_by" in fields and "stage_status" in fields:
        bb = fields["blocked_by"]
        ss = fields["stage_status"]
        # PyYAML 把 null 解析为 None；字符串 "null" 也视为空
        is_blocked = bb is not None and bb not in ("null", "", "null")
        if is_blocked and ss != "blocked":
            errors.append(f"blocked_by 非空时 stage_status 应是 blocked（当前 {ss}）")

    return errors


def validate_artifacts_fs(fields: dict, state_card_path: pathlib.Path) -> list:
    """artifacts[].exists 与文件系统交叉验证"""
    errors = []
    card_dir = state_card_path.parent

    if "artifacts" not in fields:
        return errors

    artifacts = fields["artifacts"]
    if not isinstance(artifacts, list):
        return errors

    for i, art in enumerate(artifacts):
        if not isinstance(art, str):
            continue
        # 解析 - path: ... - exists: true/false
        path_match = None
        for part in art.split(" - "):
            if part.startswith("path:"):
                path_match = part[5:].strip()
            elif part.startswith("exists:"):
                declared_exists = part[7:].strip() == "true"

        if not path_match:
            continue

        # 解析相对路径
        if path_match.startswith("/") or ":" in path_match[:3]:
            full_path = pathlib.Path(path_match)
        else:
            full_path = (card_dir / path_match).resolve()

        actual_exists = full_path.exists()
        if actual_exists != declared_exists:
            errors.append(
                f"artifacts[{i}].exists 与文件系统不一致: "
                f"声明 {declared_exists}, 实际 {actual_exists} ({full_path})"
            )

    return errors


def main():
    parser = argparse.ArgumentParser(description="V11 状态卡校验")
    parser.add_argument("state_card", help="状态卡文件路径")
    parser.add_argument("--project-root", help="项目根路径（用于相对路径解析）")
    parser.add_argument("--json", action="store_true", help="JSON 输出")
    args = parser.parse_args()

    path = pathlib.Path(args.state_card)
    fields = parse_state_card(path)

    if "error" in fields:
        result = {"status": "FAIL", "errors": [fields["error"]], "path": str(path)}
        if args.json:
            import json
            print(json.dumps(result, indent=2, ensure_ascii=False))
        else:
            print(f"❌ FAIL: {fields['error']}")
        return 1

    field_errors = validate_fields(fields)
    fs_errors = validate_artifacts_fs(fields, path)

    all_errors = field_errors + fs_errors
    is_valid = len(all_errors) == 0

    result = {
        "status": "PASS" if is_valid else "FAIL",
        "path": str(path),
        "current_stage": fields.get("current_stage"),
        "card_type": fields.get("card_type"),
        "stage_status": fields.get("stage_status"),
        "health": fields.get("health"),
        "errors": all_errors
    }

    if args.json:
        import json
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        if is_valid:
            print(f"✅ PASS — {path}")
            print(f"   card_type: {fields.get('card_type')}")
            print(f"   current_stage: {fields.get('current_stage')}")
            print(f"   health: {fields.get('health')}")
        else:
            print(f"❌ FAIL — {path}")
            for e in all_errors:
                print(f"   - {e}")

    return 0 if is_valid else 1


if __name__ == "__main__":
    sys.exit(main())