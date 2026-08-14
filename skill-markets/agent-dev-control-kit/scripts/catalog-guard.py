#!/usr/bin/env python3
"""catalog-guard.py — commit 前 catalog 覆盖测试

直接对应你的 commits hook (.husky/pre-commit 风格):
  任意 commit → 跑 catalog tests → 阻断并打印 hint

用法:
    python scripts/catalog-guard.py                  # 跑 catalog 测试
    AGENT_HINTS=0 python scripts/catalog-guard.py    # 关闭 hint 写日志

退出码:
    0 = catalog 全部通过
    1 = catalog 至少一个 fail(阻断 commit)

对应 trap 反例:
    - AP-CAT-001~005:覆盖测试自身
    - AP-11.1.1:写完 gate 必须真反例验证 §11.1.1
"""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parents[1]
CATALOG_TEST = "tests/catalogs/test_catalog_coverage.py"


def run_catalog_tests() -> int:
    """跑 catalog 覆盖测试,返回 pytest returncode。"""
    env = os.environ.copy()
    # 默认让 hint 写到日志(便于后续聚合),可用 AGENT_HINTS=0 关
    env.pop("AGENT_HINTS", None)

    cmd = [
        sys.executable,
        "-m",
        "pytest",
        CATALOG_TEST,
        "-v",
        "--tb=short",
    ]
    return subprocess.call(cmd, cwd=str(SKILL_ROOT), env=env)


def banner_fail(rc: int) -> None:
    print(
        "\n"
        "═══════════════════════════════════════════════════════════\n"
        "  🛑 CATALOG GUARD 阻断 commit\n"
        "═══════════════════════════════════════════════════════════\n"
        "  至少一个 catalog 测试 fail。\n"
        f"  pytest returncode: {rc}\n"
        "\n"
        "  🛠 agent 应当:\n"
        "    1. 读 stderr 中每条 HINT-* 的 what / where / minimal_fix\n"
        "    2. 按 next_skill 调用 Skill(name=...) 补齐\n"
        "    3. 重跑 `python scripts/catalog-guard.py` 验证\n"
        "\n"
        "  📚 详见 references/traps.md §AP-CAT-* 与 §AP-3\n"
        "═══════════════════════════════════════════════════════════\n",
        file=sys.stderr,
    )


def main() -> int:
    rc = run_catalog_tests()
    if rc != 0:
        banner_fail(rc)
        return rc
    print("✅ catalog guard passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
