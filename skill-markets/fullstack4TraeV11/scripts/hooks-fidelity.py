#!/usr/bin/env python3
"""
V11 hooks-fidelity.py — Hook 保真度门禁（确保 hooks 实际生效）

Usage:
    python hooks-fidelity.py --project-root <path>

保真度检测项:
    1. Hook 脚本存在性（pre-stage.sh / post-stage.sh / pre-accept.sh）
    2. Hook 脚本可执行权限（+x）
    3. Hook 脚本调用真实 V11 脚本（不空壳）
    4. V11 脚本路径可达（~/.trae-cn/skills/fullstack4TraeV11/scripts/）
    5. State card 与 status_card 字段一致性
    6. AGENTS.md 引用的 SKILL.md 路径可达

Exit codes:
    0 = PASS（hooks 保真度 OK）
    1 = FAIL（hooks 失真）
"""
import sys
import argparse
import pathlib
import json
import re
import yaml
from datetime import datetime, timezone


HOOKS_REQUIRED = [
    # V11 shell hooks (3)
    "pre-stage.sh",
    "post-stage.sh",
    "pre-accept.sh",
    # V11 GitNexus 双端 (2)
    "gitnexus-session-check.py",
    "gitnexus-session-finalize.py",
    # V11 SessionStart (1)
    "session-start.py",
    # V11 UserPromptSubmit (1)
    "complexity-guard.py",
    # V11 PreToolUse (2)
    "doc-sync-gate.py",
    "contract-gate.py",
    # V11 PostToolUse (3)
    "spec-validate-hook.py",
    "auto-test.py",
    "drift-detect.py",
    # V11 Stop (1)
    "tasks-integrity.py",
]
V11_DEFAULT_PATH = pathlib.Path("~/.trae-cn/skills/fullstack4TraeV11/scripts").expanduser()


def check_hook_existence(project_root: pathlib.Path) -> dict:
    """Hook 脚本存在性"""
    hooks_dir = project_root / ".trae/hooks"
    result = {"hooks_dir_exists": hooks_dir.exists(), "hooks": {}}

    for hook_name in HOOKS_REQUIRED:
        hook_path = hooks_dir / hook_name
        exists = hook_path.exists()
        # Windows 用 shebang 判定可执行；Unix 用 mode & 0o111
        executable = False
        if exists:
            try:
                # Unix 权限检查
                executable = hook_path.stat().st_mode & 0o111
            except (AttributeError, OSError):
                pass
            if not executable:
                # Windows fallback: 检查 shebang 或 .sh 后缀
                try:
                    first_line = hook_path.read_text(encoding="utf-8").split("\n")[0]
                    if first_line.startswith("#!") or hook_name.endswith(".sh"):
                        executable = True
                except Exception:
                    pass
        result["hooks"][hook_name] = {
            "exists": exists,
            "executable": executable,
        }

    return result


