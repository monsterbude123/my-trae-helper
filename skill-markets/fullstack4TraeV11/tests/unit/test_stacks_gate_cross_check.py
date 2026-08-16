"""run-all-guards.py stack-gate 交叉校验 + scaffold 必填字段单元测试。

覆盖维度(P3-1 + P3-2):
  - P3-1 PASS:stack 的 gates/guards 都在 gates.yaml/guards.yaml 登记 → PASS
  - P3-1 FAIL:stack 的 gates 含未登记 gate id → FAIL
  - P3-1 FAIL:stack 的 guards 含未登记 guard id → FAIL
  - P3-2 PASS:stack 含 name/gates/guards 三必填字段 → PASS
  - P3-2 FAIL:stack 缺 name/gates/guards 任一字段 → FAIL
  - 集成:run-all-guards.py 跑真反例 stack → 整体 exit 1
"""
from __future__ import annotations

import importlib.util
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

pytestmark = pytest.mark.unit

SCRIPT_PATH = (
    Path(__file__).resolve().parents[2] / "scripts" / "run-all-guards.py"
)
SKILL_ROOT = Path(__file__).resolve().parents[2]
REGISTRY_DIR = SKILL_ROOT / "registry"


def _load_run_all_guards():
    spec = importlib.util.spec_from_file_location("run_all_guards", SCRIPT_PATH)
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _real_registry_ids():
    """读真实 registry/gates.yaml + guards.yaml 收集 id。"""
    import yaml
    with open(REGISTRY_DIR / "gates.yaml", encoding="utf-8") as f:
        gates = yaml.safe_load(f)
    with open(REGISTRY_DIR / "guards.yaml", encoding="utf-8") as f:
        guards = yaml.safe_load(f)
    return (
        {g["id"] for g in gates.get("gates", []) if g.get("id")},
        {g["id"] for g in guards.get("guards", []) if g.get("id")},
    )


# ============================================================================
# TestValidateStack — validate_stack() 单元(P3-1 + P3-2)
# ============================================================================
class TestValidateStack:
    def test_real_stack_passes(self):
        """PASS:registry/stacks.yaml 真实 nodejs stack 含合法 gates/guards。"""
        mod = _load_run_all_guards()
        gates_ids, guards_ids = _real_registry_ids()
        real_stack = {
            "id": "nodejs",
            "name": "Node.js",
            "gates": ["stage-spec", "stage-real-verify"],
            "guards": ["code-hygiene", "contract-integrity", "acceptance-audit", "rot-scan"],
        }
        errors = mod.validate_stack(real_stack, gates_ids, guards_ids)
        assert errors == [], f"真实 stack 应通过,实际: {errors}"

    def test_stack_with_unregistered_gate_fails(self):
        """P3-1 FAIL:stack.gates 含未登记 gate id。"""
        mod = _load_run_all_guards()
        gates_ids, guards_ids = _real_registry_ids()
        bad_stack = {
            "id": "bad-stack",
            "name": "Bad",
            "gates": ["nonexistent-stage-X"],
            "guards": ["code-hygiene"],
        }
        errors = mod.validate_stack(bad_stack, gates_ids, guards_ids)
        assert any("未登记 gate" in e and "nonexistent-stage-X" in e for e in errors), errors

    def test_stack_with_unregistered_guard_fails(self):
        """P3-1 FAIL:stack.guards 含未登记 guard id。"""
        mod = _load_run_all_guards()
        gates_ids, guards_ids = _real_registry_ids()
        bad_stack = {
            "id": "bad-stack",
            "name": "Bad",
            "gates": ["stage-spec"],
            "guards": ["code-hygiene", "ghost-guard-zzz"],
        }
        errors = mod.validate_stack(bad_stack, gates_ids, guards_ids)
        assert any("未登记 guard" in e and "ghost-guard-zzz" in e for e in errors), errors

    def test_stack_missing_required_fields_fails(self):
        """P3-2 FAIL:stack 缺 name/gates/guards 必填字段。"""
        mod = _load_run_all_guards()
        gates_ids, guards_ids = _real_registry_ids()
        bad_stack = {"id": "incomplete"}
        errors = mod.validate_stack(bad_stack, gates_ids, guards_ids)
        assert any("缺必填字段" in e for e in errors), errors

    def test_stack_with_empty_gates_and_guards_passes(self):
        """边界:stack.gates 和 guards 都为空 list → PASS(可选)。"""
        mod = _load_run_all_guards()
        gates_ids, guards_ids = _real_registry_ids()
        empty_stack = {
            "id": "empty-stack",
            "name": "Empty",
            "gates": [],
            "guards": [],
        }
        errors = mod.validate_stack(empty_stack, gates_ids, guards_ids)
        assert errors == [], f"空 list 应通过,实际: {errors}"


# ============================================================================
# TestIntegrationWithCli — 集成测试:跑 CLI 期望 exit code
# ============================================================================
class TestIntegrationWithCli:
    """跑 subprocess 验证 CLI 集成行为。"""

    def _build_registry(self, tmp_path: Path, stacks_yaml_text: str) -> Path:
        """复制真实 registry,gates/guards 保持完整,替换 stacks.yaml。"""
        reg = tmp_path / "registry"
        reg.mkdir()
        # 复制真实 gates/guards/state-machine/repair-flow(必须保持完整)
        for fname in ("gates.yaml", "guards.yaml", "state-machine.yaml", "repair-flow.yaml"):
            src = REGISTRY_DIR / fname
            if src.exists():
                shutil.copy(src, reg / fname)
        # 写入测试 stacks.yaml
        (reg / "stacks.yaml").write_text(stacks_yaml_text, encoding="utf-8")
        return reg

    def test_cli_passes_with_real_stacks(self, tmp_path):
        """PASS:真实 stacks.yaml 内容 → exit 0。"""
        reg = self._build_registry(
            tmp_path,
            """version: 1.0.0
stacks:
  - id: nodejs
    name: Node.js
    gates:
      - stage-spec
      - stage-real-verify
    guards:
      - code-hygiene
      - contract-integrity
""",
        )
        # 用 skill_root/scripts 路径调用
        result = subprocess.run(
            [sys.executable, str(SCRIPT_PATH),
             "--registry-dir", str(reg),
             "--validate-only"],
            capture_output=True, text=True, timeout=60,
        )
        assert "stack=nodejs status=PASS" in result.stdout, result.stdout
        assert "stack_fail=0" in result.stdout, result.stdout

    def test_cli_fails_with_unregistered_gate(self, tmp_path):
        """FAIL:stacks/node-bad-test.yaml 含未登记 gate → CLI exit 1。"""
        reg = self._build_registry(
            tmp_path,
            """version: 1.0.0
stacks:
  - id: node-bad-test
    name: Bad
    gates:
      - nonexistent-stage-X
    guards:
      - code-hygiene
""",
        )
        result = subprocess.run(
            [sys.executable, str(SCRIPT_PATH),
             "--registry-dir", str(reg),
             "--validate-only"],
            capture_output=True, text=True, timeout=60,
        )
        assert result.returncode == 1, f"期望 exit 1,实际 {result.returncode}: {result.stdout}"
        assert "stack=node-bad-test status=FAIL" in result.stdout
        assert "未登记 gate" in result.stdout
        assert "nonexistent-stage-X" in result.stdout