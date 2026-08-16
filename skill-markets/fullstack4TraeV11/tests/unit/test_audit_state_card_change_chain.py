"""audit_state_card_change 串接测试(P3-6 NEW)。

覆盖维度:
  - setup-feature.py 创建一个 change → .trae/logs/state-card-audit.jsonl 有新记录
  - 直接 Edit 状态卡(跳过 setup-feature.py)+ state-card-validator.py --strict-audit → FAIL 含 audit log 缺失
  - setup-feature.py 写后 + state-card-validator.py --strict-audit → PASS
  - change-status.py read 也会记录 audit
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

pytestmark = pytest.mark.unit

SETUP_FEATURE = Path(__file__).resolve().parents[2] / "scripts" / "setup-feature.py"
CHANGE_STATUS = Path(__file__).resolve().parents[2] / "scripts" / "change-status.py"
STATE_CARD_VALIDATOR = Path(__file__).resolve().parents[2] / "scripts" / "state-card-validator.py"


def _run(script: Path, args, cwd: Path | None = None) -> tuple:
    return subprocess.run(
        [sys.executable, str(script), *args],
        cwd=str(cwd) if cwd else None,
        capture_output=True,
        text=True,
        check=False,
        timeout=30,
    )


# ============================================================================
# TestSetupFeatureAuditChain
# ============================================================================
class TestSetupFeatureAuditChain:
    def test_setup_feature_writes_audit_log(self, tmp_path):
        """PASS:跑 setup-feature.py 创建一个 change → audit log 有新记录。"""
        result = _run(SETUP_FEATURE, ["--change-id", "test-audit-001", "--project-root", str(tmp_path)])
        assert result.returncode == 0, f"setup-feature FAIL: {result.stdout}\n{result.stderr}"

        audit_log = tmp_path / ".trae/logs/state-card-audit.jsonl"
        assert audit_log.exists(), f"audit log 未创建: {audit_log}"

        content = audit_log.read_text(encoding="utf-8")
        assert "test-audit-001" in content, f"audit log 缺 change_id: {content}"
        assert '"operation": "create"' in content, f"operation 字段非 create: {content}"


# ============================================================================
# TestStrictAuditOnGhostWrite
# ============================================================================
class TestStrictAuditOnGhostWrite:
    def test_strict_audit_fails_when_no_audit_log(self, tmp_path):
        """FAIL:直接 Edit 状态卡(跳过 setup-feature.py)→ --strict-audit FAIL。"""
        # 1) 手动建状态卡(跳过 setup-feature,模拟 ghost write)
        change_dir = tmp_path / "docs/specs/changes/ghost-write"
        change_dir.mkdir(parents=True)
        state_card = change_dir / ".state-card.md"
        state_card.write_text(
            "---\n"
            "card_type: change\n"
            "card_id: ghost-write\n"
            "current_stage: -1/intake\n"
            "stage_status: pending\n"
            "stage_started_at: 2026-08-16T00:00:00+00:00\n"
            "updated_at: 2026-08-16T00:00:00+00:00\n"
            "updated_by: main\n"
            "health: '🟢 on-track'\n"
            "artifacts: []\n"
            "gate_result:\n"
            "  status: PENDING\n"
            "  gate: stage-gate.py\n"
            "next_stage:\n"
            "  id: 0/plan\n"
            "actor: main\n"
            "duration_minutes: 0\n"
            "notes: ghost write test\n"
            "---\n"
            "# State Card\n",
            encoding="utf-8",
        )
        # 2) 跑 --strict-audit(此时 .trae/logs/state-card-audit.jsonl 不存在)
        result = _run(STATE_CARD_VALIDATOR, [
            str(state_card),
            "--project-root", str(tmp_path),
            "--strict-audit",
        ])
        assert result.returncode == 1, f"期望 FAIL,实际 exit {result.returncode}: {result.stdout}"
        assert "audit log" in result.stdout.lower() or "audit_state_card_change" in result.stdout.lower(), \
            f"未含 audit log 错误信息: {result.stdout}"

    def test_strict_audit_passes_after_setup_feature(self, tmp_path):
        """PASS:setup-feature 写后,state-card-validator --strict-audit PASS。"""
        # 1) 跑 setup-feature 创建(会自动写 audit log)
        result = _run(SETUP_FEATURE, ["--change-id", "test-strict-pass", "--project-root", str(tmp_path)])
        assert result.returncode == 0

        # 2) 跑 state-card-validator --strict-audit
        state_card = tmp_path / "docs/specs/changes/test-strict-pass/.state-card.md"
        result = _run(STATE_CARD_VALIDATOR, [
            str(state_card),
            "--project-root", str(tmp_path),
            "--strict-audit",
        ])
        assert result.returncode == 0, f"期望 PASS,实际 {result.returncode}: {result.stdout}\n{result.stderr}"

    def test_change_status_records_audit_read(self, tmp_path):
        """PASS:跑 setup-feature → change-status read 也会记录 audit。"""
        # 1) setup-feature 写
        _run(SETUP_FEATURE, ["--change-id", "test-read-audit", "--project-root", str(tmp_path)])

        # 2) change-status read
        result = _run(CHANGE_STATUS, ["--change-id", "test-read-audit", "--project-root", str(tmp_path)])
        assert result.returncode == 0, result.stderr

        # 3) audit log 应含 'read-via-change-status'
        audit_log = tmp_path / ".trae/logs/state-card-audit.jsonl"
        content = audit_log.read_text(encoding="utf-8")
        assert "read-via-change-status" in content, \
            f"change-status 未记录 audit: {content}"