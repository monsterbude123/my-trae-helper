#!/usr/bin/env python3
"""
forge_project_rules_skill.py — 锻造器

把项目 .trae/rules/*.md 收纳为 .trae/skills/project_rules_skills/ 入口 skill。

用法:
    python forge_project_rules_skill.py --project-root .
    python forge_project_rules_skill.py --project-root . --dry-run
    python forge_project_rules_skill.py --project-root . --force
    python forge_project_rules_skill.py --project-root . --move   # 物理移走源 rules

默认行为:
    1. 检测每个 rule 是否含 YAML frontmatter,缺则自动注入(description 字段从文件名推断)
    2. 复制到 .trae/skills/project_rules_skills/references/(源不动)

--move 模式:
    物理移走 .trae/rules/{rule}.md → .trae/rules/_archived/{rule}.md
    防 sub-agent 绕过 skill 直接 Read 源文件。

依赖:
    仅 Python 3.8+ 标准库。无第三方依赖。

安全:
    - 仅在 --project-root 指定的目录内操作
    - 不联网、不执行 shell
    - 不删除任何 rule 文件(--move 是移走 + 归档,不是 rm)
    - .trae/rules/README.md 是改写频率最高的文件(改为强制入口)
"""
import argparse
import pathlib
import sys
from datetime import datetime


# skill 自身所在的目录
SELF_DIR = pathlib.Path(__file__).resolve().parent
SKILL_DIR = SELF_DIR.parent
TEMPLATES_DIR = SKILL_DIR / "templates"
WORKFLOWS_SRC = SKILL_DIR / "workflows"

RULES_DIR = pathlib.Path(".trae/rules")
SKILL_OUTPUT_DIR = pathlib.Path(".trae/skills/project_rules_skills")
README_FILENAME = "README.md"

# 默认路由表(可被项目自定义)
DEFAULT_ROUTES = [
    ("改 API / 改契约", ["coding-standards.md", "paths.md"]),
    ("改前端 / 改样式", ["coding-standards.md", "paths.md"]),
    ("改依赖 / 改 build", ["stack.md", "paths.md"]),
    ("提 PR / 合分支", ["git.md", "paths.md"]),
    ("修 bug", ["coding-standards.md", "paths.md"]),
]


def log(level: str, msg: str) -> None:
    ts = datetime.now().strftime("%H:%M:%S")
    print(f"[{ts}] [{level}] {msg}")


def err(msg: str) -> None:
    log("ERROR", msg)


def info(msg: str) -> None:
    log("INFO", msg)


def ok(msg: str) -> None:
    log("OK", msg)


def step(msg: str) -> None:
    log("STEP", msg)


def scan_rules(project_root: pathlib.Path) -> list:
    """扫描 .trae/rules/*.md,排除 README.md

    注: pathlib glob("*.md") 不递归,_archived/ 下的文件不会扫到。
    """
    rules_dir = project_root / RULES_DIR
    if not rules_dir.exists():
        return []
    return sorted([
        f.name for f in rules_dir.glob("*.md")
        if f.name != README_FILENAME
    ])


def has_frontmatter(content: str) -> bool:
    """检测文件是否已有 YAML frontmatter(以 --- 开头 + 第二行 --- 结束)"""
    lines = content.splitlines()
    if not lines or lines[0].strip() != "---":
        return False
    for line in lines[1:]:
        if line.strip() == "---":
            return True
    return False


def inject_frontmatter(rule_path: pathlib.Path, rule_name: str) -> bool:
    """如果 rule 文件缺 frontmatter,在顶部追加一段最小元信息

    返回: 是否修改了文件
    """
    content = rule_path.read_text(encoding="utf-8")
    if has_frontmatter(content):
        return False

    # 默认 description 从文件名推断
    description = {
        "stack.md": "项目栈命令速查 — 构建/测试/lint/dev server + V11 验收命令",
        "paths.md": "项目级禁读路径 + MCP 查询防护 + 脏逻辑记录 + 安全红线",
        "git.md": "Git 工作流 — 分支策略 + commit 标签规范 + PR 模板 + 提交前自检",
        "coding-standards.md": "项目专属编码规范 — 桩代码标记 + 模型重复判定等",
    }.get(rule_name, f"项目级 rule: {rule_name}")

    frontmatter = (
        f"---\n"
        f"description: {description}\n"
        f"---\n"
        f"\n"
    )
    rule_path.write_text(frontmatter + content, encoding="utf-8")
    return True


