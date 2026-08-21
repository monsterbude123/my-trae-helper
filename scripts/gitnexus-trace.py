#!/usr/bin/env python3
# scripts/gitnexus-trace.py — GitNexus MCP 调用 trace 记录器 + 校验器
#
# 设计目的（2026-08-18 guard-smith 委派落地）:
#   fullstack4TraeV11 skill 的主上下文和子代理从未真正驱动 gitnexus MCP 工具,
#   仅是"文字声明"。本脚本提供 trace 写盘 + 校验,把"声明"变成"硬执行"。
#
# 行为约定:
#   - 写盘位置: <REPO_ROOT>/.trae/logs/gitnexus-trace.jsonl (append-only)
#   - 仅 stdlib: argparse + json + os + time + sys (无 requests/pyyaml 等三方)
#   - 跨平台: Windows/macOS/Linux 用 os.path 路径拼接(避免 pathlib 3.10 旧依赖)
#   - 输出前缀统一: [gitnexus-trace]
#   - stdout 用 key=value 便于 CI 解析
#   - 失败不阻断会话(exit != 0 仅用于 git hook/主动验证场景)
#
# CLI:
#   append  --tool <name> --target <X> --ok <bool> [--note "..."]   追加一条 trace
#   summary                                                       输出 called_count / blocked_attempts / last_run_at
#   check                                                          验证上次 trace 24h 内
#   install-trace  --skill <name> --hook <hook>                    注册 hook 路由(router 接入用)
#
# 退出码:
#   0 = PASS
#   1 = BLOCK(用户调用错误 / 数据损坏)
#   2 = WARN(check 超 24h 仅警告)
#
# 详见 AGENTS.md §1.11 铁律 + skill-markets/guard-gate-smith/SKILL.md §2.4

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from typing import Any, Dict, List, Optional


# ---------- 路径 / 常量 ----------

PREFIX = "[gitnexus-trace]"
TRACE_REL_PATH = os.path.join(".trae", "logs", "gitnexus-trace.jsonl")
CHECK_WINDOW_SECONDS = 24 * 60 * 60  # 24h


def _emit(kv: Dict[str, Any]) -> None:
    """统一 stdout 格式: [gitnexus-trace] key=value 空格分隔"""
    parts = [PREFIX]
    for k, v in kv.items():
        if isinstance(v, bool):
            s = "true" if v else "false"
        else:
            s = str(v)
        parts.append(f"{k}={s}")
    print(" ".join(parts))


def _repo_root() -> str:
    """
    推断仓库根目录:
      1. 环境变量 MTH_REPO_ROOT(测试 hook 注入用)
      2. 从本脚本路径向上找,直到找到同时存在 AGENTS.md + .husky 的目录
      3. 兜底: cwd
    """
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


def _trace_file() -> str:
    """trace 写盘位置(append-only)"""
    root = _repo_root()
    path = os.path.join(root, TRACE_REL_PATH)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    return path


def _safe_bool(s: str) -> bool:
    if isinstance(s, bool):
        return s
    return str(s).strip().lower() in ("true", "1", "yes", "y", "t")


# ---------- 子命令实现 ----------

def cmd_append(args: argparse.Namespace) -> int:
    """追加一条 trace 记录"""
    if not args.tool or not args.target:
        _emit({"event": "Append", "ok": False, "reason": "missing required --tool / --target"})
        return 1

    record = {
        "ts": int(time.time()),
        "ts_iso": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "tool": args.tool,
        "target": args.target,
        "ok": _safe_bool(args.ok),
        "note": args.note or "",
    }

    path = _trace_file()
    line = json.dumps(record, ensure_ascii=False, separators=(",", ":"))
    try:
        with open(path, "a", encoding="utf-8") as f:
            f.write(line + "\n")
            f.flush()
            try:
                os.fsync(f.fileno())
            except OSError:
                # Windows 上对已关闭句柄 fsync 可能抛错,忽略
                pass
    except OSError as e:
        _emit({"event": "Append", "ok": False, "reason": f"write-fail:{e}"})
        return 1

    _emit({
        "event": "Append",
        "ok": True,
        "path": path.replace("\\", "/"),
        "tool": record["tool"],
        "target": record["target"],
        "trace_ok": record["ok"],
    })
    return 0


