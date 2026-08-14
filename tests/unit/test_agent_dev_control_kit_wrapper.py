"""
test_agent_dev_control_kit_wrapper.py — 自验收 scripts/run-agent-dev-control-kit-tests.py

对应 §2.4 反例自验收强制:
  - PASS 态:现状 catalog + scripts 完整 → 期望 exit 0
  - FAIL 态:故意破坏 catalog → 期望 exit 1
  - 边界态:logs/agent-hints.jsonl 缺失 → 期望 exit 0

运行:python -m pytest tests/unit/test_agent_dev_control_kit_wrapper.py -v
"""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
WRAPPER = REPO_ROOT / "scripts" / "run-agent-dev-control-kit-tests.py"
TARGET_DIR = REPO_ROOT / "skill-markets" / "agent-dev-control-kit"


def _run_wrapper() -> tuple[int, str, str]:
    """跨平台跑 wrapper,返回 (returncode, stdout, stderr)。"""
    cmd = [sys.executable, str(WRAPPER)]
    proc = subprocess.run(
        cmd,
        cwd=str(REPO_ROOT),
        env=os.environ.copy(),
        capture_output=True,
        text=True,
        check=False,
        timeout=180,
    )
    return proc.returncode, proc.stdout, proc.stderr


class TestWrapperPassState:
    def test_happy_path_exits_zero(self):
        """happy-path: 现状 catalog 完整 → exit 0。"""
        rc, stdout, _ = _run_wrapper()
        assert rc == 0, f"happy-path 应 exit 0,得到 {rc}\nstdout head: {stdout[:300]!r}"
        assert "OK: agent-dev-control-kit 测试全通过" in stdout


class TestWrapperFailState:
    def test_corrupt_catalog_exits_one(self):
        """FAIL 态(§2.4 自验收):故意破坏 catalog → exit 1。"""
        catalog = TARGET_DIR / "tests" / "catalogs" / "skill-catalog.yaml"
        backup = catalog.read_text(encoding="utf-8")
        try:
            data = yaml.safe_load(backup)
            data.setdefault("required_docs", []).append(
                {
                    "path": "WRAPPER_TEST_MISSING_zzz.md",
                    "purpose": "wrapper 自验收",
                    "must_contain": ["X"],
                }
            )
            catalog.write_text(
                yaml.safe_dump(data, allow_unicode=True, sort_keys=False),
                encoding="utf-8",
            )
            rc, stdout, stderr = _run_wrapper()
            combined = stdout + stderr
            assert rc == 1, (
                f"违反 catalog 必须 exit 1,得到 {rc}\nstdout: {stdout[:200]!r}"
            )
            assert "🛑 CATALOG GUARD 阻断 commit" in combined, (
                f"必须输出 block banner\ncombined head: {combined[:300]!r}"
            )
        finally:
            catalog.write_text(backup, encoding="utf-8")


class TestWrapperBoundary:
    def test_wrapper_source_has_missing_dir_check(self):
        """wrapper 源码层:skill-dir 缺失应 exit 3。"""
        text = WRAPPER.read_text(encoding="utf-8")
        assert "return 3" in text or "exit 3" in text, (
            "wrapper 缺 missing-dir 检查(应 return 3 或 sys.exit(3))"
        )

    def test_no_hints_log_still_exits_zero(self):
        """logs/agent-hints.jsonl 缺失 → 仍 exit 0。"""
        hint_log = TARGET_DIR / "logs" / "agent-hints.jsonl"
        backup = hint_log.read_bytes() if hint_log.exists() else None
        try:
            if backup is not None:
                hint_log.unlink()
            rc, _, _ = _run_wrapper()
            assert rc == 0, f"无 hints log 仍应 exit 0,得到 {rc}"
        finally:
            if backup is not None:
                hint_log.write_bytes(backup)


class TestWrapperScriptExists:
    def test_wrapper_file_exists(self):
        assert WRAPPER.is_file(), f"缺失 wrapper: {WRAPPER}"

    def test_wrapper_is_python_script(self):
        head = WRAPPER.read_text(encoding="utf-8")[:32]
        assert head.startswith("#!/usr/bin/env python") or head.startswith(
            "#!/usr/bin/python"
        ), "wrapper 必须是 Python 脚本"

    def test_wrapper_uses_skill_root_path(self):
        text = WRAPPER.read_text(encoding="utf-8")
        # 路径通过 Path 拼接(REPO_ROOT / "skill-markets" / "agent-dev-control-kit")
        assert "agent-dev-control-kit" in text, "wrapper 路径错误"
        assert "REPO_ROOT" in text, "wrapper 缺 REPO_ROOT 锚点"

    def test_wrapper_uses_sys_executable(self):
        """§1.7 跨平台:wrapper 必须用 sys.executable 找 python。"""
        text = WRAPPER.read_text(encoding="utf-8")
        assert "sys.executable" in text, "wrapper 应用 sys.executable(§1.7 跨平台)"
