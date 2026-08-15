#!/usr/bin/env python3
"""
scripts/goal-mode-guard.py — goal-mode 专属守卫（2026-08-14 拆分方案 A 自动生成 + 强门禁合并）

设计目的:
  每个 skill 在 scripts/<name>-guard.py 自带守卫（项目侧，非 skill 子目录）。
  合并以下 aspect 的检查结果: structure, state, gate
  其中 state / gate 为 goal-mode v2.0 强门禁不变量（见 goal-mode SKILL.md）：

  a) state/completion_candidate.yaml 的 status 状态合法性
     (in_progress / candidate_complete / complete / blocked)
  b) 检测 Agent 非法写 complete（state 为 complete 但 gate/verify-goal.py 不存在，
     或缺少 verdict 字段）—— 只有外部验证器 verify-goal.py 才能写 complete
  c) gate/verify-goal.py 完整性（含 sys.exit 调用）
  d) gate/acceptance_manifest.yaml 完整性（含 goal + checks 字段）

用法:
  python scripts/goal-mode-guard.py goal-mode

退出码:
  0 = PASS（errors=0, warnings=0）
  1 = BLOCK（errors≥1）
  2 = WARN（errors=0 但 warnings≥1）

禁止:
  - 禁止 import skill-markets/<pkg>/scripts/*（与 AGENTS.md §1.11 冲突）
  - 禁止修改本文件的 import 顺序（与 _guard_lib 契约不一致会导致 guard-router 失败）
"""
import importlib.util
import sys
import json
from pathlib import Path

_SCRIPTS_DIR = Path(__file__).resolve().parent

try:
    import yaml
except ImportError:
    yaml = None


def _load_sibling_module(filename: str):
    """加载同目录下的连字符文件名模块（Python import 不支持 hyphen 文件名）."""
    spec = importlib.util.spec_from_file_location(
        filename.replace('.py', ''),
        _SCRIPTS_DIR / filename
    )
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


# 共享守卫加载（连字符文件名用 importlib）
_module_structure = _load_sibling_module("skill-structure-guard.py")
check_structure_fn = getattr(_module_structure, "check_structure_for_skill")


def _merge_results(results: list) -> dict:
    """合并多个 {passed, errors, warnings, info} 结果，去重并保持顺序."""
    merged = {'passed': True, 'errors': [], 'warnings': [], 'info': []}
    for r in results:
        if not r.get('passed', False):
            merged['passed'] = False
        merged['errors'].extend(r.get('errors') or [])
        merged['warnings'].extend(r.get('warnings') or [])
        merged['info'].extend(r.get('info') or [])
    seen = set()
    for key in ('errors', 'warnings', 'info'):
        deduped = []
        for item in merged[key]:
            if item not in seen:
                deduped.append(item)
                seen.add(item)
        merged[key] = deduped
    return merged


def check_state_file_aspect(skill_dir: Path) -> dict:
    """强门禁不变量 a) + b) — 检查 state/completion_candidate.yaml."""
    result = {'passed': True, 'errors': [], 'warnings': [], 'info': []}
    state_file = skill_dir / "state" / "completion_candidate.yaml"

    if not state_file.exists():
        result['info'].append("state/completion_candidate.yaml 不存在，跳过检查")
        return result

    try:
        if yaml:
            content = yaml.safe_load(state_file.read_text(encoding="utf-8"))
        else:
            content = json.loads(state_file.read_text(encoding="utf-8"))
    except Exception as e:
        result['passed'] = False
        result['errors'].append(f"解析 state/completion_candidate.yaml 失败: {e}")
        return result

    status = content.get("status", "unknown")

    # b) 检测 Agent 非法写 complete
    if status == "complete":
        verify_script = skill_dir / "gate" / "verify-goal.py"
        if not verify_script.exists():
            result['passed'] = False
            result['errors'].append("❌ 违规: state 为 complete 但 gate/verify-goal.py 不存在")
            result['errors'].append("   只有验证器可以写 complete，Agent 不能自己写")
        else:
            verdict = content.get("verdict", {})
            if not verdict:
                result['warnings'].append("⚠️ state 为 complete 但缺少 verdict 字段")

    # a) 状态合法性
    if status not in ["in_progress", "candidate_complete", "complete", "blocked"]:
        result['warnings'].append(f"⚠️ state 包含未知状态: {status}")

    return result


def check_gate_integrity_aspect(skill_dir: Path) -> dict:
    """强门禁不变量 c) + d) — 检查 gate/ 目录完整性."""
    result = {'passed': True, 'errors': [], 'warnings': [], 'info': []}
    gate_dir = skill_dir / "gate"

    if not gate_dir.exists():
        result['info'].append("gate/ 目录不存在，跳过完整性检查")
        return result

    # c) gateway verify-goal.py 完整性
    verify_script = gate_dir / "verify-goal.py"
    if verify_script.exists():
        content = verify_script.read_text(encoding="utf-8")
        if "import sys" not in content or "sys.exit" not in content:
            result['warnings'].append("⚠️ gate/verify-goal.py 缺少 sys.exit 调用")
    else:
        result['info'].append("gate/verify-goal.py 不存在，跳过验证器完整性检查")

    # d) acceptance_manifest.yaml 完整性
    manifest = gate_dir / "acceptance_manifest.yaml"
    if manifest.exists():
        try:
            if yaml:
                data = yaml.safe_load(manifest.read_text(encoding="utf-8"))
            else:
                data = json.loads(manifest.read_text(encoding="utf-8"))
            if "goal" not in data:
                result['warnings'].append("⚠️ gate/acceptance_manifest.yaml 缺少 goal 字段")
            if "checks" not in data:
                result['warnings'].append("⚠️ gate/acceptance_manifest.yaml 缺少 checks 字段")
        except Exception as e:
            result['warnings'].append(f"⚠️ gate/acceptance_manifest.yaml 解析失败: {e}")
    else:
        result['info'].append("gate/acceptance_manifest.yaml 不存在，跳过验收清单检查")

    return result


def check_goal_mode(skill_path: str) -> dict:
    """goal-mode 专属守卫 — 组合 3 个 aspect 的检查结果.

    Aspects: structure, state, gate
    """
    skill_dir = Path(skill_path)
    results = [
        check_structure_fn(skill_path),
        check_state_file_aspect(skill_dir),
        check_gate_integrity_aspect(skill_dir),
    ]
    return _merge_results(results)


# 主入口 — 统一通过 _guard_lib 输出 JSON + exit code
from _guard_lib import cli_main

if __name__ == '__main__':
    sys.exit(cli_main(check_goal_mode, 'structure'))
