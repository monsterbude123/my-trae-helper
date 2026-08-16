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

Gate Hardening (2026-08-14):
    - Environment validation (V11_GATE_ENFORCED / V11_GATE_STAGE / V11_GATE_CALLER)
    - SHA-256 signature generation and verification
    - Gate execution validation (evidence chain + gate ID + timestamp)
"""
import sys
import argparse
import pathlib
import hashlib
import os
import json
from datetime import datetime, timezone

# 13 stage 名单（必须严格匹配 registry/state-machine.yaml）
VALID_STAGES = [
    "-1/intake", "0/plan", "0.5/test-plan", "1/spec", "1.5/prototype",
    "2/contract", "3/implement", "3.5/real-verify", "4/review",
    "4.5/rot-scan", "5/accept", "6/bug-fix", "7/health"
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


def validate_environment() -> dict:
    """验证 V11 Gate 环境变量（V11_GATE_ENFORCED / V11_GATE_STAGE / V11_GATE_CALLER）
    
    Returns:
        dict: {"valid": bool, "enforced": str, "stage": str, "caller": str, "errors": list}
    """
    enforced = os.getenv("V11_GATE_ENFORCED", "")
    stage = os.getenv("V11_GATE_STAGE", "")
    caller = os.getenv("V11_GATE_CALLER", "")
    
    result = {
        "valid": True,
        "enforced": enforced,
        "stage": stage,
        "caller": caller,
        "errors": []
    }
    
    if enforced and enforced.lower() not in ("true", "1", "yes"):
        result["valid"] = False
        result["errors"].append(f"V11_GATE_ENFORCED={enforced} 非法（应为 true/false）")
    
    if stage and stage not in VALID_STAGES:
        result["valid"] = False
        result["errors"].append(f"V11_GATE_STAGE={stage} 非法（不在 13 stage 名单中）")
    
    return result


def sign_gate_result(result: dict) -> str:
    """生成 Gate 结果的 SHA-256 签名
    
    Args:
        result: Gate 结果字典（必须含 status / gate_id / stage / timestamp）
    
    Returns:
        str: SHA-256 签名（hex）
    """
    canonical = json.dumps({
        "status": result.get("status"),
        "gate_id": result.get("gate_id", ""),
        "stage": result.get("stage", result.get("current_stage", "")),
        "timestamp": result.get("timestamp", "")
    }, sort_keys=True, ensure_ascii=False)
    
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def verify_gate_signature(result: dict, signature: str) -> bool:
    """验证 Gate 结果签名
    
    Args:
        result: Gate 结果字典
        signature: 预期签名（hex）
    
    Returns:
        bool: 签名是否匹配
    """
    expected = sign_gate_result(result)
    return expected == signature


def validate_gate_execution(result: dict, env_info: dict) -> dict:
    """验证 Gate 执行完整性（环境变量 + 签名 + 证据链 + 门禁 ID + 时间戳）
    
    Args:
        result: Gate 结果字典
        env_info: validate_environment() 返回的环境信息
    
    Returns:
        dict: {"valid": bool, "errors": list, "warnings": list}
    """
    errors = []
    warnings = []
    
    if not env_info.get("valid"):
        errors.extend(env_info.get("errors", []))
    
    if "gate_id" not in result:
        warnings.append("缺 gate_id（建议在 husky hook 中生成）")
    
    if "timestamp" not in result:
        warnings.append("缺 timestamp（建议使用 ISO 8601 格式）")
    
    if "status" not in result:
        errors.append("缺 status 字段")
    
    if "evidence" not in result and "artifacts" not in result:
        warnings.append("缺 evidence/artifacts（证据链不完整）")
    
    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings
    }


def parse_state_card(path: pathlib.Path) -> dict:
    """解析状态卡 frontmatter（委托 _lib_state_card 共用库）"""
    import sys
    sys.path.insert(0, str(pathlib.Path(__file__).parent))
    from _lib_state_card import parse_state_card as _parse
    return _parse(path)


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
        # bb 为 Python None(YAML null 关键字解析结果)才是真无 blocker;
        # 字符串 "null"(用户显式标注)或 dict/list 都视为"有 blocker"
        if bb is not None and ss == "completed":
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
    parser = argparse.ArgumentParser(description="V11 阶段门禁（硬化版）")
    parser.add_argument("--state-card", required=True, help="状态卡文件路径")
    parser.add_argument("--stage", help="期望 stage（与状态卡 current_stage 一致）")
    parser.add_argument("--next-stage", nargs="?", default=None,
                        help="下一 stage（P0-2 NEW：校验 current_stage → next_stage 转换合法性）")
    parser.add_argument("--registry-dir", default=None,
                        help="registry 目录（默认 skill_root/registry，可被 --project-root/.trae/registry 自动探测覆盖）")
    parser.add_argument("--project-root", default=None,
                        help="项目根（自动探测 <project_root>/.trae/registry/）")
    parser.add_argument("--json", action="store_true", help="JSON 输出")
    parser.add_argument("--verify-signature", help="验证 Gate 签名（hex）")
    parser.add_argument("--skip-env-check", action="store_true", help="跳过环境变量验证")
    # P0-2:stage-id 可能以 - 开头（如 -1/intake），会被 argparse 当作 flag 报错。
    # 用 nargs="?" 让 argparse 接受"无值"情形，把 - 开头的值留在 remaining 中。
    pre_parsed, remaining = parser.parse_known_args()
    args = pre_parsed
    if pre_parsed.next_stage is None and remaining:
        # 匹配 V11 stage-id 格式:可选负号 + 数字 + / + 文本（如 -1/intake, 0/plan, 4.5/rot-scan）
        import re as _re
        stage_id_re = _re.compile(r"^-?\d+(?:\.\d+)?/[A-Za-z][\w-]*$")
        for tok in remaining:
            if stage_id_re.match(tok):
                args.next_stage = tok
                break

    path = pathlib.Path(args.state_card)
    fields = parse_state_card(path)

    if "error" in fields:
        result = {
            "status": "FAIL",
            "errors": [fields["error"]],
            "path": str(path),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "gate_id": f"stage-gate-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        }
        signature = sign_gate_result(result)
        result["signature"] = signature
        print_json_or_text(result, args.json)
        return 1

    is_valid, errors = validate_state_card(fields, args.stage)

    # P0-2 NEW：--next-stage 提供时校验状态转换合法性
    # registry_dir 解析优先级:显式 --registry-dir > 自动探测项目级 > skill_root/registry
    transition_check = None
    if args.next_stage:
        # 解析 registry_dir
        skill_root = pathlib.Path(__file__).resolve().parent.parent
        if args.registry_dir:
            reg_dir = pathlib.Path(args.registry_dir)
        else:
            reg_dir = None
            if args.project_root:
                proj_reg = pathlib.Path(args.project_root) / ".trae" / "registry"
                if proj_reg.is_dir() and (proj_reg / "state-machine.yaml").is_file():
                    reg_dir = proj_reg
            if reg_dir is None:
                reg_dir = skill_root / "registry"

        from _lib_state_card import load_state_machine, validate_transition
        state_machine = load_state_machine(reg_dir)
        from_stage = fields.get("current_stage", "")
        ok, reason = validate_transition(state_machine, from_stage, args.next_stage)
        transition_check = {
            "from_stage": from_stage,
            "to_stage": args.next_stage,
            "valid": ok,
            "reason": reason,
            "registry_dir": str(reg_dir),
        }
        if not ok:
            errors.append(f"transition FAIL: {reason}")

    if is_valid and not errors:
        result = {
            "status": "PASS",
            "current_stage": fields.get("current_stage"),
            "next_stage_id": (fields.get("next_stage") or {}).get("id"),
            "health": fields.get("health"),
            "gate_status": (fields.get("gate_result") or {}).get("status"),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "gate_id": f"stage-gate-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "artifacts": fields.get("artifacts", [])
        }

        if not args.skip_env_check:
            env_info = validate_environment()
            result["environment"] = env_info

            exec_validation = validate_gate_execution(result, env_info)
            result["execution_valid"] = exec_validation["valid"]
            if exec_validation["errors"]:
                result["execution_errors"] = exec_validation["errors"]
            if exec_validation["warnings"]:
                result["execution_warnings"] = exec_validation["warnings"]

        if transition_check is not None:
            result["transition_check"] = transition_check

        signature = sign_gate_result(result)
        result["signature"] = signature

        if args.verify_signature:
            sig_valid = verify_gate_signature(result, args.verify_signature)
            result["signature_valid"] = sig_valid

        print_json_or_text(result, args.json)
        return 0
    else:
        result = {
            "status": "FAIL",
            "errors": errors,
            "path": str(path),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "gate_id": f"stage-gate-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        }
        if transition_check is not None:
            result["transition_check"] = transition_check
        signature = sign_gate_result(result)
        result["signature"] = signature
        print_json_or_text(result, args.json)
        # P0-2 NEW:transition FAIL → exit 2;field FAIL → exit 1
        if transition_check is not None and not transition_check.get("valid"):
            return 2
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