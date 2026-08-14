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
    7. Gate 层验证（检测 .husky/pre-commit / .husky/pre-push 存在性）
    8. Guard 层验证（检测 TRAE IDE Hooks 是否实际安装）
    9. 硬化验证（检测 echo-skip 反例）

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
    # 优先探测新路径 docs/specs/changes/{id}/.state-card.md，找不到回退顶层旧路径
    state_card = None
    change_cards = list((project_root / "docs" / "specs" / "changes").glob("*/.state-card.md")) if (project_root / "docs" / "specs" / "changes").exists() else []
    if change_cards:
        state_card = change_cards[0]
    else:
        top_card = project_root / "docs/specs/.state-card.md"
        if top_card.exists():
            state_card = top_card
    result = {"state_card_exists": state_card is not None and state_card.exists()}

    if not state_card or not state_card.exists():
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


def check_gate_layer(project_root: pathlib.Path) -> dict:
    """Gate 层验证：检测 .husky/pre-commit 和 .husky/pre-push 是否存在、可执行、已硬化"""
    husky_dir = project_root / ".husky"
    result = {"husky_dir_exists": husky_dir.exists()}
    for hook_name in ["pre-commit", "pre-push"]:
        hook_path = husky_dir / hook_name
        info = {"exists": False, "executable": False, "has_hardening": False}
        if hook_path.exists():
            info["exists"] = True
            try:
                info["executable"] = bool(hook_path.stat().st_mode & 0o111)
            except (AttributeError, OSError):
                info["executable"] = False
            if not info["executable"]:
                # Windows fallback: 检查 .sh 后缀或 shebang
                try:
                    first = hook_path.read_text(encoding="utf-8").split("\n")[0]
                    if first.startswith("#!") or hook_name.endswith(".sh"):
                        info["executable"] = True
                except Exception:
                    pass
            # 硬化检测：必须含 set -e 或 set -euo pipefail
            try:
                content = hook_path.read_text(encoding="utf-8")
                info["has_hardening"] = "set -euo pipefail" in content or "set -e" in content
            except Exception:
                info["has_hardening"] = False
        result[hook_name] = info
    return result


def check_guard_layer(project_root: pathlib.Path) -> dict:
    """Guard 层验证：检测 .trae/hooks/ 下 TRAE IDE event hooks 是否安装"""
    hooks_dir = project_root / ".trae" / "hooks"
    expected = ["doc-sync-gate.py", "contract-gate.py", "spec-validate-hook.py", "auto-test.py", "drift-detect.py"]
    result = {"trae_hooks_dir_exists": hooks_dir.exists(), "hooks_expected": expected, "missing_hooks": [], "hooks_installed": 0}
    if hooks_dir.exists():
        installed = 0
        for name in expected:
            if (hooks_dir / name).exists():
                installed += 1
            else:
                result["missing_hooks"].append(name)
        result["hooks_installed"] = installed
    else:
        result["missing_hooks"] = expected[:]
    return result


def check_gitnexus_freshness(project_root: pathlib.Path) -> dict:
    """GitNexus 运行痕迹新鲜度校验（V11.4 NEW）
    会话开始写 last-run-check.json，会话结束写 last-run.json。
    用最近一条痕迹的时间戳判断 gitnexus hook 是否真的跑过。"""
    gitnexus_dir = project_root / ".gitnexus"
    result = {
        "gitnexus_dir_exists": False,
        "trace_files": [],          # 实际存在的痕迹文件
        "missing_trace_files": [],  # 缺失的痕迹文件
        "last_run_at": None,        # 最近一次运行时间(ISO)
        "fresh": False,             # 是否 24h 内跑过
        "stale_days": None,
    }
    if not gitnexus_dir.exists():
        result["missing_trace_files"] = ["last-run.json", "last-run-check.json"]
        return result
    result["gitnexus_dir_exists"] = True
    expected = ["last-run.json", "last-run-check.json"]
    latest = None
    for name in expected:
        p = gitnexus_dir / name
        if p.exists():
            result["trace_files"].append(name)
            try:
                data = json.loads(p.read_text(encoding="utf-8"))
                at = data.get("at")
                if at and (latest is None or at > latest):
                    latest = at
            except (OSError, ValueError):
                pass
        else:
            result["missing_trace_files"].append(name)
    result["last_run_at"] = latest
    if latest:
        try:
            from datetime import datetime, timezone
            dt = datetime.fromisoformat(latest)
            delta = datetime.now(timezone.utc) - dt
            result["stale_days"] = round(delta.total_seconds() / 86400, 2)
            result["fresh"] = delta.total_seconds() < 86400  # 24h 内
        except (ValueError, TypeError):
            result["fresh"] = False
    return result


def check_hardening(project_root: pathlib.Path) -> dict:
    """硬化验证：检测 echo-skip 占位符反例"""
    result = {"checked_files": 0, "violations": [], "passed": True}
    for d in [project_root / ".husky", project_root / ".trae" / "hooks"]:
        if not d.exists():
            continue
        for f in d.glob("*"):
            if not f.is_file():
                continue
            try:
                content = f.read_text(encoding="utf-8")
            except Exception:
                continue
            result["checked_files"] += 1
            if re.search(r'echo\s+["\']?(skip|not|skipp)', content, re.IGNORECASE):
                result["violations"].append({"file": str(f), "pattern": "echo-skip detected"})
                result["passed"] = False
    return result


