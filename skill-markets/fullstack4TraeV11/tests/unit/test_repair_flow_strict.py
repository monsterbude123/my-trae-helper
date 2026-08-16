"""P2-2 repair-flow-gate.py --strict 模式单元测试。

覆盖:
  - C1 --strict 缺 --step → FAIL(exit 1)
  - C2 --step step-4 --strict --evidence-paths 空 → FAIL(数量错)
  - C3 --step step-4 --strict --evidence-paths 3 项 → FAIL(数量错)
  - C4 --step step-4 --strict --evidence-paths 4 项文件存在 + 顺序正确 → PASS
  - C5 --step step-1 不带 --strict → 默认行为 PASS(原 --step)
  - C6 --step step-4 --strict 但 evidence_paths[0..2] 缺 → FAIL(prereq 关系注解)
  - C7 --step step-4 --strict 但 evidence_paths 顺序乱(step-2 给出 step-1 没) → FAIL(顺序错)
  - C8 --step step-4 --strict --evidence-paths 含空字符串 → FAIL(空路径)
  - C9 --step 不存在的 step(如 step-99)→ 原行为 FAIL
  - C10 --step step-4 --strict --evidence-paths 在顺序正确但路径无 step-N 前缀 → 不强制顺序(弱校验通过)
  - C11 --step step-4 --strict --evidence-paths 含路径指向目录而非文件 → FAIL
"""
from __future__ import annotations

import importlib.util
import sys
import subprocess
from pathlib import Path

import pytest

pytestmark = pytest.mark.unit

SCRIPT_DIR = Path(__file__).resolve().parents[2] / "scripts"
SCRIPT_PATH = SCRIPT_DIR / "repair-flow-gate.py"
SKILL_ROOT = Path(__file__).resolve().parents[2]


def _load_module():
    spec = importlib.util.spec_from_file_location(
        "repair_flow_gate_p2_2", SCRIPT_PATH
    )
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _run_cli(*args) -> tuple:
    """以子进程跑 repair-flow-gate.py,捕获 (returncode, stdout, stderr)"""
    r = subprocess.run(
        [sys.executable, str(SCRIPT_PATH), *args],
        capture_output=True, text=True, cwd=str(SKILL_ROOT),
    )
    return r.returncode, r.stdout, r.stderr


def _write_strict_evidence(tmp_path: Path, count: int = 4, prefix: bool = True) -> list:
    """造 4 份顺序正确的 evidence 文件。prefix=True → 文件名含 step-N 前缀。"""
    from skill_markets_test_helpers import write_step_files  # 预防性 import,实际用下方的内联
    return None


