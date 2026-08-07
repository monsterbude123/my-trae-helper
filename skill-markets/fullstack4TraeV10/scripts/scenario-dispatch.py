#!/usr/bin/env python3
"""scenario-dispatch.py — V10.9 场景编排器（10 场景 step-by-step）

基于 [scenarios.md](../scenarios.md) 10 场景，输出执行清单。
混合调度 agent + 脚本 + 协议 + skill。

用法:
  python scripts/scenario-dispatch.py --scenario 1
  python scripts/scenario-dispatch.py --scenario 3 --json
  python scripts/scenario-dispatch.py --all
  python scripts/scenario-dispatch.py --list
"""
import argparse
import json
import sys
from typing import Dict

# 10 场景 step-by-step（精简版）
SCENARIOS: Dict[int, Dict] = {
    1: {"name": "项目 0→1 初始化", "type": "mixed",
     "steps": [
        {"id": 1, "type": "context", "action": "主上下文必走 §0.5 协议"},
        {"id": 2, "type": "context", "action": "检测项目类型 (CLI/全栈/后端/纯前端)"},
        {"id": 3, "type": "script", "action": "setup-feature.py 调用模板覆盖机制", "cmd": "--print-template-path"},
        {"id": 4, "type": "script", "action": "执行 setup-feature.py", "cmd": "--name 00-01-init-scaffold"},
        {"id": 5, "type": "script", "action": "验证 Article XIV 注入", "cmd": "--check-article-xiv"},
        {"id": 6, "type": "context", "action": "主上下文验证", "cmd": "ls docs/specs/00-01-init-scaffold/"},
     ]},
    2: {"name": "已有代码迷雾消除", "type": "agent",
     "steps": [
        {"id": 1, "type": "context", "action": "主上下文必走 §0.5 协议"},
        {"id": 2, "type": "agent", "name": "project-health-auditor", "action": "4 维度诊断"},
        {"id": 3, "type": "agent", "name": "project-health-auditor", "action": "输出 doc/reports/project-health-{date}.md+json"},
        {"id": 4, "type": "context", "action": "主上下文阅读报告 → 决策"},
     ]},
    3: {"name": "新增功能完整链（核心）", "type": "agent",
     "steps": [
        {"id": 1, "type": "context", "action": "主上下文必走 §0.5 协议"},
        {"id": 2, "type": "agent", "name": "planner", "phase": "plan", "action": "3 子代理并行探索"},
        {"id": 3, "type": "agent", "name": "spec-enhancer", "phase": "spec", "action": "Enhanced Acceptance"},
        {"id": 4, "type": "agent", "name": "contract-writer", "phase": "contract", "action": "contracts/ 四件套"},
        {"id": 5, "type": "agent", "name": "implementer", "phase": "implement", "action": "TDD 三步循环"},
        {"id": 6, "type": "agent", "name": "reviewer", "phase": "review", "action": "质疑式验收"},
        {"id": 7, "type": "script", "phase": "rot-detector", "action": "★ Phase 4.5 必跑", "cmd": "proactive-scan.py"},
        {"id": 8, "type": "context", "action": "Accept: 归档"},
     ]},
    4: {"name": "Spec 累积生长", "type": "mixed",
     "steps": [
        {"id": 1, "type": "context", "action": "主上下文必走 §0.5 协议"},
        {"id": 2, "type": "agent", "name": "implementer", "phase": "merge", "action": "读 Delta spec → 判定 ADDED/MODIFIED/REMOVED"},
        {"id": 3, "type": "script", "action": "spec-merge.py", "cmd": "docs/specs/{feature}/spec.md docs/specs/{feature}/spec.md"},
        {"id": 4, "type": "agent", "name": "implementer", "action": "合并后: 检查 [ ] / 触发 reviewer / 委派 spec-purge"},
        {"id": 5, "type": "script", "action": "spec-purge.py 路径检查", "cmd": "--feature {feature} --check-path"},
        {"id": 6, "type": "context", "action": "主上下文 Completion Report"},
     ]},
    5: {"name": "Bug 修复快捷链", "type": "agent",
     "steps": [
        {"id": 1, "type": "context", "action": "主上下文必走 §0.5 协议"},
        {"id": 2, "type": "agent", "name": "debugger", "phase": "debug", "action": "5 步流水 + 6 层排查"},
        {"id": 3, "type": "agent", "name": "implementer", "phase": "fix", "action": "轻量 TDD RED→GREEN"},
        {"id": 4, "type": "agent", "name": "reviewer", "phase": "review-light", "action": "验证回归"},
        {"id": 5, "type": "script", "phase": "rot-detector", "action": "★ Phase 4.5 必跑", "cmd": "proactive-scan.py"},
     ]},
    6: {"name": "审核不通过返工", "type": "agent",
     "steps": [
        {"id": 1, "type": "agent", "name": "reviewer", "phase": "review", "action": "5 维度 + 回流"},
        {"id": 2, "type": "script", "phase": "rot-detector", "action": "联动腐化扫描", "cmd": "proactive-scan.py"},
        {"id": 3, "type": "context", "action": "主上下文审核腐化报告"},
     ]},
    7: {"name": "Spec 回流重构", "type": "mixed",
     "steps": [
        {"id": 1, "type": "context", "action": "主上下文必走 §0.5 协议"},
        {"id": 2, "type": "agent", "name": "implementer", "phase": "refactor", "action": "委派 spec-purge", "cmd": "spec-purge.py --feature {feature}"},
        {"id": 3, "type": "agent", "name": "implementer", "action": "写 REFACTOR_MODE.md"},
        {"id": 4, "type": "agent", "name": "spec-writer", "phase": "respec", "action": "spec-validate", "cmd": "--mode full"},
        {"id": 5, "type": "agent", "name": "contract-writer", "phase": "recontract"},
        {"id": 6, "type": "agent", "name": "implementer", "phase": "reimplement", "action": "TDD 重头"},
        {"id": 7, "type": "script", "action": "spec-knowledge-extract.py", "cmd": "--feature {feature}"},
        {"id": 8, "type": "context", "action": "主上下文验收"},
     ]},
    8: {"name": "反复反馈升级", "type": "protocol",
     "steps": [
        {"id": 1, "type": "trigger", "action": "用户对同一类问题反馈 ≥ 2 轮"},
        {"id": 2, "type": "protocol", "action": "clarify-checklist.md §7 (6 步根因诊断)"},
        {"id": 3, "type": "protocol", "action": "SKILL.md §7.5 AskUserQuestion 反模式"},
        {"id": 4, "type": "protocol", "action": "process-rot-analysis.md §5.5 rot #21/22/23"},
        {"id": 5, "type": "skill", "name": "session-distiller", "action": "集中反馈机制"},
        {"id": 6, "type": "loop", "action": "3 层循环 (PFC/Skill/项目)"},
        {"id": 7, "type": "verify", "action": "闭环验证 (4 维度 + scenarios + rot)"},
     ]},
    9: {"name": "V9.2 项目迁移", "type": "script",
     "steps": [
        {"id": 1, "type": "context", "action": "主上下文必走 §0.5 协议"},
        {"id": 2, "type": "context", "action": "Step 0: 项目类型判定"},
        {"id": 3, "type": "script", "action": "DRY-RUN", "cmd": "migrate-v9-to-v10.py --project-type {type} --dry-run"},
        {"id": 4, "type": "script", "action": "正式迁移", "cmd": "migrate-v9-to-v10.py --project-type {type}"},
        {"id": 5, "type": "agent", "name": "project-health-auditor", "action": "4 维度自检"},
        {"id": 6, "type": "script", "action": "rot-detector", "cmd": "proactive-scan.py"},
     ]},
    10: {"name": "项目健康度自检", "type": "agent",
     "steps": [
        {"id": 1, "type": "context", "action": "主上下文必走 §0.5 协议"},
        {"id": 2, "type": "agent", "name": "project-health-auditor", "phase": "diagnose", "action": "项目类型判定"},
        {"id": 3, "type": "agent", "name": "project-health-auditor", "action": "4 维度检查"},
        {"id": 4, "type": "agent", "name": "project-health-auditor", "action": "输出诊断报告"},
        {"id": 5, "type": "context", "action": "主上下文审计 → P0/P1/P2"},
        {"id": 6, "type": "context", "action": "手动修正（不自动）"},
     ]},
}