def main():
    parser = argparse.ArgumentParser(description="V11 Hook 保真度门禁（硬化版）")
    parser.add_argument("--project-root", default=".", help="项目根路径")
    parser.add_argument("--json", action="store_true", help="JSON 输出")
    args = parser.parse_args()

    project_root = pathlib.Path(args.project_root).resolve()

    # 9 维度检查（新增 Gate 层 + Guard 层 + 硬化验证）
    existence = check_hook_existence(project_root)
    invocation = check_hook_invocation(project_root)
    reachability = check_v11_script_reachable()
    consistency = check_state_card_consistency(project_root)
    agents_md = check_agents_md_paths(project_root)
    gate_layer = check_gate_layer(project_root)
    guard_layer = check_guard_layer(project_root)
    hardening = check_hardening(project_root)
    gitnexus_freshness = check_gitnexus_freshness(project_root)

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

    # 6. Gate 层验证（.husky/pre-commit / .husky/pre-push）
    if not gate_layer["husky_dir_exists"]:
        issues.append("缺 .husky/ 目录（Gate 层未配置）")
    else:
        for hook_name in ["pre-commit", "pre-push"]:
            hook_info = gate_layer.get(hook_name, {})
            if not hook_info.get("exists"):
                issues.append(f"缺 Gate hook: .husky/{hook_name}")
            elif not hook_info.get("executable"):
                issues.append(f"Gate hook 无 +x: .husky/{hook_name}")
            elif not hook_info.get("has_hardening"):
                issues.append(f"Gate hook 未硬化: .husky/{hook_name}（缺 set -euo pipefail）")

    # 7. Guard 层验证（TRAE IDE Hooks 安装）
    if not guard_layer["trae_hooks_dir_exists"]:
        issues.append("缺 .trae/hooks/ 目录（Guard 层未配置）")
    else:
        missing_count = len(guard_layer["missing_hooks"])
        if missing_count > 0:
            issues.append(f"Guard 层缺失 {missing_count} 个 hook（期望 {len(guard_layer['hooks_expected'])} 个）")

    # 8. 硬化验证（echo-skip 反例）
    if not hardening["passed"]:
        for violation in hardening["violations"]:
            issues.append(f"硬化违规: {violation['file']} — {violation['pattern']}")

    # 9. GitNexus 运行痕迹新鲜度（V11.4 NEW — 证明 gitnexus hook 真的跑过）
    if not gitnexus_freshness["gitnexus_dir_exists"]:
        issues.append("缺 .gitnexus/ 目录（GitNexus 未运行，无运行痕迹）")
    elif not gitnexus_freshness["fresh"]:
        issues.append(f"GitNexus 运行痕迹过期（stale_days={gitnexus_freshness['stale_days']}, last_run_at={gitnexus_freshness['last_run_at']}）")
    elif gitnexus_freshness["missing_trace_files"]:
        issues.append(f"GitNexus 痕迹文件缺失: {', '.join(gitnexus_freshness['missing_trace_files'])}")

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
            "gate_layer": gate_layer,
            "guard_layer": guard_layer,
            "hardening": hardening,
            "gitnexus_freshness": gitnexus_freshness,
        },
        "issues": issues,
        "status": "PASS" if is_pass else "FAIL",
    }

    if args.json:
        print(json.dumps(output, indent=2, ensure_ascii=False, default=str))
    else:
        icon = "✅" if is_pass else "❌"
        print(f"{icon} {output['status']} — Hook 保真度门禁（硬化版）")
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

        print(f"\n6. Gate 层（.husky）: {'✅' if gate_layer['husky_dir_exists'] else '❌'}")
        for hook_name in ["pre-commit", "pre-push"]:
            info = gate_layer.get(hook_name, {})
            hardening_mark = "✓" if info.get("has_hardening") else "✗"
            print(f"   [{hardening_mark}] .husky/{hook_name}: exists={info.get('exists')}, hardened={info.get('has_hardening')}")

        print(f"\n7. Guard 层（.trae/hooks）: {'✅' if guard_layer['trae_hooks_dir_exists'] else '❌'}")
        print(f"   已安装: {guard_layer['hooks_installed']}/{len(guard_layer['hooks_expected'])}")

        print(f"\n8. 硬化验证: {'✅' if hardening['passed'] else '❌'}")
        print(f"   检查文件: {hardening['checked_files']}, 违规: {len(hardening['violations'])}")

        print(f"\n9. GitNexus 运行痕迹: {'✅' if gitnexus_freshness['fresh'] else '❌'}")
        print(f"   .gitnexus 存在: {gitnexus_freshness['gitnexus_dir_exists']}")
        print(f"   痕迹文件: {gitnexus_freshness['trace_files'] or '无'}")
        print(f"   最近运行: {gitnexus_freshness['last_run_at'] or 'N/A'}, stale_days={gitnexus_freshness['stale_days']}")

        if issues:
            print(f"\n⚠️ 问题:")
            for i in issues:
                print(f"   - {i}")

    return 0 if is_pass else 1


if __name__ == "__main__":
    sys.exit(main())