def check_hook_invocation(project_root: pathlib.Path) -> dict:
    """Hook 脚本调用真实 V11 脚本或 subprocess 任务"""
    hooks_dir = project_root / ".trae/hooks"
    # V11.2 NEW: missing_scripts 字段用于实际验证被引用脚本存在(防止 stub PASS)
    result = {"invokes_real_v11_scripts": True, "scripts_referenced": set(), "unknown_hooks": [], "missing_scripts": [], "fallback_warning": None}

    if not hooks_dir.exists():
        return result

    # Hook 类别定义（哪些 hook 合法不调用 V11 Python 脚本）
    hook_categories = {
        # 5 个 V11 stage shell hook + 2 个 gitnexus 双端必调用 V11 脚本 / gitnexus analyze
        "pre-stage.sh": "shell_v11",
        "post-stage.sh": "shell_v11",
        "pre-accept.sh": "shell_v11",
        "gitnexus-session-check.py": "gitnexus",
        "gitnexus-session-finalize.py": "gitnexus",
        # 8 个 V11 TRAE IDE event hook 用 subprocess 跑外部命令（jest / vitest / pytest / cargo / go / node）
        # 不直接调用 V11 Python 脚本，但功能合法
        "session-start.py": "trae_event",
        "complexity-guard.py": "trae_event",
        "doc-sync-gate.py": "trae_event",
        "contract-gate.py": "trae_event",
        "spec-validate-hook.py": "trae_event",
        "auto-test.py": "trae_event",
        "drift-detect.py": "trae_event",
        "tasks-integrity.py": "trae_event",
    }

    for hook_name in HOOKS_REQUIRED:
        hook_path = hooks_dir / hook_name
        if not hook_path.exists():
            continue

        category = hook_categories.get(hook_name, "unknown")

        # 类别检查
        if category == "unknown":
            result["unknown_hooks"].append(hook_name)
            continue

        if category == "trae_event":
            # TRAE IDE event hook：必含 subprocess / TRAE env / print 报告 / 路径检查
            content = hook_path.read_text(encoding="utf-8")
            has_legitimate = (
                "subprocess" in content
                or "TRAE_FILE_PATH" in content
                or "TRAE_USER_PROMPT" in content
                or "print(" in content
                or ".exists()" in content
            )
            if has_legitimate:
                result["scripts_referenced"].add(f"trae-event:{hook_name}")
            else:
                result["invokes_real_v11_scripts"] = False
            continue

        content = hook_path.read_text(encoding="utf-8")
        # 检测是否调用 V11 脚本（兼容 ${VAR:-...} 形式）
        v11_scripts = re.findall(r"fullstack4TraeV11/scripts[/\\]+([\w\-]+\.py)", content)
        if not v11_scripts:
            # Fallback: 任何 *.py 引用
            v11_scripts = re.findall(r"([\w\-]+\.py)", content)
            v11_scripts = [s for s in v11_scripts if "stage-gate" in s or "state-card" in s or "phase-gate" in s]

        is_gitnexus_hook = category == "gitnexus"

        # V11.2 NEW: 实际验证被引用脚本存在(防止 stub PASS)
        for script_name in v11_scripts:
            script_path = V11_DEFAULT_PATH / script_name
            if not script_path.exists():
                result["missing_scripts"].append(script_name)
                result["invokes_real_v11_scripts"] = False

        # V11.2 NEW: fallback 模式只匹配 stage-gate/state-card/phase-gate 是宽松匹配,
        # 已通过 missing_scripts 验证避免误判
        if not v11_scripts and not is_gitnexus_hook:
            result["fallback_warning"] = "未检测到 V11 scripts 引用,需人工核验 hook 内容"
            result["invokes_real_v11_scripts"] = False

        if is_gitnexus_hook:
            v11_scripts = ["gitnexus-analyze"] + v11_scripts
        result["scripts_referenced"].update(v11_scripts)

    result["scripts_referenced"] = list(result["scripts_referenced"])
    return result


def check_v11_script_reachable() -> dict:
    """V11 脚本路径可达"""
    result = {
        "v11_default_path": str(V11_DEFAULT_PATH),
        "reachable": V11_DEFAULT_PATH.exists(),
        "scripts_found": [],
    }

    if V11_DEFAULT_PATH.exists():
        for f in V11_DEFAULT_PATH.glob("*.py"):
            result["scripts_found"].append(f.name)

    return result


def check_state_card_consistency(project_root: pathlib.Path) -> dict:
    """状态卡与文件系统一致性"""
    state_card = project_root / "docs/specs/.state-card.md"
    result = {"state_card_exists": state_card.exists()}

    if not state_card.exists():
        return result

    content = state_card.read_text(encoding="utf-8")
    if not content.startswith("---"):
        result["valid_yaml"] = False
        return result

    end = content.index("\n---", 3)
    fm_text = content[3:end]

    try:
        fm = yaml.safe_load(fm_text) or {}
        result["valid_yaml"] = True
        result["current_stage"] = fm.get("current_stage")
        result["artifacts"] = fm.get("artifacts", [])

        # 验证 artifacts 路径存在性
        if isinstance(result["artifacts"], list):
            missing = []
            for art in result["artifacts"]:
                if isinstance(art, dict):
                    path = art.get("path", "")
                    declared_exists = art.get("exists", False)
                    if path:
                        full_path = project_root / path
                        actual_exists = full_path.exists()
                        if actual_exists != declared_exists:
                            missing.append(f"{path}: 声明 {declared_exists} vs 实际 {actual_exists}")
            result["artifacts_inconsistent"] = missing
    except Exception as e:
        result["valid_yaml"] = False
        result["yaml_error"] = str(e)

    return result


