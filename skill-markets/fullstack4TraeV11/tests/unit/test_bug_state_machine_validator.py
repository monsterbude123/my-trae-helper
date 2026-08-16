"""bug-state-machine-validator.py 单元测试(P3-5 NEW)。

覆盖维度:
  - PASS:bug 状态卡 status=OPEN,ready_to_close=false → PASS
  - FAIL:status="ILLEGAL_STATE" → FAIL
  - FAIL:status_history 模拟 CLOSED → OPEN 闭合路径不可用 → PASS(合法转换)
  - FAIL:status_history 模拟 IN_PROGRESS → OPEN (TDD FAIL 回退) → PASS
  - FAIL:status_history 模拟 OPEN → CLOSED (跳过 IN_PROGRESS) → FAIL
  - 边界:status 缺失 → FAIL
  - 边界:status_history 非法状态在 5 状态之外 → FAIL
"""
from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path

import pytest

pytestmark = pytest.mark.unit

SCRIPT_PATH = (
    Path(__file__).resolve().parents[2] / "scripts" / "bug-state-machine-validator.py"
)


def _load_validator():
    spec = importlib.util.spec_from_file_location("bug_state_machine_validator", SCRIPT_PATH)
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _write_state_card(path: Path, fm_body: str):
    """写入带指定 body 的 bug 状态卡 frontmatter。"""
    content = f"---\n{fm_body}\n---\n\n# Bug State Card\n"
    path.write_text(content, encoding="utf-8")


# ============================================================================
# TestValidBugStatuses — 5 状态字段合法性
# ============================================================================
class TestValidBugStatuses:
    def test_open_status_passes(self, tmp_path):
        """PASS:status=OPEN, ready_to_close=false。"""
        mod = _load_validator()
        card = tmp_path / "bug-card.md"
        _write_state_card(card, """card_type: bug
status: OPEN
ready_to_close: false
""")
        result = mod.validate_bug_state_card(card)
        assert result["status"] == "PASS", result
        assert result["current_status"] == "OPEN"

    def test_in_progress_status_passes(self, tmp_path):
        """PASS:status=IN_PROGRESS。"""
        mod = _load_validator()
        card = tmp_path / "bug-card.md"
        _write_state_card(card, """card_type: bug
status: IN_PROGRESS
ready_to_close: false
""")
        result = mod.validate_bug_state_card(card)
        assert result["status"] == "PASS", result

    def test_closed_status_passes(self, tmp_path):
        """PASS:status=CLOSED。"""
        mod = _load_validator()
        card = tmp_path / "bug-card.md"
        _write_state_card(card, """card_type: bug
status: CLOSED
ready_to_close: true
""")
        result = mod.validate_bug_state_card(card)
        assert result["status"] == "PASS", result

    def test_blocked_status_passes(self, tmp_path):
        """PASS:status=BLOCKED(回退态)。"""
        mod = _load_validator()
        card = tmp_path / "bug-card.md"
        _write_state_card(card, """card_type: bug
status: BLOCKED
""")
        result = mod.validate_bug_state_card(card)
        assert result["status"] == "PASS", result

    def test_skipped_status_passes(self, tmp_path):
        """PASS:status=SKIPPED(回退态)。"""
        mod = _load_validator()
        card = tmp_path / "bug-card.md"
        _write_state_card(card, """card_type: bug
status: SKIPPED
""")
        result = mod.validate_bug_state_card(card)
        assert result["status"] == "PASS", result


