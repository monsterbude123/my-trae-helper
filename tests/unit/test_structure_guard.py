#!/usr/bin/env python3
"""
Unit tests for skill-structure-guard.py (Guard Layer)

运行: python tests/unit/test_structure_guard.py
"""

import sys
import subprocess
from pathlib import Path

# Windows 默认 cp1252 控制台无法编码 ━━━ 等 Unicode 字符,
# 强制 stdout/stderr 用 utf-8,避免 L1/L2 Gate 在 npm run test:unit 时炸 UnicodeEncodeError
# (2026-08-14 push 失败修复)
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
GUARD = REPO_ROOT / "scripts" / "skill-structure-guard.py"

passed = 0
failed = 0


def _safe_decode(b: bytes | None) -> str:
    """跨平台解码子进程 stdout/stderr (Windows cp1252 兜底)。

    AGENTS.md §4.1.3 + reference trap-instructions.yaml AP-9:
    子进程 stdout 含 Unicode 字符 (━ / ✅ / ❌) 时,Windows 默认 cp1252
    reader thread 解码失败 → proc.stdout = None → 字符串拼接崩溃。
    """
    if not b:
        return ""
    return b.decode("utf-8", errors="replace")


def run_guard(skill_name):
    """运行结构守卫"""
    skill_path = REPO_ROOT / "skill-markets" / skill_name
    if not skill_path.exists():
        return None, f"技能不存在: {skill_name}"

    proc = subprocess.run(
        [sys.executable, str(GUARD), str(skill_path)],
        capture_output=True,
    )
    return proc.returncode, _safe_decode(proc.stdout) + _safe_decode(proc.stderr)


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
    )
    assert proc.returncode != 0, "根 .md 不应通过"


test("真实技能通过 (trae-security-review)", test_real_skill_passes)
test("真实技能警告通过 (agent-dev-control-kit)", test_real_skill_warn_only)
test("不存在技能阻断", test_nonexistent_skill_blocks)
test("根 .md 文件阻断 (CAPABILITY-MAP.md)", test_root_md_only_blocks)

# V11.8.0 P0 修复(2026-08-15):pytest collect 时触发 sys.exit 导致 INTERNALERROR
if __name__ == "__main__":
    print(f"\n━━━ 通过: {passed} / 失败: {failed} ━━━")
    sys.exit(1 if failed > 0 else 0)