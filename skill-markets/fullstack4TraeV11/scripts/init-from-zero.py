#!/usr/bin/env python3
"""
V11 init-from-zero.py — 全新项目基础设施初始化（仅 config + hooks）

Usage:
    python init-from-zero.py --project-root <path> [--project-name <name>] [--project-type <type>]

生成（仅基础设施）:
  <project-root>/.trae/fullstack4traev11.config.yaml
  <project-root>/.trae/hooks/{pre-stage,post-stage,pre-accept}.sh

不生成（让 agent 按需配置）:
  AGENTS.md           ← 由 agent 读取 templates/project-agents-example.md 配置
  .trae/rules/         ← 由 agent 读取 templates/project-rules-example/ 按需配置

设计原则（无冗余）:
  - V11 skill 内部已含的内容（16 Articles / stage 流水线 / 4 维评分 / 反模式库）→ 不复制
  - AGENTS.md / rules 必含**项目独有**信息 → 由 agent 读 template 按项目实情配置
  - config.yaml / hooks 是 V11 强约束的基础设施 → 脚本生成保证一致性

Exit codes:
    0 = PASS
    1 = FAIL
"""
import sys
import argparse
import pathlib
import json
from datetime import datetime, timezone

V11_SKILL_ROOT = pathlib.Path("~/.trae-cn/skills/fullstack4TraeV11").expanduser()
V11_TEMPLATES = V11_SKILL_ROOT / "templates"
AGENTS_TEMPLATE = V11_TEMPLATES / "project-agents-example.md"
RULES_README = V11_TEMPLATES / "project-rules-example" / "README.md"


CONFIG_TEMPLATE = """project:
  name: "{project_name}"
  type: "{project_type}"
  language: ["{language}"]

stage_config:
  implement:
    skills: [ponytail4Trae]
  real-verify:
    skills: [visual-evidence-discipline, screenshot, playwright-best-practices]
  bug-fix:
    skills: [gitnexus4Trae, debugger4Trae]

# 必走 stage
required_stages:
  - -1/intake
  - 0/plan
  - 1/spec
  - 3.5/real-verify
  - 4.5/rot-scan

# 上下文保护（项目级 + V11 默认合并）
forbidden_paths:
  - docs/archive/**
  - .trae/tmp/**
  - secrets/**
  - deploy/prod/**
"""


HOOK_PRE_STAGE = """#!/bin/bash
# V11 pre-stage hook: stage 切换前必走
set -e
STATE_CARD="${{STATE_CARD_PATH:-.trae/state-card.md}}"
EXPECTED_STAGE="${{EXPECTED_STAGE:-}}"
python "${{V11_SCRIPTS:-~/.trae-cn/skills/fullstack4TraeV11/scripts}}/stage-gate.py" \\
    --state-card "$STATE_CARD" \\
    ${{EXPECTED_STAGE:+--stage "$EXPECTED_STAGE"}}
echo "✅ pre-stage PASS"
"""


HOOK_POST_STAGE = """#!/bin/bash
# V11 post-stage hook: stage 结束后必走
set -e
CHANGE_ID="${{CHANGE_ID:-}}"
if [ -z "$CHANGE_ID" ]; then
    echo "❌ 缺 CHANGE_ID env"
    exit 1
fi
STATE_CARD="docs/specs/changes/${{CHANGE_ID}}/.state-card.md"
python "${{V11_SCRIPTS:-~/.trae-cn/skills/fullstack4TraeV11/scripts}}/state-card-validator.py" "$STATE_CARD"
echo "✅ post-stage PASS"
"""


HOOK_PRE_ACCEPT = """#!/bin/bash
# V11 pre-accept hook: Stage 5 Accept 前必跑 rot-scan
set -e
CHANGE_ID="${{CHANGE_ID:-}}"
if [ -z "$CHANGE_ID" ]; then
    echo "❌ 缺 CHANGE_ID env"
    exit 1
fi
python "${{V11_SCRIPTS:-~/.trae-cn/skills/fullstack4TraeV11/scripts}}/phase-gate.py" \\
    --state-card "docs/specs/changes/${{CHANGE_ID}}/.state-card.md" \\
    --verify-rot-scan \\
    --change-id "$CHANGE_ID"
echo "✅ pre-accept PASS"
"""


def detect_project_type(project_root: pathlib.Path) -> str:
    """自动检测项目类型"""
    if (project_root / "src-tauri").exists():
        return "tauri"
    if (project_root / "package.json").exists():
        return "web"
    if (project_root / "pyproject.toml").exists():
        return "cli" if (project_root / "bin").exists() else "library"
    if (project_root / "Cargo.toml").exists():
        return "cli"
    return "library"


def detect_language(project_root: pathlib.Path) -> str:
    """自动检测主语言"""
    if (project_root / "package.json").exists():
        return "typescript"
    if (project_root / "pyproject.toml").exists():
        return "python"
    if (project_root / "Cargo.toml").exists():
        return "rust"
    if (project_root / "go.mod").exists():
        return "go"
    return "typescript"


