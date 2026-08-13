#!/usr/bin/env python3
"""
Unit tests for skill-security-guard.py (Guard Layer)

运行: python tests/unit/test_security_guard.py
"""

import sys
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
GUARD = REPO_ROOT / "scripts" / "skill-security-guard.py"

passed = 0
failed = 0


def run_guard(skill_name):
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


print("━━━ skill-security-guard.py ━━━")


def test_real_skill_passes():
    """真实安全技能应通过"""
    code, output = run_guard("coding-xinfa")
    assert code == 0, f"exit={code}, output={output}"


def test_agent_dev_control_passes():
    """agent-dev-control-kit 含 scaffold 示例代码, 整体应通过 (scaffold 文件含 HARDCODED_SECRET示例但为文档引用)"""
    code, output = run_guard("agent-dev-control-kit")
    # 允许 PASS 或 WARN(真风险需文档豁免),但不应 BLOCK
    assert code in (0, 2), f"应 PASS/WARN 但 exit={code}, output={output}"


def test_nonexistent_skill():
    """不存在的技能路径"""
    proc = subprocess.run(
        [sys.executable, str(GUARD), str(REPO_ROOT / "skill-markets" / "never-existed-zzz")],
        capture_output=True,
        text=True
    )
    assert proc.returncode != 0, "应阻断"


def test_real_risk_detected():
    """真实 HIGH 风险代码应被 BLOCK"""
    import tempfile
    with tempfile.TemporaryDirectory() as tmp:
        # 创建一个含真实硬编码密钥的 .py 文件
        risky_file = Path(tmp) / "risky.py"
        risky_file.write_text('api_key = "sk-real-secret-key-12345678"\n')

        proc = subprocess.run(
            [sys.executable, str(GUARD), tmp],
            capture_output=True,
            text=True
        )
        assert proc.returncode == 1, f"应 BLOCK 但 exit={proc.returncode}, output={proc.stdout}"
        assert "BLOCK" in proc.stdout or "BLOCK" in proc.stderr


test("真实安全技能通过 (coding-xinfa)", test_real_skill_passes)
test("agent-dev-control-kit 应 PASS/WARN", test_agent_dev_control_passes)
test("不存在技能阻断", test_nonexistent_skill)
test("真实风险代码 BLOCK", test_real_risk_detected)

print(f"\n━━━ 通过: {passed} / 失败: {failed} ━━━")
sys.exit(1 if failed > 0 else 0)