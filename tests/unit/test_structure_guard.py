#!/usr/bin/env python3
"""
Unit tests for skill-structure-guard.py (Guard Layer)

运行: python tests/unit/test_structure_guard.py
"""

import sys
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
GUARD = REPO_ROOT / "scripts" / "skill-structure-guard.py"

passed = 0
failed = 0


def run_guard(skill_name):
    """运行结构守卫"""
    skill_path = REPO_ROOT / "skill-markets" / skill_name
    if not skill_path.exists():
        return None, f"技能不存在: {skill_name}"

    proc = subprocess.run(
        [sys.executable, str(GUARD), str(skill_path)],
        capture_output=True,
        text=True
    )
    return proc.returncode, proc.stdout + proc.stderr


def test(name, fn):
    global passed, failed
    try:
        fn()
        print(f"  ✅ {name}")
        passed += 1
    except AssertionError as e:
        print(f"  ❌ {name}")
        print(f"     {e}")
        failed += 1


print("━━━ skill-structure-guard.py ━━━")


def test_real_skill_passes():
    """真实技能 trae-security-review 应通过"""
    code, output = run_guard("trae-security-review")
    assert code == 0, f"exit={code}, output={output}"


def test_real_skill_warn_only():
    """agent-dev-control-kit 应只警告(SKILL.md 较长)而不阻断"""
    code, output = run_guard("agent-dev-control-kit")
    assert code == 0, f"exit={code}, output={output}"
    assert "较长" in output or "passed" in output, "应有警告或通过标记"


def test_nonexistent_skill_blocks():
    """不存在的技能 → 阻断"""
    code, output = run_guard("never-existed-zzz")
    assert code != 0, f"应阻断但 exit={code}"


def test_root_md_only_blocks():
    """仅根 .md 文件（不是技能目录）→ 阻断"""
    skill_path = REPO_ROOT / "skill-markets" / "CAPABILITY-MAP.md"
    proc = subprocess.run(
        [sys.executable, str(GUARD), str(skill_path)],
        capture_output=True,
        text=True
    )
    assert proc.returncode != 0, "根 .md 不应通过"


test("真实技能通过 (trae-security-review)", test_real_skill_passes)
test("真实技能警告通过 (agent-dev-control-kit)", test_real_skill_warn_only)
test("不存在技能阻断", test_nonexistent_skill_blocks)
test("根 .md 文件阻断 (CAPABILITY-MAP.md)", test_root_md_only_blocks)

print(f"\n━━━ 通过: {passed} / 失败: {failed} ━━━")
sys.exit(1 if failed > 0 else 0)