ICON = {"context": "��", "agent": "��", "script": "��", "protocol": "��",
        "trigger": "⚡", "skill": "��", "loop": "��", "verify": "✅"}


def render_markdown(scenario_id: int, cfg: Dict) -> str:
    lines = [f"# 场景 {scenario_id}: {cfg['name']}", "",
             f"**类型**: {cfg['type']} | **步骤**: {len(cfg['steps'])}", "",
             "## Step-by-Step 执行清单"]
    for s in cfg["steps"]:
        icon = ICON.get(s["type"], "•")
        name = s.get("name", "")
        phase = s.get("phase", "")
        cmd = s.get("cmd", "")
        lines.append(f"{icon} Step {s['id']}: **{s['action']}**")
        if name:
            lines.append(f"   - 执行方: `{name}` (phase={phase})")
        if cmd:
            lines.append(f"   - cmd: `{cmd}`")
        lines.append("")
    return "\n".join(lines)


def render_json(scenario_id: int, cfg: Dict) -> str:
    return json.dumps({"scenario": scenario_id, "config": cfg}, ensure_ascii=False, indent=2)


def main() -> int:
    parser = argparse.ArgumentParser(description="V10.9 场景编排器")
    parser.add_argument("--scenario", type=int, choices=range(1, 11))
    parser.add_argument("--all", action="store_true")
    parser.add_argument("--list", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    if args.list:
        for sid, cfg in SCENARIOS.items():
            print(f"  {sid}: {cfg['name']} ({cfg['type']}) - {len(cfg['steps'])} 步")
        return 0
    if args.all:
        for sid, cfg in SCENARIOS.items():
            print(render_markdown(sid, cfg))
            print("\n" + "=" * 60 + "\n")
        return 0
    if args.scenario is None:
        parser.error("必须指定 --scenario N / --all / --list")
    cfg = SCENARIOS[args.scenario]
    print(render_json(args.scenario, cfg) if args.json else render_markdown(args.scenario, cfg))
    return 0


if __name__ == "__main__":
    sys.exit(main())
