#!/usr/bin/env python3
"""V11 gitnexus-session-finalize.py — Stop Hook

每次会话结束 (Stop) 时在后台触发 `gitnexus analyze`, 确保下次会话
启动时看到最新的索引。设计与 SessionStart 端的 staleness check 配对
使用: 本 hook 负责"写" (更新索引), SessionStart 端负责"读" (检测
陈旧)。

V11 继承 V10.10 双端设计。

设计要点:
  - 后台执行: subprocess.Popen + DETACHED_PROCESS, 不阻塞 Stop
  - 可关闭:    GITNEXUS_AUTO_ANALYZE=0 跳过
  - 退出码:    始终 0, 失败只打印警告 (Stop hook 不应阻止会话退出)
  - 跑前检测:  HEAD 与 meta.json:lastCommit 一致时跳过, 避免空跑

适用事件: Stop

SECURITY 标注: subprocess.Popen 后台调用（git / gitnexus analyze），
全部为 Stop 钩子触发知识图谱更新需要。无外网。
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

    cursor = Path(__file__).resolve().parent
    while cursor != cursor.parent:
        if (cursor / ".gitnexus").exists():
            return cursor
        cursor = cursor.parent

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
    if not meta_path.exists():
        return None
    try:
        data = json.loads(meta_path.read_text(encoding="utf-8"))
        return data.get("lastCommit")
    except (OSError, ValueError):
        return None


def detect_workspace_dirty() -> bool:
    """检测工作区是否脏（agent 是否改过代码但未提交）。

    用 `git status --porcelain` 判断，只要输出非空即视为脏。
    **排除 `.gitnexus/` 自身** —— 工具把索引/痕迹文件写进该目录，
    若不排除，analyze 每次写入都会让工作区变"脏"，导致 Stop 永远触发 analyze（死循环）。
    git 不可用 / 非 repo 时保守返回 True（宁可多跑一次 analyze）。
    """
    try:
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=str(project_root),
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.returncode != 0:
            return True
        # 仅保留真实代码/配置改动，忽略 .gitnexus/ 工具自身产物
        significant = [
            line
            for line in result.stdout.splitlines()
            if line and not line.startswith("?? .gitnexus/")
                 and "/.gitnexus/" not in line
        ]
        return bool(significant)
    except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
        return True


def write_trace(run_reason: str, head_sha: str, dirty: bool) -> None:
    """写运行痕迹到 .gitnexus/last-run.json，便于验证 hook 是否跑过。"""
    trace = {
        "hook": "gitnexus-session-finalize",
        "at": datetime.now(timezone.utc).isoformat(),
        "head": head_sha,
        "workspace_dirty": dirty,
        "run_reason": run_reason,
        "exit": 0,
    }
    trace_path = project_root / ".gitnexus" / "last-run.json"
    try:
        trace_path.parent.mkdir(parents=True, exist_ok=True)
        trace_path.write_text(json.dumps(trace, ensure_ascii=False, indent=2), encoding="utf-8")
    except OSError as exc:
        print(f"[gitnexus] event=Stop reason=trace_write_error action=error detail={exc}")


def trigger_analyze_background() -> None:
    if not runner.exists():
        print("[gitnexus] event=Stop reason=runner_missing action=error detail=.gitnexus/run.cjs")
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
        print("[gitnexus] event=Stop reason=analyze_scheduled action=analyze detail=.gitnexus/analyze.log")
    except (OSError, ValueError) as exc:
        print(f"[gitnexus] event=Stop reason=analyze_spawn_error action=error detail={exc}")


def main() -> int:
    print("[gitnexus] event=Stop reason=start action=check")

    if os.environ.get("GITNEXUS_AUTO_ANALYZE") == "0":
        print("[gitnexus] event=Stop reason=disabled action=skip")
        write_trace(run_reason="disabled", head_sha="", dirty=False)
        return 0

    head_sha = run_git("rev-parse", "HEAD")
    if head_sha is None:
        print("[gitnexus] event=Stop reason=no_head action=skip detail=not a git repo")
        write_trace(run_reason="no_head", head_sha="", dirty=detect_workspace_dirty())
        return 0

    dirty = detect_workspace_dirty()
    last_commit = read_meta_last_commit()

    if not dirty and last_commit == head_sha:
        write_trace(run_reason="no_change_skipped", head_sha=head_sha, dirty=dirty)
        print(f"[gitnexus] event=Stop reason=no_change_skipped action=skip head={head_sha} dirty=false")
        return 0

    # 触发 analyze（工作区脏 或 索引过期）
    reason = "workspace_dirty" if dirty else "index_stale"
    write_trace(run_reason=reason, head_sha=head_sha, dirty=dirty)
    print(f"[gitnexus] event=Stop reason={reason} action=analyze head={head_sha} dirty={'true' if dirty else 'false'}")
    trigger_analyze_background()
    return 0


if __name__ == "__main__":
    sys.exit(main())