#!/usr/bin/env python3
"""prototype-backfill-check.py — V11.2 NEW 原型双产物最低门禁检查(蒸馏自 V10 prototype.md §最低门禁)

蒸馏来源: fullstack4TraeV10/references/prototype.md §最低门禁 + §反向补全
失败模式: design-prompt.md 缺 5 状态 / ui-ux-logic.md 缺组件树/交互流/状态表/错误处理

用法:
    python scripts/prototype-backfill-check.py --change-id {change-id}
    python scripts/prototype-backfill-check.py --change-id {change-id} --json
    python scripts/prototype-backfill-check.py --project-root . --all
"""
import argparse
import json
import pathlib
import re
import sys
from typing import Dict


# V10 §最低门禁 + §反向补全
DESIGN_PROMPT_MIN = {
    "5_states": ["加载中", "空数据", "正常态", "错误态", "边界态"],
    "responsive_breakpoints_min": 2,
}

UI_UX_LOGIC_MIN = {
    "component_tree_sections": 1,
    "interaction_flow_sections": 2,
    "state_table_rows": 3,
    "error_handling_rows": 3,
}


def check_design_prompt(path: pathlib.Path) -> Dict:
    """V11.2 NEW: design-prompt.md 5 状态 + 响应式断点检查
    V11.3 NEW: + Fidelity 等级字段读取(L1/L2/L3,默认 L2 mockup)
    """
    result = {
        "exists": path.exists(),
        "5_states_found": [],
        "responsive_breakpoints": 0,
        "issues": [],
        # V11.3 NEW
        "fidelity_level": None,  # "L1" | "L2" | "L3" | None
        "fidelity_default": False,  # True = 未标注,默认 L2
    }
    if not result["exists"]:
        result["issues"].append("design-prompt.md 不存在(P0 阻塞)")
        return result

    content = path.read_text(encoding="utf-8")

    # 5 状态检查
    for state in DESIGN_PROMPT_MIN["5_states"]:
        if state in content:
            result["5_states_found"].append(state)

    if len(result["5_states_found"]) < 5:
        missing = set(DESIGN_PROMPT_MIN["5_states"]) - set(result["5_states_found"])
        result["issues"].append(f"5 状态缺失: {missing}")

    # 响应式断点(检查 Desktop/Tablet/Mobile 至少 2)
    breakpoints = sum(1 for bp in ["Desktop", "Tablet", "Mobile"] if bp in content)
    result["responsive_breakpoints"] = breakpoints
    if breakpoints < DESIGN_PROMPT_MIN["responsive_breakpoints_min"]:
        result["issues"].append(f"响应式断点不足: {breakpoints} < {DESIGN_PROMPT_MIN['responsive_breakpoints_min']}")

    # V11.3 NEW: 读取 Fidelity 等级 (匹配模板中的 Fidelity 等级字段)
    fidelity_match = re.search(
        r'(?:Fidelity\s*等级|##\s*Fidelity)[^\n]*?(\[ \]\s*L1|\[ \]\s*L2|\[ \]\s*L3|\bL1\b|\bL2\b|\bL3\b)',
        content,
    )
    if fidelity_match:
        result["fidelity_level"] = fidelity_match.group(1).replace("[ ] ", "").strip()
    else:
        # 默认 L2 mockup (V11.3 §8.1 默认值)
        result["fidelity_level"] = "L2"
        result["fidelity_default"] = True

    return result


def check_ui_ux_logic(path: pathlib.Path) -> Dict:
    """V11.2 NEW: ui-ux-logic.md 组件树/交互流/状态表/错误处理检查"""
    result = {
        "exists": path.exists(),
        "component_tree_section": False,
        "interaction_flow_count": 0,
        "state_table_rows": 0,
        "error_handling_rows": 0,
        "issues": [],
    }
    if not result["exists"]:
        result["issues"].append("ui-ux-logic.md 不存在(P0 阻塞)")
        return result

    content = path.read_text(encoding="utf-8")

    # 组件树
    result["component_tree_section"] = "## 组件树" in content
    if not result["component_tree_section"]:
        result["issues"].append("缺 ## 组件树 章节")

    # 交互流(## 交互流 下 ## 流 N: 计数)
    interaction_section = re.search(r'##\s*交互流([\s\S]*?)(?=##\s|\Z)', content)
    if interaction_section:
        result["interaction_flow_count"] = len(re.findall(r'###\s*流\s*\d+:', interaction_section.group(1)))
    if result["interaction_flow_count"] < UI_UX_LOGIC_MIN["interaction_flow_sections"]:
        result["issues"].append(f"交互流不足: {result['interaction_flow_count']} < {UI_UX_LOGIC_MIN['interaction_flow_sections']}")

    # 状态表(## 状态管理 下表格行数)
    state_section = re.search(r'##\s*状态管理([\s\S]*?)(?=##\s|\Z)', content)
    if state_section:
        rows = [r for r in state_section.group(1).split('\n') if r.strip().startswith('|') and not r.strip().startswith('|---')]
        result["state_table_rows"] = max(0, len(rows) - 1)
    if result["state_table_rows"] < UI_UX_LOGIC_MIN["state_table_rows"]:
        result["issues"].append(f"状态表行数不足: {result['state_table_rows']} < {UI_UX_LOGIC_MIN['state_table_rows']}")

    # 错误与边界处理
    error_section = re.search(r'##\s*错误与边界处理([\s\S]*?)(?=##\s|\Z)', content)
    if error_section:
        rows = [r for r in error_section.group(1).split('\n') if r.strip().startswith('|') and not r.strip().startswith('|---')]
        result["error_handling_rows"] = max(0, len(rows) - 1)
    if result["error_handling_rows"] < UI_UX_LOGIC_MIN["error_handling_rows"]:
        result["issues"].append(f"错误处理行数不足: {result['error_handling_rows']} < {UI_UX_LOGIC_MIN['error_handling_rows']}")

    return result


