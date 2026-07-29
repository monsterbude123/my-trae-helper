"""
V9.2 Hook 安装脚本 — 从技能包安装 hooks 到目标项目。

用法:
  python install-hooks.py --project-root <目标项目路径>
  python install-hooks.py --project-root D:/workspace/my-project --force

功能:
  1. 复制 8 个 .py Hook 脚本到 .trae/hooks/
  2. 复制 hooks.json 到 .trae/hooks.json
  3. 复制 3 个 .py 支持脚本到 .trae/scripts/
  4. 创建 .trae/logs/ 目录
  5. 输出安装摘要

原理: 技能包 templates/ 是模板源，脚本确定性复制到项目。
      与 env-init.py 不同：env-init 是项目端检查修复，install-hooks 是技能端安装部署。
"""

import argparse
import shutil
import os
import sys
from pathlib import Path
from datetime import datetime


# ─── 常量 ─────────────────────────────────────────────

HOOK_SCRIPTS = [
    "session-start.py",
    "complexity-guard.py",
    "doc-sync-gate.py",
    "contract-gate.py",
    "spec-validate-hook.py",
    "auto-test.py",
    "drift-detect.py",
    "tasks-integrity.py",
]

SUPPORT_SCRIPTS = [
    "env-init.py",
    "render-cockpit.py",
    "log-agent-prompt.py",
]

# 技能包内模板目录（相对路径，由脚本自身位置计算）
def get_skill_root() -> Path:
    """从脚本位置推算技能包根目录: .../fullstack4TraeV9/"""
    return Path(__file__).resolve().parent.parent

TEMPLATES_HOOKS = get_skill_root() / "templates" / "hooks"
TEMPLATES_SCRIPTS = get_skill_root() / "templates" / "scripts"


# ─── 安装逻辑 ─────────────────────────────────────────

def install(project_root: Path, force: bool = False) -> dict:
    """安装 hooks 到目标项目。返回安装摘要。"""
    result = {
        "project": str(project_root),
        "hooks_installed": [],
        "scripts_installed": [],
        "json_installed": False,
        "logs_created": False,
        "skipped": [],
        "errors": [],
    }

    # 1. 确保目标目录存在
    hooks_dir = project_root / ".trae" / "hooks"
    hooks_dir.mkdir(parents=True, exist_ok=True)
    logs_dir = project_root / ".trae" / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)
    result["logs_created"] = True

    # 2. 复制 .py Hook 脚本
    for script_name in HOOK_SCRIPTS:
        src = TEMPLATES_HOOKS / script_name
        dst = hooks_dir / script_name

        if not src.exists():
            result["errors"].append(f"源文件缺失: {src}")
            continue

        if dst.exists() and not force:
            result["skipped"].append(script_name)
            continue

        try:
            shutil.copy2(src, dst)
            result["hooks_installed"].append(script_name)
        except Exception as e:
            result["errors"].append(f"复制失败 {script_name}: {e}")

    # 3. 复制 hooks.json 到项目根 .trae/
    json_src = TEMPLATES_HOOKS / "fullstack-hooks.json"
    json_dst = project_root / ".trae" / "hooks.json"

    if json_src.exists():
        if not json_dst.exists() or force:
            try:
                shutil.copy2(json_src, json_dst)
                result["json_installed"] = True
            except Exception as e:
                result["errors"].append(f"hooks.json 复制失败: {e}")
        else:
            result["skipped"].append("hooks.json")
    else:
        result["errors"].append(f"hooks.json 模板缺失: {json_src}")

    # 4. 复制 .py 支持脚本
    scripts_dir = project_root / ".trae" / "scripts"
    scripts_dir.mkdir(parents=True, exist_ok=True)
    for script_name in SUPPORT_SCRIPTS:
        src = TEMPLATES_SCRIPTS / script_name
        dst = scripts_dir / script_name
        dst.parent.mkdir(parents=True, exist_ok=True)

        if not src.exists():
            result["errors"].append(f"源文件缺失: {src}")
            continue

        if dst.exists() and not force:
            result["skipped"].append(script_name)
            continue

        try:
            shutil.copy2(src, dst)
            result["scripts_installed"].append(script_name)
        except Exception as e:
            result["errors"].append(f"复制失败 {script_name}: {e}")

    # 5. 复制 README.md
    readme_src = TEMPLATES_HOOKS / "README.md"
    readme_dst = hooks_dir / "README.md"
    if readme_src.exists():
        try:
            shutil.copy2(readme_src, readme_dst)
        except Exception as e:
            result["errors"].append(f"README.md 复制失败: {e}")

    # 6. 写入安装日志
    install_log = logs_dir / "hook-install.log"
    with open(install_log, "a", encoding="utf-8") as f:
        f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] "
                f"V9.2 hooks installed | {len(result['hooks_installed'])} hooks | "
                f"{len(result['scripts_installed'])} scripts | "
                f"skipped: {len(result['skipped'])} | errors: {len(result['errors'])}\n")

    return result


