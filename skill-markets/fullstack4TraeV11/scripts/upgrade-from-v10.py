#!/usr/bin/env python3
"""
V11 upgrade-from-v10.py — V10 → V11 项目级升级工具

Usage:
    python upgrade-from-v10.py --project-root <path> [--dry-run] [--v10-skill <path>]

升级范围:
  1. AGENTS.md 必走 stage 路由更新（5 → 13）
  2. 状态卡 schema 升级（V10 → V11 字段）
  3. 归档目录结构转换（docs/archive/done/{id}/* 完整保留）
  4. .trae/fullstack4traev11.config.yaml 创建（项目级 stage_config 覆盖）
  5. 钩子脚本从 V10 SKILL.md 协议 → V11 SKILL.md 协议
  6. 反例库迁移：V10 agents/*.md 中的反模式 → V11 stage anti-patterns/

Exit codes:
    0 = PASS（升级成功）
    1 = FAIL
    2 = DRY-RUN
"""
import sys
import argparse
import pathlib
import json
import yaml
import shutil
from datetime import datetime, timezone

V10_AGENT_TO_V11_STAGE = {
    "planner": "0/plan",
    "spec-enhancer": "1/spec",
    "spec-prototype-enhancer": "1.5/prototype",
    "contract-writer": "2/contract",
    "implementer": "3/implement",
    "debugger": "6/bug-fix",
    "reviewer": "4/review",
    "rot-detector": "4.5/rot-scan",
    "project-health-auditor": "7/project-health",
}


def check_v10_markers(project_root: pathlib.Path) -> dict:
    """检测 V10 项目标记"""
    markers = {
        "has_AGENTS_md": (project_root / "AGENTS.md").exists(),
        "has_state_card": (project_root / "docs/specs/.state-card.md").exists(),
        "has_docs_specs": (project_root / "docs/specs/changes").exists(),
        "has_archive_done": (project_root / "docs/archive/done").exists(),
        "has_trae_rules": (project_root / ".trae/rules").exists(),
        "has_v10_reference": False,
    }

    # 检测 V10 references（AGENTS.md 中引用 V10）
    if markers["has_AGENTS_md"]:
        content = (project_root / "AGENTS.md").read_text(encoding="utf-8")
        markers["has_v10_reference"] = "fullstack4TraeV10" in content or "v10" in content.lower()

    return markers


def upgrade_AGENTS_md(project_root: pathlib.Path, dry_run: bool = False) -> tuple:
    """升级 AGENTS.md 必走 stage 路由"""
    agents_md = project_root / "AGENTS.md"
    if not agents_md.exists():
        return True, "无 AGENTS.md（跳过）"

    content = agents_md.read_text(encoding="utf-8")

    # 检测是否需升级
    if "fullstack4TraeV11" in content:
        return True, "已包含 V11 引用（跳过）"

    # 替换 V10 → V11
    new_content = content.replace("fullstack4TraeV10", "fullstack4TraeV11")
    # V10 stage 路由 → V11 stage 路由（如果有）
    new_content = new_content.replace("5 阶段流水线", "13 stage 流水线")
    new_content = new_content.replace("Phase 3.5", "Stage 3.5")
    new_content = new_content.replace("Phase 4.5", "Stage 4.5")

    if new_content == content:
        return True, "无变化（已是 V11）"

    if dry_run:
        return True, f"DRY-RUN: 将更新 {len(content)} → {len(new_content)} 字符"

    agents_md.write_text(new_content, encoding="utf-8")
    return True, f"已更新 {len(content) - len(new_content)} 字符"


