"""tests/_helpers/agent_hint.py — 主动指引机制

对应 ai-short-studio-monster 的 ERRORS.md / LEARNINGS.md + docs-sync-guard:
  - 测试失败时,通过 emit_hint() 把"缺什么 / 在哪补 / 调用哪个 Skill"
    写到 logs/agent-hints.jsonl + stdout
  - agent (无论人或 AI) 拿到 hint 后可以无歧义补齐

调用约定:
    from tests._helpers.agent_hint import emit_hint, hint_assert

    def test_x():
        emit_hint(
            trap_id="AP-2",
            what="echo-skip 占位脚本未被检测",
            where="scripts/validate-gate-integrity.py:check_nodejs",
            minimal_fix=["把 echo-skip 替换为真实命令"],
            next_skill="trae-ponytail",
            see_also=["references/traps.md §AP-2"],
        )
        assert "V2-NODEJS-ECHO-SKIP" in codes

    def test_x_with_hint():
        @hint_assert(
            trap_id="AP-2",
            what="缺 lint 脚本",
            minimal_fix=["在 package.json scripts 中加 lint"],
        )
        def _inner():
            assert "lint" in pkg_scripts  # 失败时自动 emit
        _inner()
"""
from __future__ import annotations

import json
import os
import sys
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Callable

SKILL_ROOT = Path(__file__).resolve().parents[2]
HINT_LOG_PATH = SKILL_ROOT / "logs" / "agent-hints.jsonl"

# 让 logs/ 目录自动出现(若 .gitignore 已忽略此目录,符合 §1.6)
HINT_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)


def _is_hints_disabled() -> bool:
    """通过环境变量可关闭 hint 写入(避免 CI 噪声)。"""
    return os.environ.get("AGENT_HINTS") == "0"


def emit_hint(
    trap_id: str,
    what: str,
    *,
    where: str = "",
    minimal_fix: list[str] | None = None,
    next_skill: str = "",
    next_skill_action: str = "",
    see_also: list[str] | None = None,
    severity: str = "HIGH",
    extra: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """生成一条 hint,既打印到 stderr 又写到日志。

    返回 hint dict 供调用方嵌入 assert msg。
    """
    hint = {
        "id": f"HINT-{trap_id}-{uuid.uuid4().hex[:6]}",
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "trap_id": trap_id,
        "severity": severity,
        "what": what,
        "where": where,
        "minimal_fix": minimal_fix or [],
        "next_skill": next_skill,
        "next_skill_action": next_skill_action,
        "see_also": see_also or [],
        "extra": extra or {},
    }

    # 人类可读打印(stderr,不污染 stdout)
    print(f"\n🛑 {hint['id']} [{hint['severity']}] {trap_id}: {what}", file=sys.stderr)
    if where:
        print(f"   📍 {where}", file=sys.stderr)
    if minimal_fix:
        for i, fix in enumerate(minimal_fix, 1):
            print(f"   🛠 {i}. {fix}", file=sys.stderr)
    if next_skill:
        action = f" — {next_skill_action}" if next_skill_action else ""
        print(f"   🤖 next: Skill(name='{next_skill}'){action}", file=sys.stderr)
    if see_also:
        for ref in see_also:
            print(f"   📚 {ref}", file=sys.stderr)

    # 写日志(jsonl 格式,便于机器读取 + 跨会话聚合)
    if not _is_hints_disabled():
        try:
            with HINT_LOG_PATH.open("a", encoding="utf-8") as f:
                f.write(json.dumps(hint, ensure_ascii=False) + "\n")
        except OSError:
            pass  # logs/ 写失败不影响测试

    return hint


def hint_assert(
    trap_id: str,
    what: str,
    *,
    where: str = "",
    minimal_fix: list[str] | None = None,
    next_skill: str = "",
    next_skill_action: str = "",
    see_also: list[str] | None = None,
) -> Callable:
    """装饰器: 失败自动 emit hint。"""

    def deco(fn: Callable) -> Callable:
        def wrapper(*args, **kwargs):
            try:
                return fn(*args, **kwargs)
            except AssertionError as e:
                hint = emit_hint(
                    trap_id=trap_id,
                    what=what,
                    where=where or fn.__qualname__,
                    minimal_fix=minimal_fix,
                    next_skill=next_skill,
                    next_skill_action=next_skill_action,
                    see_also=see_also,
                    extra={"original_assertion": str(e)},
                )
                # 把 hint id 嵌入 assert msg,方便 agent 看一眼 hint_id 就定位
                raise AssertionError(f"{hint['id']}: {what} | {e}") from e
        return wrapper
    return deco


def read_emitted_hints() -> list[dict[str, Any]]:
    """读取已记录的 hints(便于聚合脚本消费)。"""
    if not HINT_LOG_PATH.is_file():
        return []
    hints: list[dict[str, Any]] = []
    for line in HINT_LOG_PATH.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            hints.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return hints


def clear_emitted_hints() -> None:
    """清空 hints 日志(conftest fixture 用)。"""
    if HINT_LOG_PATH.is_file():
        HINT_LOG_PATH.unlink()


if __name__ == "__main__":  # pragma: no cover
    h = emit_hint(
        trap_id="DEMO",
        what="演示 hint",
        minimal_fix=["xx"],
    )
    print(json.dumps(h, ensure_ascii=False, indent=2))
