"""v11-doc-sync.py 反例单元测试(V11.7.0+)

每个用例对应 4 维度:
  - L1 light 模式: 给长文库插 1 行入口标记 + 幂等
  - L2 full 模式: stage SKILL.md 完整入口块 + frontmatter scripts 同步
  - L3 白名单: templates/* + skills/00-boot/* + 工具自身 + CHANGELOG.md 跳过
  - L4 --check 模式: CI gate 校验, missing 数 = 0 → PASS / > 0 → NEEDS_REVIEW

覆盖 V11 门禁自验收铁律(§4):
  - sync 后再 sync = 全 skip(幂等)
  - check missing = 0 / > 0 边界
  - 白名单不被污染
  - stage SKILL.md frontmatter scripts 同步正确
"""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pytest

pytestmark = pytest.mark.unit


# ----------------------------------------------------------------------
# Helper — 动态装载 v11-doc-sync.py(文件名含连字符)
# ----------------------------------------------------------------------
def _load_v11_doc_sync():
    """动态加载 v11-doc-sync.py(文件名含连字符, importlib)."""
    skill_root = Path(__file__).resolve().parent.parent.parent
    path = skill_root / "scripts" / "v11-doc-sync.py"
    spec = importlib.util.spec_from_file_location("v11_doc_sync", path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["v11_doc_sync"] = mod
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def v11_doc_sync():
    return _load_v11_doc_sync()


# ----------------------------------------------------------------------
# TestLightMode — L4 长文库极简 1 行入口标记
# ----------------------------------------------------------------------
class TestLightMode:
    """L4 长文库模式: 给 # 标题后插 1 行入口标记. 幂等."""

    def test_insert_after_heading(self, tmp_path: Path, v11_doc_sync):
        p = tmp_path / "doc.md"
        p.write_text("# Title\n\ncontent", encoding="utf-8")
        status, msg = v11_doc_sync.inject_light(p, v11_doc_sync.DEFAULT_MARK)
        assert status == "ok"
        text = p.read_text(encoding="utf-8")
        # 标记应在 # Title 之后, content 之前
        lines = text.splitlines()
        assert lines[0] == "# Title"
        assert "V11.7.0+ 设计入口" in lines[2]
        assert "content" in lines[-1]

    def test_idempotent(self, tmp_path: Path, v11_doc_sync):
        p = tmp_path / "doc.md"
        p.write_text("# Title\n\ncontent", encoding="utf-8")
        v11_doc_sync.inject_light(p, v11_doc_sync.DEFAULT_MARK)
        first = p.read_text(encoding="utf-8")
        v11_doc_sync.inject_light(p, v11_doc_sync.DEFAULT_MARK)
        second = p.read_text(encoding="utf-8")
        # 二次跑应 skip,文本不变
        assert first == second

    def test_skip_when_already_has_marker(self, tmp_path: Path, v11_doc_sync):
        p = tmp_path / "doc.md"
        p.write_text("# Title\n\n> **V11.7.0+ 设计入口**: ...", encoding="utf-8")
        status, msg = v11_doc_sync.inject_light(p, v11_doc_sync.DEFAULT_MARK)
        assert status == "skip"

    def test_skip_when_has_jarvis_keyword(self, tmp_path: Path, v11_doc_sync):
        """已含 '贾维斯' 关键字视为已同步(手动改的入口块也认)。"""
        p = tmp_path / "doc.md"
        p.write_text("# Title\n\n> 贾维斯门禁守护", encoding="utf-8")
        status, msg = v11_doc_sync.inject_light(p, v11_doc_sync.DEFAULT_MARK)
        assert status == "skip"

    def test_skip_when_no_heading(self, tmp_path: Path, v11_doc_sync):
        """无 # 标题也接受(从文件开头插)。"""
        p = tmp_path / "doc.md"
        p.write_text("just content", encoding="utf-8")
        status, msg = v11_doc_sync.inject_light(p, v11_doc_sync.DEFAULT_MARK)
        assert status == "ok"
        assert "V11.7.0+" in p.read_text(encoding="utf-8")


# ----------------------------------------------------------------------
# TestFullMode — L2 stage SKILL.md 完整入口块 + frontmatter 同步
# ----------------------------------------------------------------------
class TestFullMode:
    """L2 stage SKILL.md 模式: 完整入口块 + scripts 列表同步."""

    def _build_stage_skill(self, tmp_path: Path, v11_root: Path) -> Path:
        skill_dir = v11_root / "skills" / "03-test-plan"
        skill_dir.mkdir(parents=True, exist_ok=True)
        p = skill_dir / "SKILL.md"
        p.write_text(
            "---\n"
            "name: fullstack-03-test-plan\n"
            "stage: 0.5\n"
            "scripts:\n"
            "  - ../../scripts/stage-gate.py\n"
            "references:\n"
            "  - ../../references/common-iron-rules.md\n"
            "---\n"
            "\n"
            "# Stage 0.5 Test Plan\n"
            "\n"
            "old content\n",
            encoding="utf-8",
        )
        return p

    def test_insert_full_entry_and_scripts(self, tmp_path: Path, v11_doc_sync):
        v11_root = tmp_path / "v11"
        v11_root.mkdir()
        p = self._build_stage_skill(tmp_path, v11_root)
        status, msg = v11_doc_sync.inject_full_entry(p, v11_root)
        assert status == "ok"

        text = p.read_text(encoding="utf-8")
        # 入口块存在
        assert "V11.7.0+ 设计入口" in text
        assert "AC 核销门禁" in text
        assert "贾维斯门禁守护" in text
        # frontmatter scripts 同步
        assert "gate-integrity-guard.py" in text
        # references 同步
        assert "gate-configuration-protocol.md" in text

    def test_idempotent_full(self, tmp_path: Path, v11_doc_sync):
        v11_root = tmp_path / "v11"
        v11_root.mkdir()
        p = self._build_stage_skill(tmp_path, v11_root)
        v11_doc_sync.inject_full_entry(p, v11_root)
        first = p.read_text(encoding="utf-8")
        v11_doc_sync.inject_full_entry(p, v11_root)
        second = p.read_text(encoding="utf-8")
        assert first == second

    def test_skip_when_no_frontmatter(self, tmp_path: Path, v11_doc_sync):
        v11_root = tmp_path / "v11"
        v11_root.mkdir()
        skill_dir = v11_root / "skills" / "03-test-plan"
        skill_dir.mkdir(parents=True, exist_ok=True)
        p = skill_dir / "SKILL.md"
        p.write_text("# no frontmatter", encoding="utf-8")
        status, msg = v11_doc_sync.inject_full_entry(p, v11_root)
        assert status == "fail"
        assert "frontmatter" in msg


# ----------------------------------------------------------------------
# TestWhitelist — L5 白名单路径不动
# ----------------------------------------------------------------------
class TestWhitelist:
    """白名单(templates/ + skills/00-boot/ + 工具自身 + CHANGELOG.md)完全跳过."""

    def test_should_skip_templates(self, v11_doc_sync):
        assert v11_doc_sync.should_skip("templates/checklist-template.md")
        assert v11_doc_sync.should_skip("templates/constitution-template.md")

    def test_should_skip_00boot(self, v11_doc_sync):
        assert v11_doc_sync.should_skip("skills/00-boot/SKILL.md")
        assert v11_doc_sync.should_skip("skills/00-boot/agents/jarvis.md")

    def test_should_skip_tool_itself(self, v11_doc_sync):
        assert v11_doc_sync.should_skip("scripts/v11-doc-sync.py")

    def test_should_skip_changelog(self, v11_doc_sync):
        assert v11_doc_sync.should_skip("CHANGELOG.md")

    def test_should_not_skip_normal(self, v11_doc_sync):
        assert not v11_doc_sync.should_skip("skills/03-test-plan/SKILL.md")
        assert not v11_doc_sync.should_skip("references/constitution.md")


# ----------------------------------------------------------------------
# TestCheckMode — --check CI gate
# ----------------------------------------------------------------------
class TestCheckMode:
    """--check 模式: missing 数 = 0 → PASS / > 0 → NEEDS_REVIEW."""

    def test_check_passes_when_all_marked(self, tmp_path: Path, v11_doc_sync):
        """全部含标记 → check 应 PASS."""
        v11_root = tmp_path / "v11"
        v11_root.mkdir()
        (v11_root / "references").mkdir()
        (v11_root / "references" / "doc1.md").write_text(
            "# D\n\n> **V11.7.0+ 设计入口**: x", encoding="utf-8"
        )

        # 模拟 cmd_check 逻辑
        missing = []
        for path in sorted(v11_root.rglob("*.md")):
            rel = str(path.relative_to(v11_root)).replace("\\", "/")
            if v11_doc_sync.should_skip(rel):
                continue
            text = path.read_text(encoding="utf-8")
            if not v11_doc_sync._has_marker(text, v11_doc_sync.DEFAULT_MARK):
                missing.append(rel)
        assert missing == []

    def test_check_flags_unmarked(self, tmp_path: Path, v11_doc_sync):
        """有未含标记文档 → check 应列入 missing."""
        v11_root = tmp_path / "v11"
        v11_root.mkdir()
        (v11_root / "references").mkdir()
        (v11_root / "references" / "marked.md").write_text(
            "# D\n\n> **V11.7.0+ 设计入口**: x", encoding="utf-8"
        )
        (v11_root / "references" / "unmarked.md").write_text(
            "# D\n\nold content", encoding="utf-8"
        )

        missing = []
        for path in sorted(v11_root.rglob("*.md")):
            rel = str(path.relative_to(v11_root)).replace("\\", "/")
            if v11_doc_sync.should_skip(rel):
                continue
            text = path.read_text(encoding="utf-8")
            if not v11_doc_sync._has_marker(text, v11_doc_sync.DEFAULT_MARK):
                missing.append(rel)
        assert "references/unmarked.md" in missing
        assert "references/marked.md" not in missing

    def test_check_ignores_whitelist(self, tmp_path: Path, v11_doc_sync):
        """白名单内文档即使没标记,check 也不报 missing."""
        v11_root = tmp_path / "v11"
        v11_root.mkdir()
        templates = v11_root / "templates"
        templates.mkdir()
        (templates / "user-template.md").write_text("# User Template", encoding="utf-8")

        missing = []
        for path in sorted(v11_root.rglob("*.md")):
            rel = str(path.relative_to(v11_root)).replace("\\", "/")
            if v11_doc_sync.should_skip(rel):
                continue
            text = path.read_text(encoding="utf-8")
            if not v11_doc_sync._has_marker(text, v11_doc_sync.DEFAULT_MARK):
                missing.append(rel)
        assert missing == []  # user-template 在白名单,即使没标记也不报


# ----------------------------------------------------------------------
# TestMarkerKeywords — _has_marker 关键字检测
# ----------------------------------------------------------------------
class TestMarkerKeywords:
    """_has_marker 关键字检测: 6 关键字任一命中即视为已同步."""

    def test_detect_v11_7_marker(self, v11_doc_sync):
        assert v11_doc_sync._has_marker("> V11.7.0+ 设计入口", "x") is True

    def test_detect_v11_6_marker(self, v11_doc_sync):
        """手动改的 V11.6.0 条目也应被认作已同步(向后兼容)。"""
        assert v11_doc_sync._has_marker("> V11.6.0 AC 核销门禁", "x") is True

    def test_detect_jarvis_keyword(self, v11_doc_sync):
        assert v11_doc_sync._has_marker("> 贾维斯门禁守护", "x") is True

    def test_detect_gate_config_protocol_link(self, v11_doc_sync):
        assert v11_doc_sync._has_marker("详见 gate-configuration-protocol.md", "x") is True

    def test_detect_mark_prefix(self, v11_doc_sync):
        """mark[:30] 也匹配(自定义 mark 文本 — text 含 mark 前缀)。"""
        custom_mark = "> **V11.8.0+ 设计入口**: 这是新版入口"
        # 文档含 mark 前 30 字符
        text_containing_mark_prefix = "old content " + custom_mark[:30]
        assert v11_doc_sync._has_marker(text_containing_mark_prefix, custom_mark) is True

    def test_unmarked_returns_false(self, v11_doc_sync):
        assert v11_doc_sync._has_marker("# Title\n\nplain content", "x") is False