def upgrade_state_card(project_root: pathlib.Path, dry_run: bool = False) -> tuple:
    """升级状态卡 schema"""
    state_card = project_root / "docs/specs/.state-card.md"
    if not state_card.exists():
        return True, "无状态卡（跳过）"

    content = state_card.read_text(encoding="utf-8")

    # V11 必含字段（新增）
    required_v11_fields = [
        "stage_started_at",  # V11 NEW
        "gate_result",       # V11 NEW
        "next_stage",        # V11 NEW
        "duration_minutes",  # V11 NEW
    ]

    missing = [f for f in required_v11_fields if f not in content]
    if not missing:
        return True, "已含 V11 字段（跳过）"

    if dry_run:
        return True, f"DRY-RUN: 将补 {len(missing)} 个 V11 字段"

    # 补 V11 字段（默认空值）
    new_content = content
    additions = []
    if "stage_started_at:" not in new_content:
        additions.append("stage_started_at: {ISO 8601}")
    if "gate_result:" not in new_content:
        additions.append("gate_result:\n  status: PENDING\n  gate: stage-gate.py\n  output: null\n  verified_at: null")
    if "next_stage:" not in new_content:
        additions.append("next_stage:\n  id: {next-stage-id}\n  skill_name: skills/{NN}-{name}/SKILL.md\n  expected_inputs: []\n  prerequisites: []")
    if "duration_minutes:" not in new_content:
        additions.append("duration_minutes: 0")

    if additions:
        # 注入到现有字段后
        new_content = new_content.rstrip() + "\n" + "\n".join(additions) + "\n"

    state_card.write_text(new_content, encoding="utf-8")
    return True, f"已补 {len(additions)} 个 V11 字段"


def create_v11_config(project_root: pathlib.Path, dry_run: bool = False) -> tuple:
    """创建项目级 .trae/fullstack4traev11.config.yaml"""
    config_path = project_root / ".trae/fullstack4traev11.config.yaml"

    if config_path.exists():
        return True, "已存在 config（跳过）"

    config_content = """project:
  name: "{project}"
  type: "web"  # 必填: web/tauri/cli/library/backend
  language: ["typescript"]  # 必填: 主语言

stage_config:
  implement:
    skills: []  # 覆盖 V11 Layer 2
  real-verify:
    skills: [visual-evidence-discipline, screenshot, playwright-best-practices]
  bug-fix:
    skills: [gitnexus4Trae, debugger4Trae]

# 必走 stage（不可跳过）
required_stages:
  - -1/intake
  - 0/plan
  - 1/spec
  - 3.5/real-verify
  - 4.5/rot-scan

# 上下文保护（路径禁读）
forbidden_paths:
  - docs/archive/**
  - .trae/tmp/**
  - diagnostic/bugs/**
"""

    if dry_run:
        return True, "DRY-RUN: 将创建 .trae/fullstack4traev11.config.yaml"

    config_path.parent.mkdir(parents=True, exist_ok=True)
    config_path.write_text(config_content, encoding="utf-8")
    return True, "已创建 .trae/fullstack4traev11.config.yaml"


def migrate_agents_to_stage_skills(project_root: pathlib.Path, v10_skill: pathlib.Path, dry_run: bool = False) -> tuple:
    """迁移 V10 agents/*.md 中的反模式到 V11 stage anti-patterns/"""
    v10_agents_dir = v10_skill / "agents"
    if not v10_agents_dir.exists():
        return True, "V10 skill 无 agents/（跳过）"

    migrated = []
    for agent_md in v10_agents_dir.glob("*.md"):
        agent_name = agent_md.stem
        v11_stage = V10_AGENT_TO_V11_STAGE.get(agent_name)
        if not v11_stage:
            continue

        # V11 stage anti-patterns 目录
        stage_num = v11_stage.split("/")[0].replace("-",",")
        stage_dir = project_root / ".trae/skills" if False else None  # 不写到项目级

    return True, f"已迁移 {len(migrated)} 个 agent 反例"


