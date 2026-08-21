#!/usr/bin/env python3
# scripts/gitnexus-session-finalize.py — Stop 时机探测脚本
#
# 设计目的（2026-08-18 guard-smith 委派落地）:
#   在会话结束(Stop)时探测 workspace 是否有未提交改动,并通过 gitnexus-trace.py
#   append 写一条 trace 记录 — 确保 hard-execution 留痕。
#
# 与 session-check 的区别:
#   - check  → SessionStart,关注索引新鲜度(可重新生成)
#   - finalize → Stop,关注 workspace 状态(脏则提示 commit/丢弃)
#
# 输出统一前缀: [gitnexus]
# 退出码: 不阻断(exit 0 永远)— Stop 是会话边界,不应再有阻断
#
# 详见 AGENTS.md §4.1 / skill-markets/guard-gate-smith/SKILL.md

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from typing import Any, Dict, Optional


PREFIX = "[gitnexus]"
TRACE_SCRIPT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "gitnexus-trace.py")


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


def _detect_workspace_dirty(root: str) -> Dict[str, Any]:
    """
    通过 git status --porcelain 探测 workspace 脏状态
    返回: { is_git: bool, dirty: bool, dirty_count: int, sample: list }
    不抛错:git 不可用时降级为 is_git=False
    """
    if not os.path.exists(os.path.join(root, ".git")):
        return {"is_git": False, "dirty": False, "dirty_count": 0, "sample": []}
    try:
        proc = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=root, capture_output=True, text=True, timeout=5, check=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        return {"is_git": False, "dirty": False, "dirty_count": 0, "sample": []}
    if proc.returncode != 0:
        return {"is_git": True, "git_ok": False, "dirty": False, "dirty_count": 0, "sample": []}
    lines = [ln for ln in proc.stdout.splitlines() if ln.strip()]
    return {
        "is_git": True,
        "git_ok": True,
        "dirty": bool(lines),
        "dirty_count": len(lines),
        "sample": lines[:5],
    }


def _record_trace(reason: str, ok: bool, note: str) -> None:
    """探测留痕 — 失败不阻断"""
    if not os.path.exists(TRACE_SCRIPT):
        return
    py = sys.executable or "python3"
    try:
        subprocess.run(
            [py, TRACE_SCRIPT, "append",
             "--tool", "session-stop-probe",
             "--target", reason,
             "--ok", "true" if ok else "false",
             "--note", note],
            timeout=5,
            check=False,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    except (OSError, subprocess.TimeoutExpired):
        pass


def main(argv: Optional[list] = None) -> int:
    parser = argparse.ArgumentParser(prog="gitnexus-session-finalize.py")
    parser.add_argument("--repo-root", default=None)
    args = parser.parse_args(argv)

    root = args.repo_root or _repo_root()
    state = _detect_workspace_dirty(root)

    if not state.get("is_git"):
        _emit({
            "event": "Stop",
            "reason": "not-git-repo",
            "action": "skip-workspace-check",
            "workspace_dirty": False,
        })
        _record_trace("not-git-repo", True, "skip")
        return 0

    if not state.get("git_ok"):
        _emit({
            "event": "Stop",
            "reason": "git-unavailable",
            "action": "skip-workspace-check",
            "workspace_dirty": False,
        })
        _record_trace("git-unavailable", False, "skip")
        return 0

    if state["dirty"]:
        # 脏工作区 — 不阻断,但必须提示并留痕(这是 agent 风格的诚实交付)
        _emit({
            "event": "Stop",
            "reason": "workspace-dirty",
            "action": "suggest-commit-or-stash",
            "workspace_dirty": True,
            "dirty_count": state["dirty_count"],
        })
        for ln in state["sample"]:
            # 转义冒号,避免命令行解析坑
            safe = ln.replace("\n", "\\n").replace(":", ";")
            print(f"{PREFIX} dirty.sample={safe}")
        _record_trace(
            "workspace-dirty",
            False,
            f"count={state['dirty_count']}",
        )
        return 0

    _emit({
        "event": "Stop",
        "reason": "workspace-clean",
        "action": "no-op",
        "workspace_dirty": False,
    })
    _record_trace("workspace-clean", True, "ok")
    return 0


if __name__ == "__main__":
    sys.exit(main())
