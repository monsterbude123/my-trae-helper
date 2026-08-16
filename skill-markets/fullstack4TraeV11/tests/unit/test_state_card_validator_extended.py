"""state-card-validator.py P1-2 扩展校验单元测试。

覆盖 dimensions:
  - C1 stage_status=completed 缺 stage_ended_at → FAIL
  - C2 card_type=bug 缺 bug_severity → FAIL
  - C2 card_type=bug bug_severity 非法 → FAIL
  - C3 parent_change 引用不存在 → FAIL (--project-root 模式下)
  - C4 visual_evidence.screenshots[].read_by_main_context=false → FAIL
  - C5 reset_history 缺 5 子字段 → FAIL
  - PASS:有效 fixture 全部字段齐 → PASS
"""
from __future__ import annotations

import importlib.util
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

import pytest

pytestmark = pytest.mark.unit

SCRIPT_DIR = Path(__file__).resolve().parents[2] / "scripts"
SCRIPT_PATH = SCRIPT_DIR / "state-card-validator.py"


def _load_validator():
    spec = importlib.util.spec_from_file_location(
        "state_card_validator", SCRIPT_PATH
    )
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _write_card(tmp_path: Path, fields: dict) -> Path:
    """写一张最小状态卡 + 覆盖字段。"""
    card = tmp_path / ".state-card.md"
    lines = ["---"]
    # 完整字段集(给基础字段合法值)
    base = {
        "card_type": "change",
        "card_id": "test-card",
        "version": "1.0.0",
        "current_stage": "3/implement",
        "stage_status": "working",
        "stage_started_at": datetime.now(timezone.utc).isoformat(),
        "stage_ended_at": None,
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "updated_by": "test",
        "health": "🟢 on-track",
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
        "notes": "测试 fixture",
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


def _format_value(v) -> str:
    if v is None:
        return "null"
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, str) and any(ch in v for ch in [":", "#"]):
        return f'"{v}"'
    return str(v)


# ============================================================================
# TestCompletedStageEndedAt — C1
# ============================================================================
class TestCompletedStageEndedAt:
    def test_completed_without_ended_at_fails(self, tmp_path):
        """反例:stage_status=completed 但 stage_ended_at 为 null → FAIL。"""
        mod = _load_validator()
        card = _write_card(tmp_path, {
            "stage_status": "completed",
            "stage_ended_at": None,
        })
        errors = mod.validate_fields(
            mod.parse_state_card(card),
        )
        assert any("stage_ended_at" in e for e in errors), (
            f"应输出 stage_ended_at 错误，实际: {errors}"
        )

    def test_completed_with_ended_at_passes(self, tmp_path):
        """PASS:stage_status=completed + stage_ended_at 有值 → 不报错。"""
        mod = _load_validator()
        card = _write_card(tmp_path, {
            "stage_status": "completed",
            "stage_ended_at": datetime.now(timezone.utc).isoformat(),
        })
        errors = mod.validate_fields(
            mod.parse_state_card(card),
        )
        assert not any("stage_ended_at 必填" in e for e in errors)


# ============================================================================
# TestBugSeverity — C2
# ============================================================================
class TestBugSeverity:
    def test_bug_without_severity_fails(self, tmp_path):
        """反例:card_type=bug 但 bug_severity 缺 → FAIL。"""
        mod = _load_validator()
        card = _write_card(tmp_path, {
            "card_type": "bug",
            "current_stage": "6/bug-fix",
            # bug_severity 缺失
        })
        errors = mod.validate_fields(mod.parse_state_card(card))
        assert any("bug_severity" in e for e in errors)

    def test_bug_with_invalid_severity_fails(self, tmp_path):
        """反例:bug_severity 非法值 → FAIL。"""
        mod = _load_validator()
        card = _write_card(tmp_path, {
            "card_type": "bug",
            "current_stage": "6/bug-fix",
            "bug_severity": "P9",  # 非法
        })
        errors = mod.validate_fields(mod.parse_state_card(card))
        assert any("bug_severity 非法" in e for e in errors)

    def test_bug_with_valid_severity_passes(self, tmp_path):
        """PASS:bug_severity ∈ {P0, P1, P2, P3} → 不报错。"""
        mod = _load_validator()
        for sev in ["P0", "P1", "P2", "P3"]:
            card = _write_card(tmp_path, {
                "card_type": "bug",
                "current_stage": "6/bug-fix",
                "bug_severity": sev,
            })
            errors = mod.validate_fields(mod.parse_state_card(card))
            assert not any("bug_severity" in e for e in errors), (
                f"P{sev} 应 PASS，实际 errors: {errors}"
            )


