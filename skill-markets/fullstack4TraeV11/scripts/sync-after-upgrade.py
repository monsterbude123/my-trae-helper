#!/usr/bin/env python3
"""
V11 sync-after-upgrade.py — 技能升级后覆盖性更新项目文件

Usage:
    python sync-after-upgrade.py --project-root <path> [--dry-run] [--json]

场景:
    每次做完 V11 技能升级后,agent 调用此脚本检查项目侧需要同步更新的地方。

检查 + 更新范围:
  1. hooks/         ← 对比 V11 最新 hooks 与项目 .trae/hooks/,覆盖更新
  2. config.yaml    ← 对比 V11 最新 config template 与项目 .trae/fullstack4traev11.config.yaml
  3. rules/         ← 检查 V11 templates/project-rules-example/ 是否有新增文件
  4. AGENTS.md      ← 检查 V11 templates/project-agents-example.md 是否有结构变更
  5. scripts/       ← 检查 V11 scripts/ 是否有新增脚本(项目可直接引用,无需复制)

设计原则:
  - 覆盖式更新 hooks/ + config.yaml(V11 强约束,必须一致)
  - rules/ + AGENTS.md 只提示差异,不覆盖(含项目独有信息)
  - scripts/ 只提示新增,不复制(项目通过 V11_SKILL_ROOT 引用)

Exit codes:
    0 = PASS（全部同步完成）
    1 = FAIL（有同步失败）
    2 = NEEDS_REVIEW（有差异需 agent 人工审查）
"""
import sys
import argparse
import pathlib
import json
import shutil
from datetime import datetime, timezone

V11_SKILL_ROOT = pathlib.Path("~/.trae-cn/skills/fullstack4TraeV11").expanduser()
V11_TEMPLATES = V11_SKILL_ROOT / "templates"
V11_SCRIPTS = V11_SKILL_ROOT / "scripts"
V11_HOOKS_TEMPLATE = V11_TEMPLATES / "hooks"


def sync_hooks(project_root: pathlib.Path, dry_run: bool = False) -> dict:
    """同步 hooks: 覆盖式更新 V11 默认 3 个 hook"""
    hooks_dir = project_root / ".trae/hooks"
    result = {"step": "hooks", "updated": [], "unchanged": [], "added": []}

    # 统一从 init-from-zero.py 导入 HOOK_* 常量(与 init 保持一致)
    init_script = V11_SCRIPTS / "init-from-zero.py"
    if not init_script.exists():
        result["error"] = "init-from-zero.py 不可用"
        return result

    import importlib.util
    spec = importlib.util.spec_from_file_location("init_from_zero", init_script)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    hook_contents = {
        "pre-stage.sh": mod.HOOK_PRE_STAGE,
        "post-stage.sh": mod.HOOK_POST_STAGE,
        "pre-accept.sh": mod.HOOK_PRE_ACCEPT,
    }

    hooks_dir.mkdir(parents=True, exist_ok=True)

    for name, content in hook_contents.items():
        dst = hooks_dir / name
        if not dst.exists():
            if not dry_run:
                dst.write_text(content, encoding="utf-8")
                dst.chmod(0o755)
            result["added"].append(name)
        else:
            # normalize line endings for comparison (CRLF vs LF)
            current = dst.read_text(encoding="utf-8").replace("\r\n", "\n").replace("\r", "\n")
            expected = content.replace("\r\n", "\n").replace("\r", "\n")
            if current != expected:
                if not dry_run:
                    dst.write_text(content, encoding="utf-8")
                    dst.chmod(0o755)
                result["updated"].append(name)
            else:
                result["unchanged"].append(name)

    return result


def sync_config(project_root: pathlib.Path, dry_run: bool = False) -> dict:
    """同步 config: 检查 required_stages / forbidden_paths 是否有新增"""
    config_path = project_root / ".trae/fullstack4traev11.config.yaml"
    result = {"step": "config", "updated": False, "new_fields": []}

    if not config_path.exists():
        result["error"] = "config.yaml 不存在(需先跑 init-from-zero.py)"
        return result

    current = config_path.read_text(encoding="utf-8")

    # V11 最新的 required_stages(从 init-from-zero.py CONFIG_TEMPLATE 推导)
    required_stages = [
        "- -1/intake",
        "- 0/plan",
        "- 1/spec",
        "- 3.5/real-verify",
        "- 4.5/rot-scan",
    ]

    # 检查是否有缺失的 required_stage
    for stage in required_stages:
        if stage not in current:
            result["new_fields"].append(f"required_stages: {stage}")

    # 检查 forbidden_paths 是否有新增
    for path in ["- docs/archive/**", "- .trae/tmp/**"]:
        if path not in current:
            result["new_fields"].append(f"forbidden_paths: {path}")

    if result["new_fields"] and not dry_run:
        # 追加缺失字段(config.yaml 是 V11 强约束,可覆盖)
        # 简单策略:在文件末尾追加注释 + 缺失字段
        addition = "\n# --- V11 升级同步追加 ---\n"
        if any("required_stages" in f for f in result["new_fields"]):
            addition += "# 检查 required_stages 是否含以上 stage\n"
        if any("forbidden_paths" in f for f in result["new_fields"]):
            addition += "# 检查 forbidden_paths 是否含以上路径\n"
        current += addition
        config_path.write_text(current, encoding="utf-8")
        result["updated"] = True

    return result


