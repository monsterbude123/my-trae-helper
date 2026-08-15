"""_check_protocol_coverage.py 反例单元测试(2026-08-15 NEW)

每个用例对应 .agents/skills/project-rule-skill/references/skill-creation-workflow.md §2.2 多维度同步约束(V11.8.0.1 路径迁移)的反例固化:
  - PASS 路径:已引用的规则
  - FAIL 路径:未引用的协议
  - 边界:--scope package vs global 区分
  - 工具错误:协议文件不存在

覆盖 dimensions:
  - G1 protocol-scope-detection: --scope {package,global}
  - G2 file-references-protocol: 文件名 / 全路径 / stem 三种引用形式
  - G3 dimension-collect: 6 维度(包) / 1 维度(全局)
  - G4 cli-flow: 真实 skill-creation-workflow.md 的引用情况
"""
from __future__ import annotations

import importlib.util
import pathlib
import sys

import pytest

# ----------------------------------------------------------------------
# Helper — 动态装载 _check_protocol_coverage.py
# ----------------------------------------------------------------------
def _load_module():
    """动态加载 _check_protocol_coverage.py(文件名带 _ 前缀,importlib)"""
    project_root = pathlib.Path(__file__).resolve().parent.parent.parent
    path = project_root / "scripts" / "_check_protocol_coverage.py"
    spec = importlib.util.spec_from_file_location("check_protocol_coverage", path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["check_protocol_coverage"] = mod
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def cov():
    return _load_module()


# ----------------------------------------------------------------------
# TestFileReferencesProtocol — G2 文件引用检测
# ----------------------------------------------------------------------
class TestFileReferencesProtocol:
    """G2: 检测文件是否引用协议 — 3 种引用形式"""

    def test_filename_reference(self, tmp_path: Path, cov):
        protocol = tmp_path / "my-protocol.md"
        protocol.write_text("# Protocol")
        ref_file = tmp_path / "ref.md"
        ref_file.write_text("See my-protocol.md for details")
        assert cov.file_references_protocol(ref_file, protocol, tmp_path) is True

    def test_relative_path_reference(self, tmp_path: Path, cov):
        protocol = tmp_path / "my-protocol.md"
        protocol.write_text("# Protocol")
        ref_file = tmp_path / "ref.md"
        ref_file.write_text("See references/my-protocol.md for details")
        assert cov.file_references_protocol(ref_file, protocol, tmp_path) is True

    def test_stem_reference(self, tmp_path: Path, cov):
        protocol = tmp_path / "my-protocol.md"
        protocol.write_text("# Protocol")
        ref_file = tmp_path / "ref.md"
        ref_file.write_text("详见 my-protocol 这个文档")
        assert cov.file_references_protocol(ref_file, protocol, tmp_path) is True

    def test_no_reference(self, tmp_path: Path, cov):
        protocol = tmp_path / "my-protocol.md"
        protocol.write_text("# Protocol")
        ref_file = tmp_path / "ref.md"
        ref_file.write_text("没有任何引用")
        assert cov.file_references_protocol(ref_file, protocol, tmp_path) is False

    def test_nonexistent_file(self, tmp_path: Path, cov):
        protocol = tmp_path / "my-protocol.md"
        protocol.write_text("# Protocol")
        ref_file = tmp_path / "missing.md"  # 不存在
        assert cov.file_references_protocol(ref_file, protocol, tmp_path) is False


# ----------------------------------------------------------------------
# TestDimensions — G3 维度收集
# ----------------------------------------------------------------------
class TestDimensions:
    """G3: 维度集合 — package(6 维度) vs global(1 维度)"""

    def test_package_dimensions_count(self, cov):
        assert len(cov.PACKAGE_DIMENSIONS) == 6
        assert "SKILL.md" in cov.PACKAGE_DIMENSIONS
        assert "reference" in cov.PACKAGE_DIMENSIONS
        assert "workflow" in cov.PACKAGE_DIMENSIONS
        assert "script" in cov.PACKAGE_DIMENSIONS
        assert "guard" in cov.PACKAGE_DIMENSIONS
        assert "other-refs" in cov.PACKAGE_DIMENSIONS

    def test_global_dimensions_count(self, cov):
        assert len(cov.GLOBAL_DIMENSIONS) == 1
        assert "other-refs" in cov.GLOBAL_DIMENSIONS


# ----------------------------------------------------------------------
# TestScopeDetection — G1 scope 区分
# ----------------------------------------------------------------------
class TestScopeDetection:
    """G1: --scope {package,global} 决定维度集"""

    def test_parse_args_default_scope(self, cov):
        """不传 --scope 时,默认 package"""
        # 用 monkeypatch 模拟 sys.argv
        old_argv = sys.argv
        try:
            sys.argv = ["cov.py", "--protocol", "/tmp/x.md"]
            args = cov.parse_args()
            assert args.scope == "package"
        finally:
            sys.argv = old_argv

    def test_parse_args_global_scope(self, cov):
        old_argv = sys.argv
        try:
            sys.argv = ["cov.py", "--protocol", "/tmp/x.md", "--scope", "global"]
            args = cov.parse_args()
            assert args.scope == "global"
        finally:
            sys.argv = old_argv


# ----------------------------------------------------------------------
# TestRealProject — G4 真实项目验证
# ----------------------------------------------------------------------
class TestRealProject:
    """G4: 用真实 my-trae-helper 项目验证 — skill-creation-workflow.md 已同步"""

    def test_skill_creation_workflow_referenced(self, cov):
        """skill-creation-workflow.md 应被多处引用(项目级规则)"""
        project_root = pathlib.Path(__file__).resolve().parent.parent.parent
        protocol = project_root / ".agents" / "rules" / "skill-creation-workflow.md"
        if not protocol.exists():
            pytest.skip("skill-creation-workflow.md 不存在(可能未创建)")

        # 收集 global scope 的 other-refs 维度
        results = []
        for pattern in cov.GLOBAL_DIMENSIONS["other-refs"]:
            results.extend(cov.collect_dimension_files(project_root, pattern))

        # 应至少 3 个引用
        refs = [f for f in results if cov.file_references_protocol(f, protocol, project_root)]
        assert len(refs) >= 3, f"项目级规则应被 ≥3 处引用,实际 {len(refs)}: {[str(f) for f in refs]}"

    def test_scope_global_passes_for_project_rule(self, cov):
        """--scope global 对项目级规则应 PASS"""
        project_root = pathlib.Path(__file__).resolve().parent.parent.parent
        protocol = project_root / ".agents" / "rules" / "skill-creation-workflow.md"
        if not protocol.exists():
            pytest.skip("skill-creation-workflow.md 不存在(可能未创建)")

        # 一次性收集所有 global pattern 的文件,验证至少 1 个引用
        all_files = cov.collect_dimension_files(project_root, cov.GLOBAL_DIMENSIONS["other-refs"])
        refs = [f for f in all_files if cov.file_references_protocol(f, protocol, project_root)]
        assert len(refs) >= 3, f"项目级规则应被 ≥3 处引用,实际 {len(refs)}: {[str(f) for f in refs]}"


# ----------------------------------------------------------------------
# TestMainCli — main() 集成
# ----------------------------------------------------------------------
class TestMainCli:
    """main() 集成测试 — PASS / FAIL / 边界"""

    def test_global_scope_passes(self, tmp_path, cov, monkeypatch, capsys):
        """--scope global + 项目级规则 → exit 0"""
        # 创建最小项目:1 个 AGENTS.md + 1 个 rule
        rules = tmp_path / ".agents" / "rules"
        rules.mkdir(parents=True)
        (rules / "my-rule.md").write_text("# My Rule")
        (tmp_path / "AGENTS.md").write_text("References [my-rule.md](my-rule.md)")

        monkeypatch.setattr(sys, "argv", [
            "cov.py", "--protocol", str(rules / "my-rule.md"), "--scope", "global",
            "--project-root", str(tmp_path),
        ])
        rc = cov.main()
        captured = capsys.readouterr()
        assert rc == 0
        assert "PASS" in captured.out

    def test_global_scope_fails_when_unreferenced(self, tmp_path, cov, monkeypatch, capsys):
        """协议没被任何维度引用 → exit 1"""
        rules = tmp_path / ".agents" / "rules"
        rules.mkdir(parents=True)
        (rules / "lonely-rule.md").write_text("# Lonely Rule")
        # 不创建任何引用文件

        monkeypatch.setattr(sys, "argv", [
            "cov.py", "--protocol", str(rules / "lonely-rule.md"), "--scope", "global",
            "--project-root", str(tmp_path),
        ])
        rc = cov.main()
        captured = capsys.readouterr()
        assert rc == 1
        assert "缺失" in captured.out

    def test_nonexistent_protocol_exits_1(self, tmp_path, cov, monkeypatch, capsys):
        """协议文件不存在 → exit 1 + 报错"""
        monkeypatch.setattr(sys, "argv", [
            "cov.py", "--protocol", str(tmp_path / "missing.md"),
            "--project-root", str(tmp_path),
        ])
        rc = cov.main()
        captured = capsys.readouterr()
        assert rc == 1
        assert "不存在" in captured.err or "不存在" in captured.out