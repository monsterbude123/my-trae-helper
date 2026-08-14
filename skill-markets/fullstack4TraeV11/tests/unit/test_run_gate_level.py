"""run-gate-level.py 双栈（nodejs/python）支持 + 反例固化测试

覆盖 dimensions:
  - detect_project_type: nodejs / python / unknown 三态
  - run_python_check: 未知 check / 工具缺失 / 真实执行 三态
  - nodejs echo-skip 反例（AP-2 关联）
"""
from __future__ import annotations

from pathlib import Path

import pytest

pytestmark = pytest.mark.unit


# ============================================================================
# TestDetectProjectType
# ============================================================================
class TestDetectProjectType:
    def test_nodejs(self, run_gate_level, tmp_path):
        (tmp_path / "package.json").write_text("{}", encoding="utf-8")
        assert run_gate_level.detect_project_type(tmp_path) == "nodejs"

    def test_python_pyproject(self, run_gate_level, tmp_path):
        (tmp_path / "pyproject.toml").write_text("[project]\n", encoding="utf-8")
        assert run_gate_level.detect_project_type(tmp_path) == "python"

    def test_python_requirements(self, run_gate_level, tmp_path):
        (tmp_path / "requirements.txt").write_text("requests\n", encoding="utf-8")
        assert run_gate_level.detect_project_type(tmp_path) == "python"

    def test_unknown(self, run_gate_level, tmp_path):
        assert run_gate_level.detect_project_type(tmp_path) == "unknown"


# ============================================================================
# TestRunPythonCheck
# ============================================================================
class TestRunPythonCheck:
    @pytest.mark.trap
    def test_unknown_check_fails(self, run_gate_level, tmp_path):
        """未知 python check 名 → FAIL（不静默跳过）。"""
        assert run_gate_level.run_python_check(tmp_path, "no-such-check", 60) == "FAIL"

    @pytest.mark.trap
    def test_missing_tool_fails(self, run_gate_level, tmp_path):
        """工具缺失 → FAIL（不静默跳过）。"""
        # 用不存在的工具名映射
        run_gate_level.PY_CHECK_COMMANDS["lint"] = ["totally-nonexistent-tool-xyz", "check", "."]
        assert run_gate_level.run_python_check(tmp_path, "lint", 60) == "FAIL"

    @pytest.mark.trap
    def test_echo_skip_placeholder_not_applicable(self, run_gate_level):
        """python 路径不消费 package.json 的 echo-skip（nodejs 专属）。"""
        # 确认 python 检查命令映射不含 npm 语义依赖
        assert "echo" not in str(run_gate_level.PY_CHECK_COMMANDS)


# ============================================================================
# TestNodejsEchoSkip — AP-2 反例关联
# ============================================================================
class TestNodejsEchoSkip:
    def test_echo_skip_detected(self, run_gate_level):
        assert run_gate_level.is_echo_skip('echo "skipping lint"') is True
        assert run_gate_level.is_echo_skip("echo skip") is True

    def test_real_script_not_flagged(self, run_gate_level):
        assert run_gate_level.is_echo_skip("ruff check .") is False
        assert run_gate_level.is_echo_skip("pytest -q") is False