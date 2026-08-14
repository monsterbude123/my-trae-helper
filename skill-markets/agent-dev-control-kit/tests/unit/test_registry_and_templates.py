"""registry + scaffolds + presets + templates 一致性测试

覆盖:
  - stacks.yaml / gates.yaml / guards.yaml 字段完整性 + 互相引用
  - scaffolds/* /scaffold.yaml 必填字段
  - templates/*.md 结构
  - presets/*.yaml 对齐 registry
  - 5 个子 skill(execution/guard/gate/asset/release)SKILL.md 最小合规
"""
from __future__ import annotations

from pathlib import Path

import pytest
import yaml

pytestmark = pytest.mark.unit


REGISTRY = Path(__file__).resolve().parent.parent.parent / "registry"
SCAFFOLDS = Path(__file__).resolve().parent.parent.parent / "scaffolds"
PRESETS = Path(__file__).resolve().parent.parent.parent / "presets"
TEMPLATES = Path(__file__).resolve().parent.parent.parent / "templates"
SKILLS = Path(__file__).resolve().parent.parent.parent / "skills"


def _load_yaml(p: Path) -> dict:
    return yaml.safe_load(p.read_text(encoding="utf-8")) or {}


# ============================================================================
# TestRegistryConsistency
# ============================================================================
class TestRegistryConsistency:
    @pytest.fixture(scope="class")
    def stacks(self):
        return _load_yaml(REGISTRY / "stacks.yaml")

    @pytest.fixture(scope="class")
    def gates(self):
        return _load_yaml(REGISTRY / "gates.yaml")

    @pytest.fixture(scope="class")
    def guards(self):
        return _load_yaml(REGISTRY / "guards.yaml")

    def test_stacks_required_top_keys(self, stacks):
        for k in ("version", "stacks"):
            assert k in stacks, f"stacks.yaml 缺 {k}"

    def test_stacks_entries_required_fields(self, stacks):
        for s in stacks["stacks"]:
            for k in ("id", "name", "scaffold"):
                assert k in s, f"stack {s.get('id','?')} 缺 {k}"

    def test_gates_entries_required_fields(self, gates):
        for g in gates["gates"]:
            for k in ("id", "name", "guards"):
                assert k in g, f"gate {g.get('id','?')} 缺 {k}"

    def test_guards_entries_required_fields(self, guards):
        for g in guards["guards"]:
            for k in ("id", "name"):
                assert k in g, f"guard {g.get('id','?')} 缺 {k}"

    @pytest.mark.trap
    def test_gate_guards_reference_known_guard_ids(self, gates, guards):
        """AP-7 防御:gate 中列出的 guard id 必须在 guards.yaml 中存在。"""
        known = {g["id"] for g in guards["guards"]}
        for gate in gates["gates"]:
            for gid in gate.get("guards", []) or []:
                assert gid in known, (
                    f"gate {gate['id']} 引用未知 guard '{gid}',"
                    f"已知: {sorted(known)}"
                )


# ============================================================================
# TestScaffoldConsistency
# ============================================================================
class TestScaffoldConsistency:
    EXPECTED_IDS = {"nodejs", "python", "go", "java-maven"}

    def test_expected_scaffold_dirs_exist(self):
        actual = {p.name for p in SCAFFOLDS.iterdir() if p.is_dir()}
        missing = self.EXPECTED_IDS - actual
        assert not missing, f"scaffolds/ 缺: {missing}"

    @pytest.mark.parametrize("sid", sorted(EXPECTED_IDS))
    def test_scaffold_yaml_has_files_and_required_scripts(self, sid):
        cfg = _load_yaml(SCAFFOLDS / sid / "scaffold.yaml")
        for k in ("id", "name", "files", "required_scripts"):
            assert k in cfg, f"scaffold[{sid}] 缺 {k}"
        rs = cfg.get("required_scripts") or {}
        # 至少应有 pre_commit + pre_push 阶段
        assert "pre_commit" in rs and "pre_push" in rs, (
            f"scaffold[{sid}] required_scripts 必须含 pre_commit + pre_push"
        )

    @pytest.mark.parametrize("sid", sorted(EXPECTED_IDS))
    def test_scaffold_files_directory_holds_pre_commit_and_pre_push(self, sid):
        files = SCAFFOLDS / sid / "files"
        gates = files / "gates"
        assert gates.is_dir(), f"scaffold[{sid}]/files/gates/ 不存在"
        assert (gates / "pre-commit.sh").exists(), f"scaffold[{sid}] 缺 pre-commit.sh"
        assert (gates / "pre-push.sh").exists(), f"scaffold[{sid}] 缺 pre-push.sh"