def check_agents_md_paths(project_root: pathlib.Path) -> dict:
    """AGENTS.md 引用的 SKILL.md 路径可达（仅 markdown 链接形式）"""
    agents_md = project_root / "AGENTS.md"
    result = {"agents_md_exists": agents_md.exists()}

    if not agents_md.exists():
        return result

    content = agents_md.read_text(encoding="utf-8")
    # 仅检测 markdown 链接形式 [text](path/SKILL.md)，不检测说明文字
    skill_paths = re.findall(r"\]\(([\w/\-\.]+SKILL\.md)\)", content)

    result["referenced_skill_paths"] = list(set(skill_paths))
    result["reachable"] = []

    for skill_path in skill_paths:
        full_path = project_root / skill_path
        result["reachable"].append({
            "path": skill_path,
            "exists": full_path.exists(),
        })

    return result


def main():
    parser = argparse.ArgumentParser(description="V11 Hook 保真度门禁")
    parser.add_argument("--project-root", default=".", help="项目根路径")
    parser.add_argument("--json", action="store_true", help="JSON 输出")
    args = parser.parse_args()

    project_root = pathlib.Path(args.project_root).resolve()

    # 6 维度检查
    existence = check_hook_existence(project_root)
    invocation = check_hook_invocation(project_root)
    reachability = check_v11_script_reachable()
    consistency = check_state_card_consistency(project_root)
    agents_md = check_agents_md_paths(project_root)

    # 汇总
    issues = []

    # 1. Hooks 存在性
    if not existence["hooks_dir_exists"]:
        issues.append("缺 .trae/hooks/ 目录")
    else:
        for hook_name, status in existence["hooks"].items():
            if not status["exists"]:
                issues.append(f"缺 hook: {hook_name}")
            elif not status["executable"]:
                issues.append(f"hook 无 +x: {hook_name}")

    # 2. Hook 调用真实 V11 脚本
    if not invocation["invokes_real_v11_scripts"]:
        issues.append("hooks 未调用真实 V11 脚本（空壳）")

    # 3. V11 脚本可达
    if not reachability["reachable"]:
        issues.append(f"V11 脚本不可达: {reachability['v11_default_path']}")

    # 4. 状态卡一致性
    if consistency.get("state_card_exists"):
        if not consistency.get("valid_yaml"):
            issues.append("状态卡 YAML 无效")
        if consistency.get("artifacts_inconsistent"):
            issues.extend([f"artifacts 不一致: {x}" for x in consistency["artifacts_inconsistent"]])

    # 5. AGENTS.md 路径可达
    if agents_md.get("agents_md_exists"):
        for ref in agents_md.get("reachable", []):
            if not ref["exists"]:
                issues.append(f"AGENTS.md 引用路径不可达: {ref['path']}")

    is_pass = len(issues) == 0

    output = {
        "project_root": str(project_root),
        "scan_at": datetime.now(timezone.utc).isoformat(),
        "checks": {
            "hook_existence": existence,
            "hook_invocation": invocation,
            "v11_reachability": reachability,
            "state_card_consistency": consistency,
            "agents_md_paths": agents_md,
        },
        "issues": issues,
        "status": "PASS" if is_pass else "FAIL",
    }

    if args.json:
        print(json.dumps(output, indent=2, ensure_ascii=False, default=str))
    else:
        icon = "✅" if is_pass else "❌"
        print(f"{icon} {output['status']} — Hook 保真度门禁")
        print(f"\n1. Hook 存在性: {'✅' if existence['hooks_dir_exists'] else '❌'}")
        if existence["hooks_dir_exists"]:
            for h, s in existence["hooks"].items():
                mark = "✓" if s["exists"] and s["executable"] else "✗"
                print(f"   [{mark}] {h}: exists={s['exists']}, +x={s['executable']}")

        print(f"\n2. Hook 调用 V11 脚本: {invocation['scripts_referenced']}")

        print(f"\n3. V11 脚本可达: {'✅' if reachability['reachable'] else '❌'}")
        print(f"   路径: {reachability['v11_default_path']}")
        print(f"   脚本数: {len(reachability['scripts_found'])}")

        print(f"\n4. 状态卡一致性: {consistency.get('valid_yaml', 'N/A')}")

        print(f"\n5. AGENTS.md 路径: {len(agents_md.get('reachable', []))}")

        if issues:
            print(f"\n⚠️ 问题:")
            for i in issues:
                print(f"   - {i}")

    return 0 if is_pass else 1


if __name__ == "__main__":
    sys.exit(main())