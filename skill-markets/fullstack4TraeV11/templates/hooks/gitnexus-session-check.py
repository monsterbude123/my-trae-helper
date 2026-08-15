#!/usr/bin/env python3
"""V11 gitnexus-session-check.py — SessionStart Hook

每次会话启动时检测 GitNexus 索引是否过期（基于 git HEAD SHA vs
`.gitnexus/meta.json:lastCommit`）。如果过期或缺失则在后台触发
`node run.cjs analyze`，确保本次会话使用最新的知识图谱。

V11 继承 V10.10 双端设计（SessionStart 读 + Stop 写）。

设计要点:
  - 状态判定: `meta.json` 存在 + `lastCommit` == `git rev-parse HEAD` = 同步
  - 后台执行: 用 subprocess.Popen 启动并立即返回, 不阻塞 session 启动
  - 退出码:    始终 0, 失败只打印警告
  - 可关闭:    环境变量 GITNEXUS_AUTO_ANALYZE=0 跳过

触发条件 (SessionStart):
  - .gitnexus/meta.json 不存在   → 触发 analyze
  - meta.json.lastCommit != HEAD → 触发 analyze
  - meta.json 解析失败            → 触发 analyze
  - 索引同步                      → 跳过, 只打一行确认

SECURITY 标注（V10.12.2 NEW）: subprocess.Popen 后台调用（git / gitnexus analyze），
全部为 SessionStart 钩子触发知识图谱重建需要。无外网（gitnexus analyze 仅读本地代码）。
<!-- scan-whitelist:SHELL_EXEC --><!-- /scan-whitelist -->
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


def resolve_project_root() -> Path:
    """从 git rev-parse 找项目根，避免 .trae/ 软链跟随"""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode == 0 and result.stdout.strip():
            return Path(result.stdout.strip().replace("/", os.sep))
    except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
        pass

    # Fallback: 向上找 .gitnexus/
    cursor = Path(__file__).resolve().parent
    while cursor != cursor.parent:
        if (cursor / ".gitnexus").exists():
            return cursor
        cursor = cursor.parent

    # Last resort
    return Path(__file__).resolve().parent.parent.parent


project_root = resolve_project_root()
meta_path = project_root / ".gitnexus" / "meta.json"
runner = project_root / ".gitnexus" / "run.cjs"


def run_git(*args: str):
    """Run a git command in project_root; return trimmed stdout or None."""
    try:
        result = subprocess.run(
            ["git", *args],
            cwd=str(project_root),
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
        return None
    return None


def read_meta_last_commit():
    """Return (lastCommit, indexedAt) from .gitnexus/meta.json or (None, None)."""
    if not meta_path.exists():
        return None, None
    try:
        data = json.loads(meta_path.read_text(encoding="utf-8"))
        return data.get("lastCommit"), data.get("indexedAt")
    except (OSError, ValueError):
        return None, None


def write_trace(run_reason: str, head_sha: str) -> None:
    """写运行痕迹到 .gitnexus/last-run-check.json，便于验证会话开始时确实跑过。

    文件名与 finalize 端的 last-run.json 区分，避免并发写冲突。
    """
    trace = {
        "hook": "gitnexus-session-check",
        "at": datetime.now(timezone.utc).isoformat(),
        "head": head_sha,
        "run_reason": run_reason,
        "exit": 0,
    }
    trace_path = project_root / ".gitnexus" / "last-run-check.json"
    try:
        trace_path.parent.mkdir(parents=True, exist_ok=True)
        trace_path.write_text(json.dumps(trace, ensure_ascii=False, indent=2), encoding="utf-8")
    except OSError as exc:
        print(f"[gitnexus] event=SessionStart reason=trace_write_error action=error detail={exc}")


def trigger_analyze_background() -> None:
    """Spawn `node run.cjs analyze` detached; return immediately."""
    if not runner.exists():
        print("[gitnexus] event=SessionStart reason=runner_missing action=error detail=.gitnexus/run.cjs")
        return
    try:
        log_path = project_root / ".gitnexus" / "analyze.log"
        log_path.parent.mkdir(parents=True, exist_ok=True)
        log_fp = open(log_path, "ab")
        subprocess.Popen(
            ["node", str(runner), "analyze"],
            cwd=str(project_root),
            stdout=log_fp,
            stderr=log_fp,
            stdin=subprocess.DEVNULL,
            creationflags=getattr(subprocess, "DETACHED_PROCESS", 0)
            | getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0),
            close_fds=True,
        )
        print("[gitnexus] event=SessionStart reason=analyze_scheduled action=analyze detail=.gitnexus/analyze.log")
    except (OSError, ValueError) as exc:
        print(f"[gitnexus] event=SessionStart reason=analyze_spawn_error action=error detail={exc}")


def main() -> int:
    print("[gitnexus] event=SessionStart reason=start action=check")

    if os.environ.get("GITNEXUS_AUTO_ANALYZE") == "0":
        print("[gitnexus] event=SessionStart reason=disabled action=skip")
        write_trace(run_reason="disabled", head_sha="")
        return 0

    head_sha = run_git("rev-parse", "HEAD")
    if head_sha is None:
        print("[gitnexus] event=SessionStart reason=no_head action=skip detail=not a git repo")
        write_trace(run_reason="no_head", head_sha="")
        return 0

    last_commit, indexed_at = read_meta_last_commit()

    if last_commit is None:
        write_trace(run_reason="index_missing", head_sha=head_sha)
        print(f"[gitnexus] event=SessionStart reason=index_missing action=analyze head={head_sha}")
        trigger_analyze_background()
        return 0

    if last_commit != head_sha:
        behind = run_git("rev-list", "--count", f"{last_commit}..HEAD") or "?"
        write_trace(run_reason="index_stale", head_sha=head_sha)
        print(f"[gitnexus] event=SessionStart reason=index_stale action=analyze head={head_sha} detail={behind} commits behind")
        trigger_analyze_background()
        return 0

    write_trace(run_reason="index_up_to_date", head_sha=head_sha)
    print(f"[gitnexus] event=SessionStart reason=index_up_to_date action=skip head={head_sha}")
    return 0


if __name__ == "__main__":
    sys.exit(main())