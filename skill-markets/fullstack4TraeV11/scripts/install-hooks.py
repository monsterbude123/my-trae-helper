#!/usr/bin/env python3
"""
V11 install-hooks.py — 从技能包安装 hooks 到目标项目。

Usage:
    python install-hooks.py --project-root <path> [--force]

功能:
  1. 复制 V11 默认 3 个 + GitNexus 双端 2 个 = 5 个 hook 脚本到 .trae/hooks/
  2. 创建 .trae/logs/ 目录
  3. 输出安装摘要

V11 继承 V10.10 双端设计（SessionStart 读 + Stop 写）。

与 V10 区别:
  - V11 仅 5 个 hooks（3 shell + 2 gitnexus）
  - V10 10 个 hooks（含 8 个 TRAE IDE 专用）

Exit codes:
    0 = PASS
    1 = FAIL
"""
import sys
import argparse
import pathlib
import shutil
import json
from datetime import datetime, timezone


# V11 hook 列表（13 个：3 shell + 8 TRAE IDE + 2 gitnexus）
HOOK_SCRIPTS = [
    # V11 shell hooks（3 个）
    ("pre-stage.sh", "pre-stage", "V11 Stage 切换前必跑 stage-gate.py"),
    ("post-stage.sh", "post-stage", "V11 Stage 结束后必跑 state-card-validator.py"),
    ("pre-accept.sh", "pre-accept", "V11 Stage 5 Accept 前必跑 phase-gate.py --verify-rot-scan"),

    # V11 GitNexus 双端 hooks（2 个，V10.10 NEW）
    ("gitnexus-session-check.py", "gitnexus-session-check", "SessionStart: GitNexus 索引 staleness 检测 + 后台刷新"),
    ("gitnexus-session-finalize.py", "gitnexus-session-finalize", "Stop: GitNexus 索引后台刷新"),

    # V11 SessionStart hooks（1 个，蒸馏自 V10 session-start.py）
    ("session-start.py", "session-start", "SessionStart: 6 层知识发现协议 + Article XVII secret 检查"),

    # V11 UserPromptSubmit hooks（1 个，蒸馏自 V10 complexity-guard.py）
    ("complexity-guard.py", "complexity-guard", "UserPromptSubmit: 复杂度评分 + GitNexus First 提醒 + Article XVII 警告"),

    # V11 PreToolUse hooks（2 个，蒸馏自 V10）
    ("doc-sync-gate.py", "doc-sync-gate", "PreToolUse: DOC SYNC + spec-purge 历史感知"),
    ("contract-gate.py", "contract-gate", "PreToolUse: contracts/ + spec-purge 历史区分"),

    # V11 PostToolUse hooks（3 个，蒸馏自 V10）
    ("spec-validate-hook.py", "spec-validate-hook", "PostToolUse: Delta Spec + Scenario + SHALL + prototypes/"),
    ("auto-test.py", "auto-test", "PostToolUse: 自动测试 + Article XVII secret 检测 + spec.md Acceptance"),
    ("drift-detect.py", "drift-detect", "PostToolUse: 契约漂移 + spec-purge 区分"),

    # V11 Stop hooks（1 个，蒸馏自 V10 tasks-integrity.py）
    ("tasks-integrity.py", "tasks-integrity", "Stop: 任务完成度 + spec-purge 历史上下文"),
]


V11_SKILL_ROOT = pathlib.Path("~/.trae-cn/skills/fullstack4TraeV11").expanduser()
TEMPLATES_HOOKS = V11_SKILL_ROOT / "templates" / "hooks"


def install(project_root: pathlib.Path, force: bool = False) -> dict:
    """安装 hooks 到目标项目"""
    result = {
        "project": str(project_root),
        "hooks_installed": [],
        "skipped": [],
        "errors": [],
        "install_at": datetime.now(timezone.utc).isoformat(),
    }

    # 1. 确保目标目录
    hooks_dir = project_root / ".trae" / "hooks"
    hooks_dir.mkdir(parents=True, exist_ok=True)
    logs_dir = project_root / ".trae" / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)

    # 2. 复制 hooks
    if not TEMPLATES_HOOKS.exists():
        result["errors"].append(f"V11 templates/hooks 不存在: {TEMPLATES_HOOKS}")
        return result

    # 2.1 复制 fullstack-hooks.json 到项目根 .trae/
    src_json = TEMPLATES_HOOKS / "fullstack-hooks.json"
    dst_json = project_root / ".trae" / "hooks.json"
    if src_json.exists():
        if not dst_json.exists() or force:
            shutil.copy2(src_json, dst_json)
            result["json_installed"] = True

    for script_name, display_name, description in HOOK_SCRIPTS:
        src = TEMPLATES_HOOKS / script_name
        if not src.exists():
            result["errors"].append(f"缺失 source: {src}")
            continue

        dst = hooks_dir / script_name
        if dst.exists() and not force:
            result["skipped"].append(script_name)
            continue

        shutil.copy2(src, dst)
        if script_name.endswith(".sh"):
            dst.chmod(0o755)
        elif script_name.endswith(".py"):
            dst.chmod(0o755)
        result["hooks_installed"].append({
            "name": display_name,
            "file": script_name,
            "description": description,
        })

    # 3. 生成 install report
    report_path = project_root / ".trae" / "logs" / "hooks-install.json"
    report_path.write_text(
        json.dumps(result, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    return result


def main():
    parser = argparse.ArgumentParser(description="V11 install-hooks — hooks 安装")
    parser.add_argument("--project-root", default=".", help="项目根路径")
    parser.add_argument("--force", action="store_true", help="覆盖已有")
    parser.add_argument("--json", action="store_true", help="JSON 输出")
    args = parser.parse_args()

    project_root = pathlib.Path(args.project_root).resolve()

    if not project_root.exists():
        print(f"❌ 项目目录不存在: {project_root}")
        return 1

    result = install(project_root, args.force)

    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print(f"🚀 V11 install-hooks — {project_root}")
        if result["hooks_installed"]:
            print(f"\n✅ 已安装 ({len(result['hooks_installed'])} 个):")
            for h in result["hooks_installed"]:
                print(f"   - {h['file']}: {h['description']}")
        if result["skipped"]:
            print(f"\n⏭️  跳过 ({len(result['skipped'])} 个，已存在): {result['skipped']}")
        if result["errors"]:
            print(f"\n❌ 错误:")
            for e in result["errors"]:
                print(f"   - {e}")
            return 1
        print(f"\n📋 安装报告: {project_root}/.trae/logs/hooks-install.json")

    return 0 if not result["errors"] else 1


if __name__ == "__main__":
    sys.exit(main())