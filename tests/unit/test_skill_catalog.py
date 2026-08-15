"""_check_skill_catalog.py 反例单元测试(2026-08-15 NEW)

每个用例对应 catalog-protocol.md §3 校验规则:
  - 必填校验:缺字段 FAIL
  - 可选校验:声明时跑子校验
  - 结构守卫:行数 / 字段数

覆盖:
  - C1 加载 catalog:正常 / 缺失 / 格式错
  - C2 解析 SKILL.md:正常 / 缺 frontmatter / 缺闭合
  - C3 单 SKILL 校验:PASS / FAIL(缺字段) / FAIL(行数超限)
  - C4 main() 集成:PASS / FAIL
"""
from __future__ import annotations

import importlib.util
import pathlib
import sys

import pytest


# ----------------------------------------------------------------------
# Helper — 动态装载 _check_skill_catalog.py(文件名带 _ 前缀)
# ----------------------------------------------------------------------
def _load_module():
    project_root = pathlib.Path(__file__).resolve().parent.parent.parent
    path = project_root / "tests" / "catalogs" / "_check_skill_catalog.py"
    spec = importlib.util.spec_from_file_location("check_skill_catalog", path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["check_skill_catalog"] = mod
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def cat():
    return _load_module()


# ----------------------------------------------------------------------
# TestLoadCatalog — C1 加载 catalog
# ----------------------------------------------------------------------
class TestLoadCatalog:
    """C1: catalog 加载 — 正常 / 缺失 / 错误"""

    def test_load_existing_catalog(self, cat):
        project_root = pathlib.Path(__file__).resolve().parent.parent.parent
        catalog = project_root / "tests" / "catalogs" / "skill-catalog.yaml"
        if not catalog.exists():
            pytest.skip("catalog 不存在")
        loaded = cat.load_catalog(catalog)
        assert "error" not in loaded
        # V2 升级:version 从 1.0.0 → 2.0.0
        assert loaded["version"] in ("1.0.0", "2.0.0"), f"version 应为 1.0.0/2.0.0,实为 {loaded['version']}"
        assert "name" in loaded["required_metadata"]
        # V2 校验:version 必填
        assert "version" in loaded["required_metadata"], "V2 version 应在 required_metadata"
        # V2 校验:requires 应在 recommended_metadata
        assert "requires" in loaded.get("recommended_metadata", []), "V2 requires 应在 recommended_metadata"

    def test_load_missing_catalog(self, cat, tmp_path):
        loaded = cat.load_catalog(tmp_path / "missing.yaml")
        assert "error" in loaded
        assert "不存在" in loaded["error"]


# ----------------------------------------------------------------------
# TestParseSkillMd — C2 解析 SKILL.md
# ----------------------------------------------------------------------
class TestParseSkillMd:
    """C2: SKILL.md 解析 — 正常 / 缺 frontmatter / 缺闭合"""

    def test_parse_normal_frontmatter(self, cat, tmp_path):
        f = tmp_path / "SKILL.md"
        f.write_text("---\nname: test\ndescription: desc\nversion: 1.0.0\n---\n# Content\n")
        fm = cat.parse_skill_md(f)
        assert "error" not in fm
        assert fm.get("name") == "test"

    def test_parse_missing_frontmatter(self, cat, tmp_path):
        f = tmp_path / "SKILL.md"
        f.write_text("# No frontmatter\n")
        fm = cat.parse_skill_md(f)
        assert "error" in fm
        assert "缺 frontmatter" in fm["error"]

    def test_parse_unclosed_frontmatter(self, cat, tmp_path):
        f = tmp_path / "SKILL.md"
        f.write_text("---\nname: test\n")  # 缺闭合 ---
        fm = cat.parse_skill_md(f)
        assert "error" in fm
        assert "未闭合" in fm["error"]


# ----------------------------------------------------------------------
# TestCheckSkill — C3 单 SKILL 校验
# ----------------------------------------------------------------------
class TestCheckSkill:
    """C3: 单 SKILL 包校验 — PASS / FAIL / 边界"""

    def _make_skill(self, tmp_path: pathlib.Path, name: str, fm: str, content_len: int = 100) -> pathlib.Path:
        skill_dir = tmp_path / name
        skill_dir.mkdir()
        body = "x\n" * content_len
        (skill_dir / "SKILL.md").write_text(f"---\n{fm}\n---\n{body}")
        return skill_dir

    def test_passes_with_full_metadata(self, cat, tmp_path):
        skill_dir = self._make_skill(tmp_path, "good-skill",
                                     "name: good\ndescription: desc\nversion: 1.0.0\nrequires: []")
        catalog = {
            "required_metadata": ["name", "description"],
            "structural_rules": {"max_skill_md_lines": 350, "min_yaml_frontmatter_fields": 2},
        }
        result = cat.check_skill(skill_dir, catalog)
        assert result["passed"] is True, f"应通过但失败: {result['errors']}"

    def test_fails_when_missing_required(self, cat, tmp_path):
        skill_dir = self._make_skill(tmp_path, "bad-skill",
                                     "name: bad\n")  # 缺 description
        catalog = {"required_metadata": ["name", "description"]}
        result = cat.check_skill(skill_dir, catalog)
        assert result["passed"] is False
        assert any("description" in e for e in result["errors"])

    def test_warns_when_exceeds_max_lines(self, cat, tmp_path):
        skill_dir = self._make_skill(tmp_path, "long-skill",
                                     "name: long\ndescription: d\n", content_len=500)
        catalog = {
            "required_metadata": ["name", "description"],
            "structural_rules": {"max_skill_md_lines": 350, "min_yaml_frontmatter_fields": 2},
        }
        result = cat.check_skill(skill_dir, catalog)
        assert any("> 推荐 350" in w for w in result["warnings"])

    def test_v2_required_field_version(self, cat, tmp_path):
        """V2 NEW — version 必填,缺则 FAIL"""
        skill_dir = self._make_skill(tmp_path, "v2-skill",
                                     "name: v2\ndescription: d\n")  # 缺 version
        catalog = {
            "required_metadata": ["name", "description", "version"],
            "recommended_metadata": ["requires"],
        }
        result = cat.check_skill(skill_dir, catalog)
        assert result["passed"] is False
        assert any("version" in e for e in result["errors"])

    def test_v2_recommended_field_warns_only(self, cat, tmp_path):
        """V2 NEW — requires 推荐字段,缺则 WARN 不 FAIL"""
        skill_dir = self._make_skill(tmp_path, "v2-skill",
                                     "name: v2\ndescription: d\nversion: 1.0.0\n")  # 缺 requires
        catalog = {
            "required_metadata": ["name", "description", "version"],
            "recommended_metadata": ["requires"],
        }
        result = cat.check_skill(skill_dir, catalog)
        assert result["passed"] is True, f"推荐字段缺不应 FAIL: {result['errors']}"
        assert any("requires" in w for w in result["warnings"])

    def test_v2_all_required_pass(self, cat, tmp_path):
        """V2 — 全必填字段满足 + recommended 也满足 → PASS 无 warn"""
        skill_dir = self._make_skill(tmp_path, "v2-skill",
                                     "name: v2\ndescription: d\nversion: 1.0.0\nrequires:\n  - foo\n")
        catalog = {
            "required_metadata": ["name", "description", "version"],
            "recommended_metadata": ["requires"],
        }
        result = cat.check_skill(skill_dir, catalog)
        assert result["passed"] is True
        assert not any("requires" in w for w in result["warnings"])


# ----------------------------------------------------------------------
# TestMainCli — C4 main() 集成
# ----------------------------------------------------------------------
class TestMainCli:
    """main() 集成 — PASS / FAIL"""

    def test_main_passes(self, cat, tmp_path, monkeypatch, capsys):
        """catalog + skill 都满足 → exit 0"""
        skills_root = tmp_path / "skills"
        skills_root.mkdir()
        skill_dir = skills_root / "my-skill"
        skill_dir.mkdir()
        (skill_dir / "SKILL.md").write_text(
            "---\nname: my-skill\ndescription: desc\nversion: 1.0.0\n---\n# Body\n"
        )
        catalog_path = tmp_path / "catalog.yaml"
        catalog_path.write_text(
            "version: 1.0.0\nscope: skill-metadata\nrequired_metadata:\n  - name\n  - description\n"
        )
        monkeypatch.setattr(sys, "argv", [
            "cov.py", "--catalog", str(catalog_path), "--skills-root", str(skills_root),
        ])
        rc = cat.main()
        captured = capsys.readouterr()
        assert rc == 0, f"exit={rc}, out={captured.out}"
        assert "PASS" in captured.out

    def test_main_report_only_by_default(self, cat, tmp_path, monkeypatch, capsys):
        """默认 report-only 模式 — skill 缺字段 → exit 0(报告但不阻断)"""
        skills_root = tmp_path / "skills"
        skills_root.mkdir()
        skill_dir = skills_root / "bad-skill"
        skill_dir.mkdir()
        (skill_dir / "SKILL.md").write_text("---\nname: bad\n---\n# Body\n")
        catalog_path = tmp_path / "catalog.yaml"
        catalog_path.write_text(
            "version: 1.0.0\nscope: skill-metadata\nrequired_metadata:\n  - name\n  - description\n"
        )
        monkeypatch.setattr(sys, "argv", [
            "cov.py", "--catalog", str(catalog_path), "--skills-root", str(skills_root),
        ])
        rc = cat.main()
        captured = capsys.readouterr()
        assert rc == 0, "默认 report-only 应 exit 0"
        assert "description" in captured.out
        assert "report-only" in captured.out

    def test_main_strict_fails_when_missing_field(self, cat, tmp_path, monkeypatch, capsys):
        """--strict 模式 — skill 缺字段 → exit 1"""
        skills_root = tmp_path / "skills"
        skills_root.mkdir()
        skill_dir = skills_root / "bad-skill"
        skill_dir.mkdir()
        (skill_dir / "SKILL.md").write_text("---\nname: bad\n---\n# Body\n")
        catalog_path = tmp_path / "catalog.yaml"
        catalog_path.write_text(
            "version: 1.0.0\nscope: skill-metadata\nrequired_metadata:\n  - name\n  - description\n"
        )
        monkeypatch.setattr(sys, "argv", [
            "cov.py", "--catalog", str(catalog_path), "--skills-root", str(skills_root), "--strict",
        ])
        rc = cat.main()
        captured = capsys.readouterr()
        assert rc == 1
        assert "STRICT" in captured.out