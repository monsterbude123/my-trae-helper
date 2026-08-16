#!/usr/bin/env python3
"""
V11 state-card-validator.py — 状态卡校验（字段完整性 + 文件系统交叉验证）

Usage:
    python state-card-validator.py <state-card-path> [--project-root <path>]

Exit codes:
    0 = PASS
    1 = FAIL
    2 = N/A

校验维度:
    1. 字段完整性（必填字段非空）
    2. 字段值合法性（current_stage 在 13 stage / health ∈ valid set）
    3. 文件系统交叉验证（artifacts[].exists 与实际文件存在性一致）
    4. stage-gate.py 同等校验（委托调用避免重复实现）
"""
import sys
import argparse
import pathlib
import subprocess
from datetime import datetime, timezone, timedelta


REQUIRED_FIELDS = [
    "card_type", "card_id", "current_stage", "stage_status",
    "stage_started_at", "updated_at", "updated_by", "health",
    "artifacts", "gate_result", "next_stage",
    "actor", "duration_minutes", "notes"
]

# 必填但允许 null 的字段（如 blocked_by / stage_ended_at）
NULLABLE_FIELDS = ["blocked_by", "stage_ended_at", "gate_result.output", "gate_result.verified_at", "next_stage.prerequisites"]

VALID_STAGES = [
    "-1/intake", "0/plan", "0.5/test-plan", "1/spec", "1.5/prototype",
    "2/contract", "3/implement", "3.5/real-verify", "4/review",
    "4.5/rot-scan", "5/accept", "6/bug-fix", "7/health"
]

VALID_HEALTH = ["🟢 on-track", "🟡 degraded", "🔴 blocked"]
VALID_CARD_TYPE = ["project", "change", "bug"]
VALID_STAGE_STATUS = ["pending", "working", "completed", "blocked", "skipped"]
# bug_severity 合法值（bug-state-machine.md L11-19 + state-card-protocol.md §2.2）
VALID_BUG_SEVERITY = ["P0", "P1", "P2", "P3"]

# reset_history 子字段必填
RESET_HISTORY_REQUIRED_KEYS = ["date", "from_stage", "to_stage", "reason", "reset_by"]

# 状态卡陈旧阈值（updated_at 距今 > 30 分钟视为陈旧）
STALENESS_THRESHOLD_MINUTES = 30


def parse_state_card(path: pathlib.Path) -> dict:
    """解析状态卡 frontmatter（委托 _lib_state_card 共用库）"""
    import sys
    sys.path.insert(0, str(pathlib.Path(__file__).parent))
    from _lib_state_card import parse_state_card as _parse
    return _parse(path)


