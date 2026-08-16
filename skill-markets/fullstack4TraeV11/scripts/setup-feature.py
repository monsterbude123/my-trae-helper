#!/usr/bin/env python3
"""
V11 setup-feature.py — 创建 change 骨架（Stage -1 Intake 必走）

Usage:
    python setup-feature.py --change-id <id> [--project-root <path>]

生成:
  docs/specs/changes/{change-id}/
    ├── spec.md（空模板）
    ├── plan.md（空模板）
    ├── .state-card.md
    └── contracts/（空目录）

Exit codes:
    0 = PASS
    1 = FAIL
"""
import sys
import argparse
import pathlib
import json
import yaml
from datetime import datetime, timezone


STATE_CARD_TEMPLATE = """---
card_type: change
card_id: {change_id}
version: "1.0.0"
current_stage: -1/intake
stage_status: pending
stage_started_at: {now}
stage_ended_at: null
updated_at: {now}
updated_by: 主上下文
health: "🟢 on-track"
artifacts:
  - path: docs/specs/changes/{change_id}/.state-card.md
    type: file
    exists: true
    evidence: "Stage -1 Intake 初始化"
gate_result:
  status: PENDING
  gate: stage-gate.py
  output: null
  verified_at: null
next_stage:
  id: 0/plan
  skill_name: skills/02-plan/SKILL.md
  expected_inputs: [intent_class, project_convention]
  prerequisites: [intake_complete]
blocked_by: null
actor: 主上下文
duration_minutes: 0
parent_change: null
related_changes: []
risk_level: LOW
priority: P1
notes: |
  Change 骨架初始化
---

# State Card: {change_id}

> 自动生成，请勿手动编辑（用 stage-gate.py 更新）
"""


SPEC_TEMPLATE = """# Spec: {change_id}

## Acceptance Criteria

- AC-1:
- AC-2:

## Invariants (INV)

- INV-1:

## Edge Cases

- EC-1:

---
*待 Stage 1  填充*
"""

PLAN_TEMPLATE = """# Plan: {change_id}

## Capabilities

- CAP-1:

## Non-Goals

- NG-1:

## 3 路径评估

1. 路径 A:
2. 路径 B:
3. 路径 C:

---
*待 Stage 0  填充*
"""


def create_feature(change_id: str, project_root: pathlib.Path) -> dict:
    """创建 change 骨架"""
    change_dir = project_root / f"docs/specs/changes/{change_id}"

    if change_dir.exists():
        return {"status": "FAIL", "message": f"change 已存在: {change_dir}"}

    change_dir.mkdir(parents=True, exist_ok=True)
    (change_dir / "contracts").mkdir(exist_ok=True)

    now = datetime.now(timezone.utc).isoformat()

    # 写 spec.md
    (change_dir / "spec.md").write_text(
        SPEC_TEMPLATE.format(change_id=change_id), encoding="utf-8"
    )

    # 写 plan.md
    (change_dir / "plan.md").write_text(
        PLAN_TEMPLATE.format(change_id=change_id), encoding="utf-8"
    )

    # 写 .state-card.md
    state_card_path = change_dir / ".state-card.md"
    state_card_content = STATE_CARD_TEMPLATE.format(change_id=change_id, now=now)
    state_card_path.write_text(state_card_content, encoding="utf-8")

    # P3-6 NEW: 写状态卡后必调 audit_state_card_change() → 写 .trae/logs/state-card-audit.jsonl
    # 防止 setup-feature.py 绕过审计。失败不阻断主流程(best-effort,记录到 stderr)。
    try:
        sys.path.insert(0, str(pathlib.Path(__file__).parent))
        from _lib_state_card import audit_state_card_change
        audit_state_card_change(
            path=state_card_path,
            operation="create",
            actor="setup-feature.py",
            content_after=state_card_content,
            project_root=project_root,
        )
    except Exception as e:
        sys.stderr.write(f"[setup-feature] WARN: audit_state_card_change 失败(不阻断): {e}\n")

    return {
        "status": "PASS",
        "change_id": change_id,
        "path": str(change_dir),
        "artifacts": [
            "spec.md",
            "plan.md",
            ".state-card.md",
            "contracts/",
        ],
    }


def main():
    parser = argparse.ArgumentParser(description="V11 setup-feature 创建 change 骨架")
    parser.add_argument("--change-id", required=True, help="change ID（如 2026-08-11-add-feature）")
    parser.add_argument("--project-root", default=".", help="项目根路径")
    parser.add_argument("--json", action="store_true", help="JSON 输出")
    args = parser.parse_args()

    project_root = pathlib.Path(args.project_root).resolve()
    result = create_feature(args.change_id, project_root)

    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        icon = "✅" if result["status"] == "PASS" else "❌"
        print(f"{icon} {result['status']} — {result.get('path', result.get('message'))}")
        for art in result.get("artifacts", []):
            print(f"   - {art}")

    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())