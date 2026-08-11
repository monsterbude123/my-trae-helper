#!/usr/bin/env python3
"""gitnexus-session-check.py — SessionStart Hook

每次会话启动时检测 GitNexus 索引是否过期（基于 git HEAD SHA vs
`.gitnexus/meta.json:lastCommit`）。如果过期或缺失则在后台触发
`gitnexus analyze`，确保本次会话使用最新的知识图谱。

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
    # Fall back to walking up from __file__ looking for .gitnexus/ — this lets
    # the hook still work even when invoked outside a git repo (e.g. for tests).
    cursor = Path(__file__).resolve().parent
    while cursor != cursor.parent:
        if (cursor / ".gitnexus").exists():
            project_root = str(cursor)
            break
        cursor = cursor.parent
    else:
        # Last resort: file location (matches the pre-existing hook behaviour
        # for non-git invocations; the meta lookup will simply find nothing).
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


def read_meta_last_commit() -> tuple[str | None, str | None]:
    """Return (lastCommit, indexedAt) from .gitnexus/meta.json or (None, None)."""
    if not meta_path.exists():
        return None, None
    try:
        data = json.loads(meta_path.read_text(encoding="utf-8"))
        return data.get("lastCommit"), data.get("indexedAt")
    except (OSError, ValueError):
        return None, None


def trigger_analyze_background() -> None:
    """Spawn `node run.cjs analyze` detached; return immediately."""
    if not runner.exists():
        print("[GitNexus Check] ⚠️  runner missing: .gitnexus/run.cjs")
        return
    try:
        # DETACHED_PROCESS (Windows) / setsid equivalent so the child survives
        # the hook exiting. Logs go to .gitnexus/analyze.log for diagnosis.
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
        print("[GitNexus Check] 🔄 analyze scheduled (background) — see .gitnexus/analyze.log")
    except (OSError, ValueError) as exc:
        print(f"[GitNexus Check] ⚠️  failed to spawn analyze: {exc}")


def main() -> int:
    print("[GitNexus Check] SessionStart — verifying index freshness")

    if os.environ.get("GITNEXUS_AUTO_ANALYZE") == "0":
        print("[GitNexus Check] ⏸  disabled via GITNEXUS_AUTO_ANALYZE=0")
        return 0

    head_sha = run_git("rev-parse", "HEAD")
    if head_sha is None:
        print("[GitNexus Check] ⚠️  not a git repo or git unavailable — skipping")
        return 0

    last_commit, indexed_at = read_meta_last_commit()

    if last_commit is None:
        print(f"[GitNexus Check] ⚠️  no .gitnexus/meta.json — index missing")
        print(f"   HEAD: {head_sha[:12]}")
        trigger_analyze_background()
        return 0

    if last_commit != head_sha:
        # Count commits between HEAD and the indexed commit to estimate scope
        behind = run_git("rev-list", "--count", f"{last_commit}..HEAD") or "?"
        print(f"[GitNexus Check] ⚠️  index stale: {behind} commit(s) since last analyze")
        print(f"   indexed: {last_commit[:12]} @ {indexed_at or '?'}")
        print(f"   HEAD:    {head_sha[:12]}")
        trigger_analyze_background()
        return 0

    print(f"[GitNexus Check] ✅ index fresh @ {last_commit[:12]} ({indexed_at or '?'})")
    return 0


if __name__ == "__main__":
    sys.exit(main())