def _load_records() -> List[Dict[str, Any]]:
    """加载全部 trace 行(损坏行跳过,append-only 协议不变)"""
    path = _trace_file()
    if not os.path.exists(path):
        return []
    records: List[Dict[str, Any]] = []
    with open(path, "r", encoding="utf-8") as f:
        for raw in f:
            line = raw.strip()
            if not line:
                continue
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError:
                # 损坏行不致命,跳过(append-only 不修改历史)
                continue
    return records


def cmd_summary(_args: argparse.Namespace) -> int:
    """输出统计摘要"""
    records = _load_records()
    total = len(records)
    ok_count = sum(1 for r in records if r.get("ok") is True)
    blocked = sum(1 for r in records if r.get("ok") is False)
    last = records[-1] if records else None
    last_ts = last.get("ts_iso", "n/a") if last else "n/a"

    # 按 tool 聚合
    by_tool: Dict[str, int] = {}
    for r in records:
        t = r.get("tool", "?")
        by_tool[t] = by_tool.get(t, 0) + 1

    _emit({
        "event": "Summary",
        "called_count": total,
        "ok_count": ok_count,
        "blocked_attempts": blocked,
        "tools_distinct": len(by_tool),
        "last_run_at": last_ts,
    })
    # 工具分布单行 key=value(便于人读)
    for t, n in sorted(by_tool.items()):
        print(f"{PREFIX} tool.{t}={n}")
    return 0


def cmd_check(_args: argparse.Namespace) -> int:
    """验证上次 trace 在 24h 内"""
    records = _load_records()
    if not records:
        _emit({"event": "Check", "result": "FAIL", "reason": "no-trace", "window_hours": 24})
        # pre-commit 主动验证场景:无 trace → FAIL(不是 stub 假通过)
        return 1

    last = records[-1]
    last_ts = int(last.get("ts", 0))
    now = int(time.time())
    age = now - last_ts
    fresh = age <= CHECK_WINDOW_SECONDS

    if fresh:
        _emit({
            "event": "Check",
            "result": "PASS",
            "age_seconds": age,
            "last_run_at": last.get("ts_iso", "?"),
        })
        return 0

    _emit({
        "event": "Check",
        "result": "STALE",
        "age_seconds": age,
        "window_seconds": CHECK_WINDOW_SECONDS,
        "last_run_at": last.get("ts_iso", "?"),
    })
    # STALE 视为 WARN(exit 2),不阻断但提示
    return 2


def cmd_install_trace(args: argparse.Namespace) -> int:
    """
    注册 hook 路由(供 guard-router 探测用)
    仅打印声明,不实际改写注册表 — 注册表由 guard-smith agent 维护。
    """
    if not args.skill or not args.hook:
        _emit({"event": "InstallTrace", "ok": False, "reason": "missing required --skill / --hook"})
        return 1

    _emit({
        "event": "InstallTrace",
        "ok": True,
        "skill": args.skill,
        "hook": args.hook,
        "trace_file": _trace_file().replace("\\", "/"),
        "note": "登记 router 探测条目;注册表条目需 guard-smith 委派写入",
    })
    return 0


# ---------- argparse ----------

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="gitnexus-trace.py",
        description="GitNexus MCP 调用 trace 记录与校验",
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    p_app = sub.add_parser("append", help="追加一条 trace")
    p_app.add_argument("--tool", required=True, help="MCP 工具名(impact/context/query/...)")
    p_app.add_argument("--target", required=True, help="目标符号 / 文件 / 概念")
    p_app.add_argument("--ok", required=True, help="调用是否成功(true/false)")
    p_app.add_argument("--note", default="", help="附加说明")
    p_app.set_defaults(func=cmd_append)

    p_sum = sub.add_parser("summary", help="输出统计摘要")
    p_sum.set_defaults(func=cmd_summary)

    p_chk = sub.add_parser("check", help="验证上次 trace 在 24h 内")
    p_chk.set_defaults(func=cmd_check)

    p_inst = sub.add_parser("install-trace", help="登记 hook 路由(路由器探测)")
    p_inst.add_argument("--skill", required=True)
    p_inst.add_argument("--hook", required=True)
    p_inst.set_defaults(func=cmd_install_trace)

    return p


def main(argv: Optional[List[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return int(args.func(args) or 0)
    except KeyboardInterrupt:
        _emit({"event": "Interrupt", "ok": False})
        return 130


if __name__ == "__main__":
    sys.exit(main())