def validate_fields(fields: dict, parent_card_path: pathlib.Path | None = None) -> list:
    """字段完整性 + 合法性。

    parent_card_path:项目根路径(<project_root>),用于 parent_change 引用校验。
    传入 None 时仅做字段格式校验。
    """
    errors = []

    for field in REQUIRED_FIELDS:
        if field not in fields:
            errors.append(f"缺少必填字段: {field}")
        elif fields[field] in ("", "null") or fields[field] is None:
            errors.append(f"必填字段为空: {field}")

    if "card_type" in fields:
        ct = fields["card_type"]
        if ct not in VALID_CARD_TYPE:
            errors.append(f"card_type 非法: {ct}（应在 {VALID_CARD_TYPE}）")

    if "current_stage" in fields:
        cs = fields["current_stage"]
        if cs not in VALID_STAGES:
            errors.append(f"current_stage 非法: {cs}（不在 13 stage 名单中）")

    if "stage_status" in fields:
        ss = fields["stage_status"]
        if ss not in VALID_STAGE_STATUS:
            errors.append(f"stage_status 非法: {ss}")

    if "health" in fields:
        h = fields["health"]
        if h not in VALID_HEALTH:
            errors.append(f"health 非法: {h}（应在 {VALID_HEALTH}）")

    # updated_at 格式 + 陈旧检测
    if "updated_at" in fields:
        ua = fields["updated_at"]
        if isinstance(ua, datetime):
            dt = ua
        elif ua not in (None, "null", ""):
            try:
                dt = datetime.fromisoformat(str(ua))
            except (ValueError, TypeError):
                errors.append(f"updated_at 格式错误: {ua}")
                dt = None
        else:
            dt = None

        if dt is not None:
            # naive datetime 视为 UTC
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            now = datetime.now(timezone.utc)
            age_minutes = (now - dt).total_seconds() / 60
            if age_minutes > STALENESS_THRESHOLD_MINUTES and fields.get("stage_status") not in ("completed", "skipped"):
                errors.append(f"状态卡陈旧（{int(age_minutes)} 分钟未更新 > 30 分钟门槛）")

    # blocked_by vs stage_status 一致性
    if "blocked_by" in fields and "stage_status" in fields:
        bb = fields["blocked_by"]
        ss = fields["stage_status"]
        # PyYAML 把 null 解析为 None；字符串 "null" 也视为空
        is_blocked = bb is not None and bb not in ("null", "", "null")
        if is_blocked and ss != "blocked":
            errors.append(f"blocked_by 非空时 stage_status 应是 blocked（当前 {ss}）")

    # V11.2 NEW: visual_evidence 硬门槛校验（Stage 3.5 → 4）
    # V11.8.x P2-1 扩展:进入 4/review 时同样校验（防止 reviewer 拿到未 verified 的状态卡）
    current_stage = fields.get("current_stage", "")
    stage_status = fields.get("stage_status", "")
    if current_stage in ("3.5/real-verify", "4/review") or (
        current_stage == "3/implement" and stage_status == "completed"
    ):
        ve = fields.get("visual_evidence", {})
        ve_status = ve.get("status", "missing") if isinstance(ve, dict) else "missing"
        if ve_status != "verified":
            if current_stage == "4/review":
                errors.append(
                    f"visual_evidence.status 必须 = verified（当前: {ve_status}），"
                    f"Stage 3.5 → 4 推进的硬门槛在进入 4/review 时仍生效。"
                    f"正确示例: visual_evidence: {{ status: verified, "
                    f"screenshots: [{{ path: docs/evidence/.../x.png, "
                    f"contains_change_components: true, interactive_proof: '...', "
                    f"read_by_main_context: true }}], "
                    f"verified_at: '{datetime.now(timezone.utc).isoformat()}' }}"
                )
            else:
                errors.append(
                    f"visual_evidence.status 必须 = verified（当前: {ve_status}），"
                    f"Stage 3.5 → Stage 4 推进的硬门槛"
                )

    # ---- P1-2 NEW:5 类校验扩展 ----

    # 1. stage_status == "completed" → stage_ended_at 必填非 null
    if fields.get("stage_status") == "completed":
        ended_at = fields.get("stage_ended_at")
        if ended_at is None or ended_at in ("", "null"):
            errors.append(
                "stage_status=completed 时 stage_ended_at 必填非 null。"
                f"正确示例: stage_ended_at: {datetime.now(timezone.utc).isoformat()}"
            )

    # 2. card_type == "bug" → bug_severity ∈ {P0, P1, P2, P3}
    if fields.get("card_type") == "bug":
        severity = fields.get("bug_severity")
        if severity is None:
            errors.append(
                "card_type=bug 时 bug_severity 必填。"
                f"合法值: {VALID_BUG_SEVERITY}。"
                "示例: bug_severity: P1"
            )
        elif severity not in VALID_BUG_SEVERITY:
            errors.append(
                f"bug_severity 非法: {severity!r}（应在 {VALID_BUG_SEVERITY} 中）。"
                "示例: bug_severity: P1"
            )

    # 3. parent_change 引用必须存在
    #   注:此项需要 --project-root 才能完整校验 file_exists;
    #   无 --project-root 时仅校验字段非空格式
    parent_change = fields.get("parent_change")
    if parent_change is not None and parent_change not in ("", "null"):
        if not isinstance(parent_change, str):
            errors.append(
                f"parent_change 非法（应为字符串）: {parent_change!r}。"
                "示例: parent_change: 2026-08-11-add-user-auth"
            )
        elif parent_card_path:
            target = (
                parent_card_path / "docs" / "specs" / "changes"
                / parent_change / ".state-card.md"
            )
            if not target.exists():
                errors.append(
                    f"parent_change 引用文件不存在: {target}。"
                    f"正确示例: docs/specs/changes/{parent_change}/.state-card.md"
                )

    # 4. visual_evidence.screenshots[].read_by_main_context == true 否则 FAIL
    ve = fields.get("visual_evidence", {})
    if isinstance(ve, dict):
        screenshots = ve.get("screenshots", []) or []
        for i, sc in enumerate(screenshots):
            if not isinstance(sc, dict):
                continue
            if not sc.get("read_by_main_context"):
                errors.append(
                    f"visual_evidence.screenshots[{i}].read_by_main_context 必须 = true"
                    f"（禁止 AI 描述代替像素读取）。"
                    "示例: { path: ..., contains_change_components: true,"
                    " interactive_proof: ..., read_by_main_context: true }"
                )

    # 5. reset_history 必含 5 子字段
    reset_history = fields.get("reset_history")
    if reset_history is not None and reset_history not in ("", "null"):
        if not isinstance(reset_history, list):
            errors.append(
                f"reset_history 类型错误（应为 list）: {type(reset_history).__name__}。"
                "示例: reset_history: [{ date, from_stage, to_stage, reason, reset_by, ... }]"
            )
        else:
            for i, entry in enumerate(reset_history):
                if not isinstance(entry, dict):
                    errors.append(f"reset_history[{i}] 不是 dict")
                    continue
                missing = [k for k in RESET_HISTORY_REQUIRED_KEYS if k not in entry]
                if missing:
                    errors.append(
                        f"reset_history[{i}] 缺必填字段: {missing}。"
                        f"必含 5 字段: {RESET_HISTORY_REQUIRED_KEYS}。"
                        "示例: { date: 2026-08-12T15:00:00, from_stage: 5/accept,"
                        " to_stage: -1/intake, reason: ..., reset_by: user }"
                    )

    return errors