def detect_ui_involved(change_id: str, project_root: pathlib.Path) -> bool:
    """V11.2.1: 检测 change 是否涉及 UI(spec.md 含 UI 声明 → True)

    启发式: spec.md 全文含 UI 关键字(页面/组件/视觉/交互/前端/UI/UX/prototypes 等)
    纯后端/API/CLI 不涉及 → 返回 False,跳过整个双产物检查
    """
    spec_md = project_root / "docs/specs/changes" / change_id / "spec.md"
    if not spec_md.exists():
        return True  # 无 spec.md 时默认视为涉及(保守)
    content = spec_md.read_text(encoding="utf-8")
    ui_keywords = ["UI", "UX", "页面", "组件", "视觉", "交互", "前端", "prototypes", "design-prompt", "ui-ux-logic"]
    return any(kw in content for kw in ui_keywords)


def check_change(change_id: str, project_root: pathlib.Path) -> Dict:
    """检查单 change 的 prototypes/ 最低门禁(仅 UI 涉及 change)"""
    prototypes_dir = project_root / "docs/specs/changes" / change_id / "prototypes"
    design_prompt = prototypes_dir / "design-prompt.md"
    ui_ux_logic = prototypes_dir / "ui-ux-logic.md"

    ui_involved = detect_ui_involved(change_id, project_root)

    result = {
        "change_id": change_id,
        "ui_involved": ui_involved,
        "prototypes_dir_exists": prototypes_dir.exists(),
        "design_prompt": check_design_prompt(design_prompt),
        "ui_ux_logic": check_ui_ux_logic(ui_ux_logic),
    }

    if not ui_involved:
        # 纯后端/API/CLI:跳过双产物检查
        result["all_pass"] = True
        result["issues_count"] = 0
        result["skipped_reason"] = "纯后端/API/CLI change,无 UI 涉及,跳过 prototypes/ 检查"
        return result

    all_issues = result["design_prompt"]["issues"] + result["ui_ux_logic"]["issues"]
    result["all_pass"] = len(all_issues) == 0 and result["prototypes_dir_exists"]
    result["issues_count"] = len(all_issues)

    return result


def main() -> int:
    parser = argparse.ArgumentParser(description="V11.2 prototype-backfill-check: 原型双产物最低门禁")
    parser.add_argument("--project-root", default=".", help="项目根路径")
    parser.add_argument("--change-id", help="指定 change-id(如 2026-08-12-feature)")
    parser.add_argument("--all", action="store_true", help="扫描所有 changes/")
    parser.add_argument("--json", action="store_true", help="JSON 输出")
    args = parser.parse_args()

    project_root = pathlib.Path(args.project_root).resolve()

    if args.change_id:
        results = [check_change(args.change_id, project_root)]
    elif args.all:
        changes_dir = project_root / "docs/specs/changes"
        results = [check_change(d.name, project_root) for d in sorted(changes_dir.iterdir()) if d.is_dir()]
    else:
        parser.error("必须指定 --change-id 或 --all")

    all_pass = all(r["all_pass"] for r in results)

    if args.json:
        print(json.dumps({"results": results, "all_pass": all_pass}, indent=2, ensure_ascii=False))
    else:
        for r in results:
            if r.get("skipped_reason"):
                # 纯后端/API/CLI:跳过双产物
                print(f"[SKIP] {r['change_id']} (纯后端/API/CLI,跳过 prototypes/ 检查)")
            else:
                status = "[PASS]" if r["all_pass"] else "[FAIL]"
                print(f"{status} {r['change_id']} (issues: {r['issues_count']})")
                # V11.3 NEW: 输出 fidelity 等级(便于评审员对照阈值)
                dp = r.get("design_prompt", {})
                fidelity = dp.get("fidelity_level") or "N/A"
                if dp.get("fidelity_default"):
                    print(f"  ⚠️ design-prompt.md 未标注 fidelity 等级,默认 L2 mockup(V11.3 §8.1)")
                else:
                    print(f"  Fidelity 等级: {fidelity}")
                for issue in r["design_prompt"]["issues"] + r["ui_ux_logic"]["issues"]:
                    print(f"  - {issue}")

    return 0 if all_pass else 1


if __name__ == "__main__":
    sys.exit(main())