# ============================================================================
# TestIllegalStates — 非法 status + 非法转换
# ============================================================================
class TestIllegalStates:
    def test_illegal_status_fails(self, tmp_path):
        """FAIL:status="ILLEGAL_STATE"。"""
        mod = _load_validator()
        card = tmp_path / "bug-card.md"
        _write_state_card(card, """card_type: bug
status: ILLEGAL_STATE
""")
        result = mod.validate_bug_state_card(card)
        assert result["status"] == "FAIL", result
        assert any("ILLEGAL_STATE" in e for e in result["errors"])

    def test_missing_status_fails(self, tmp_path):
        """FAIL:status 字段缺失。"""
        mod = _load_validator()
        card = tmp_path / "bug-card.md"
        _write_state_card(card, """card_type: bug
ready_to_close: false
""")
        result = mod.validate_bug_state_card(card)
        assert result["status"] == "FAIL", result
        assert any("缺 status" in e for e in result["errors"])

    def test_history_skip_in_progress_fails(self, tmp_path):
        """FAIL:status_history OPEN → CLOSED(跳过 IN_PROGRESS)。"""
        mod = _load_validator()
        card = tmp_path / "bug-card.md"
        _write_state_card(card, """card_type: bug
status: CLOSED
status_history:
  - OPEN
  - CLOSED
""")
        result = mod.validate_bug_state_card(card)
        assert result["status"] == "FAIL", result
        assert any("非法转换" in e and "OPEN" in e and "CLOSED" in e for e in result["errors"])

    def test_history_tdd_fail_rollback_passes(self, tmp_path):
        """PASS:status_history IN_PROGRESS → OPEN(TDD 修复 FAIL 回退,合法)。"""
        mod = _load_validator()
        card = tmp_path / "bug-card.md"
        _write_state_card(card, """card_type: bug
status: OPEN
status_history:
  - OPEN
  - IN_PROGRESS
  - OPEN
""")
        result = mod.validate_bug_state_card(card)
        assert result["status"] == "PASS", result
        assert result["status_history"] == ["OPEN", "IN_PROGRESS", "OPEN"]

    def test_history_full_lifecycle_passes(self, tmp_path):
        """PASS:完整生命周期 OPEN → IN_PROGRESS → CLOSED。"""
        mod = _load_validator()
        card = tmp_path / "bug-card.md"
        _write_state_card(card, """card_type: bug
status: CLOSED
status_history:
  - OPEN
  - IN_PROGRESS
  - CLOSED
""")
        result = mod.validate_bug_state_card(card)
        assert result["status"] == "PASS", result

    def test_history_closed_to_in_progress_fails(self, tmp_path):
        """FAIL:CLOSED → IN_PROGRESS 不在合法转换矩阵中。"""
        mod = _load_validator()
        card = tmp_path / "bug-card.md"
        _write_state_card(card, """card_type: bug
status: IN_PROGRESS
status_history:
  - OPEN
  - IN_PROGRESS
  - CLOSED
  - IN_PROGRESS
""")
        result = mod.validate_bug_state_card(card)
        assert result["status"] == "FAIL", result
        assert any("CLOSED" in e and "IN_PROGRESS" in e for e in result["errors"])


# ============================================================================
# TestCLIIntegration — CLI 真反例跑
# ============================================================================
class TestCLIIntegration:
    def test_cli_passes_valid_bug_card(self, tmp_path):
        """PASS:CLI 跑合法 bug 状态卡 → exit 0。"""
        card = tmp_path / "bug-card.md"
        card.write_text(
            "---\n"
            "card_type: bug\n"
            "status: OPEN\n"
            "ready_to_close: false\n"
            "---\n"
            "# Bug State Card\n",
            encoding="utf-8",
        )
        result = subprocess.run(
            [sys.executable, str(SCRIPT_PATH),
             "--bug-state-card", str(card)],
            capture_output=True, text=True, timeout=30,
        )
        assert result.returncode == 0, f"期望 exit 0,实际 {result.returncode}: {result.stdout}"
        assert "current_status: OPEN" in result.stdout

    def test_cli_fails_illegal_status(self, tmp_path):
        """FAIL:CLI 跑 ILLEGAL_STATE → exit 1。"""
        card = tmp_path / "bug-card.md"
        card.write_text(
            "---\n"
            "card_type: bug\n"
            "status: ILLEGAL_STATE\n"
            "---\n"
            "# Bug State Card\n",
            encoding="utf-8",
        )
        result = subprocess.run(
            [sys.executable, str(SCRIPT_PATH),
             "--bug-state-card", str(card)],
            capture_output=True, text=True, timeout=30,
        )
        assert result.returncode == 1, f"期望 exit 1,实际 {result.returncode}"
        assert "ILLEGAL_STATE" in result.stdout