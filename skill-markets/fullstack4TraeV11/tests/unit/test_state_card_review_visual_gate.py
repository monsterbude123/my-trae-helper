"""state-card-validator.py P2-1 扩展校验单元测试。

覆盖 P2-1 修复:进入 4/review 时校验 visual_evidence.status = verified
(原 L121-130 仅在 3.5/real-verify + 3/implement completed 时校验,
缺 4/review 进入点,导致 reviewer 拿到未 verified 的状态卡)。

测试维度:
  - C1 3.5/real-verify + visual_evidence.status=unverified → FAIL (保持原有行为)
  - C2 3.5/real-verify + visual_evidence.status=verified → PASS (保持原有行为)
  - C3 3/implement + stage_status=completed + visual_evidence.status=unverified → FAIL
  - C4 4/review + visual_evidence.status=pending → FAIL (P2-1 主要修复)
  - C5 4/review + visual_evidence.status=verified → PASS (P2-1 期望结果)
  - C6 4/review + visual_evidence 缺 (None) → FAIL (P2-1 边界)
  - C7 4/review + visual_evidence.status=skipped → FAIL (P2-1 边界)
  - C8 5/accept + visual_evidence 缺 → PASS (本条不强制,验证非目标 stage 不受影响)
  - C9 4/review 错误消息含 "正确示例" 关键字 (P2-1 明确要求)
"""
from __future__ import annotations

import importlib.util
import sys
from datetime import datetime, timezone
from pathlib import Path

import pytest

pytestmark = pytest.mark.unit

SCRIPT_DIR = Path(__file__).resolve().parents[2] / "scripts"
SCRIPT_PATH = SCRIPT_DIR / "state-card-validator.py"


def _load_validator():
    spec = importlib.util.spec_from_file_location(
        "state_card_validator_p2_1", SCRIPT_PATH
    )
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _format_value(v) -> str:
    if v is None:
        return "null"
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, str) and any(ch in v for ch in [":", "#"]):
        return f'"{v}"'
    return str(v)


def _write_card(tmp_path: Path, fields: dict) -> Path:
    """写一张最小状态卡 + 覆盖字段。"""
    card = tmp_path / ".state-card.md"
    lines = ["---"]
    base = {
        "card_type": "change",
        "card_id": "test-card-p2-1",
        "version": "1.0.0",
        "current_stage": "3/implement",
        "stage_status": "working",
        "stage_started_at": datetime.now(timezone.utc).isoformat(),
        "stage_ended_at": None,
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "updated_by": "test",
        "health": "�� on-track",
        "artifacts": [],
        "visual_evidence": {
            "status": "unverified",
            "screenshots": [],
            "verified_at": None,
        },
        "gate_result": {"status": "PENDING", "gate": None, "output": None, "verified_at": None},
        "next_stage": {"id": None, "skill_name": None, "expected_inputs": [], "prerequisites": []},
        "blocked_by": None,
        "actor": "test",
        "duration_minutes": 0,
        "notes": "P2-1 fixture",
    }
    base.update(fields)
    for k, v in base.items():
        if isinstance(v, dict):
            lines.append(f"{k}:")
            for kk, vv in v.items():
                lines.append(f"  {kk}: {_format_value(vv)}")
        elif isinstance(v, list):
            lines.append(f"{k}:")
            for item in v:
                if isinstance(item, dict):
                    lines.append(f"  - ")
                    for kk, vv in item.items():
                        lines.append(f"    {kk}: {_format_value(vv)}")
                else:
                    lines.append(f"  - {_format_value(item)}")
        else:
            lines.append(f"{k}: {_format_value(v)}")
    lines.append("---")
    card.write_text("\n".join(lines), encoding="utf-8")
    return card


def _has_visual_evidence_error(errors: list) -> bool:
    return any("visual_evidence.status" in e for e in errors)


