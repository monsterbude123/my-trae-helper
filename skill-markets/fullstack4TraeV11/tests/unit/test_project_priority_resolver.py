"""project-priority-resolver.py 单元测试。

覆盖 dimensions:
  - P1-1 反例固化:无 config.yaml → 输出 V11 默认 skills
  - P1-1 PASS:有 config.yaml → 3 层合并,项目级前置
  - P1-1 forbidden_paths 命中 → exit 1
  - P1-1 forbidden_paths 未命中 → exit 0
  - P1-3 PASS:合并 anti-patterns.md
  - P1-3 反例:项目级 anti-patterns 不存在 → 只含 V11 通用
"""
from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
from pathlib import Path

import pytest

pytestmark = pytest.mark.unit

SCRIPT_DIR = Path(__file__).resolve().parents[2] / "scripts"
SCRIPT_PATH = SCRIPT_DIR / "project-priority-resolver.py"
SKILL_ROOT = SCRIPT_DIR.parent


def _load_resolver():
    """动态加载 project-priority-resolver.py。"""
    spec = importlib.util.spec_from_file_location(
        "project_priority_resolver", SCRIPT_PATH
    )
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _run_cli(project_root: Path, *args: str):
    """通过 subprocess 调用,避免 argparse 副作用。"""
    import subprocess
    cmd = [
        sys.executable, str(SCRIPT_PATH),
        "--project-root", str(project_root),
        *args,
    ]
    return subprocess.run(cmd, capture_output=True, text=True)


# ============================================================================
# TestResolveSkills — 3 层优先级解析
# ============================================================================
class TestResolveSkills:
    def test_no_project_config_returns_v11_default(self):
        """反例:无 config.yaml → 用 V11 默认(Layer1 + Layer2)。"""
        mod = _load_resolver()
        with tempfile.TemporaryDirectory() as tmp:
            pr = Path(tmp)
            skills = mod.resolve_skills("3/implement", {}, SKILL_ROOT)
        # 必有 layer1 全局 10 个 + layer2 implement 的 ponytail/gitnexus
        assert "gitnexus4Trae" in skills
        assert "ponytail4Trae" in skills
        assert len(skills) >= 10

    def test_project_overrides_prepend(self):
        """PASS:项目级 stage_config.skills 前置于 V11 通用。"""
        mod = _load_resolver()
        project_config = {
            "stage_config": {
                "3/implement": {
                    "skills": ["my-custom-skill", "second-custom"]
                }
            }
        }
        with tempfile.TemporaryDirectory() as tmp:
            pr = Path(tmp)
            skills = mod.resolve_skills("3/implement", project_config, SKILL_ROOT)
        # 项目级应在前
        assert skills[0] == "my-custom-skill"
        assert skills[1] == "second-custom"
        # 项目级覆盖顺序明确 → my-custom-skill 在 gitnexus 之前
        assert "gitnexus4Trae" in skills  # V11 通用仍在

    def test_dedup(self):
        """项目级与 V11 重复 skill → 去重保留首次出现。"""
        mod = _load_resolver()
        project_config = {
            "stage_config": {
                "3/implement": {"skills": ["gitnexus4Trae", "my-new"]}
            }
        }
        with tempfile.TemporaryDirectory() as tmp:
            skills = mod.resolve_skills("3/implement", project_config, SKILL_ROOT)
        # gitnexus4Trae 只出现 1 次
        assert skills.count("gitnexus4Trae") == 1
        assert "my-new" in skills


# ============================================================================
# TestCheckForbidden
# ============================================================================
class TestCheckForbidden:
    def test_no_config_returns_allow(self, tmp_path):
        """无 config.yaml → 无规则 → allow。"""
        blocked, rule, reason = _load_resolver().check_forbidden(tmp_path, "any/path.md")
        assert blocked is False

    def test_forbidden_match_blocks(self, tmp_path):
        """PASS:有 config.yaml 且命中规则 → blocked=True。"""
        # 写 config.yaml
        cfg = tmp_path / ".trae"
        cfg.mkdir()
        (cfg / "fullstack4traev11.config.yaml").write_text(
            "forbidden_paths:\n  - docs/archive/**\n",
            encoding="utf-8",
        )
        blocked, rule, reason = _load_resolver().check_forbidden(
            tmp_path, "docs/archive/foo.md"
        )
        assert blocked is True
        assert "docs/archive/**" in rule

    def test_forbidden_no_match_allows(self, tmp_path):
        """PASS:有 config.yaml 但路径不在规则 → allow。"""
        cfg = tmp_path / ".trae"
        cfg.mkdir()
        (cfg / "fullstack4traev11.config.yaml").write_text(
            "forbidden_paths:\n  - docs/archive/**\n",
            encoding="utf-8",
        )
        blocked, _, _ = _load_resolver().check_forbidden(tmp_path, "docs/specs/x.md")
        assert blocked is False


