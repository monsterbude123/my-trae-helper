#!/usr/bin/env python3
"""dispatch-agent.py — V11.1 Agent 编排统一入口（蒸馏自 V10.9）

基于 V11 13 stage，生成可执行的 agent 编排模板。

V11 vs V10 差异:
- V10: 10 场景 × 5 phase（plan/spec/contract/implement/review）
- V11: 11 场景 × 13 stage（intake/plan/test-plan/spec/prototype/contract/implement/real-verify/review/rot-scan/accept/bug-fix/project-health）

用法:
  python scripts/dispatch-agent.py --scenario 3
  python scripts/dispatch-agent.py --scenario 3 --json
  python scripts/dispatch-agent.py --list
"""
import argparse
import json
import sys
from typing import Dict


# 11 场景 Agent 编排（V11 完整版）
SCENARIOS: Dict[int, Dict] = {
    1: {"name": "项目 0→1 初始化", "type": "mixed",
     "scripts": [
        {"step": 1, "name": "init-from-zero.py", "cmd": "--project-root . --type {web|tauri|cli|library|backend}"},
        {"step": 2, "name": "setup-feature.py", "cmd": "--name 00-01-init-scaffold"},
        {"step": 3, "name": "stage-gate.py", "cmd": "--stage -1/intake --check Article XIV"},
     ]},
    2: {"name": "已有代码迷雾消除（项目健康度）", "type": "agent",
     "agents": [
        {"step": 1, "name": "project-health-auditor", "skill": "skills/13-project-health",
         "must_read": ["references/four-dimension-check.md", "references/gitnexus-impact-audit.md"]},
     ]},
    3: {"name": "新增功能完整链（核心 13 stage）", "type": "agent",
     "agents": [
        {"step": 1, "name": "intake-agent", "skill": "skills/01-intake",
         "must_read": ["references/intent-types.md"]},
        {"step": 2, "name": "planner", "skill": "skills/02-plan",
         "must_read": ["references/impact-assessment.md", "references/dedup-by-atom.md"]},
        {"step": 3, "name": "test-planner", "skill": "skills/03-test-plan",
         "must_read": ["references/coverage-rules.md"]},
        {"step": 4, "name": "spec-enhancer", "skill": "skills/04-spec",
         "must_read": ["references/acceptance-enhancement.md", "references/clarify-checklist.md"]},
        {"step": 5, "name": "spec-prototype-enhancer", "skill": "skills/05-prototype"},
        {"step": 6, "name": "contract-writer", "skill": "skills/06-contract"},
        {"step": 7, "name": "implementer", "skill": "skills/07-implement",
         "must_read": ["references/tdd-workflow.md", "references/drift-detect.md", "references/gitnexus-impact.md"]},
        {"step": 8, "name": "real-verifier", "skill": "skills/08-real-verify"},
        {"step": 9, "name": "reviewer", "skill": "skills/09-review",
         "must_read": ["references/four-dimension-scoring.md", "references/multi-round-revision.md"]},
        {"step": 10, "name": "rot-detector", "skill": "skills/10-rot-scan"},
        {"step": 11, "name": "archive-agent", "skill": "skills/11-accept"},
     ],
     "scripts": [
        {"step": 12, "name": "proactive-scan.py", "phase": "rot-detector"},
     ]},
    4: {"name": "Bug 修复 6 层排查链", "type": "agent",
     "agents": [
        {"step": 1, "name": "intake-agent", "skill": "skills/01-intake",
         "must_read": ["references/intent-types.md"]},
        {"step": 2, "name": "debugger", "skill": "skills/12-bug-fix",
         "must_read": ["references/six-layer-diagnosis.md", "references/five-step-flow.md", "references/gitnexus-6-layer.md", "references/cross-layer-fix.md", "anti-patterns/01-skip-e2e-first.md"]},
        {"step": 3, "name": "implementer", "skill": "skills/07-implement"},
        {"step": 4, "name": "reviewer", "skill": "skills/09-review", "phase": "review-light"},
     ],
     "scripts": [
        {"step": 5, "name": "proactive-scan.py", "phase": "rot-detector"},
     ]},
    5: {"name": "审核不通过返工", "type": "agent",
     "agents": [
        {"step": 1, "name": "reviewer", "skill": "skills/09-review", "phase": "review"},
     ],
     "scripts": [
        {"step": 2, "name": "proactive-scan.py", "phase": "rot-detector"},
     ]},
    6: {"name": "Spec 回流重构", "type": "mixed",
     "agents": [
        {"step": 1, "name": "implementer", "skill": "skills/07-implement", "phase": "refactor"},
        {"step": 2, "name": "spec-enhancer", "skill": "skills/04-spec", "phase": "respec"},
        {"step": 3, "name": "contract-writer", "skill": "skills/06-contract", "phase": "recontract"},
        {"step": 4, "name": "implementer", "skill": "skills/07-implement", "phase": "reimplement"},
     ],
     "scripts": [
        {"step": 5, "name": "spec-purge.py", "cmd": "--change {change-id}"},
        {"step": 6, "name": "spec-knowledge-extract.py", "cmd": "--change {change-id}"},
     ]},
    7: {"name": "5 步精简 Bug 链（小 bug 流线化）", "type": "agent",
     "agents": [
        {"step": 1, "name": "debugger", "skill": "skills/12-bug-fix", "phase": "5-step-flow",
         "must_read": ["references/five-step-flow.md", "references/six-layer-diagnosis.md", "references/bug-state-machine.md"]},
        {"step": 2, "name": "reviewer", "skill": "skills/09-review", "phase": "review-light"},
     ]},
    8: {"name": "项目健康度自检（异步支线）", "type": "agent",
     "agents": [
        {"step": 1, "name": "project-health-auditor", "skill": "skills/13-project-health",
         "must_read": ["references/four-dimension-check.md", "references/anti-distortion.md", "references/gitnexus-impact-audit.md"]},
     ],
     "scripts": [
        {"step": 2, "name": "proactive-scan.py"},
     ]},
    9: {"name": "V10 → V11 升级", "type": "mixed",
     "scripts": [
        {"step": 1, "name": "upgrade-from-v10.py", "cmd": "--project-root . --dry-run"},
        {"step": 2, "name": "upgrade-from-v10.py", "cmd": "--project-root ."},
        {"step": 3, "name": "hooks-fidelity.py", "cmd": "--project-root ."},
        {"step": 4, "name": "proactive-scan.py"},
     ]},
    10: {"name": "gitnexus 索引初始化", "type": "script",
     "scripts": [
        {"step": 1, "name": "gitnexus-session-check.py", "cmd": "(由 SessionStart hook 自动跑)"},
        {"step": 2, "name": "gitnexus analyze", "cmd": "npx gitnexus analyze --deep"},
        {"step": 3, "name": "hooks-fidelity.py", "cmd": "--project-root ."},
     ]},
    11: {"name": "破坏性操作（含 secret 清理）", "type": "mixed",
     "agents": [
        {"step": 1, "name": "主上下文必走 4 步", "must_read": ["references/sub-agent-rules.md §12"]},
     ],
     "scripts": [
        {"step": 2, "name": "列清单", "cmd": "find/ls/Get-ChildItem | measure"},
        {"step": 3, "name": "用户确认", "cmd": "（强制等用户回复'确认'）"},
        {"step": 4, "name": "mv 到 _trash_<ts>/", "cmd": "（禁止直接 rmtree）"},
        {"step": 5, "name": "secret 扫描", "cmd": "grep -E 'password|token|api_key' src/（必查）"},
     ]},
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
                skill = it.get("skill", "")
                phase = it.get("phase", "")
                must = ", ".join(it.get("must_read", []))
                cmd = it.get("cmd", "")
                if cmd:
                    lines.append(f"- Step {it['step']}: `{tag[:-1]}.{it['name']} {cmd}` (skill={skill} phase={phase})")
                else:
                    lines.append(f"- Step {it['step']}: **{it['name']}** (skill={skill} phase={phase}) [{must}]")
    lines.append("")
    lines.append("## 产物 [OUTPUT]")
    lines.append("- artifacts: 见 scenarios.md")
    lines.append("- evidence: 5 维度 + rot-detector")
    lines.append("- status: ✓/⚠️/❌")
    return "\n".join(lines)


def render_json(scenario_id: int, cfg: Dict) -> str:
    return json.dumps({"scenario": scenario_id, "config": cfg}, ensure_ascii=False, indent=2)


def main() -> int:
    parser = argparse.ArgumentParser(description="V11.1 Agent 编排统一入口")
    parser.add_argument("--scenario", type=int, choices=range(1, 12))
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