#!/usr/bin/env python3
"""dispatch-agent.py — V10.9 Agent 统一入口

基于 [scenarios.md](../scenarios.md) 10 个场景，生成可执行的 agent 编排模板。

用法:
  python scripts/dispatch-agent.py --scenario 3
  python scripts/dispatch-agent.py --scenario 3 --json
  python scripts/dispatch-agent.py --list
"""
import argparse
import json
import sys
from typing import Dict, List

# 10 场景 Agent 编排（精简版）
SCENARIOS: Dict[int, Dict] = {
    1: {"name": "项目 0→1 初始化", "type": "mixed",
     "scripts": [
        {"step": 1, "name": "setup-feature.py", "cmd": "--name 00-01-init-scaffold --print-template-path"},
        {"step": 2, "name": "setup-feature.py", "cmd": "--name 00-01-init-scaffold"},
        {"step": 3, "name": "setup-feature.py", "cmd": "--check-article-xiv"},
     ]},
    2: {"name": "已有代码迷雾消除", "type": "agent",
     "agents": [{"step": 1, "name": "project-health-auditor", "must_read": ["references/project-health-checklist.md"]}]},
    3: {"name": "新增功能完整链（核心）", "type": "agent",
     "agents": [
        {"step": 1, "name": "planner", "phase": "plan"},
        {"step": 2, "name": "spec-enhancer", "phase": "spec", "must_read": ["references/clarify-checklist.md"]},
        {"step": 3, "name": "contract-writer", "phase": "contract"},
        {"step": 4, "name": "implementer", "phase": "implement"},
        {"step": 5, "name": "reviewer", "phase": "review"},
     ],
     "scripts": [{"step": 6, "name": "proactive-scan.py", "phase": "rot-detector"}]},
    4: {"name": "Spec 累积生长", "type": "mixed",
     "agents": [{"step": 1, "name": "implementer", "phase": "merge"}],
     "scripts": [
        {"step": 2, "name": "spec-merge.py", "cmd": "docs/specs/{feature}/spec.md docs/specs/{feature}/spec.md"},
        {"step": 3, "name": "spec-purge.py", "cmd": "--feature {feature} --check-path"},
     ]},
    5: {"name": "Bug 修复快捷链", "type": "agent",
     "agents": [
        {"step": 1, "name": "debugger", "phase": "debug"},
        {"step": 2, "name": "implementer", "phase": "fix"},
        {"step": 3, "name": "reviewer", "phase": "review-light"},
     ],
     "scripts": [{"step": 4, "name": "proactive-scan.py", "phase": "rot-detector"}]},
    6: {"name": "审核不通过返工", "type": "agent",
     "agents": [{"step": 1, "name": "reviewer", "phase": "review"}],
     "scripts": [{"step": 2, "name": "proactive-scan.py", "phase": "rot-detector"}]},
    7: {"name": "Spec 回流重构", "type": "mixed",
     "agents": [
        {"step": 1, "name": "implementer", "phase": "refactor"},
        {"step": 2, "name": "spec-writer", "phase": "respec"},
        {"step": 3, "name": "contract-writer", "phase": "recontract"},
        {"step": 4, "name": "implementer", "phase": "reimplement"},
     ],
     "scripts": [
        {"step": 5, "name": "spec-purge.py", "cmd": "--feature {feature}"},
        {"step": 6, "name": "spec-validate.py", "cmd": "docs/specs/{feature}/spec.md --mode full"},
        {"step": 7, "name": "spec-knowledge-extract.py", "cmd": "--feature {feature}"},
     ]},
    8: {"name": "反复反馈升级", "type": "protocol",
     "skills": [{"step": 1, "name": "session-distiller"}],
     "scripts": [{"step": 2, "name": "proactive-scan.py", "phase": "rot-detector"}]},
    9: {"name": "V9.2 项目迁移", "type": "script",
     "scripts": [
        {"step": 1, "name": "migrate-v9-to-v10.py", "cmd": "--project-root . --project-type {type} --dry-run"},
        {"step": 2, "name": "migrate-v9-to-v10.py", "cmd": "--project-root . --project-type {type}"},
        {"step": 3, "name": "project-health-auditor (agent)", "internal": True},
        {"step": 4, "name": "proactive-scan.py", "cmd": ""},
     ]},
    10: {"name": "项目健康度自检", "type": "agent",
     "agents": [{"step": 1, "name": "project-health-auditor", "phase": "diagnose"}]},
}


def render_markdown(scenario_id: int, cfg: Dict) -> str:
    lines = [f"# 场景 {scenario_id}: {cfg['name']}", "",
             f"**类型**: {cfg['type']}", "",
             "## 流水线 [PIPELINE]"]
    for tag in ("agents", "skills", "scripts"):
        items = cfg.get(tag, [])
        if items:
            label = {"agents": "Agent", "skills": "Skill", "scripts": "脚本"}[tag]
            lines.append(f"### {label}")
            for it in items:
                phase = it.get("phase", "")
                must = ", ".join(it.get("must_read", []))
                cmd = it.get("cmd", "")
                if cmd:
                    lines.append(f"- Step {it['step']}: `{tag[:-1]}.{it['name']} {cmd}` (phase={phase})")
                else:
                    lines.append(f"- Step {it['step']}: **{it['name']}** (phase={phase}) [{must}]")
    lines.append("")
    lines.append("## 产物 [OUTPUT]")
    lines.append("- artifacts: 见 scenarios.md")
    lines.append("- evidence: 5 维度 + rot-detector")
    lines.append("- status: ✓/⚠️/❌")
    return "\n".join(lines)


def render_json(scenario_id: int, cfg: Dict) -> str:
    return json.dumps({"scenario": scenario_id, "config": cfg}, ensure_ascii=False, indent=2)


def main() -> int:
    parser = argparse.ArgumentParser(description="V10.9 Agent 统一入口")
    parser.add_argument("--scenario", type=int, choices=range(1, 11))
    parser.add_argument("--list", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    if args.list:
        for sid, cfg in SCENARIOS.items():
            print(f"  {sid}: {cfg['name']} ({cfg['type']})")
        return 0
    if args.scenario is None:
        parser.error("必须指定 --scenario N 或 --list")
    cfg = SCENARIOS[args.scenario]
    print(render_json(args.scenario, cfg) if args.json else render_markdown(args.scenario, cfg))
    return 0


if __name__ == "__main__":
    sys.exit(main())
