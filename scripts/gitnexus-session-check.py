#!/usr/bin/env python3
# scripts/gitnexus-session-check.py — SessionStart 时机探测脚本
#
# 设计目的（2026-08-18 guard-smith 委派落地）:
#   在会话启动时检查 gitnexus MCP 索引新鲜度。
#   当 MCP 不可用时降级为"探测 .gitnexus/last-run.json 24h 新鲜度"。
#   同时通过 gitnexus-trace.py append 记录探测尝试。
#
# 输出统一前缀: [gitnexus]
# 输出格式: event=<name> reason=<why> action=<what>
#
# 退出码:
#   0 = PASS(索引新鲜 OR 探测动作已完成)
#   1 = BLOCK(MCP 不可用 + 索引也不新鲜,且无法回退)
#   2 = WARN(MCP 不可用,但有回退路径)
#
# 详见 .agents/rules/learning.md + AGENTS.md §1.11 + skill-markets/guard-gate-smith/SKILL.md

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from typing import Any, Dict, Optional


PREFIX = "[gitnexus]"
TRACE_SCRIPT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "gitnexus-trace.py")
INDEX_REL_PATHS = [
    os.path.join(".gitnexus", "last-run.json"),
    os.path.join(".gitnexus", "index.json"),
]
CHECK_WINDOW_SECONDS = 24 * 60 * 60


def _emit(kv: Dict[str, Any]) -> None:
    parts = [PREFIX]
    for k, v in kv.items():
        if isinstance(v, bool):
            s = "true" if v else "false"
        else:
            s = str(v)
        parts.append(f"{k}={s}")
    print(" ".join(parts))


def _repo_root() -> str:
    env = os.environ.get("MTH_REPO_ROOT")
    if env and os.path.isdir(env):
        return env
    cur = os.path.abspath(os.path.dirname(__file__))
    for _ in range(10):
        if os.path.exists(os.path.join(cur, "AGENTS.md")) and \
           os.path.exists(os.path.join(cur, ".husky")):
            return cur
        parent = os.path.dirname(cur)
        if parent == cur:
            break
        cur = parent
    return os.getcwd()


def _record_trace(reason: str, ok: bool, note: str) -> None:
    """调用 gitnexus-trace.py append 记录本探测尝试"""
    if not os.path.exists(TRACE_SCRIPT):
        return
    py = sys.executable or "python3"
    try:
        # 留出顶层 [gitnexus-trace] 前缀输出,本脚本外层再前缀 [gitnexus]
        # 但 gitnexus-trace.py 自身已前缀,无需重复包裹
        subprocess.run(
            [py, TRACE_SCRIPT, "append",
             "--tool", "session-start-probe",
             "--target", reason,
             "--ok", "true" if ok else "false",
             "--note", note],
            timeout=5,
            check=False,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    except (OSError, subprocess.TimeoutExpired):
        # 探测性调用,绝不能阻断会话
        pass


def _probe_index(root: str) -> Dict[str, Any]:
    """
    探测 .gitnexus/last-run.json 的 24h 新鲜度
    返回:
      {available: bool, age_seconds: int|None, last_run_iso: str|None}
    """
    for rel in INDEX_REL_PATHS:
        abs_p = os.path.join(root, rel)
        if not os.path.exists(abs_p):
            continue
        try:
            with open(abs_p, "r", encoding="utf-8") as f:
                raw = json.load(f)
        except (OSError, json.JSONDecodeError):
            return {"available": True, "parse_ok": False, "path": abs_p.replace("\\", "/")}
        # 常见字段名: last_run, updated_at, timestamp, ts
        ts = raw.get("last_run") or raw.get("updated_at") or raw.get("timestamp") or raw.get("ts")
        if ts is None:
            return {"available": True, "parse_ok": False, "path": abs_p.replace("\\", "/")}
        try:
            ts_int = int(ts)
            if ts_int < 10**12:  # 合理秒级时间戳
                ts_int = ts_int
        except (TypeError, ValueError):
            return {"available": True, "parse_ok": False, "path": abs_p.replace("\\", "/")}
        age = int(time.time()) - ts_int
        return {
            "available": True,
            "parse_ok": True,
            "path": abs_p.replace("\\", "/"),
            "age_seconds": age,
            "fresh": age <= CHECK_WINDOW_SECONDS,
        }
    return {"available": False}


def main(argv: Optional[list] = None) -> int:
    parser = argparse.ArgumentParser(prog="gitnexus-session-check.py")
    parser.add_argument("--repo-root", default=None, help="仓库根(可选,默认自动探测)")
    args = parser.parse_args(argv)

    root = args.repo_root or _repo_root()
    info = _probe_index(root)

    if info.get("available") and info.get("parse_ok"):
        if info.get("fresh"):
            _emit({
                "event": "SessionStart",
                "reason": "index-fresh",
                "action": "no-op",
                "age_seconds": info["age_seconds"],
                "path": info["path"],
            })
            _record_trace("index-fresh", True, info["path"])
            return 0
        # 索引存在但过期
        _emit({
            "event": "SessionStart",
            "reason": "index-stale",
            "action": "suggest-reindex",
            "age_seconds": info["age_seconds"],
            "window_seconds": CHECK_WINDOW_SECONDS,
        })
        _record_trace("index-stale", False, f"age={info['age_seconds']}s")
        # STALE = WARN(exit 2),不阻断会话启动
        return 2

    if info.get("available"):
        # 文件存在但解析失败
        _emit({
            "event": "SessionStart",
            "reason": "index-unparseable",
            "action": "manual-inspect",
            "path": info.get("path", "?"),
        })
        _record_trace("index-unparseable", False, "parse-fail")
        return 2

    # 完全没有任何索引文件
    _emit({
        "event": "SessionStart",
        "reason": "no-index",
        "action": "run-gitnexus-analyze",
        "hint": "node .gitnexus/run.cjs analyze",
    })
    _record_trace("no-index", False, "absent")
    return 2


if __name__ == "__main__":
    sys.exit(main())
