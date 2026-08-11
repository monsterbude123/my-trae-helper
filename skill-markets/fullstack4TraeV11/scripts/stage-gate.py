#!/usr/bin/env python3
"""
V11 stage-gate.py — V11 阶段门禁（13 stage 统一）

Usage:
    python stage-gate.py --state-card <path> [--stage <stage-id>]

Exit codes:
    0 = PASS
    1 = FAIL
    2 = N/A（标注理由）

13 stage 名单（V11 标准）:
    -1/intake | 0/plan | 0.5/test-plan | 1/spec | 1.5/prototype | 2/contract
    3/implement | 3.5/real-verify | 4/review | 4.5/rot-scan | 5/accept
    6/bug-fix | 7/project-health
"""
import sys
import argparse
import pathlib
from datetime import datetime

# 13 stage 名单（必须严格匹配编排器 stage_config）
VALID_STAGES = [
    "-1/intake", "0/plan", "0.5/test-plan", "1/spec", "1.5/prototype",
    "2/contract", "3/implement", "3.5/real-verify", "4/review",
    "4.5/rot-scan", "5/accept", "6/bug-fix", "7/project-health"
]

# 不可跳过的 stage（V11 §0 必走）
REQUIRED_STAGES = [
    "-1/intake", "0/plan", "1/spec", "3.5/real-verify", "4.5/rot-scan"
]

REQUIRED_FIELDS = [
    "card_type", "card_id", "current_stage", "stage_status",
    "updated_at", "updated_by", "health", "artifacts", "gate_result",
    "next_stage", "actor", "duration_minutes", "notes"
]

VALID_HEALTH = ["🟢 on-track", "🟡 degraded", "🔴 blocked"]
VALID_STATUS = ["PENDING", "PASS", "FAIL", "N/A"]


def parse_state_card(path: pathlib.Path) -> dict:
    """解析状态卡 frontmatter（委托 PyYAML）"""
    import yaml
    if not path.exists():
        return {"error": f"状态卡文件不存在: {path}"}

    content = path.read_text(encoding="utf-8")
    if not content.startswith("---"):
        return {"error": "状态卡缺 frontmatter 分隔符 ---"}

    try:
        end = content.index("\n---", 3)
    except ValueError:
        return {"error": "状态卡 frontmatter 未闭合"}

    fm_text = content[3:end]
    try:
        fields = yaml.safe_load(fm_text) or {}
    except Exception as e:
        return {"error": f"YAML 解析失败: {e}"}

    # 清理字符串字段的外层引号
    for k, v in list(fields.items()):
        if isinstance(v, str):
            if len(v) >= 2 and v[0] in ('"', "'") and v[-1] == v[0]:
                fields[k] = v[1:-1]

    return fields


def validate_state_card(fields: dict, stage: str = None) -> tuple:
    """验证状态卡字段"""
    errors = []

    # 必填字段
    for field in REQUIRED_FIELDS:
        if field not in fields:
            errors.append(f"缺少必填字段: {field}")

    # current_stage 校验
    if "current_stage" in fields:
        cs = fields["current_stage"]
        if cs not in VALID_STAGES:
            errors.append(f"current_stage 非法: {cs}（不在 13 stage 名单中）")

    # stage 参数与 current_stage 一致
    if stage and "current_stage" in fields:
        if stage != fields["current_stage"]:
            errors.append(f"--stage {stage} 与状态卡 current_stage {fields['current_stage']} 不一致")

    # health 校验
    if "health" in fields:
        h = fields["health"]
        if h not in VALID_HEALTH:
            errors.append(f"health 非法: {h}（应在 {VALID_HEALTH} 中）")

    # gate_result.status 校验
    if "gate_result" in fields:
        gr = fields["gate_result"]
        if "status" not in gr:
            errors.append("gate_result 缺 status 字段")

    # blocked_by vs stage_status 一致性
    if "blocked_by" in fields and "stage_status" in fields:
        bb = fields["blocked_by"]
        ss = fields["stage_status"]
        if bb != "null" and ss == "completed":
            errors.append(f"blocked_by={bb} 时 stage_status 不能是 completed")

    # updated_at 格式
    if "updated_at" in fields:
        ua = fields["updated_at"]
        if isinstance(ua, datetime):
            pass  # PyYAML 已解析
        elif ua not in (None, "null", ""):
            try:
                datetime.fromisoformat(str(ua))
            except (ValueError, TypeError):
                errors.append(f"updated_at 格式错误（应为 ISO 8601）: {ua}")

    return (len(errors) == 0, errors)


def main():
    parser = argparse.ArgumentParser(description="V11 阶段门禁")
    parser.add_argument("--state-card", required=True, help="状态卡文件路径")
    parser.add_argument("--stage", help="期望 stage（与状态卡 current_stage 一致）")
    parser.add_argument("--json", action="store_true", help="JSON 输出")
    args = parser.parse_args()

    path = pathlib.Path(args.state_card)
    fields = parse_state_card(path)

    if "error" in fields:
        result = {"status": "FAIL", "errors": [fields["error"]], "path": str(path)}
        print_json_or_text(result, args.json)
        return 1

    is_valid, errors = validate_state_card(fields, args.stage)

    if is_valid:
        result = {
            "status": "PASS",
            "current_stage": fields.get("current_stage"),
            "next_stage_id": (fields.get("next_stage") or {}).get("id"),
            "health": fields.get("health"),
            "gate_status": (fields.get("gate_result") or {}).get("status")
        }
        print_json_or_text(result, args.json)
        return 0
    else:
        result = {"status": "FAIL", "errors": errors, "path": str(path)}
        print_json_or_text(result, args.json)
        return 1


def print_json_or_text(result, as_json):
    if as_json:
        import json
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        if result["status"] == "PASS":
            print(f"✅ PASS")
            for k, v in result.items():
                if k != "status":
                    print(f"   {k}: {v}")
        else:
            print(f"❌ FAIL")
            for e in result.get("errors", []):
                print(f"   - {e}")


if __name__ == "__main__":
    sys.exit(main())