# ============================================================================
# 纯模块函数级单测(不跑 subprocess)
# ============================================================================
class TestValidateStrictEvidence:
    def test_c2_empty_evidence_paths_fails(self):
        """C2:--evidence-paths 空 → FAIL(数量错)。"""
        mod = _load_module()
        errors = mod.validate_strict_evidence(
            step_id="step-4-user-confirm",
            evidence_paths=[],
            step_ids_in_registry=["step-1-e2e-fail", "step-2-6layer", "step-3-fix-and-regression", "step-4-user-confirm"],
        )
        assert any("必须含 4 项" in e for e in errors), (
            f"应含 '必须含 4 项' 错误,实际: {errors}"
        )

    def test_c3_three_evidence_paths_fails(self):
        """C3:--evidence-paths 3 项 → FAIL(数量错)。"""
        mod = _load_module()
        errors = mod.validate_strict_evidence(
            step_id="step-4-user-confirm",
            evidence_paths=["a.md", "b.md", "c.md"],
            step_ids_in_registry=["step-1-e2e-fail", "step-2-6layer", "step-3-fix-and-regression", "step-4-user-confirm"],
        )
        assert any("必须含 4 项" in e for e in errors)

    def test_c6_missing_evidence_files_fails(self, tmp_path):
        """C6:--step step-4 --strict 但 evidence_paths[0..2] 缺 → FAIL(prereq 关系注解)。"""
        mod = _load_module()
        # 4 个路径,前 3 个不存在
        errors = mod.validate_strict_evidence(
            step_id="step-4-user-confirm",
            evidence_paths=[
                str(tmp_path / "missing-1.md"),
                str(tmp_path / "missing-2.md"),
                str(tmp_path / "missing-3.md"),
                str(tmp_path / "step-4.md"),  # 这个存在也救不了前 3 个
            ],
            step_ids_in_registry=["step-1-e2e-fail", "step-2-6layer", "step-3-fix-and-regression", "step-4-user-confirm"],
        )
        # 前 3 个各自报"文件不存在"
        assert any("step-1-e2e-fail" in e and "不存在" in e for e in errors)
        assert any("step-2-6layer" in e and "不存在" in e for e in errors)
        assert any("step-3-fix-and-regression" in e and "不存在" in e for e in errors)
        # step-4-user-confirm 跑前必前 3 步完成的关系注解
        assert any("step-4-user-confirm 跑前必" in e for e in errors)

    def test_c8_empty_path_in_evidence_fails(self):
        """C8:--evidence-paths 含空字符串 → FAIL。"""
        mod = _load_module()
        # 4 项里有 1 项是空字符串
        # validate_strict_evidence 直接接 list,length==4,通过规则 1
        # 规则 2 报 empty paths[1]
        errors = mod.validate_strict_evidence(
            step_id="step-4-user-confirm",
            evidence_paths=["a.md", "", "c.md", "d.md"],
            step_ids_in_registry=["step-1-e2e-fail", "step-2-6layer", "step-3-fix-and-regression", "step-4-user-confirm"],
        )
        assert any("evidence_paths[1] 为空" in e for e in errors), (
            f"空字符串路径应报 'evidence_paths[1] 为空',实际: {errors}"
        )

    def test_c11_path_is_directory_fails(self, tmp_path):
        """C11:--evidence-paths 路径指向目录 → FAIL。"""
        mod = _load_module()
        # 4 个路径,前 3 个是目录
        dirs = [tmp_path / f"d{i}" for i in range(3)]
        for d in dirs:
            d.mkdir()
        errors = mod.validate_strict_evidence(
            step_id="step-4-user-confirm",
            evidence_paths=[
                str(dirs[0]) + "/",
                str(dirs[1]) + "/",
                str(dirs[2]) + "/",
                str(tmp_path / "step-4.md"),
            ],
            step_ids_in_registry=["step-1-e2e-fail", "step-2-6layer", "step-3-fix-and-regression", "step-4-user-confirm"],
        )
        # 注意:路径带 "/" 的话,会被 strip + 判定为不存在
        # 这里换一种语义:直接给"是目录"路径
        dir_paths = [str(d) for d in dirs] + [str(tmp_path / "step-4.md")]
        # 注意:validate 函数只看 .exists() 和 .is_file();目录 .exists()=True, .is_file()=False
        # 但前面的 4 项长度对不上:我把 4 个 item 全传
        # 实际我们的函数期望用 4 项;现在补到 4 项:
        # 简便起见:用 4 项,前 3 项是目录
        # 重做
        errors = mod.validate_strict_evidence(
            step_id="step-4-user-confirm",
            evidence_paths=[
                str(dirs[0]),
                str(dirs[1]),
                str(dirs[2]),
                str(tmp_path / "step-4.md"),
            ],
            step_ids_in_registry=["step-1-e2e-fail", "step-2-6layer", "step-3-fix-and-regression", "step-4-user-confirm"],
        )
        assert any("不是文件" in e for e in errors), (
            f"目录路径应报'不是文件',实际: {errors}"
        )

    def test_c4_all_evidence_files_exist_passes(self, tmp_path):
        """C4:4 项证据文件齐全 → PASS。"""
        mod = _load_module()
        files = [
            tmp_path / "step-1-e2e-fail.md",
            tmp_path / "step-2-6layer.md",
            tmp_path / "step-3-fix-and-regression.md",
            tmp_path / "step-4-user-confirm.md",
        ]
        for f in files:
            f.write_text("evidence", encoding="utf-8")
        errors = mod.validate_strict_evidence(
            step_id="step-4-user-confirm",
            evidence_paths=[str(f) for f in files],
            step_ids_in_registry=["step-1-e2e-fail", "step-2-6layer", "step-3-fix-and-regression", "step-4-user-confirm"],
        )
        assert errors == [], f"4 项全齐应 PASS,实际: {errors}"


# ============================================================================
# check_step_order_against_paths 单元测试
# ============================================================================
class TestCheckStepOrder:
    def test_correct_order_passes(self, tmp_path):
        """正序:step-1, step-2, step-3, step-4 → PASS。"""
        mod = _load_module()
        files = [
            tmp_path / "step-1-e2e-fail.md",
            tmp_path / "step-2-6layer.md",
            tmp_path / "step-3-fix-and-regression.md",
            tmp_path / "step-4-user-confirm.md",
        ]
        for f in files:
            f.write_text("x", encoding="utf-8")
        errors = mod.check_step_order_against_paths([str(f) for f in files])
        assert errors == [], f"正序应 PASS,实际: {errors}"

    def test_shuffled_order_fails(self, tmp_path):
        """乱序:step-2 给出 step-1 没 → FAIL(顺序错)。"""
        mod = _load_module()
        files = [
            tmp_path / "step-2-6layer.md",
            tmp_path / "step-1-e2e-fail.md",  # 乱的
            tmp_path / "step-3-fix-and-regression.md",
            tmp_path / "step-4-user-confirm.md",
        ]
        for f in files:
            f.write_text("x", encoding="utf-8")
        errors = mod.check_step_order_against_paths([str(f) for f in files])
        assert any("顺序与 P2_2_STEP_ORDER 不一致" in e for e in errors), (
            f"乱序应报顺序错,实际: {errors}"
        )

    def test_no_step_prefix_weak_pass(self, tmp_path):
        """C10:路径无 step-N 前缀 → 不强制顺序(弱校验通过)。"""
        mod = _load_module()
        files = [tmp_path / f"evidence-{i}.md" for i in range(4)]
        for f in files:
            f.write_text("x", encoding="utf-8")
        errors = mod.check_step_order_against_paths([str(f) for f in files])
        assert errors == [], f"无前缀路径应弱校验通过,实际: {errors}"