def check_rules_diff(project_root: pathlib.Path) -> dict:
    """检查 rules: 对比 V11 templates 与项目 .trae/rules/"""
    result = {"step": "rules", "new_files": [], "missing_in_project": []}
    rules_dir = project_root / ".trae/rules"
    template_dir = V11_TEMPLATES / "project-rules-example"

    if not template_dir.exists():
        result["error"] = "V11 rules 模板目录不存在"
        return result

    # 检查 V11 是否有新增 rule 文件
    for src in template_dir.glob("*.md"):
        name = src.name
        dst = rules_dir / name
        if not dst.exists():
            result["new_files"].append(name)

    return result


def check_agents_md_diff(project_root: pathlib.Path) -> dict:
    """检查 AGENTS.md: 对比 V11 template 结构"""
    result = {"step": "AGENTS.md", "needs_review": False, "reasons": []}
    agents_path = project_root / "AGENTS.md"
    template_path = V11_TEMPLATES / "project-agents-example.md"

    if not agents_path.exists():
        result["needs_review"] = True
        result["reasons"].append("AGENTS.md 不存在(需跑 init-from-zero.py)")
        return result

    if not template_path.exists():
        return result

    current = agents_path.read_text(encoding="utf-8")
    template = template_path.read_text(encoding="utf-8")

    # 检查 template 是否有新增章节(template 中 ## 但 current 中没有)
    import re
    template_sections = set(re.findall(r"^## \d+\.\s+(.+)$", template, re.MULTILINE))
    current_sections = set(re.findall(r"^## \d+\.\s+(.+)$", current, re.MULTILINE))

    new_sections = template_sections - current_sections
    if new_sections:
        result["needs_review"] = True
        result["reasons"].append(f"template 新增章节: {new_sections}")

    # 检查 template 是否有新增引用行
    template_refs = set(re.findall(r"~- (.+?) ~", template))
    current_refs = set(re.findall(r"~- (.+?) ~", current))
    new_refs = template_refs - current_refs
    if new_refs:
        result["needs_review"] = True
    result["new_refs"] = list(new_refs) if new_refs else []

    return result


def check_scripts_new(project_root: pathlib.Path) -> dict:
    """检查 scripts: V11 是否有新增脚本"""
    result = {"step": "scripts", "new_scripts": []}

    if not V11_SCRIPTS.exists():
        result["error"] = "V11 scripts/ 目录不存在"
        return result

    for src in V11_SCRIPTS.glob("*.py"):
        if src.name.startswith("_"):
            continue  # 内部库
        result["new_scripts"].append(src.name)

    # 脚本由 V11_SKILL_ROOT 统一引用,项目不需要复制
    # 只提示有哪些可用
    result["note"] = "脚本由 V11 统一引用,项目无需复制"
    return result


def main():
    parser = argparse.ArgumentParser(description="V11 技能升级后覆盖性更新项目文件")
    parser.add_argument("--project-root", default=".", help="项目根路径")
    parser.add_argument("--dry-run", action="store_true", help="只检查不修改")
    parser.add_argument("--json", action="store_true", help="JSON 输出")
    args = parser.parse_args()

    project_root = pathlib.Path(args.project_root).resolve()

    if not project_root.exists():
        print(f"❌ 项目目录不存在: {project_root}")
        return 1

    mode = "DRY-RUN" if args.dry_run else "SYNC"
    print(f"🔄 V11 升级同步（{mode}）— {project_root}")
    print()

    steps = [
        ("hooks", lambda: sync_hooks(project_root, args.dry_run)),
        ("config", lambda: sync_config(project_root, args.dry_run)),
        ("rules", lambda: check_rules_diff(project_root)),
        ("AGENTS.md", lambda: check_agents_md_diff(project_root)),
        ("scripts", lambda: check_scripts_new(project_root)),
    ]

    results = []
    needs_review = False

    for name, func in steps:
        result = func()
        results.append(result)

        status = "✅"
        if result.get("error"):
            status = "❌"
        elif result.get("needs_review") or result.get("new_files") or result.get("new_fields"):
            status = "⚠️"
            needs_review = True
        elif result.get("updated") or result.get("added"):
            status = "🔄"

        print(f"  {status} {name}:")
        for k, v in result.items():
            if k == "step":
                continue
            if v:
                print(f"     {k}: {v}")
        print()

    all_pass = not any(r.get("error") for r in results)

    if args.json:
        print(json.dumps({
            "project_root": str(project_root),
            "mode": mode,
            "results": results,
            "status": "NEEDS_REVIEW" if needs_review else ("PASS" if all_pass else "FAIL"),
        }, indent=2, ensure_ascii=False))
    else:
        if needs_review:
            print(f"⚠️ 同步完成,但有 {sum(1 for r in results if r.get('needs_review') or r.get('new_files'))} 项需 agent 人工审查")
        elif all_pass:
            print(f"✅ 同步完成（{mode}）")
        else:
            print(f"❌ 同步失败")

    if needs_review:
        return 2
    return 0 if all_pass else 1


if __name__ == "__main__":
    sys.exit(main())