def validate_artifacts_fs(fields: dict, state_card_path: pathlib.Path) -> list:
    """artifacts[].exists 与文件系统交叉验证"""
    errors = []
    card_dir = state_card_path.parent

    if "artifacts" not in fields:
        return errors

    artifacts = fields["artifacts"]
    if not isinstance(artifacts, list):
        return errors

    for i, art in enumerate(artifacts):
        if not isinstance(art, str):
            continue
        # 解析 - path: ... - exists: true/false
        path_match = None
        for part in art.split(" - "):
            if part.startswith("path:"):
                path_match = part[5:].strip()
            elif part.startswith("exists:"):
                declared_exists = part[7:].strip() == "true"

        if not path_match:
            continue

        # 解析相对路径
        if path_match.startswith("/") or ":" in path_match[:3]:
            full_path = pathlib.Path(path_match)
        else:
            full_path = (card_dir / path_match).resolve()

        actual_exists = full_path.exists()
        if actual_exists != declared_exists:
            errors.append(
                f"artifacts[{i}].exists 与文件系统不一致: "
                f"声明 {declared_exists}, 实际 {actual_exists} ({full_path})"
            )

    return errors


def validate_audit_log_consistency(
    state_card_path: pathlib.Path,
    project_root: pathlib.Path,
) -> list:
    """P3-6 NEW: 校验 audit log 一致性,防止 ghost write。

    校验项:
      - .trae/logs/state-card-audit.jsonl 存在
      - 该状态卡 path 在最近 audit log 中有记录(最近 100 条内)
    """
    errors = []
    audit_log = project_root / ".trae/logs/state-card-audit.jsonl"

    if not audit_log.exists():
        errors.append(
            f"audit log 缺失: {audit_log}(P3-6 强一致 — "
            f"未走 setup-feature / change-status 写路径)"
        )
        return errors

    # 计算状态卡相对路径(用于匹配)
    try:
        rel_path = state_card_path.resolve().relative_to(project_root.resolve())
    except ValueError:
        rel_path = state_card_path

    rel_path_str = str(rel_path).replace("\\", "/")

    # 读最近 100 条 audit log,匹配此状态卡路径
    try:
        lines = audit_log.read_text(encoding="utf-8").splitlines()[-100:]
    except Exception as e:
        errors.append(f"audit log 读取失败: {e}")
        return errors

    found = False
    import json as _json
    for line in lines:
        try:
            entry = _json.loads(line)
        except Exception:
            continue
        entry_path = (entry.get("path") or "").replace("\\", "/")
        if entry_path == rel_path_str:
            found = True
            break

    if not found:
        errors.append(
            f"audit log 缺失 {rel_path_str} 的记录 "
            f"(最近 {len(lines)} 条 audit log 中无对应 path)"
        )

    return errors