def build_routes_table(existing_rules: list) -> str:
    """根据现有 rules 动态构建路由表,过滤掉不存在的"""
    lines = ["| 场景关键词 | 必加载 rules |", "|-----------|-------------|"]
    for scene, files in DEFAULT_ROUTES:
        # 只列存在的 rules
        available = [f for f in files if f in existing_rules]
        if not available:
            continue
        lines.append(f"| {scene} | {' + '.join(available)} |")
    lines.append("| 任何场景(未列出) | 全加载 |")
    return "\n".join(lines)


def build_rules_list(existing_rules: list) -> str:
    return "\n".join(f"- `{r}`" for r in existing_rules)


def render_skill_md(project_name: str, existing_rules: list) -> str:
    """渲染入口 skill 的 SKILL.md"""
    template_path = TEMPLATES_DIR / "SKILL.md.template"
    if not template_path.exists():
        err(f"模板缺失: {template_path}")
        sys.exit(1)

    template = template_path.read_text(encoding="utf-8")
    routes_table = build_routes_table(existing_rules)
    rules_list = build_rules_list(existing_rules)

    rendered = template.replace("{{PROJECT_NAME}}", project_name)
    rendered = rendered.replace("{{RULES_LIST}}", rules_list)
    rendered = rendered.replace("{{ROUTES_TABLE}}", routes_table)
    rendered = rendered.replace("{{GENERATED_AT}}", datetime.now().isoformat(timespec="seconds"))

    return rendered


def render_readme(project_name: str, existing_rules: list) -> str:
    """渲染入口 skill 的 README.md"""
    template_path = TEMPLATES_DIR / "README.md.template"
    if not template_path.exists():
        err(f"模板缺失: {template_path}")
        sys.exit(1)

    template = template_path.read_text(encoding="utf-8")
    rules_list = build_rules_list(existing_rules)

    rendered = template.replace("{{PROJECT_NAME}}", project_name)
    rendered = rendered.replace("{{RULES_LIST}}", rules_list)
    rendered = rendered.replace("{{GENERATED_AT}}", datetime.now().isoformat(timespec="seconds"))

    return rendered


def render_rules_readme(project_name: str, existing_rules: list) -> str:
    """改写 .trae/rules/README.md 为强制入口"""
    rules_list = build_rules_list(existing_rules)
    return f"""# .trae/rules/ 强制入口

> **🔴 必读 · 本目录是规则源,本 README.md 是唯一可被 Read 的文件**
> 
> 任何 agent(主 agent / sub-agent)进入本项目执行任务前,
> **必须先调用** `Skill(name="project-rules")` 获取本会话所需 rules。
> 
> **禁止绕过本入口**直接 Read `.trae/rules/*.md` 中除本 README.md 外的其他文件。
> 
> skill 入口: `.trae/skills/project_rules_skills/SKILL.md`
> 
> ---
> 
> ## 本项目 rules 列表(由 forge_project_rules_skill.py 检测)
> 
> {rules_list}
> 
> ## 加载协议
> 
> ```
> Step 1: 调用 Skill(name="project-rules")
> Step 2: 按路由表拿本会话所需 rules(SKILL.md §3)
> Step 3: 只 Read 选中的 rules(在 .trae/skills/project_rules_skills/references/)
> Step 4: sub-agent 必须在 Completion Report 声明 rules_loaded / rules_skipped
> ```
> 
> ## 详细说明
> 
> 详见 [.trae/skills/project_rules_skills/SKILL.md](../../skills/project_rules_skills/SKILL.md)
> 
> 项目名: {project_name}
> 
> 由 common-project-coding-conf v1.0 锻造
"""