def create_config(project_root: pathlib.Path, project_name: str, project_type: str, language: str) -> bool:
    """创建项目级 .trae/fullstack4traev11.config.yaml"""
    config_path = project_root / ".trae/fullstack4traev11.config.yaml"
    if config_path.exists():
        print(f"   ⏭️  config 已存在（跳过）")
        return True

    config_path.parent.mkdir(parents=True, exist_ok=True)
    content = CONFIG_TEMPLATE.format(
        project_name=project_name,
        project_type=project_type,
        language=language,
    )
    config_path.write_text(content, encoding="utf-8")
    print(f"   ✅ .trae/fullstack4traev11.config.yaml ({len(content)} 字符)")
    return True


def create_hooks(project_root: pathlib.Path) -> bool:
    """创建 V11 默认 3 个 hook"""
    hooks_dir = project_root / ".trae/hooks"
    hooks_dir.mkdir(parents=True, exist_ok=True)

    hooks = {
        "pre-stage.sh": HOOK_PRE_STAGE,
        "post-stage.sh": HOOK_POST_STAGE,
        "pre-accept.sh": HOOK_PRE_ACCEPT,
    }

    created = []
    skipped = []
    for name, content in hooks.items():
        path = hooks_dir / name
        if path.exists():
            skipped.append(name)
            continue
        path.write_text(content, encoding="utf-8")
        path.chmod(0o755)
        created.append(name)

    if created:
        print(f"   ✅ .trae/hooks/{', '.join(created)}")
    if skipped:
        print(f"   ⏭️  hooks/{', '.join(skipped)} 已存在（跳过）")
    return True


def print_agent_handoff(project_name: str, project_type: str, language: str) -> None:
    """引导 agent 读取 template 配置 AGENTS.md + rules"""
    print()
    print(f"{'='*70}")
    print(f"📋 下一步：让 agent 读取 V11 template 配置项目级文件")
    print(f"{'='*70}")
    print()
    print(f"检测到的项目栈：")
    print(f"   类型: {project_type} | 项目名: {project_name} | 语言: {language}")
    print()
    print(f"agent 必走的 3 步：")
    print(f"   Step 1: 读取 AGENTS.md 模板")
    print(f"           {AGENTS_TEMPLATE}")
    print(f"           按项目实际情况填充占位符 → 输出到项目根 AGENTS.md")
    print()
    print(f"   Step 2: 读取 rules README（4 步流程）")
    print(f"           {RULES_README}")
    print(f"           按项目场景选择：纯净 web / CLI / Library / 单文件")
    print(f"           复制 templates/project-rules-example/{{stack,paths,git}}.md 到 .trae/rules/")
    print(f"           按项目实际情况修改")
    print()
    print(f"   Step 3: 验证（hooks-fidelity.py PASS）")
    print(f"           python ~/.trae-cn/skills/fullstack4TraeV11/scripts/hooks-fidelity.py --project-root .")
    print()
    print(f"{'='*70}")


def main():
    parser = argparse.ArgumentParser(description="V11 全新项目基础设施初始化")
    parser.add_argument("--project-root", default=".", help="项目根路径")
    parser.add_argument("--project-name", help="项目名（默认：项目根目录名）")
    parser.add_argument("--project-type", choices=["web", "tauri", "cli", "library", "backend"], help="项目类型")
    parser.add_argument("--language", help="主语言")
    parser.add_argument("--quiet", action="store_true", help="不打印 agent handoff")
    parser.add_argument("--json", action="store_true", help="JSON 输出")
    args = parser.parse_args()

    project_root = pathlib.Path(args.project_root).resolve()

    if not project_root.exists():
        print(f"❌ 项目目录不存在: {project_root}")
        return 1

    # 自动检测或使用参数
    project_name = args.project_name or project_root.name
    project_type = args.project_type or detect_project_type(project_root)
    language = args.language or detect_language(project_root)

    print(f"🚀 V11 初始化（仅基础设施）— {project_root}")
    print(f"   项目名: {project_name} | 类型: {project_type} | 语言: {language}")
    print()

    steps = [
        ("config.yaml", lambda: create_config(project_root, project_name, project_type, language)),
        ("hooks/", lambda: create_hooks(project_root)),
    ]

    results = []
    for name, func in steps:
        is_pass = func()
        results.append({"step": name, "status": "PASS" if is_pass else "FAIL"})

    all_pass = all(r["status"] == "PASS" for r in results)

    output = {
        "project_root": str(project_root),
        "project_meta": {
            "name": project_name,
            "type": project_type,
            "language": language,
        },
        "infra_steps": results,
        "agent_next_steps": {
            "AGENTS_template": str(AGENTS_TEMPLATE),
            "rules_README": str(RULES_README),
            "rules_dir": "templates/project-rules-example/",
        },
        "status": "PASS" if all_pass else "FAIL",
    }

    if args.json:
        print(json.dumps(output, indent=2, ensure_ascii=False))
    else:
        print(f"\n{'✅' if all_pass else '❌'} 基础设施初始化 {'PASS' if all_pass else 'FAIL'}")
        if not args.quiet:
            print_agent_handoff(project_name, project_type, language)

    return 0 if all_pass else 1


if __name__ == "__main__":
    sys.exit(main())