# ============================================================================
# TestPresetsConsistency
# ============================================================================
class TestPresetsConsistency:
    def test_index_yaml_references_existing_presets(self):
        idx = _load_yaml(PRESETS / "_index.yaml")
        for p in idx.get("presets") or []:
            sid = p["id"]
            assert (PRESETS / sid).is_dir(), f"presets/{sid}/ 不存在"
            assert (PRESETS / sid / "preset.yaml").is_file()

    def test_preset_yaml_minimal_fields(self):
        for d in PRESETS.iterdir():
            if not (d.is_dir() and (d / "preset.yaml").exists()):
                continue
            cfg = _load_yaml(d / "preset.yaml")
            for k in ("id", "name", "toolchain", "commands"):
                assert k in cfg, f"preset {d.name} 缺 {k}"


# ============================================================================
# TestTemplates
# ============================================================================
class TestTemplates:
    def test_execution_skill_template_has_sections(self):
        tpl = (TEMPLATES / "execution-skill-template.md").read_text(encoding="utf-8")
        for section in ("## 触发词", "## 执行流程", "## 输出规范", "## 错误处理", "## 示例用法"):
            assert section in tpl, f"execution-skill-template.md 缺 {section}"

    def test_guard_skill_template_has_required_keys(self):
        tpl = (TEMPLATES / "guard-skill-template.md").read_text(encoding="utf-8")
        for marker in ("守卫规则", "前置守卫", "后置守卫", "异常守卫", "状态守卫"):
            assert marker in tpl, f"guard-skill-template.md 缺 {marker}"

    def test_gate_skill_template_has_levels(self):
        tpl = (TEMPLATES / "gate-skill-template.md").read_text(encoding="utf-8")
        for level in ("L1", "L2", "L3", "L4"):
            assert level in tpl, f"gate-skill-template.md 缺 {level}"


# ============================================================================
# TestSubSkills — 5 个子 skill SKILL.md 最小合规
# ============================================================================
SUB_SKILL_IDS = [
    "execution-control",
    "guard-control",
    "gate-control",
    "asset-management-control",
    "release-process-control",
]


class TestSubSkills:
    @pytest.mark.parametrize("sid", SUB_SKILL_IDS)
    def test_sub_skill_md_has_frontmatter(self, sid):
        p = SKILLS / sid / "SKILL.md"
        assert p.is_file(), f"skills/{sid}/SKILL.md 不存在"
        content = p.read_text(encoding="utf-8")
        assert content.startswith("---"), f"{sid} 缺 YAML frontmatter"
        # 必含 name + description
        assert "name:" in content[:300], f"{sid} 缺 name 字段"
        assert "description:" in content[:600], f"{sid} 缺 description 字段"

    def test_no_duplicate_sub_skill_names(self):
        names = []
        for sid in SUB_SKILL_IDS:
            p = SKILLS / sid / "SKILL.md"
            content = p.read_text(encoding="utf-8")
            for line in content.splitlines()[:15]:
                if line.strip().startswith("name:"):
                    names.append(line.split(":", 1)[1].strip())
        assert len(names) == len(set(names)), f"重复 name: {names}"


# ============================================================================
# TestPyprojectIfExists — 如果将来 test 包自身需要 setup,确保模板兼容
# ============================================================================
class TestAgentDevControlKitSafeGuard:
    """§11.1.2:三项 gate 配置同步(本会话级铁律)。"""

    @pytest.mark.trap
    def test_no_echo_skip_in_builtin_husky_hooks(self):
        """反例 AP-2:内嵌 .husky 模板不能包含 echo skipping。"""
        for sid in TestScaffoldConsistency.EXPECTED_IDS:
            for hook in ("pre-commit", "pre-push"):
                f = SCAFFOLDS / sid / "files" / "gates" / hook
                if not f.exists():
                    continue
                text = f.read_text(encoding="utf-8")
                assert "echo" not in text.lower() or "skipping" not in text.lower(), (
                    f"scaffold[{sid}] {hook} 含 echo-skip,违反 §11.1.2"
                )