# ============================================================================
# TestP21RevisitOriginalBehavior — 3.5/3 原有行为不破坏
# ============================================================================
class TestP21RevisitOriginalBehavior:
    def test_3_5_with_unverified_fails(self, tmp_path):
        """C1:3.5/real-verify + status=unverified → FAIL (保持原有)。"""
        mod = _load_validator()
        card = _write_card(tmp_path, {
            "current_stage": "3.5/real-verify",
            "visual_evidence": {
                "status": "unverified",
                "screenshots": [],
                "verified_at": None,
            },
        })
        errors = mod.validate_fields(mod.parse_state_card(card))
        assert _has_visual_evidence_error(errors), (
            f"3.5 + unverified 应 FAIL,实际: {errors}"
        )

    def test_3_5_with_verified_passes(self, tmp_path):
        """C2:3.5/real-verify + status=verified → PASS (保持原有)。"""
        mod = _load_validator()
        card = _write_card(tmp_path, {
            "current_stage": "3.5/real-verify",
            "visual_evidence": {
                "status": "verified",
                "screenshots": [{
                    "path": "shots/x.png",
                    "contains_change_components": True,
                    "interactive_proof": "clicked",
                    "read_by_main_context": True,
                }],
                "verified_at": datetime.now(timezone.utc).isoformat(),
            },
        })
        errors = mod.validate_fields(mod.parse_state_card(card))
        assert not _has_visual_evidence_error(errors), (
            f"3.5 + verified 应 PASS,实际: {errors}"
        )

    def test_3_implement_completed_unverified_fails(self, tmp_path):
        """C3:3/implement + stage_status=completed + unverified → FAIL (保持原有)。"""
        mod = _load_validator()
        card = _write_card(tmp_path, {
            "current_stage": "3/implement",
            "stage_status": "completed",
            "stage_ended_at": datetime.now(timezone.utc).isoformat(),
            "visual_evidence": {
                "status": "unverified",
                "screenshots": [],
                "verified_at": None,
            },
        })
        errors = mod.validate_fields(mod.parse_state_card(card))
        assert _has_visual_evidence_error(errors), (
            f"3 implement completed + unverified 应 FAIL,实际: {errors}"
        )


# ============================================================================
# TestP21NewReviewGate — 4/review 进入点校验 (P2-1 新增)
# ============================================================================
class TestP21NewReviewGate:
    def test_4_review_pending_fails(self, tmp_path):
        """C4:4/review + status=pending → FAIL (P2-1 主要修复)。"""
        mod = _load_validator()
        card = _write_card(tmp_path, {
            "current_stage": "4/review",
            "stage_status": "working",
            "visual_evidence": {
                "status": "pending",
                "screenshots": [],
                "verified_at": None,
            },
        })
        errors = mod.validate_fields(mod.parse_state_card(card))
        assert _has_visual_evidence_error(errors), (
            f"4/review + pending 应 FAIL,实际: {errors}"
        )

    def test_4_review_verified_passes(self, tmp_path):
        """C5:4/review + status=verified → PASS (P2-1 期望结果)。"""
        mod = _load_validator()
        card = _write_card(tmp_path, {
            "current_stage": "4/review",
            "stage_status": "working",
            "visual_evidence": {
                "status": "verified",
                "screenshots": [{
                    "path": "shots/x.png",
                    "contains_change_components": True,
                    "interactive_proof": "clicked",
                    "read_by_main_context": True,
                }],
                "verified_at": datetime.now(timezone.utc).isoformat(),
            },
        })
        errors = mod.validate_fields(mod.parse_state_card(card))
        assert not _has_visual_evidence_error(errors), (
            f"4/review + verified 应 PASS,实际: {errors}"
        )

    def test_4_review_missing_evidence_fails(self, tmp_path):
        """C6:4/review + visual_evidence 缺(None) → FAIL (P2-1 边界)。"""
        mod = _load_validator()
        card = _write_card(tmp_path, {
            "current_stage": "4/review",
            "stage_status": "working",
            "visual_evidence": None,
        })
        errors = mod.validate_fields(mod.parse_state_card(card))
        assert _has_visual_evidence_error(errors), (
            f"4/review + 缺 visual_evidence 应 FAIL,实际: {errors}"
        )

    def test_4_review_skipped_fails(self, tmp_path):
        """C7:4/review + status=skipped → FAIL (P2-1 边界,confirmed 不可跳过)。"""
        mod = _load_validator()
        card = _write_card(tmp_path, {
            "current_stage": "4/review",
            "stage_status": "working",
            "visual_evidence": {
                "status": "skipped",
                "screenshots": [],
                "verified_at": None,
            },
        })
        errors = mod.validate_fields(mod.parse_state_card(card))
        assert _has_visual_evidence_error(errors), (
            f"4/review + skipped 应 FAIL,实际: {errors}"
        )

    def test_5_accept_missing_evidence_passes(self, tmp_path):
        """C8:5/accept + visual_evidence 缺 → PASS (本条不强制,验证非目标 stage 不受影响)。"""
        mod = _load_validator()
        card = _write_card(tmp_path, {
            "current_stage": "5/accept",
            "stage_status": "working",
            "visual_evidence": None,
        })
        errors = mod.validate_fields(mod.parse_state_card(card))
        assert not _has_visual_evidence_error(errors), (
            f"5/accept + 缺 visual_evidence 应 PASS(本条不强制),实际: {errors}"
        )

    def test_4_review_error_message_contains_example(self, tmp_path):
        """C9:4/review 错误消息含 '正确示例' 关键字 (P2-1 明确要求)。"""
        mod = _load_validator()
        card = _write_card(tmp_path, {
            "current_stage": "4/review",
            "stage_status": "working",
            "visual_evidence": {
                "status": "pending",
                "screenshots": [],
                "verified_at": None,
            },
        })
        errors = mod.validate_fields(mod.parse_state_card(card))
        visual_errors = [e for e in errors if "visual_evidence.status" in e]
        assert len(visual_errors) >= 1
        assert "正确示例" in visual_errors[0], (
            f"4/review 错误消息应含 '正确示例',实际: {visual_errors[0]}"
        )
        # 错误消息应指明 4/review 上下文
        assert "4/review" in visual_errors[0], (
            f"4/review 错误消息应提及 4/review,实际: {visual_errors[0]}"
        )


