#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
completion-self-check.py — fullstack4TraeV11 V11.8.7 NEW

主代理会话启动反向守门核对器(c7 + c8 双核对器)。
跨项目复用,零外部依赖(仅 Python 3.8+ stdlib)。

用法:
  python scripts/completion-self-check.py --intent qa-loop-audit
  python scripts/completion-self-check.py --intent change-start [--project-root .]

退出码:
  0 = PASS
  1 = FAIL
  2 = WARN(可继续,但记录在案)

V11.8.7 SSOT:
  - role-protocol.md §H+(bug-in-scope 闭环硬约束)
  - role-protocol.md §I+(qa-loop 反向守门自检)
  - config.example.yaml intake.intents_no_change + stage_5.light_mode_when_zero_scope
  - common-anti-patterns.md §22 main-agent-direct-test
"""

from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import List, Optional, Tuple


# ============ 常量定义(SSOT) ============

V11_VERSION = "11.8.7"

# V11.8.7 §I+ — 主代理亲自跑测试的命令(检测特征)
TEST_COMMAND_PATTERNS = [
    re.compile(r"\bnpx\s+vitest\b", re.IGNORECASE),
    re.compile(r"\bnpm\s+run\s+test\b", re.IGNORECASE),
    re.compile(r"\bnpx\s+playwright\s+test\b", re.IGNORECASE),
    re.compile(r"\byarn\s+test\b", re.IGNORECASE),
    re.compile(r"\bpnpm\s+test\b", re.IGNORECASE),
]

# 主代理本人标识(无 [test-expert] tag 即视为主代理)
TEST_EXPERT_TAG = re.compile(r"\[test-expert\]", re.IGNORECASE)
SUB_AGENT_PREFIX = re.compile(r"^sub-agent-", re.IGNORECASE)

# V11.8.7 §H+ — bug 单状态枚举
BUG_STATES_INCOMPLETE = {"OPEN", "IN-FIX"}
BUG_STATES_OK = {"FIXED", "VERIFIED", "CLOSED", "OBSOLETE"}

# intents_no_change 默认白名单(V11.8.7 扩展)
INTENTS_NO_CHANGE_DEFAULT = [
    "ops",
    "init",
    "diagnostic",
    "health-check",
    "archive-purge",
    "qa-loop-audit",  # V11.8.7 NEW
]

CHANGES_REQUIRED_INTENTS_DEFAULT = [
    "change-start",
    "bug-fix",
    "project-init",
    "rollback",
]


# ============ 工具函数 ============


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


def _now_minus(hours: int) -> str:
    """git log --since 用 ISO 时间。"""
    return (now_utc() - timedelta(hours=hours)).strftime("%Y-%m-%dT%H:%M:%S")


def run_git_log(project_root: Path, since_hours: int = 24, limit: int = 50) -> List[str]:
    """git log --since=24h --pretty=format:... -n 50"""
    cmd = [
        "git",
        "-C",
        str(project_root),
        "log",
        f"--since={_now_minus(since_hours)}",
        "--pretty=format:%H|%an|%ae|%s",
        f"-n",
        str(limit),
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        if result.returncode != 0:
            return []
        return [line for line in result.stdout.splitlines() if line.strip()]
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return []


def is_test_command(commit_msg: str) -> bool:
    return any(p.search(commit_msg) for p in TEST_COMMAND_PATTERNS)


def is_test_expert_author(author: str, email: str) -> bool:
    """test-expert sub-agent = author 字段含 [test-expert] tag 或 email 含 test-expert"""
    if TEST_EXPERT_TAG.search(author) or TEST_EXPERT_TAG.search(email):
        return True
    return False


def parse_bug_state(bug_md: Path) -> Optional[str]:
    """从 bug 单 markdown frontmatter 解析 status。"""
    try:
        text = bug_md.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return None
    # 简单 frontmatter 解析(第一段 --- 内)
    m = re.match(r"^---\s*\n(.*?)\n---", text, re.DOTALL)
    if not m:
        return None
    for line in m.group(1).splitlines():
        m2 = re.match(r"^status:\s*(\S+)", line, re.IGNORECASE)
        if m2:
            return m2.group(1).upper()
    return None


def scan_bug_states(project_root: Path) -> List[Tuple[str, str]]:
    """扫 docs/bugs/ 下所有 bug 单,返回 [(bug_id, status), ...]"""
    bugs_dir = project_root / "docs" / "bugs"
    if not bugs_dir.is_dir():
        return []
    results: List[Tuple[str, str]] = []
    for bug_dir in sorted(bugs_dir.iterdir()):
        if not bug_dir.is_dir():
            continue
        # 优先读 .state-card.md,fallback 到 bug-*.md
        for cand in [bug_dir / ".state-card.md"] + list(bug_dir.glob("bug-*.md")):
            if cand.is_file():
                state = parse_bug_state(cand)
                if state:
                    results.append((bug_dir.name, state))
                    break
    return results


# ============ c7 qa-loop-audit 核对器(V11.8.7 §I+) ============


def c7_qa_loop_audit(project_root: Path) -> Tuple[str, str]:
    """
    扫描最近 24h git log 检测 qa-loop 协议违反:
    - commit msg 含 vitest/playwright/test 等测试命令
    - commit author = 主代理本人(无 [test-expert] tag)
    任一命中 → FAIL
    """
    commits = run_git_log(project_root, since_hours=24, limit=50)
    if not commits:
        return ("PASS", "无最近 24h git log 可扫描(no commits)")

    violations: List[str] = []
    for line in commits:
        parts = line.split("|", 3)
        if len(parts) < 4:
            continue
        sha, author, email, msg = parts
        if not is_test_command(msg):
            continue
        if is_test_expert_author(author, email):
            continue
        # 边界态:author 含 sub-agent- 前缀但非 [test-expert] → WARN
        if SUB_AGENT_PREFIX.search(author):
            violations.append(
                f"WARN: {sha[:8]} author={author} 含 sub-agent- 但无 [test-expert] tag,msg={msg[:60]}"
            )
            continue
        violations.append(
            f"FAIL: {sha[:8]} author={author} 亲自跑测试,msg={msg[:60]}"
        )

    if not violations:
        return ("PASS", f"扫描 {len(commits)} 个 commit,无主代理亲自跑测试")
    fails = [v for v in violations if v.startswith("FAIL")]
    warns = [v for v in violations if v.startswith("WARN")]
    if fails:
        detail = "; ".join(fails[:5]) + (f" (+{len(fails) - 5} more)" if len(fails) > 5 else "")
        return ("FAIL", f"主代理亲自跑测试 {len(fails)} 次: {detail}")
    return ("WARN", "; ".join(warns[:5]))


# ============ c8 bug-in-scope 核对器(V11.8.7 §H+) ============


def c8_bug_in_scope(project_root: Path) -> Tuple[str, str]:
    """
    扫 docs/bugs/ OPEN/IN-FIX 状态 bug 单。
    - 数 > 0 → FAIL
    - 数 = 0 → PASS
    """
    bugs = scan_bug_states(project_root)
    if not bugs:
        return ("PASS", "docs/bugs/ 下无 bug 单(或无 status 字段)")

    incomplete = [(bid, st) for bid, st in bugs if st in BUG_STATES_INCOMPLETE]
    if not incomplete:
        return ("PASS", f"扫描 {len(bugs)} 个 bug 单,全部 FIXED/VERIFIED/CLOSED")

    detail = ", ".join(f"{bid}={st}" for bid, st in incomplete[:5])
    return (
        "FAIL",
        f"backlog bug 单 {len(incomplete)} 个未闭环(OPEN/IN-FIX): {detail}",
    )


# ============ intent 路由 ============


def route_intent(intent: str, project_root: Path) -> int:
    """
    路由 intent → 调用对应核对器 → 输出结果 → 返回退出码。
    """
    results: List[Tuple[str, str, str]] = []

    if intent == "qa-loop-audit":
        s1, d1 = c7_qa_loop_audit(project_root)
        results.append(("c7 qa-loop-audit", s1, d1))
        s2, d2 = c8_bug_in_scope(project_root)
        results.append(("c8 bug-in-scope", s2, d2))

    elif intent == "change-start":
        # 集成 c7 + c8 到 change-start(原有 c1-c6 留待扩展)
        s1, d1 = c7_qa_loop_audit(project_root)
        results.append(("c7 qa-loop-audit", s1, d1))
        s2, d2 = c8_bug_in_scope(project_root)
        results.append(("c8 bug-in-scope", s2, d2))

    elif intent == "diagnostic":
        # 兼容:diagnostic 仅跑 c8(轻量)
        s2, d2 = c8_bug_in_scope(project_root)
        results.append(("c8 bug-in-scope", s2, d2))

    elif intent in INTENTS_NO_CHANGE_DEFAULT:
        # ops/init/health-check/archive-purge 等意图无需 c7/c8(本核对器不参与)
        results.append((f"c0 intent={intent}", "PASS", "intent 在 intents_no_change 白名单,无需 c7/c8"))

    elif intent in CHANGES_REQUIRED_INTENTS_DEFAULT:
        # change-start/bug-fix 等要求强校验(等同于 change-start)
        s1, d1 = c7_qa_loop_audit(project_root)
        results.append(("c7 qa-loop-audit", s1, d1))
        s2, d2 = c8_bug_in_scope(project_root)
        results.append(("c8 bug-in-scope", s2, d2))

    else:
        print(f"⚠️ 未知 intent '{intent}',按 default 兜底走 change-start")
        s1, d1 = c7_qa_loop_audit(project_root)
        results.append(("c7 qa-loop-audit", s1, d1))
        s2, d2 = c8_bug_in_scope(project_root)
        results.append(("c8 bug-in-scope", s2, d2))

    # 输出报告
    print(f"\n=== fullstack4TraeV11 V{V11_VERSION} completion-self-check ===")
    print(f"intent: {intent}")
    print(f"project_root: {project_root}")
    print(f"checks: {len(results)}")
    print()
    fail_count = 0
    warn_count = 0
    for name, status, detail in results:
        icon = {"PASS": "✅", "WARN": "⚠️ ", "FAIL": "🛑"}.get(status, "?")
        print(f"{icon} {name}: {status} — {detail}")
        if status == "FAIL":
            fail_count += 1
        elif status == "WARN":
            warn_count += 1

    print()
    if fail_count > 0:
        print(f"🛑 OVERALL: FAIL ({fail_count} failed)")
        return 1
    if warn_count > 0:
        print(f"⚠️  OVERALL: WARN ({warn_count} warnings)")
        return 2
    print("✅ OVERALL: PASS")
    return 0


# ============ CLI 入口 ============


def main() -> int:
    parser = argparse.ArgumentParser(
        description="fullstack4TraeV11 V11.8.7 completion-self-check (c7 + c8)"
    )
    parser.add_argument(
        "--intent",
        default="qa-loop-audit",
        help=f"意图(V11.8.7 默认 qa-loop-audit);可选: {', '.join(INTENTS_NO_CHANGE_DEFAULT + CHANGES_REQUIRED_INTENTS_DEFAULT)}",
    )
    parser.add_argument(
        "--project-root",
        default=".",
        help="项目根目录(默认当前目录)",
    )
    args = parser.parse_args()

    project_root = Path(args.project_root).resolve()
    if not project_root.is_dir():
        print(f"🛑 project_root 不存在: {project_root}", file=sys.stderr)
        return 1

    return route_intent(args.intent, project_root)


if __name__ == "__main__":
    sys.exit(main())