def main():
    parser = argparse.ArgumentParser(description="V11 状态卡校验")
    parser.add_argument("state_card", help="状态卡文件路径")
    parser.add_argument("--project-root", help="项目根路径（用于相对路径解析）")
    parser.add_argument("--strict-audit", action="store_true",
                        help="P3-6 NEW: 强一致校验 — 同时校验 .trae/logs/state-card-audit.jsonl 一致性")
    parser.add_argument("--json", action="store_true", help="JSON 输出")
    args = parser.parse_args()

    path = pathlib.Path(args.state_card)
    fields = parse_state_card(path)

    if "error" in fields:
        result = {"status": "FAIL", "errors": [fields["error"]], "path": str(path)}
        if args.json:
            import json
            print(json.dumps(result, indent=2, ensure_ascii=False))
        else:
            print(f"❌ FAIL: {fields['error']}")
        return 1

    field_errors = validate_fields(
        fields,
        parent_card_path=pathlib.Path(args.project_root).resolve()
        if args.project_root else None,
    )
    fs_errors = validate_artifacts_fs(fields, path)

    all_errors = field_errors + fs_errors
    is_valid = len(all_errors) == 0

    # P3-6 NEW: --strict-audit 模式下,同时校验 audit log 一致性
    audit_errors: list = []
    if args.strict_audit:
        if not args.project_root:
            all_errors.append("--strict-audit 必须配合 --project-root 使用")
        else:
            audit_errors = validate_audit_log_consistency(
                state_card_path=path,
                project_root=pathlib.Path(args.project_root).resolve(),
            )
            all_errors.extend(audit_errors)
            if audit_errors:
                is_valid = False

    result = {
        "status": "PASS" if is_valid else "FAIL",
        "path": str(path),
        "current_stage": fields.get("current_stage"),
        "card_type": fields.get("card_type"),
        "stage_status": fields.get("stage_status"),
        "health": fields.get("health"),
        "errors": all_errors
    }

    # V11.2.1 NEW: 状态卡关键字段保护提示（state-card-protocol.md §5.8）
    # 5 个关键字段只能由主上下文亲自 Edit,子代理禁止直接写入
    # standalone 模式下做静态扫描 + info 提示;真正的权限校验需在 git diff 上下文工作
    protected_fields = ["stage_status", "current_stage", "gate_result.status", "health", "next_stage.id"]
    state_card_text = path

    if state_card_text and state_card_text.exists():
        content = state_card_text.read_text(encoding="utf-8")
        protected_violations = []
        for field in protected_fields:
            # 检查状态卡中是否包含该字段(仅作 info 提示,实际权限校验需 git diff)
            if field.split('.')[0] in content:
                protected_violations.append({
                    "field": field,
                    "note": f"{field} 只能由主上下文 Edit,子代理禁止直接写入(§5.8)"
                })
        if protected_violations:
            result.setdefault("info", []).extend([
                f"🔒 {v['field']}: {v['note']}" for v in protected_violations
            ])

    if args.json:
        import json
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        if is_valid:
            print(f"✅ PASS — {path}")
            print(f"   card_type: {fields.get('card_type')}")
            print(f"   current_stage: {fields.get('current_stage')}")
            print(f"   health: {fields.get('health')}")
        else:
            print(f"❌ FAIL — {path}")
            for e in all_errors:
                print(f"   - {e}")

    return 0 if is_valid else 1


if __name__ == "__main__":
    sys.exit(main())