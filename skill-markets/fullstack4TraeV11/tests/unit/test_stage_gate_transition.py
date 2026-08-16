"""stage-gate.py --next-stage 转换校验单元测试。

覆盖 dimensions:
  - P0-2 反例固化:非法转换 → exit 2 + transition_check.valid=false
  - P0-2 PASS:合法转换 → exit 0 + transition_check.valid=true
  - 13 stage 全 PASS 转换路径（主线 11 + 支线 2 + 自身切换）
  - 13 stage 全 FAIL 反例（跨段非法跳跃 + 回退）
"""
from __future__ import annotations

import importlib.util
import pathlib
import sys
import tempfile
from pathlib import Path

import pytest

pytestmark = pytest.mark.unit

SCRIPT_DIR = Path(__file__).resolve().parents[2] / "scripts"
SCRIPT_PATH = SCRIPT_DIR / "stage-gate.py"


# ----------------------------------------------------------------------
# Helper — 写状态卡 fixture
# ----------------------------------------------------------------------
def _write_state_card(tmp_path: Path, current_stage: str) -> Path:
    """生成一张最小合法状态卡，current_stage 可变。"""
    card = tmp_path / ".state-card.md"
    card.write_text(
        f"""---
card_type: change
card_id: test-card
version: "1.0.0"
current_stage: {current_stage}
stage_status: working
stage_started_at: 2026-08-16T00:00:00
stage_ended_at: null
updated_at: 2026-08-16T00:00:00
updated_by: test
health: "🟢 on-track"
artifacts: []
visual_evidence:
  status: unverified
  screenshots: []
  verified_at: null
gate_result:
  status: PENDING
  gate: null
  output: null
  verified_at: null
next_stage:
  id: null
  skill_name: null
  expected_inputs: []
  prerequisites: []
blocked_by: null
actor: test
duration_minutes: 0
notes: ""
---
""",
        encoding="utf-8",
    )
    return card


def _run_stage_gate(state_card: Path, next_stage: str | None, project_root: Path | None = None):
    """通过 subprocess 调用 stage-gate.py，避免 import 副作用。"""
    import subprocess
    cmd = [
        sys.executable,
        str(SCRIPT_PATH),
        "--state-card", str(state_card),
        "--skip-env-check",
    ]
    if next_stage is not None:
        cmd += ["--next-stage", next_stage]
    if project_root is not None:
        cmd += ["--project-root", str(project_root)]
    return subprocess.run(cmd, capture_output=True, text=True)


# ============================================================================
# TestTransitionMatrix — 全 13 stage 合法 + 非法转换矩阵
# ============================================================================
# 合法转换主线（来自 state-machine.yaml transitions）
LEGAL_TRANSITIONS = [
    ("-1/intake", "0/plan"),
    ("0/plan", "0.5/test-plan"),
    ("0.5/test-plan", "1/spec"),
    ("1/spec", "1.5/prototype"),
    ("1.5/prototype", "2/contract"),
    ("2/contract", "3/implement"),
    ("3/implement", "3.5/real-verify"),
    ("3.5/real-verify", "4/review"),
    ("4/review", "4.5/rot-scan"),
    ("4.5/rot-scan", "5/accept"),
    # 支线
    ("3/implement", "6/bug-fix"),
    ("6/bug-fix", "7/health"),
    ("7/health", "5/accept"),
    ("7/health", "-1/intake"),
    ("6/bug-fix", "3/implement"),
    ("6/bug-fix", "5/accept"),
]

# 任意 stage 都可去 6/bug-fix / 7/health(P0-2 反复要的核心场景)
BUG_FIX_ALLOWED_FROM = [
    "-1/intake", "0/plan", "0.5/test-plan", "1/spec", "1.5/prototype",
    "2/contract", "3/implement", "3.5/real-verify", "4/review",
    "4.5/rot-scan",
]


class TestLegalTransitions:
    @pytest.mark.parametrize("from_stage,to_stage", LEGAL_TRANSITIONS)
    def test_legal_transition_passes(self, from_stage, to_stage, tmp_path):
        card = _write_state_card(tmp_path, from_stage)
        result = _run_stage_gate(card, to_stage)
        assert result.returncode == 0, (
            f"{from_stage} → {to_stage} 应 PASS，实际 exit={result.returncode} stderr={result.stderr}"
        )
        assert "✅ PASS" in result.stdout


class TestBugFixRoutes:
    @pytest.mark.parametrize("from_stage", BUG_FIX_ALLOWED_FROM)
    def test_to_bug_fix_legal(self, from_stage, tmp_path):
        card = _write_state_card(tmp_path, from_stage)
        result = _run_stage_gate(card, "6/bug-fix")
        assert result.returncode == 0, (
            f"{from_stage} → 6/bug-fix 应 PASS，stderr={result.stderr}"
        )


class TestIllegalTransitions:
    """核心反例固化：state-machine.yaml 无声明的转换 → exit 2。"""

    @pytest.mark.parametrize("from_stage,to_stage", [
        # 5/accept 是终态，无 allowed_transitions
        ("5/accept", "-1/intake"),
        ("5/accept", "0/plan"),
        ("5/accept", "3/implement"),
        # 反向跳跃
        ("-1/intake", "5/accept"),
        ("0/plan", "-1/intake"),
        ("4/review", "0/plan"),
        # 跨段跳跃
        ("-1/intake", "4/review"),
        ("0/plan", "4/review"),
        ("1/spec", "3/implement"),
        ("0.5/test-plan", "3/implement"),
        # 5/accept → 任何
        ("5/accept", "0/plan"),
        # 8/health 不存在（验证未知状态拦截）
        ("0/plan", "8/nonexistent"),
    ])
    def test_illegal_transition_fails(self, from_stage, to_stage, tmp_path):
        card = _write_state_card(tmp_path, from_stage)
        result = _run_stage_gate(card, to_stage)
        assert result.returncode == 2, (
            f"{from_stage} → {to_stage} 应 exit 2（transition FAIL），"
            f"实际 exit={result.returncode}, stdout={result.stdout[:200]}"
        )
        assert "transition FAIL" in result.stdout, (
            f"应输出 transition FAIL，实际 stdout={result.stdout[:300]}"
        )


class TestNoNextStage:
    def test_no_next_stage_still_works(self, tmp_path):
        """不传 --next-stage → 跳过转换校验,只做字段校验。"""
        card = _write_state_card(tmp_path, "3/implement")
        result = _run_stage_gate(card, None)
        # 字段合法 → PASS
        assert result.returncode == 0
        assert "✅ PASS" in result.stdout


class TestProjectRegistryAutoDetect:
    def test_project_registry_auto_detect(self, tmp_path):
        """项目级 .trae/registry/ 自动探测生效。"""
        # 准备项目级 registry
        proj_reg = tmp_path / ".trae" / "registry"
        proj_reg.mkdir(parents=True)
        # copy V11 内置 state-machine.yaml
        v11_reg = SCRIPT_DIR.parent / "registry"
        (proj_reg / "state-machine.yaml").write_bytes(
            (v11_reg / "state-machine.yaml").read_bytes()
        )

        card = _write_state_card(tmp_path, "0/plan")
        result = _run_stage_gate(card, "0.5/test-plan", project_root=tmp_path)
        assert result.returncode == 0, f"stderr={result.stderr}"