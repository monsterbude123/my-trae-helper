#!/usr/bin/env python3
"""gitnexus-session-finalize.py — Stop Hook

每次会话结束 (Stop) 时在后台触发 `gitnexus analyze`, 确保下次会话
启动时看到最新的索引。设计与 SessionStart 端的 staleness check 配对
使用: 本 hook 负责"写" (更新索引), SessionStart 端负责"读" (检测
陈旧)。

设计要点:
  - 后台执行: subprocess.Popen + DETACHED_PROCESS, 不阻塞 Stop
  - 可关闭:    GITNEXUS_AUTO_ANALYZE=0 跳过
  - 退出码:    始终 0, 失败只打印警告 (Stop hook 不应阻止会话退出)
  - 跑前检测:  HEAD 与 meta.json:lastCommit 一致时跳过, 避免空跑

适用事件: Stop
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

# IMPORTANT: .trae/ in this repo is a symbolic link to D:\workspace\HJMSpaceRule\.trae.
# Path(__file__).resolve() follows that link and yields the wrong project root,
# so we discover the *logical* project root via `git rev-parse --show-toplevel`
# instead. This is also robust for git worktrees and submodules.
project_root = Path(
    subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        capture_output=True,
        text=True,
        timeout=5,
    ).stdout.strip().replace("/", os.sep)
)
if not project_root or not (project_root / ".gitnexus").exists():
    cursor = Path(__file__).resolve().parent
    while cursor != cursor.parent:
        if (cursor / ".gitnexus").exists():
            project_root = str(cursor)
            break
        cursor = cursor.parent
    else:
        project_root = str(Path(__file__).resolve().parent.parent.parent)

project_root = Path(project_root)
meta_path = project_root / ".gitnexus" / "meta.json"
runner = project_root / ".gitnexus" / "run.cjs"


def run_git(*args: str) -> str | None:
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


def read_meta_last_commit() -> str | None:
    if not meta_path.exists():
        return None
    try:
        data = json.loads(meta_path.read_text(encoding="utf-8"))
        return data.get("lastCommit")
    except (OSError, ValueError):
        return None


def trigger_analyze_background() -> None:
    if not runner.exists():
        print("[GitNexus Finalize] ⚠️  runner missing: .gitnexus/run.cjs")
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
        print("[GitNexus Finalize] 🔄 analyze scheduled (background) — see .gitnexus/analyze.log")
    except (OSError, ValueError) as exc:
        print(f"[GitNexus Finalize] ⚠️  failed to spawn analyze: {exc}")


def main() -> int:
    print("[GitNexus Finalize] Stop — refreshing index for next session")

    if os.environ.get("GITNEXUS_AUTO_ANALYZE") == "0":
        print("[GitNexus Finalize] ⏸  disabled via GITNEXUS_AUTO_ANALYZE=0")
        return 0

    head_sha = run_git("rev-parse", "HEAD")
    if head_sha is None:
        print("[GitNexus Finalize] ⚠️  not a git repo or git unavailable — skipping")
        return 0

    last_commit = read_meta_last_commit()
    if last_commit == head_sha and last_commit is not None:
        print("[GitNexus Finalize] ✅ index already fresh — skipped")
        return 0

    if last_commit is None:
        print(f"[GitNexus Finalize] ⚠️  no index yet — scheduling analyze for HEAD {head_sha[:12]}")
    else:
        print(f"[GitNexus Finalize] ⚠️  index stale ({last_commit[:12]} vs {head_sha[:12]}) — scheduling analyze")

    trigger_analyze_background()
    return 0


if __name__ == "__main__":
    sys.exit(main())