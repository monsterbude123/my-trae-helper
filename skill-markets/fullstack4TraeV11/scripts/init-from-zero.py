#!/usr/bin/env python3
"""
V11 init-from-zero.py — 全新项目完整初始化（4 步全流程）

Usage:
    python init-from-zero.py --project-root <path> [--project-name <name>] [--project-type <type>]

4 步全流程:
  Step 1: config.yaml + hooks/        ← 脚本直接生成（基础设施）
  Step 2: .trae/rules/                ← 脚本复制 template + agent 按项目修改
  Step 3: AGENTS.md                   ← 脚本生成骨架 + agent 填充项目信息
  Step 4: 文档系统骨架                 ← 脚本生成 docs/ 目录结构

设计原则（无冗余）:
  - V11 skill 内部已含的内容（16 Articles / stage 流水线 / 4 维评分 / 反模式库）→ 不复制
  - AGENTS.md / rules 必含**项目独有**信息 → 脚本生成骨架,agent 填充
  - config.yaml / hooks / docs 骨架是 V11 强约束的基础设施 → 脚本生成保证一致性

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
STATE_CARD="${{STATE_CARD_PATH:-docs/specs/.state-card.md}}"
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


def create_rules(project_root: pathlib.Path, project_type: str, language: str) -> bool:
    """Step 2: 复制 rules 模板到 .trae/rules/(覆盖式)"""
    rules_dir = project_root / ".trae/rules"
    rules_dir.mkdir(parents=True, exist_ok=True)

    templates_dir = V11_TEMPLATES / "project-rules-example"
    if not templates_dir.exists():
        print(f"   ❌ rules 模板目录不存在: {templates_dir}")
        return False

    # 复制 4 个 rule 文件(stack/paths/git/coding-standards)
    rule_files = ["stack.md", "paths.md", "git.md", "coding-standards.md"]
    created, skipped = [], []
    for name in rule_files:
        src = templates_dir / name
        if not src.exists():
            continue
        dst = rules_dir / name
        if dst.exists():
            skipped.append(name)
            continue
        dst.write_text(src.read_text(encoding="utf-8"), encoding="utf-8")
        created.append(name)

    # 复制 README.md
    readme_src = templates_dir / "README.md"
    if readme_src.exists():
        readme_dst = rules_dir / "README.md"
        if not readme_dst.exists():
            readme_dst.write_text(readme_src.read_text(encoding="utf-8"), encoding="utf-8")

    if created:
        print(f"   ✅ .trae/rules/{', '.join(created)}")
    if skipped:
        print(f"   ⏭️  rules/{', '.join(skipped)} 已存在（跳过,如需更新用 sync-after-upgrade.py）")
    print(f"   📋 agent 需按项目实际修改 stack.md 命令 + paths.md 禁读路径")
    return True


def create_agents_md(project_root: pathlib.Path, project_name: str, project_type: str, language: str) -> bool:
    """Step 3: 生成 AGENTS.md 骨架(基于 template)"""
    agents_path = project_root / "AGENTS.md"
    if agents_path.exists():
        print(f"   ⏭️  AGENTS.md 已存在（跳过,如需更新用 sync-after-upgrade.py）")
        return True

    template_path = V11_TEMPLATES / "project-agents-example.md"
    if not template_path.exists():
        print(f"   ❌ AGENTS.md 模板不存在: {template_path}")
        return False

    content = template_path.read_text(encoding="utf-8")
    # 填充占位符
    content = content.replace("{项目名}", project_name)
    content = content.replace("{web / tauri / cli / library / backend}", project_type)
    content = content.replace("{语言 + 主版本}", language)

    agents_path.write_text(content, encoding="utf-8")
    print(f"   ✅ AGENTS.md ({len(content)} 字符)")
    print(f"   📋 agent 需填充框架/测试/包管理等占位符")
    return True


def create_docs_skeleton(project_root: pathlib.Path) -> bool:
    """Step 4: 生成 V11 文档系统骨架"""
    dirs = [
        "docs/specs/changes",       # change 级 spec
        "docs/specs/changes/archive",  # 归档
        "docs/bugs",                # bug 单
        "docs/verifications",       # 验证报告
        "docs/reports",             # 周期报告
        "docs/references",          # 项目参考文档
    ]
    created = []
    for d in dirs:
        full = project_root / d
        if not full.exists():
            full.mkdir(parents=True, exist_ok=True)
            created.append(d)

    # 生成 .gitkeep 让空目录可提交
    for d in dirs:
        keep = project_root / d / ".gitkeep"
        if not keep.exists():
            keep.write_text("", encoding="utf-8")

    if created:
        print(f"   ✅ docs/ 骨架: {len(created)} 个目录")
    else:
        print(f"   ⏭️  docs/ 骨架已存在")
    print(f"   📋 agent 需初始化 docs/specs/.state-card.md（项目级状态卡）")
    return True


def create_rules_skill(project_root: pathlib.Path, project_name: str) -> bool:
    """Step 5(可选):把 .trae/rules/ 收纳到 .trae/skills/project_rules_skills/

    适用场景:项目 rules 数量 ≥6 个,主上下文全量注入会撑爆 context。
    设计:把 rules 内容留在 .trae/rules/(single source of truth),在 .trae/skills/
    下创建 project_rules_skills/ 强制入口 skill,按需加载。

    动态适应:不写死规则列表,自动从项目现有 rules 检测 + 生成 references 软链接。
    """
    rules_dir = project_root / ".trae/rules"
    if not rules_dir.exists():
        print(f"   ⏭️  .trae/rules/ 不存在(无 rules 可收纳,跳过)")
        return True

    # 检测现有 rules 列表
    existing_rules = sorted([f.name for f in rules_dir.glob("*.md") if f.name != "README.md"])
    if len(existing_rules) < 3:
        print(f"   ⏭️  rules 数量 {len(existing_rules)} < 3,无需收纳(直接 Read 即可)")
        return True

    # 创建 project_rules_skills/ 目录
    skill_dir = project_root / ".trae/skills/project_rules_skills"
    skill_dir.mkdir(parents=True, exist_ok=True)
    refs_dir = skill_dir / "references"
    refs_dir.mkdir(parents=True, exist_ok=True)
    workflows_dir = skill_dir / "workflows"
    workflows_dir.mkdir(parents=True, exist_ok=True)

    template_dir = V11_TEMPLATES / "project-rules-skill-template"

    # 复制 SKILL.md / README.md / workflows/(从模板)
    for name in ["SKILL.md", "README.md"]:
        src = template_dir / name
        dst = skill_dir / name
        if dst.exists():
            continue
        if src.exists():
            dst.write_text(src.read_text(encoding="utf-8"), encoding="utf-8")

    src_wf = template_dir / "workflows/sub-agent-delegate-load.md"
    dst_wf = workflows_dir / "sub-agent-delegate-load.md"
    if not dst_wf.exists() and src_wf.exists():
        dst_wf.write_text(src_wf.read_text(encoding="utf-8"), encoding="utf-8")

    # 动态生成 references/ 软链接(Windows: 用文件复制替代符号链接,兼容性更好)
    # 注:跨平台最佳实践是软链接,但 Windows 需权限,这里用 .ref 文件 + 指向说明
    created_links = []
    for rule_name in existing_rules:
        rule_path = rules_dir / rule_name
        link_path = refs_dir / rule_name
        if link_path.exists():
            continue

        # 创建引用文件(内容:指向 .trae/rules/ 实际文件 + 提示"single source of truth")
        link_content = f"""<!-- 本文件由 init-from-zero.py --rules-as-skill 自动生成 -->