class TestCliForbidden:
    def test_cli_blocks_with_exit1(self, tmp_path):
        """CLI 真反例:命中 forbidden_paths → exit 1。"""
        cfg = tmp_path / ".trae"
        cfg.mkdir()
        (cfg / "fullstack4traev11.config.yaml").write_text(
            "forbidden_paths:\n  - docs/archive/**\n",
            encoding="utf-8",
        )
        result = _run_cli(tmp_path, "--check-forbidden", "docs/archive/foo.md")
        assert result.returncode == 1
        assert "BLOCKED" in result.stdout + result.stderr

    def test_cli_allows_with_exit0(self, tmp_path):
        """CLI PASS:路径未命中 → exit 0。"""
        cfg = tmp_path / ".trae"
        cfg.mkdir()
        (cfg / "fullstack4traev11.config.yaml").write_text(
            "forbidden_paths:\n  - docs/archive/**\n",
            encoding="utf-8",
        )
        result = _run_cli(tmp_path, "--check-forbidden", "docs/specs/x.md")
        assert result.returncode == 0
        assert "ALLOW" in result.stdout


# ============================================================================
# TestMergeAntiPatterns — P1-3
# ============================================================================
class TestMergeAntiPatterns:
    def test_no_project_anti_patterns(self, tmp_path):
        """反例:项目级 anti-patterns 不存在 → 只含 V11 通用。"""
        mod = _load_resolver()
        result = mod.merge_anti_patterns(tmp_path, SKILL_ROOT)
        assert result["v11_path"] is not None, "V11 通用 anti-patterns 必须存在"
        assert result["project_path"] is None
        # merged_size > 0(V11 通用有内容)
        assert result["merged_size"] > 0

    def test_with_project_anti_patterns(self, tmp_path):
        """PASS:项目级 anti-patterns 存在 → 合并后含项目内容。"""
        # 写项目级 anti-patterns
        proj_dir = tmp_path / ".trae" / "skills" / "project_rules_skills" / "references"
        proj_dir.mkdir(parents=True)
        (proj_dir / "anti-patterns.md").write_text(
            "- AP-99-x: 项目级反例\n",
            encoding="utf-8",
        )
        mod = _load_resolver()
        result = mod.merge_anti_patterns(tmp_path, SKILL_ROOT)
        assert result["project_path"] is not None
        assert "AP-99-x" in result["merged_content"]
        assert "V11通用层" in result["merged_content"]


class TestCliMergeAntiPatterns:
    def test_cli_writes_merged_file(self, tmp_path):
        """CLI PASS:--merge-anti-patterns --output 写文件成功。"""
        proj_dir = tmp_path / ".trae" / "skills" / "project_rules_skills" / "references"
        proj_dir.mkdir(parents=True)
        (proj_dir / "anti-patterns.md").write_text(
            "- AP-99-x: 项目级反例\n",
            encoding="utf-8",
        )
        out_file = tmp_path / "merged.md"
        result = _run_cli(
            tmp_path, "--merge-anti-patterns", "--output", str(out_file)
        )
        assert result.returncode == 0
        assert out_file.exists()
        content = out_file.read_text(encoding="utf-8")
        assert "AP-99-x" in content


# ============================================================================
# TestCliStage
# ============================================================================
class TestCliStage:
    def test_cli_stage_returns_json(self, tmp_path):
        """CLI PASS:--stage + --json → 输出含 layers 字段。"""
        result = _run_cli(tmp_path, "--stage", "3/implement", "--json")
        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert "skills" in data
        assert "layers" in data
        assert "layer2_v11" in data["layers"]