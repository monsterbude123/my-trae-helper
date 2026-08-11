#!/usr/bin/env python3
"""
V11 phase-gate.py — V11 全局阶段门禁（13 stage 统一，含 rot-scan 验证）

Usage:
    python phase-gate.py --state-card <path> [--stage <stage-id>] [--verify-rot-scan]

Exit codes:
    0 = PASS
    1 = FAIL
    2 = N/A（标注理由）

新增 V10.11:
    --verify-rot-scan: 验证 Stage 4.5 rot-scan 已 PASS（rot-scan JSON 报告存在 + fix-list.json 非空）
"""
import sys
import argparse
import pathlib
import json
from datetime import datetime

# 委托 stage-gate.py 复用其解析逻辑（用 importlib 处理 hyphen 文件名）
def _import_stage_gate():
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "stage_gate",
        str(pathlib.Path(__file__).parent / "stage-gate.py")
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


_sg = _import_stage_gate()
VALID_STAGES = _sg.VALID_STAGES
REQUIRED_STAGES = _sg.REQUIRED_STAGES
REQUIRED_FIELDS = _sg.REQUIRED_FIELDS
VALID_HEALTH = _sg.VALID_HEALTH
validate_state_card = _sg.validate_state_card

# 不可跳过的 stage（V11 §0 硬门禁）
REQUIRED_STAGES = [
    "-1/intake", "0/plan", "1/spec", "3.5/real-verify", "4.5/rot-scan"
]

ROT_SCAN_OUTPUT_DIR = pathlib.Path("docs/reports")


def verify_rot_scan(change_id: str) -> tuple:
    """验证 Stage 4.5 rot-scan 已 PASS
    返回 (is_pass, message)
    """
    rot_scan_json = ROT_SCAN_OUTPUT_DIR / f"rot-scan-{datetime.now().strftime('%Y-%m-%d')}.json"
    if not rot_scan_json.exists():
        return False, f"缺失 rot-scan JSON 报告: {rot_scan_json}"

    try:
        data = json.loads(rot_scan_json.read_text(encoding="utf-8"))
    except Exception as e:
        return False, f"rot-scan JSON 解析失败: {e}"

    if data.get("status") != "PASS":
        return False, f"rot-scan 状态非 PASS（{data.get('status')}）"

    fix_list_path = ROT_SCAN_OUTPUT_DIR / "fix-list.json"
    if not fix_list_path.exists():
        return False, f"缺失 fix-list.json: {fix_list_path}"

    try:
        fix_data = json.loads(fix_list_path.read_text(encoding="utf-8"))
    except Exception as e:
        return False, f"fix-list.json 解析失败: {e}"

    fixes = fix_data.get("fixes", [])
    if not fixes:
        return False, "fix-list.json 为空（rot-detector 自身腐化点未产出）"

    return True, f"rot-scan PASS（{len(fixes)} 项 fix）"


def main():
    parser = argparse.ArgumentParser(description="V11 全局阶段门禁")
    parser.add_argument("--state-card", required=True, help="状态卡文件路径")
    parser.add_argument("--stage", help="期望 stage（与状态卡 current_stage 一致）")
    parser.add_argument("--verify-rot-scan", action="store_true", help="V10.11: 验证 Stage 4.5 rot-scan PASS")
    parser.add_argument("--change-id", help="change ID（用于 rot-scan 验证）")
    parser.add_argument("--json", action="store_true", help="JSON 输出")
    args = parser.parse_args()

    path = pathlib.Path(args.state_card)
    fields = _sg.parse_state_card(path)
    if "error" in fields:
        print(f"❌ FAIL: {fields['error']}")
        return 1
    is_valid, errors = validate_state_card(fields, args.stage)

    rot_scan_pass = True
    rot_scan_msg = "N/A"
    if args.verify_rot_scan:
        if not args.change_id:
            print("❌ --verify-rot-scan 必含 --change-id")
            return 1
        rot_scan_pass, rot_scan_msg = verify_rot_scan(args.change_id)

    all_pass = is_valid and rot_scan_pass

    result = {
        "status": "PASS" if all_pass else "FAIL",
        "state_card_valid": is_valid,
        "state_card_errors": errors if not is_valid else [],
        "rot_scan_pass": rot_scan_pass,
        "rot_scan_msg": rot_scan_msg,
        "rot_scan_verified": args.verify_rot_scan,
    }

    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        if all_pass:
            print(f"✅ PASS — {path}")
            if args.verify_rot_scan:
                print(f"   rot-scan: {rot_scan_msg}")
        else:
            print(f"❌ FAIL — {path}")
            for e in errors:
                print(f"   - state_card: {e}")
            if not rot_scan_pass:
                print(f"   - rot_scan: {rot_scan_msg}")

    return 0 if all_pass else 1


if __name__ == "__main__":
    sys.exit(main())