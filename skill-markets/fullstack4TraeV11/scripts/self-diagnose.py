#!/usr/bin/env python3
"""
V11 self-diagnose.py — Meta 元检测（rot-detector 自身失真检测）

Usage:
    python self-diagnose.py [--project-root <path>]

Exit codes:
    0 = PASS（rot-detector 自身未腐化）
    1 = FAIL（rot-detector 自身有腐化点）
"""
import sys
import argparse
import pathlib
import json
import re
from datetime import datetime, timezone

# Meta 检测项
META_CHECKS = {
    "rot_detector_logic": "腐化扫描逻辑自身是否最新？",
    "phase_gate_help": "phase-gate.py --help 输出是否包含 --verify-rot-scan？",
    "score_formula": "4 维评分公式是否正确？",
    "constitution_articles": "16 Articles 宪法是否对齐？",
    "state_card_schema": "状态卡 schema 是否最新？",
    "stub_markers": "stub 标记列表是否最新？",
}


def check_rot_detector_logic(project_root: pathlib.Path) -> tuple:
    """检查 rot-detector 自身逻辑是否腐化"""
    scripts = project_root / "scripts"
    rot_scan = scripts / "proactive-scan.py"
    if not rot_scan.exists():
        return False, "缺失proactive-scan.py"

    content = rot_scan.read_text(encoding="utf-8")
    # 检测 10 项扫描是否齐全
    if "obstacle-honesty" not in content or "reason-fabrication" not in content:
        return False, "缺失 V10.10 +2 项"

    return True, "10 项齐全（V10.10）"


def check_phase_gate_help(project_root: pathlib.Path) -> tuple:
    """检查 phase-gate --help 输出"""
    phase_gate = project_root / "scripts/phase-gate.py"
    if not phase_gate.exists():
        return False, "缺失 phase-gate.py"

    content = phase_gate.read_text(encoding="utf-8")
    if "--verify-rot-scan" not in content:
        return False, "phase-gate.py 缺 --verify-rot-scan 参数"

    return True, "phase-gate.py 含 --verify-rot-scan"


def check_score_formula(project_root: pathlib.Path) -> tuple:
    """检查 4 维评分公式"""
    acceptance = project_root / "scripts/acceptance-audit.py"
    if not acceptance.exists():
        return False, "缺失 acceptance-audit.py"

    content = acceptance.read_text(encoding="utf-8")
    # 必须有 4 维 + 加权公式
    required = ["DIMENSIONS", "WEIGHTS", "calculated_total"]
    missing = [r for r in required if r not in content]
    if missing:
        return False, f"缺公式组件: {missing}"

    return True, "4 维评分公式完整"


def check_constitution_articles(project_root: pathlib.Path) -> tuple:
    """检查 16 Articles 宪法"""
    constitution = project_root / "references/constitution.md"
    if not constitution.exists():
        return False, "缺失 constitution.md"

    content = constitution.read_text(encoding="utf-8")
    # 必须有 16 篇文章（I-XVI）
    articles_required = ["Article I", "Article II", "Article III", "Article IV",
                        "Article V", "Article VI", "Article VII", "Article VIII",
                        "Article IX", "Article X", "Article XI", "Article XII",
                        "Article XIII", "Article XIV", "Article XV", "Article XVI"]
    missing = [a for a in articles_required if a not in content]
    if missing:
        return False, f"缺 Articles: {missing}"

    return True, "16 Articles 齐全"


def check_state_card_schema(project_root: pathlib.Path) -> tuple:
    """检查状态卡 schema"""
    card_proto = project_root / "references/state-card-protocol.md"
    if not card_proto.exists():
        return False, "缺失 state-card-protocol.md"

    content = card_proto.read_text(encoding="utf-8")
    # 必须有 3 类状态卡（project / change / bug）
    if "project" not in content or "change" not in content or "bug" not in content:
        return False, "缺 3 类状态卡"

    return True, "3 类状态卡 schema 齐全"


def check_stub_markers(project_root: pathlib.Path) -> tuple:
    """检查 stub 标记列表"""
    rot_scan = project_root / "scripts/proactive-scan.py"
    if not rot_scan.exists():
        return False, "缺失proactive-scan.py"

    content = rot_scan.read_text(encoding="utf-8")
    # 必须含 5+ stub 标记
    markers = ["STUB:", "TODO:", "FIXME:", "XXX", "raise NotImplementedError"]
    found = [m for m in markers if m in content]

    if len(found) < 5:
        return False, f"stub 标记 < 5: {found}"

    return True, f"5 个 stub 标记齐全"


CHECK_FUNCTIONS = {
    "rot_detector_logic": check_rot_detector_logic,
    "phase_gate_help": check_phase_gate_help,
    "score_formula": check_score_formula,
    "constitution_articles": check_constitution_articles,
    "state_card_schema": check_state_card_schema,
    "stub_markers": check_stub_markers,
}


def main():
    parser = argparse.ArgumentParser(description="V11 self-diagnose 元检测")
    parser.add_argument("--project-root", default=".", help="项目根路径")
    parser.add_argument("--json", action="store_true", help="JSON 输出")
    args = parser.parse_args()

    project_root = pathlib.Path(args.project_root).resolve()

    results = []
    for name, desc in META_CHECKS.items():
        func = CHECK_FUNCTIONS[name]
        is_pass, msg = func(project_root)
        results.append({
            "name": name,
            "description": desc,
            "status": "PASS" if is_pass else "FAIL",
            "message": msg,
        })

    all_pass = all(r["status"] == "PASS" for r in results)

    output = {
        "scan_at": datetime.now(timezone.utc).isoformat(),
        "status": "PASS" if all_pass else "FAIL",
        "checks": results,
    }

    if args.json:
        print(json.dumps(output, indent=2, ensure_ascii=False))
    else:
        icon = "✅" if all_pass else "❌"
        print(f"{icon} {output['status']} — Meta 元检测")
        for r in results:
            mark = "✓" if r["status"] == "PASS" else "✗"
            print(f"  [{mark}] {r['name']}: {r['message']}")

    return 0 if all_pass else 1


if __name__ == "__main__":
    sys.exit(main())