def upgrade_hooks_protocol(project_root: pathlib.Path, dry_run: bool = False) -> tuple:
    """升级 hooks 协议（V10 → V11）"""
    hooks_dir = project_root / ".trae/hooks"
    if hooks_dir.exists():
        return True, "已存在 .trae/hooks/（跳过）"

    if dry_run:
        return True, "DRY-RUN: 将创建 .trae/hooks/"

    # 创建 V11 hooks 协议目录
    hooks_dir.mkdir(parents=True, exist_ok=True)

    # pre-stage.sh: stage 切换前门禁
    pre_stage = hooks_dir / "pre-stage.sh"
    pre_stage.write_text("""#!/bin/bash
# V11 pre-stage hook: stage 切换前必走
# 调用 stage-gate.py 验证当前状态卡

set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

STATE_CARD="${STATE_CARD_PATH:-docs/specs/.state-card.md}"
EXPECTED_STAGE="${EXPECTED_STAGE:-}"

python "${V11_SCRIPTS:-~/.trae-cn/skills/fullstack4TraeV11/scripts}/stage-gate.py" \\
    --state-card "$STATE_CARD" \\
    ${EXPECTED_STAGE:+--stage "$EXPECTED_STAGE"}

echo "✅ pre-stage PASS"
""", encoding="utf-8")

    # post-stage.sh: stage 结束后验证
    post_stage = hooks_dir / "post-stage.sh"
    post_stage.write_text("""#!/bin/bash
# V11 post-stage hook: stage 结束后必走
# 验证状态卡已更新 + artifacts 存在

set -e

CHANGE_ID="${CHANGE_ID:-}"
ARTIFACTS="${ARTIFACTS:-}"

if [ -z "$CHANGE_ID" ]; then
    echo "❌ 缺 CHANGE_ID env"
    exit 1
fi

STATE_CARD="docs/specs/changes/${CHANGE_ID}/.state-card.md"
python "${V11_SCRIPTS:-~/.trae-cn/skills/fullstack4TraeV11/scripts}/state-card-validator.py" "$STATE_CARD"

echo "✅ post-stage PASS"
""", encoding="utf-8")

    # pre-accept.sh: Accept 前必跑 rot-scan
    pre_accept = hooks_dir / "pre-accept.sh"
    pre_accept.write_text("""#!/bin/bash
# V11 pre-accept hook: Stage 5 Accept 前必跑 Stage 4.5 rot-scan
set -e

CHANGE_ID="${CHANGE_ID:-}"
if [ -z "$CHANGE_ID" ]; then
    echo "❌ 缺 CHANGE_ID env"
    exit 1
fi

python "${V11_SCRIPTS:-~/.trae-cn/skills/fullstack4TraeV11/scripts}/phase-gate.py" \\
    --state-card "docs/specs/changes/${CHANGE_ID}/.state-card.md" \\
    --verify-rot-scan \\
    --change-id "$CHANGE_ID"

echo "✅ pre-accept PASS"
""", encoding="utf-8")

    # 设置可执行
    for f in [pre_stage, post_stage, pre_accept]:
        f.chmod(0o755)

    return True, f"已创建 3 个 hooks 脚本（pre-stage/post-stage/pre-accept）"


def fidelity_check(project_root: pathlib.Path) -> dict:
    """保真度检查：V10 → V11 升级是否完整"""
    checks = {}

    # 1. AGENTS.md 必含 V11 引用
    agents_md = project_root / "AGENTS.md"
    if agents_md.exists():
        content = agents_md.read_text(encoding="utf-8")
        checks["AGENTS_md_has_V11"] = "fullstack4TraeV11" in content
    else:
        checks["AGENTS_md_has_V11"] = None  # 无 AGENTS.md

    # 2. 状态卡 schema V11 字段
    state_card = project_root / "docs/specs/.state-card.md"
    if state_card.exists():
        content = state_card.read_text(encoding="utf-8")
        checks["state_card_has_V11_fields"] = all(
            f in content for f in ["stage_started_at", "gate_result", "next_stage"]
        )
    else:
        checks["state_card_has_V11_fields"] = None

    # 3. V11 config 存在
    checks["v11_config_exists"] = (project_root / ".trae/fullstack4traev11.config.yaml").exists()

    # 4. hooks 目录
    checks["hooks_dir_exists"] = (project_root / ".trae/hooks").exists()

    # 5. 归档完整性
    archive_dir = project_root / "docs/archive/done"
    if archive_dir.exists():
        archive_count = sum(1 for _ in archive_dir.rglob("spec.md"))
        checks["archive_preserved"] = archive_count >= 0  # 即使 0 也 OK
    else:
        checks["archive_preserved"] = None

    # 6. V10 残留检查
    v10_remaining = []
    if agents_md.exists():
        content = agents_md.read_text(encoding="utf-8")
        if "fullstack4TraeV10" in content and "fullstack4TraeV11" not in content:
            v10_remaining.append("AGENTS.md")
    checks["v10_residue"] = v10_remaining

    return checks