def sync_rule_file(project_root: pathlib.Path, rule_name: str) -> None:
    """把 .trae/rules/{rule_name} 复制到入口 skill 的 references/"""
    src = project_root / RULES_DIR / rule_name
    dst = project_root / SKILL_OUTPUT_DIR / "references" / rule_name

    if not src.exists():
        err(f"源文件不存在: {src}")
        return

    content = src.read_text(encoding="utf-8")
    wrapped = (
        f"<!-- 来源: .trae/rules/{rule_name} (single source of truth) -->\n"
        f"<!-- 不要直接修改本文件,改完后跑 forge_project_rules_skill.py 同步 -->\n"
        f"\n"
        f"{content}\n"
    )
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text(wrapped, encoding="utf-8")


ARCHIVED_DIRNAME = "_archived"


def move_rule(project_root: pathlib.Path, rule_name: str) -> None:
    """物理移走 .trae/rules/{rule_name} → .trae/rules/_archived/{rule_name}

    移到 _archived/ 子目录(前缀 _ 防 forge 二次扫描),保留 git 历史 + 可回溯。
    仅在 --move 模式被调用。
    """
    src = project_root / RULES_DIR / rule_name
    if not src.exists():
        err(f"源文件不存在: {src}")
        return

    archived_dir = project_root / RULES_DIR / ARCHIVED_DIRNAME
    archived_dir.mkdir(parents=True, exist_ok=True)
    dst = archived_dir / rule_name

    # 覆盖已存在的归档
    src.replace(dst)


def copy_workflows(project_root: pathlib.Path) -> None:
    """复制委派头部模板"""
    src_dir = WORKFLOWS_SRC
    dst_dir = project_root / SKILL_OUTPUT_DIR / "workflows"
    dst_dir.mkdir(parents=True, exist_ok=True)

    if not src_dir.exists():
        err(f"workflows 源目录不存在: {src_dir}")
        return

    for f in src_dir.glob("*.md"):
        dst = dst_dir / f.name
        dst.write_text(f.read_text(encoding="utf-8"), encoding="utf-8")