# ============================================================================
# TestP21CliIntegration — CLI 端到端
# ============================================================================
class TestP21CliIntegration:
    def test_cli_4_review_pending_exits_1(self, tmp_path):
        """CLI 集成:4/review + pending → subprocess exit 1。"""
        import subprocess
        card = tmp_path / "card.md"
        now = datetime.now(timezone.utc).isoformat()
        card.write_text(
            f"""---
card_type: change
card_id: cli-review-pending
version: "1.0.0"
current_stage: 4/review
stage_status: working
stage_started_at: {now}
stage_ended_at: null
updated_at: {now}
updated_by: test
health: "�� on-track"
artifacts: []
visual_evidence:
  status: pending
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
notes: "P2-1 CLI 真反例"
---
""",
            encoding="utf-8",
        )
        result = subprocess.run(
            [sys.executable, str(SCRIPT_PATH), str(card)],
            capture_output=True, text=True,
        )
        assert result.returncode == 1, (
            f"4/review + pending 应 exit 1,实际 {result.returncode}: {result.stdout}"
        )
        assert "visual_evidence.status" in result.stdout, (
            f"输出应含 visual_evidence.status 错误,实际: {result.stdout}"
        )

    def test_cli_4_review_verified_exits_0(self, tmp_path):
        """CLI 集成:4/review + verified → subprocess exit 0。"""
        import subprocess
        card = tmp_path / "card.md"
        now = datetime.now(timezone.utc).isoformat()
        card.write_text(
            f"""---
card_type: change
card_id: cli-review-verified
version: "1.0.0"
current_stage: 4/review
stage_status: working
stage_started_at: {now}
stage_ended_at: null
updated_at: {now}
updated_by: test
health: "�� on-track"
artifacts: []
visual_evidence:
  status: verified
  screenshots:
    - path: shots/x.png
      contains_change_components: true
      interactive_proof: "clicked"
      read_by_main_context: true
  verified_at: {now}
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
notes: "P2-1 CLI PASS"
---
""",
            encoding="utf-8",
        )
        result = subprocess.run(
            [sys.executable, str(SCRIPT_PATH), str(card)],
            capture_output=True, text=True,
        )
        assert result