# ============================================================================
# TestParentChangeReference — C3
# ============================================================================
class TestParentChangeReference:
    def test_parent_change_missing_file_fails(self, tmp_path):
        """反例:parent_change 引用文件不存在 → FAIL。"""
        mod = _load_validator()
        # 制造一个项目根 + 一个 changes/{id}/ 目录
        proj = tmp_path / "project"
        proj.mkdir()
        changes_dir = proj / "docs" / "specs" / "changes"
        changes_dir.mkdir(parents=True)
        # parent_change 指向不存在的 change
        card = _write_card(tmp_path, {
            "parent_change": "non-existent-change-id",
        })
        errors = mod.validate_fields(
            mod.parse_state_card(card),
            parent_card_path=proj,
        )
        assert any("parent_change" in e for e in errors)

    def test_parent_change_existing_file_passes(self, tmp_path):
        """PASS:parent_change 指向真实存在的 change 卡 → 不报错。"""
        mod = _load_validator()
        proj = tmp_path / "project"
        proj.mkdir()
        change_dir = proj / "docs" / "specs" / "changes" / "real-change"
        change_dir.mkdir(parents=True)
        # 写一个真实 parent 卡(只有占位)
        (change_dir / ".state-card.md").write_text(
            "---\ncard_type: change\ncard_id: real-change\n---\n",
            encoding="utf-8",
        )
        card = _write_card(tmp_path, {"parent_change": "real-change"})
        errors = mod.validate_fields(
            mod.parse_state_card(card),
            parent_card_path=proj,
        )
        assert not any("parent_change" in e for e in errors)


# ============================================================================
# TestVisualEvidenceReadByMainContext — C4
# ============================================================================
class TestVisualEvidenceReadByMainContext:
    def test_screenshot_without_read_by_main_fails(self, tmp_path):
        """反例:screenshots[].read_by_main_context=false → FAIL。"""
        mod = _load_validator()
        card = _write_card(tmp_path, {
            "visual_evidence": {
                "status": "verified",
                "screenshots": [{
                    "path": "shots/x.png",
                    "contains_change_components": True,
                    "interactive_proof": "clicked",
                    "read_by_main_context": False,
                }],
                "verified_at": "2026-08-16T00:00:00",
            },
        })
        errors = mod.validate_fields(mod.parse_state_card(card))
        assert any("read_by_main_context" in e for e in errors)

    def test_screenshot_with_read_by_main_passes(self, tmp_path):
        """PASS:read_by_main_context=true → 不报错。"""
        mod = _load_validator()
        card = _write_card(tmp_path, {
            "visual_evidence": {
                "status": "verified",
                "screenshots": [{
                    "path": "shots/x.png",
                    "contains_change_components": True,
                    "interactive_proof": "clicked",
                    "read_by_main_context": True,
                }],
                "verified_at": "2026-08-16T00:00:00",
            },
        })
        errors = mod.validate_fields(mod.parse_state_card(card))
        assert not any("read_by_main_context" in e for e in errors)


# ============================================================================
# TestResetHistory — C5
# ============================================================================
class TestResetHistory:
    def test_reset_history_missing_keys_fails(self, tmp_path):
        """反例:reset_history 缺 5 子字段 → FAIL。"""
        mod = _load_validator()
        card = _write_card(tmp_path, {
            "reset_history": [
                {"date": "2026-08-12T15:00:00", "from_stage": "5/accept"}
                # 缺 to_stage / reason / reset_by
            ],
        })
        errors = mod.validate_fields(mod.parse_state_card(card))
        assert any("reset_history" in e for e in errors)

    def test_reset_history_complete_passes(self, tmp_path):
        """PASS:reset_history 含 5 子字段 → 不报错。"""
        mod = _load_validator()
        card = _write_card(tmp_path, {
            "reset_history": [{
                "date": "2026-08-12T15:00:00",
                "from_stage": "5/accept",
                "to_stage": "-1/intake",
                "reason": "用户强制重置",
                "reset_by": "user",
            }],
        })
        errors = mod.validate_fields(mod.parse_state_card(card))
        assert not any("reset_history" in e for e in errors)


# ============================================================================
# TestCliIntegration
# ============================================================================
class TestCliIntegration:
    def test_cli_complete_card_passes(self, tmp_path):
        """PASS:完整合法状态卡 → exit 0。"""
        import subprocess
        # 准备一张完整卡
        card = tmp_path / "complete.md"
        card.write_text(
            f"""---
card_type: change
card_id: complete-card
version: "1.0.0"
current_stage: 3/implement
stage_status: working
stage_started_at: {datetime.now(timezone.utc).isoformat()}
stage_ended_at: null
updated_at: {datetime.now(timezone.utc).isoformat()}
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
notes: "fixture"
---
""",
            encoding="utf-8",
        )
        result = subprocess.run(
            [sys.executable, str(SCRIPT_PATH), str(card)],
            capture_output=True, text=True,
        )
        assert result.returncode == 0, f"完整卡应 PASS,实际 {result.returncode}: {result.stdout}"