<!-- single source of truth: ../../../../.trae/rules/{rule_name} -->
<!-- 不修改本文件,直接修改 .trae/rules/{rule_name} -->

<!-- BEGIN SOURCE: .trae/rules/{rule_name} -->
"""
        link_content += rule_path.read_text(encoding="utf-8")
        link_content += "\n<!-- END SOURCE -->\n"
        link_path.write_text(link_content, encoding="utf-8")
        created_links.append(rule_name)

    # 改造 .trae/rules/README.md 为强制入口(只在该模式首次运行时)
    readme_path = rules_dir / "README.md"
    forced_entry = f"""# .trae/rules/ 强制入口

> **🔴 必读 · 本目录的唯一文件**(其他 rules 通过 .trae/skills/project_rules_skills/ 按需加载)
>
> 任何 agent(主 agent / sub-agent / 主上下文开启子 agent 时)进入本项目执行任务前,
> **必须先调用** `Skill(name="project-rules")` 获取本会话所需 rules。
>
> **禁止绕过本入口**直接 Read `.trae/rules/*.md` 中除本 README.md 外的其他文件。
>
> skill 入口:`.trae/skills/project_rules_skills/SKILL.md`
>
> ---
>
> ## 本项目 rules 列表(由 init-from-zero.py 检测)
>
> {chr(10).join(f"- `{r}`" for r in existing_rules)}
>
> ## 加载协议
>
> ```
> Step 1: 调用 Skill(name="project-rules")
> Step 2: 按路由表拿本会话所需 rules(SKILL.md §2)
> Step 3: 只 Read 选中的 rules(在 .trae/skills/project_rules_skills/references/)
> Step 4: sub-agent 必须在 Completion Report 声明 rules_loaded / rules_skipped
> ```
>
> ## 详细说明
>
> 详见 [.trae/skills/project_rules_skills/SKILL.md](../../skills/project_rules_skills/SKILL.md)
>
> 项目名: {project_name}
"""
    readme_path.write_text(forced_entry, encoding="utf-8")

    print(f"   ✅ .trae/skills/project_rules_skills/ 收纳 {len(existing_rules)} 个 rules")
    print(f"   ✅ .trae/rules/README.md 改为强制入口")
    print(f"   📋 agent 必走 Skill(name=project-rules)")
    return True


def print_agent_handoff(project_name: str, project_type: str, language: str) -> None:
    """引导 agent 读取 template 配置 AGENTS.md + rules"""
    print()
    print(f"{'='*70}")
    print(f"📋 下一步：agent 填充项目级信息（脚本已生成骨架）")
    print(f"{'='*70}")
    print()
    print(f"检测到的项目栈：")
    print(f"   类型: {project_type} | 项目名: {project_name} | 语言: {language}")
    print()
    print(f"4 步已生成骨架,agent 需填充以下占位符：")
    print()
    print(f"   Step 2 填充: .trae/rules/stack.md")
    print(f"     → 替换 {{{language}}} 为实际版本 + 框架 + 测试 + 包管理命令")
    print(f"     → 替换 .trae/rules/paths.md 禁读路径为项目实际路径")
    print(f"     → .trae/rules/git.md 按项目分支策略调整（5 类标签已合并）")
    print(f"     → .trae/rules/coding-standards.md 按项目编码规则填充（无则删除）")
    print()
    print(f"   Step 3 填充: AGENTS.md")
    print(f"     → 填充框架/测试/包管理占位符")
    print(f"     → 删除不适用章节（如 backend 无浏览器自动化 → 删 §5）")
    print(f"     → 模板参考: {AGENTS_TEMPLATE}")
    print()
    print(f"   Step 4 初始化: docs/specs/.state-card.md")
    print(f"     → 项目级状态卡（记录项目整体状态,非 change 级）")
    print(f"     → ⚠️ 绝不能用 .trae/state-card.md（V10 残留,V11 已迁移出 .trae/）")
    print(f"     → 格式参考: ~/.trae-cn/skills/fullstack4TraeV11/references/state-card-protocol.md")
    print()
    print(f"   🚨 V11 §0.5 加载协议（V11.2 NEW — 蒸馏自 canvas-asset-folders 实战）:")
    print(f"     → agent 首次进入项目必走 9 步加载")
    print(f"     → Step 3 强制调 Skill(name=project-rules)（如项目已有 .trae/skills/project_rules_skills/）")
    print(f"     → Step 5 核对状态卡路径 docs/specs/.state-card.md")
    print(f"     → 详见: ~/.trae-cn/skills/fullstack4TraeV11/SKILL.md §0.5")
    print()
    print(f"   验证（必跑）：")
    print(f"     python ~/.trae-cn/skills/fullstack4TraeV11/scripts/hooks-fidelity.py --project-root .")
    print()
    print(f"{'='*70}")


def main():
    parser = argparse.ArgumentParser(description="V11 全新项目基础设施初始化")
    parser.add_argument("--project-root", default=".", help="项目根路径")
    parser.add_argument("--project-name", help="项目名（默认：项目根目录名）")
    parser.add_argument("--project-type", choices=["web", "tauri", "cli", "library", "backend"], help="项目类型")
    parser.add_argument("--language", help="主语言")
    parser.add_argument("--rules-as-skill", action="store_true", help="Step 5 可选:把 .trae/rules/ 收纳到 .trae/skills/project_rules_skills/(适用 rules ≥3 个时)")
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

    step_count = 5 if args.rules_as_skill else 4
    print(f"🚀 V11 初始化（{step_count} 步全流程）— {project_root}")
    print(f"   项目名: {project_name} | 类型: {project_type} | 语言: {language}")
    if args.rules_as_skill:
        print(f"   模式: --rules-as-skill(Step 5 收纳 rules)")
    print()

    steps = [
        ("Step 1: config.yaml + hooks/", lambda: create_config(project_root, project_name, project_type, language) and create_hooks(project_root)),
        ("Step 2: .trae/rules/", lambda: create_rules(project_root, project_type, language)),
        ("Step 3: AGENTS.md", lambda: create_agents_md(project_root, project_name, project_type, language)),
        ("Step 4: docs/ 骨架", lambda: create_docs_skeleton(project_root)),
    ]

    if args.rules_as_skill:
        steps.append(("Step 5: 收纳 rules 到 skill", lambda: create_rules_skill(project_root, project_name)))

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