def forge(project_root: pathlib.Path, project_name: str, dry_run: bool = False, move: bool = False) -> int:
    """主入口"""
    step("=" * 60)
    step("common-project-coding-conf 锻造器 v1.0")
    step(f"项目根: {project_root.resolve()}")
    step(f"项目名: {project_name}")
    step(f"模式: {'DRY-RUN(不写文件)' if dry_run else 'FORGE'}")
    step(f"--move: {'开(物理移走原 rules)' if move else '关(复制,源不动)'}")
    step("=" * 60)

    # Step 0: 前置检查
    rules_dir = project_root / RULES_DIR
    if not rules_dir.exists():
        err(f".trae/rules/ 不存在")
        err(f"请先在 {rules_dir} 放项目级 rule 文件(stack.md / paths.md / git.md 等)")
        return 1

    existing_rules = scan_rules(project_root)
    if not existing_rules:
        err(f".trae/rules/ 无 rule 文件(只有 README.md 或空目录)")
        return 1

    if len(existing_rules) < 1:
        info(f"仅 {len(existing_rules)} 个 rule,直接 Read 即可,无需锻造")
        return 0

    info(f"检测到 {len(existing_rules)} 个 rule:")
    for r in existing_rules:
        info(f"  - {r}")

    # Step 0.5: 注入 frontmatter(默认行为,除非 --dry-run)
    if dry_run:
        info(f"[DRY-RUN] 将检测并注入 frontmatter 到缺的 rule 文件")
    else:
        injected = 0
        for rule_name in existing_rules:
            if inject_frontmatter(rules_dir / rule_name, rule_name):
                injected += 1
                ok(f"已注入 frontmatter: {rule_name}")
        if injected == 0:
            info(f"所有 rule 已有 frontmatter,跳过注入")

    # Step 1: 创建入口 skill 目录
    skill_dir = project_root / SKILL_OUTPUT_DIR
    refs_dir = skill_dir / "references"

    if dry_run:
        info(f"[DRY-RUN] 将创建: {skill_dir}")
        info(f"[DRY-RUN] 将创建: {refs_dir}")
    else:
        skill_dir.mkdir(parents=True, exist_ok=True)
        refs_dir.mkdir(parents=True, exist_ok=True)
        ok(f"已创建 {skill_dir}")

    # Step 2: 渲染 SKILL.md / README.md
    skill_md = render_skill_md(project_name, existing_rules)
    readme_md = render_readme(project_name, existing_rules)

    if dry_run:
        info(f"[DRY-RUN] 将渲染: {skill_dir / 'SKILL.md'}")
        info(f"[DRY-RUN] 将渲染: {skill_dir / 'README.md'}")
    else:
        (skill_dir / "SKILL.md").write_text(skill_md, encoding="utf-8")
        (skill_dir / "README.md").write_text(readme_md, encoding="utf-8")
        ok(f"已渲染 SKILL.md / README.md")

    # Step 3: 同步源文件到 references/
    for rule_name in existing_rules:
        if dry_run:
            info(f"[DRY-RUN] 将同步: {rule_name}")
        else:
            sync_rule_file(project_root, rule_name)
    if not dry_run:
        ok(f"已同步 {len(existing_rules)} 个 rule 到 references/")

    # Step 3.5: 可选 --move,物理移走源文件
    if move:
        step(f"Step 3.5: --move 模式,物理移走原 rules 到 _archived/")
        for rule_name in existing_rules:
            if dry_run:
                info(f"[DRY-RUN] 将移走: {rule_name}")
            else:
                move_rule(project_root, rule_name)
        if not dry_run:
            ok(f"已移走 {len(existing_rules)} 个 rule 到 _archived/")
    else:
        step(f"Step 3.5: 跳过 --move(源规则保留在 .trae/rules/)")

    # Step 4: 复制 workflows/
    if dry_run:
        info(f"[DRY-RUN] 将复制 workflows/")
    else:
        copy_workflows(project_root)
        ok(f"已复制 workflows/")

    # Step 5: 改写 .trae/rules/README.md
    rules_readme = render_rules_readme(project_name, existing_rules)
    rules_readme_path = rules_dir / README_FILENAME

    if dry_run:
        info(f"[DRY-RUN] 将改写: {rules_readme_path}")
    else:
        rules_readme_path.write_text(rules_readme, encoding="utf-8")
        ok(f"已改写 {rules_readme_path} 为强制入口")

    # Step 6: 报告
    step("=" * 60)
    ok(f"锻造完成")
    info(f"")
    info(f"📋 接下来:")
    info(f"   1. 主 agent 委派 sub-agent 时,头部必加 [PROJECT-RULES-GATE] 块")
    info(f"   2. sub-agent 必须先调 Skill(name=\"project-rules\") 拿本任务 rules")
    info(f"   3. sub-agent 必须在 Completion Report 声明 rules_loaded / rules_skipped")
    info(f"")
    info(f"📖 完整协议:")
    info(f"   - 锻造: {SKILL_DIR / 'references' / 'forge-protocol.md'}")
    info(f"   - 委派: {SKILL_DIR / 'references' / 'agent-delegate-protocol.md'}")
    info(f"")
    step("=" * 60)

    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="common-project-coding-conf 锻造器 — 把 .trae/rules/ 收纳为入口 skill"
    )
    parser.add_argument(
        "--project-root",
        default=".",
        help="项目根路径(默认: 当前目录)"
    )
    parser.add_argument(
        "--project-name",
        help="项目名(默认: 项目根目录名)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="演练模式,不写任何文件"
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="强制重跑(默认: 已存在产物则跳过)"
    )
    parser.add_argument(
        "--move",
        action="store_true",
        help="物理移走原 rules 到 .trae/rules/_archived/(默认: 复制,源不动)"
    )

    args = parser.parse_args()

    project_root = pathlib.Path(args.project_root).resolve()
    if not project_root.exists():
        err(f"项目根不存在: {project_root}")
        return 1

    project_name = args.project_name or project_root.name

    return forge(project_root, project_name, args.dry_run, args.move)


if __name__ == "__main__":
    sys.exit(main())
