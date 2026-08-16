"""run-all-guards.py 项目级 registry 自动探测单元测试。

覆盖 dimensions:
  - P0-1 反例固化:无项目级 registry → 用 V11 通用
  - P0-1 PASS:有项目级 registry → 用项目级
  - P0-1 优先级:显式 --registry-dir + 项目级同时存在 → 显式胜出
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

pytestmark = pytest.mark.unit

SCRIPT_PATH = (
    Path(__file__).resolve().parents[2] / "scripts" / "run-all-guards.py"
)


def _load_run_all_guards():
    """动态导入 scripts/run-all-guards.py(无 conftest 依赖)。"""
    spec = importlib.util.spec_from_file_location("run_all_guards", SCRIPT_PATH)
    assert spec is not None and spec.loader is not None, f"无法加载 {SCRIPT_PATH}"
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# ============================================================================
# TestResolveRegistryDir — 3 优先级场景
# ============================================================================
class TestResolveRegistryDir:
    def test_no_project_registry_uses_v11_default(self, tmp_path):
        """反例 1:无项目级 .trae/registry → 用 V11 通用层 skill_root/registry。"""
        mod = _load_run_all_guards()
        skill_root = tmp_path / "skill_root"
        skill_root.mkdir()
        registry, auto = mod.resolve_registry_dir(None, str(tmp_path), skill_root)
        assert registry == skill_root / "registry"
        assert auto is False

    def test_project_registry_present_uses_project(self, tmp_path):
        """PASS:项目级 .trae/registry/{4 表} 齐全 → 用项目级。"""
        mod = _load_run_all_guards()
        skill_root = tmp_path / "skill_root"
        skill_root.mkdir()
        proj_reg = tmp_path / ".trae" / "registry"
        proj_reg.mkdir(parents=True)
        for f in ["gates.yaml", "guards.yaml", "state-machine.yaml", "repair-flow.yaml"]:
            (proj_reg / f).write_text("{}", encoding="utf-8")

        registry, auto = mod.resolve_registry_dir(None, str(tmp_path), skill_root)
        assert registry == proj_reg.resolve()
        assert auto is True

    def test_explicit_arg_wins_over_project(self, tmp_path):
        """优先级:显式 --registry-dir + 项目级 → 显式胜出。"""
        mod = _load_run_all_guards()
        skill_root = tmp_path / "skill_root"
        skill_root.mkdir()
        # 项目级也放一份
        proj_reg = tmp_path / ".trae" / "registry"
        proj_reg.mkdir(parents=True)
        for f in ["gates.yaml", "guards.yaml", "state-machine.yaml", "repair-flow.yaml"]:
            (proj_reg / f).write_text("{}", encoding="utf-8")
        # 显式目录
        explicit = tmp_path / "explicit-registry"
        explicit.mkdir()

        registry, auto = mod.resolve_registry_dir(str(explicit), str(tmp_path), skill_root)
        assert registry == explicit
        assert auto is False

    def test_partial_project_registry_not_used(self, tmp_path):
        """边界:项目级 .trae/registry 存在但 4 表不全 → 不探测成功,回 V11。"""
        mod = _load_run_all_guards()
        skill_root = tmp_path / "skill_root"
        skill_root.mkdir()
        proj_reg = tmp_path / ".trae" / "registry"
        proj_reg.mkdir(parents=True)
        # 只放 2 个
        (proj_reg / "gates.yaml").write_text("{}", encoding="utf-8")
        (proj_reg / "guards.yaml").write_text("{}", encoding="utf-8")

        registry, auto = mod.resolve_registry_dir(None, str(tmp_path), skill_root)
        assert registry == skill_root / "registry"
        assert auto is False