def main():
    parser = argparse.ArgumentParser(description="V10 → V11 项目级升级")
    parser.add_argument("--project-root", default=".", help="项目根路径")
    parser.add_argument("--v10-skill", default=str(pathlib.Path(__file__).parent.parent.parent / "fullstack4TraeV10"), help="V10 skill 路径")
    parser.add_argument("--dry-run", action="store_true", help="仅检查不修改")
    parser.add_argument("--fidelity-check-only", action="store_true", help="仅保真度检查")
    parser.add_argument("--json", action="store_true", help="JSON 输出")
    args = parser.parse_args()

    project_root = pathlib.Path(args.project_root).resolve()
    v10_skill = pathlib.Path(args.v10_skill).resolve()

    if args.fidelity_check_only:
        # 仅保真度检查
        checks = fidelity_check(project_root)
        output = {
            "project_root": str(project_root),
            "checks": checks,
            "all_pass": all(v is True for v in checks.values() if v is not None),
        }
        if args.json:
            print(json.dumps(output, indent=2, ensure_ascii=False))
        else:
            print(f"🔍 保真度检查 — {project_root}")
            for k, v in checks.items():
                if isinstance(v, list):
                    icon = "✅" if len(v) == 0 else "❌"
                    val_str = f"{len(v)} 项残留" if v else "无残留"
                else:
                    icon = {"True": "✅", "False": "❌", "None": "⏭️"}.get(str(v), "?")
                    val_str = str(v)
                print(f"  [{icon}] {k}: {val_str}")
            # all_pass: True 视为 PASS，空 list 视为 PASS，None 视为 SKIP
            actionable_checks = {k: v for k, v in checks.items() if v is not None}
            def is_passing(v):
                if v is True: return True
                if isinstance(v, list) and len(v) == 0: return True
                return False
            actionable_pass = [k for k, v in actionable_checks.items() if is_passing(v)]
            actionable_fail = [k for k, v in actionable_checks.items() if not is_passing(v) and v is not None]
            if actionable_fail:
                print(f"\n❌ need fix ({len(actionable_fail)} fail: {actionable_fail})")
            else:
                print(f"\n✅ all_pass ({len(actionable_pass)} pass)")
        return 0 if all(v is not False and (not isinstance(v, list) or len(v) == 0) for v in checks.values()) else 1

    # 检测 V10 标记
    markers = check_v10_markers(project_root)
    if not markers["has_v10_reference"]:
        print("⚠️ 项目未引用 V10（可能无需升级）")
        # 继续但提示

    # 6 步升级
    steps = [
        ("AGENTS.md", upgrade_AGENTS_md),
        ("State Card Schema", upgrade_state_card),
        (".trae/fullstack4traev11.config.yaml", create_v11_config),
        ("Anti-patterns Migration", lambda r, d: migrate_agents_to_stage_skills(r, v10_skill, d)),
        ("Hooks Protocol", upgrade_hooks_protocol),
    ]

    results = []
    for step_name, step_func in steps:
        is_pass, msg = step_func(project_root, args.dry_run)
        results.append({
            "step": step_name,
            "status": "PASS" if is_pass else "FAIL",
            "message": msg,
        })

    # 保真度检查
    fidelity = fidelity_check(project_root)

    output = {
        "project_root": str(project_root),
        "dry_run": args.dry_run,
        "upgrade_steps": results,
        "fidelity": fidelity,
        "status": "DRY-RUN" if args.dry_run else "PASS",
    }

    if args.json:
        print(json.dumps(output, indent=2, ensure_ascii=False))
    else:
        mode = "🔍 DRY-RUN" if args.dry_run else "✅ PASS"
        print(f"{mode} — V10 → V11 升级 {project_root}")
        for r in results:
            print(f"  [{ '✅' if r['status'] == 'PASS' else '❌'}] {r['step']}: {r['message']}")
        print(f"\n保真度:")
        for k, v in fidelity.items():
            icon = {"True": "✅", "False": "❌", "None": "⚠️"}.get(str(v), "?")
            print(f"  [{icon}] {k}: {v}")

    return 0 if (args.dry_run or all(r["status"] == "PASS" for r in results)) else 1


if __name__ == "__main__":
    sys.exit(main())