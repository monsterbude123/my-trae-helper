"""
V10.5 Self-Test Runner — 验证 rot #15-17 检测器对 fixture 应正确报 FAIL/PASS

运行:
  python scripts/__self_tests__/test_v10_5_fixtures.py

<!-- scan-whitelist:SHELL_EXEC --><!-- /scan-whitelist -->
"""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
SCRIPTS = SCRIPT_DIR.parent
PROACTIVE = SCRIPTS / "proactive-scan.py"

FIXTURES = SCRIPT_DIR  # this dir
FIXTURE_V105_AGGRANDIZING = FIXTURES / "V10.5-fixture"
FIXTURE_V105_STALENESS = FIXTURES / "V10.5-staleness-fixture"
FIXTURE_V105_STUB = FIXTURES / "V10.5-stub-fixture"


def run_check(name: str, fixture: Path, expected_status: str, expected_severity: str) -> bool:
    """运行 proactive-scan 的 --only check，验证结果符合预期"""
    cmd = [
        sys.executable, str(PROACTIVE),
        "--only", name,
        "--project-root", str(fixture),
        "--json",
    ]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=30, cwd=str(SCRIPTS))
    try:
        import json
        data = json.loads(r.stdout)
    except (json.JSONDecodeError, KeyError) as e:
        print(f"  ❌ {name}: 无法解析 JSON 输出 ({e})")
        print(f"     stdout: {r.stdout[:200]}")
        return False
    fail_count = data.get("fail_count", 0)
    results = data.get("results", [])
    actual = results[0] if results else {}
    actual_status = actual.get("status", "?")
    actual_severity = actual.get("severity", "?")
    ok = actual_status == expected_status and actual_severity == expected_severity
    icon = "✅" if ok else "❌"
    print(f"  {icon} {name} (fixture={fixture.name}): expected={expected_status}/{expected_severity} actual={actual_status}/{actual_severity} evidence={actual.get('evidence', '')[:80]}")
    return ok


def main() -> int:
    print("=" * 70)
    print("V10.5 Self-Test Runner — 验证 rot #15-17 检测器")
    print("=" * 70)

    # staleness fixture 需先 set mtime 到 96h 前
    sc = FIXTURE_V105_STALENESS / "docs" / "specs" / ".state-card.md"
    if sc.exists():
        old_mtime = (os.path.getmtime(sc) - 96 * 3600)
        os.utime(sc, (old_mtime, old_mtime))
        print(f"set {sc} mtime to 96h ago")

    passed = 0
    failed = 0
    tests = [
        # (check name, fixture, expected status, expected severity)
        ("self-aggrandizing-doc", FIXTURE_V105_AGGRANDIZING, "fail", "FAIL"),
        ("state-card-staleness", FIXTURE_V105_STALENESS, "fail", "FAIL"),
        ("stub-pileup", FIXTURE_V105_STUB, "fail", "FAIL"),
    ]
    for name, fix, exp_status, exp_sev in tests:
        if not fix.is_dir():
            print(f"  ⏭️ {name}: fixture 不存在 {fix} (跳过)")
            continue
        if run_check(name, fix, exp_status, exp_sev):
            passed += 1
        else:
            failed += 1
    print()
    print(f"通过: {passed} / {passed + failed}")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
