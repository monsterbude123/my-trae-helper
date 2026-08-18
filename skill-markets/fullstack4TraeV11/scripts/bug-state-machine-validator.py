#!/usr/bin/env python3
"""
V12 bug-state-machine-validator.py — Bug 单状态机校验器(P3-5 NEW, V12 收敛)

定位:skills/12-bug-fix/references/bug-state-machine.md 定义 7 状态机(权威源) +
状态转换矩阵。01-intake/references/bug-state-machine.md + 本脚本必须向 12-bug-fix 对齐。

7 状态(bug-state-machine.md L11-19):
  - OPEN       — Bug 已录入,等待 Stage 6 处理
  - IN-FIX     — Stage 6 Bug Fix 进行中(6 层排查 + TDD 修复)
  - FIXED      — 已修复,待测试专家复测
  - VERIFIED   — 测试专家复测通过,再观察无 regression
  - CLOSED     — 关闭归档(终态,三方确认)
  - REOPENED   — 测试专家复测 FIXED 失败回退
  - OBSOLETE   — 功能变更致过时(终态)

状态转换矩阵(bug-state-machine.md L36-46):
  - (无) → OPEN
  - OPEN → IN-FIX
  - IN-FIX → FIXED
  - FIXED → VERIFIED
  - FIXED → REOPENED
  - VERIFIED → CLOSED
  - REOPENED → IN-FIX
  - IN-FIX → OPEN  (e2e 初始 PASS / TDD 修复 FAIL 回退)
  - OPEN/FIXED/VERIFIED → OBSOLETE

Usage:
    python bug-state-machine-validator.py --bug-state-card <path> [--json]
    python bug-state-machine-validator.py --bug-card <path> [--json]  # alias
    python bug-state-machine-validator.py --validate-only  # 仅校验状态机文件结构

Exit codes:
    0 = PASS(status ∈ 7 状态 + 转换合法)
    1 = FAIL(status 不合法 或 转换非法)
"""
import argparse
import json
import pathlib
import re
import sys
from typing import List, Dict, Tuple, Optional


# 7 状态(权威源:skills/12-bug-fix/references/bug-state-machine.md)
VALID_BUG_STATUSES = ["OPEN", "IN-FIX", "FIXED", "VERIFIED", "CLOSED", "REOPENED", "OBSOLETE"]

# 状态转换矩阵(从 → 到)
# 依据 skills/12-bug-fix/references/bug-state-machine.md 转换矩阵 L36-46
VALID_TRANSITIONS = {
    "OPEN": ["IN-FIX", "OBSOLETE"],          # 进入修复 或 功能变更致过时
    "IN-FIX": ["FIXED", "OPEN"],             # 修复完成 或 回退(e2e 初始 PASS / TDD FAIL)
    "FIXED": ["VERIFIED", "REOPENED", "OBSOLETE"],  # 复测通过 / 复测失败 / 功能变更致过时
    "VERIFIED": ["CLOSED", "OBSOLETE"],      # 三方确认关闭 或 功能变更致过时
    "CLOSED": [],                             # 终态
    "REOPENED": ["IN-FIX"],                  # 回到修复队列
    "OBSOLETE": [],                          # 终态
}


def parse_state_card(path: pathlib.Path) -> dict:
    """解析状态卡 frontmatter(委托 _lib_state_card 共用库)。"""
    sys.path.insert(0, str(pathlib.Path(__file__).parent))
    from _lib_state_card import parse_state_card as _parse
    return _parse(path)


def extract_bug_status(fields: dict) -> Tuple[Optional[str], Optional[str]]:
    """从状态卡 frontmatter 提取 status / ready_to_close。

    返回 (status_value, ready_to_close_value)。两个都可能 None。
    status 字段名读取顺序:status → stage_status → bug_status(从前往后命中即返回)。
    """
    status = (
        fields.get("status")
        or fields.get("stage_status")
        or fields.get("bug_status")
    )
    ready = fields.get("ready_to_close")
    return status, ready


def extract_status_history(text: str) -> List[str]:
    """从状态卡全文提取 status_history 段(如存在)。"""
    # 简单行扫描:寻找 "status_history:" 之后到下个顶层 key 之前的列表
    history = []
    in_history = False
    for line in text.splitlines():
        if line.startswith("status_history:") or line.startswith("status_history :"):
            in_history = True
            continue
        if in_history:
            stripped = line.strip()
            if not stripped or (stripped and ":" in stripped and not stripped.startswith("-")):
                in_history = False
                continue
            if stripped.startswith("- "):
                history.append(stripped[2:].strip().strip('"').strip("'"))
    return history


def validate_bug_state_card(path: pathlib.Path) -> dict:
    """校验 bug 状态卡。

    返回 {"status": "PASS/FAIL", "errors": [...], "current_status": ..., ...}
    """
    errors = []

    if not path.exists():
        return {"status": "FAIL", "errors": [f"文件不存在: {path}"]}

    fields = parse_state_card(path)
    if "error" in fields:
        return {"status": "FAIL", "errors": [f"frontmatter 解析失败: {fields['error']}"]}

    status, ready_to_close = extract_bug_status(fields)

    # 1. status 必填
    if not status:
        errors.append("状态卡缺 status / stage_status / bug_status 字段")
        return {"status": "FAIL", "errors": errors, "current_status": None}

    # 2. status ∈ 7 合法状态
    if status not in VALID_BUG_STATUSES:
        errors.append(
            f"status 非法: {status!r}（应在 {VALID_BUG_STATUSES} 中）"
        )

    # 3. status_history 转换合法性校验(如存在)
    try:
        text = path.read_text(encoding="utf-8")
    except Exception:
        text = ""
    history = extract_status_history(text)

    for i in range(1, len(history)):
        prev = history[i - 1]
        cur = history[i]
        if prev not in VALID_TRANSITIONS:
            errors.append(f"status_history[{i-1}] 状态 {prev!r} 不在 7 状态中")
            continue
        if cur not in VALID_TRANSITIONS[prev]:
            errors.append(
                f"status_history 非法转换: {prev} → {cur}"
                f"（合法转换: {VALID_TRANSITIONS[prev]}）"
            )

    return {
        "status": "PASS" if not errors else "FAIL",
        "errors": errors,
        "current_status": status,
        "ready_to_close": ready_to_close,
        "status_history": history,
        "path": str(path),
    }


def main():
    parser = argparse.ArgumentParser(
        description="V11 bug-state-machine-validator.py — Bug 单状态机校验"
    )
    parser.add_argument("--bug-state-card", help="bug 状态卡文件路径")
    parser.add_argument("--bug-card", help="alias for --bug-state-card(同义)")
    parser.add_argument("--state-machine", help="bug-state-machine.md 路径(默认 V11 内置)")
    parser.add_argument("--json", action="store_true", help="JSON 输出")
    args = parser.parse_args()

    target = args.bug_state_card or args.bug_card
    if not target:
        parser.error("必须提供 --bug-state-card 或 --bug-card 之一")

    path = pathlib.Path(target)
    result = validate_bug_state_card(path)

    # 附加诊断信息
    result["valid_statuses"] = VALID_BUG_STATUSES
    result["valid_transitions"] = VALID_TRANSITIONS

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2, default=str))
    else:
        status_icon = "❌" if result["status"] == "FAIL" else "✅"
        print(f"{status_icon} {result['status']} — {path}")
        print(f"   current_status: {result.get('current_status')}")
        print(f"   ready_to_close: {result.get('ready_to_close')}")
        if result.get("status_history"):
            print(f"   status_history: {' → '.join(result['status_history'])}")
        for e in result["errors"]:
            print(f"   - {e}")

    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())