# ============================================================================
# CLI 端到端
# ============================================================================
class TestCliIntegration:
    def test_c1_strict_without_step_fails(self):
        """C1:--strict 缺 --step → FAIL exit 1。"""
        rc, out, _ = _run_cli("--strict")
        assert rc == 1
        assert "--strict" in out and "--step" in out

    def test_c5_step_without_strict_passes(self):
        """C5:--step step-1 不带 --strict → 默认 PASS(原 --step 行为)。"""
        rc, out, _ = _run_cli("--step", "step-1-e2e-fail")
        assert rc == 0, f"step-1 不带 strict 应 PASS,实际: {rc} {out}"
        assert "step-1-e2e-fail" in out

    def test_c9_nonexistent_step_fails(self):
        """C9:--step 不存在的 step → FAIL exit 1。"""
        rc, out, _ = _run_cli("--step", "step-99-fake")
        assert rc == 1, f"不存在的 step 应 FAIL,实际: {rc} {out}"

    def test_c2_strict_empty_paths_fails(self):
        """C2(CLI):--step step-4 --strict --evidence-paths 空 → FAIL exit 1。"""
        rc, out, _ = _run_cli("--step", "step-4-user-confirm", "--strict", "--evidence-paths", "")
        assert rc == 1, f"空 evidence_paths 应 FAIL,实际: {rc} {out}"
        assert "必须含 4 项" in out, f"输出应含数量错,实际: {out}"

    def test_c4_strict_4_files_pass(self, tmp_path):
        """C4(CLI):4 个文件齐全 + 顺序正确 → PASS exit 0。"""
        files = [
            tmp_path / "step-1-e2e-fail.md",
            tmp_path / "step-2-6layer.md",
            tmp_path / "step-3-fix-and-regression.md",
            tmp_path / "step-4-user-confirm.md",
        ]
        for f in files:
            f.write_text("evidence", encoding="utf-8")
        paths = ",".join(str(f) for f in files)
        rc, out, _ = _run_cli(
            "--step", "step-4-user-confirm",
            "--strict",
            "--evidence-paths", paths,
        )
        assert rc == 0, f"4 个文件齐 + 顺序正确应 PASS,实际: {rc} {out}"
        assert "strict PASS" in out

    def test_c6_strict_missing_files_fails(self, tmp_path):
        """C6(CLI):evidence_paths 前 3 项文件不存在 → FAIL exit 1。"""
        files = [
            tmp_path / "missing-1.md",
            tmp_path / "missing-2.md",
            tmp_path / "missing-3.md",
            tmp_path / "step-4-user-confirm.md",
        ]
        # 只造 step-4 文件
        files[3].write_text("step4", encoding="utf-8")
        paths = ",".join(str(f) for f in files)
        rc, out, _ = _run_cli(
            "--step", "step-4-user-confirm",
            "--strict",
            "--evidence-paths", paths,
        )
        assert rc == 1, f"前 3 项缺应 FAIL,实际: {rc} {out}"
        assert "step-1-e2e-fail" in out
        assert "step-2-6layer" in out
        assert "step-3-fix-and-regression" in out

    def test_c7_strict_shuffled_order_fails(self, tmp_path):
        """C7(CLI):evidence_paths 顺序乱 → FAIL exit 1。"""
        files = [
            tmp_path / "step-2-6layer.md",  # 乱
            tmp_path / "step-1-e2e-fail.md",  # 乱
            tmp_path / "step-3-fix-and-regression.md",
            tmp_path / "step-4-user-confirm.md",
        ]
        for f in files:
            f.write_text("x", encoding="utf-8")
        # 故意把顺序写乱:先给 step-2 路径、后给 step-1 路径
        paths = f"{files[0]},{files[1]},{files[2]},{files[3]}"
        rc, out, _ = _run_cli(
            "--step", "step-4-user-confirm",
            "--strict",
            "--evidence-paths", paths,
        )
        assert rc == 1, f"乱序应 FAIL,实际: {rc} {out}"
        assert "顺序与 P2_2_STEP_ORDER 不一致" in out, f"输出应含顺序错,实际: {out}"