# ─── CLI ──────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="V9.2 Hook 安装脚本 — 从技能包安装 hooks 到目标项目"
    )
    parser.add_argument(
        "--project-root", required=True,
        help="目标项目根目录（如 D:/workspace/my-project）"
    )
    parser.add_argument(
        "--force", action="store_true",
        help="强制覆盖已存在的 hook 文件"
    )
    parser.add_argument(
        "--check", action="store_true",
        help="仅检查，不安装"
    )
    args = parser.parse_args()

    project_root = Path(args.project_root).resolve()

    if not project_root.exists():
        print(f"❌ 项目目录不存在: {project_root}")
        sys.exit(1)

    if args.check:
        # 检查模式：列出已安装/缺失
        hooks_dir = project_root / ".trae" / "hooks"
        scripts_dir = project_root / ".trae" / "scripts"
        json_path = project_root / ".trae" / "hooks.json"

        print(f"项目: {project_root.name}")
        print(f"路径: {project_root}")
        print()

        if json_path.exists():
            print("✅ hooks.json — 已配置")
        else:
            print("❌ hooks.json — 缺失")

        for s in HOOK_SCRIPTS:
            p = hooks_dir / s
            status = "✅" if p.exists() else "❌"
            print(f"{status} .trae/hooks/{s}")

        for s in SUPPORT_SCRIPTS:
            p = scripts_dir / s
            status = "✅" if p.exists() else "❌"
            print(f"{status} .trae/scripts/{s}")

        return

    # 安装模式
    print(f"安装 V9.2 Hooks 到: {project_root}")
    print()

    result = install(project_root, force=args.force)

    # 输出摘要
    if result["hooks_installed"]:
        print(f"✅ Hooks: {len(result['hooks_installed'])} 个")
        for s in result["hooks_installed"]:
            print(f"   + .trae/hooks/{s}")

    if result["scripts_installed"]:
        print(f"✅ 支持脚本: {len(result['scripts_installed'])} 个")
        for s in result["scripts_installed"]:
            print(f"   + .trae/scripts/{s}")

    if result["json_installed"]:
        print(f"✅ 配置: .trae/hooks.json")
    else:
        print(f"⚠️ hooks.json 已跳过（存在且非 --force）")

    if result["skipped"]:
        print(f"⚠️ 跳过: {len(result['skipped'])} 个（已存在，用 --force 覆盖）")
        for s in result["skipped"]:
            print(f"   - {s}")

    if result["errors"]:
        print(f"❌ 错误: {len(result['errors'])} 个")
        for e in result["errors"]:
            print(f"   ! {e}")
        sys.exit(1)

    if result["logs_created"]:
        print(f"✅ 日志目录: .trae/logs/")

    print()
    print("安装完成。重启 IDE 使 hooks 生效。")
    print(f"验证: python {Path(__file__).name} --project-root {project_root} --check")


if __name__ == "__main__":
    main()
