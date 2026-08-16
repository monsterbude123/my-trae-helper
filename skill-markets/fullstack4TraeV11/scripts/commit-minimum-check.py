#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
V11 commit-minimum-check.py — commit 准入最小集程序化校验(AUDIT-#13 / P3-6)

定位:SKILL.md §3.7 #10 反虚假交付反转陷阱 + references/common-anti-patterns.md §7.3
     "commit 准入最小集 ≠ 全量验收"协议落地。

4 项准入最小集校验(适配 Python 后端工具集,无 TS / Next.js 依赖):
    1. typecheck 0 错   → compileall 全部 .py
    2. 关键 5 路由 spot-check  → docs/specs/changes/{id}/spot-check.json 探测
    3. admin 探针 200    → .trae/fullstack4traev11.config.yaml gate.base_url + /health
    4. lint 预存问题不阻塞  → pyflakes 收集 → 写 .trae/logs/commit-readiness-warnings.jsonl

Usage:
    python scripts/commit-minimum-check.py
    python scripts/commit-minimum-check.py --project-root .
    python scripts/commit-minimum-check.py --json
    python scripts/commit-minimum-check.py --strict   # admin 探针失败 = 1, 不允许 N/A

Exit codes:
    0 = PASS(全部 4 项通过 / 前 3 pass + 第 4 WARN 入 log)
    1 = FAIL(前 3 任一 FAIL,阻断 commit)
    2 = N/A(未启动 dev server 跳过 #3,进 WARN)

实现要点:
    - 跨平台:Windows / macOS / Linux 统一 pathlib + subprocess(timeout=5)
    - 优雅降级:dev server 未启 → #3 = N/A,写 stderr,不阻断
    - stdout/stderr 分流:PASS → stdout,FAIL → stderr
    - 仅依赖标准库 + PyYAML(已装)
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time

# 跨平台 Windows console cp1252 兜底（V11.8.5 P1 — 反馈 2026-08-16 #5 采纳）
# Python 3.13 在 Windows 默认 cp1252，print(f"...中文...") 必崩 UnicodeEncodeError
# 必须在 import 阶段前置（subprocess 启动前），否则下游 argparse 等 print 已触发
if sys.platform == "win32" and not os.environ.get("PYTHONIOENCODING"):
    os.environ["PYTHONIOENCODING"] = "utf-8"
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")  # type: ignore[attr-defined]
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")  # type: ignore[attr-defined]
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import List, Optional, Tuple

# ============================================================================
# 常量
# ============================================================================

# log 路径(项目级,如不存在自动创建)
LOG_PATH_DEFAULT = ".trae/logs/commit-readiness-warnings.jsonl"

# spot-check 文件名(项目侧约定)
SPOT_CHECK_FILE = "spot-check.json"

# 路由变更根
CHANGES_DIR = "docs/specs/changes"

# admin 探针路径
ADMIN_PROBE_PATH = "/health"

# compileall / pyflakes 命令
COMPILE_CMD = [sys.executable, "-m", "compileall", "-q"]
PYFLAKES_CMD = [sys.executable, "-m", "pyflakes"]

# dev server 探测超时(秒)
HTTP_TIMEOUT = 5

# config 文件名(项目级)
CONFIG_FILE = "fullstack4traev11.config.yaml"

# 环境变量
ENV_BASE_URL = "V11_BASE_URL"

# ============================================================================
# 结果数据结构
# ============================================================================


@dataclass
class CheckResult:
    """单项检查结果"""
    name: str
    status: str   # "pass" | "fail" | "warn" | "na"
    detail: str
    exit_code: int  # 0/1/2 逐项(最终汇总以 sub.ExitCode 决定)
    evidence: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class Report:
    """总报告"""
    project_root: str
    strict: bool
    checks: List[CheckResult] = field(default_factory=list)
    summary: str = ""  # "PASS" / "FAIL" / "WARN"
    summary_exit_code: int = 0
    warnings_log: str = ""

    def to_dict(self) -> dict:
        return {
            "project_root": self.project_root,
            "strict": self.strict,
            "summary": self.summary,
            "summary_exit_code": self.summary_exit_code,
            "warnings_log": self.warnings_log,
            "checks": [c.to_dict() for c in self.checks],
        }


# ============================================================================
# 工具函数
# ============================================================================


def _parse_yaml_simple(path: Path) -> dict:
    """轻量 YAML 解析:支持 key: value 嵌套(2 空格缩进)。

    优先 PyYAML;缺失则降级为纯文本正则(2 空格缩进)。
    """
    if not path.exists():
        return {}
    text = path.read_text(encoding="utf-8")
    try:
        import yaml  # type: ignore

        return yaml.safe_load(text) or {}
    except ImportError:
        pass
    # 降级:解析常见 base_url / timeout 字段
    result: dict = {}
    current_section: Optional[dict] = None
    section_name: Optional[str] = None
    for raw_line in text.splitlines():
        line = raw_line.rstrip()
        if not line or line.lstrip().startswith("#"):
            continue
        if not line.startswith(" ") and line.endswith(":"):
            section_name = line[:-1].strip()
            current_section = {}
            result[section_name] = current_section
        elif current_section is not None and line.startswith("  "):
            stripped = line[2:].strip()
            if ":" in stripped:
                k, v = stripped.split(":", 1)
                current_section[k.strip()] = v.strip().strip('"').strip("'")
    return result


def _resolve_base_url(project_root: Path) -> Tuple[Optional[str], str]:
    """解析 admin 探针 base_url。

    优先级:
        1. 环境变量 V11_BASE_URL
        2. .trae/fullstack4traev11.config.yaml → gate.base_url
        3. .trae/config.yaml → gate.base_url
    Returns:
        (base_url, 来源说明)
    """
    env_url = os.environ.get(ENV_BASE_URL)
    if env_url:
        return env_url, f"env {ENV_BASE_URL}"
    for rel in (f".trae/{CONFIG_FILE}", ".trae/config.yaml", "config.yaml"):
        cfg = _parse_yaml_simple(project_root / rel)
        if not cfg:
            continue
        gate = cfg.get("gate") or {}
        url = gate.get("base_url") or cfg.get("base_url")
        if url:
            return str(url), f"file {rel}"
    return None, "no config"


def _run_cmd(cmd: List[str], cwd: Optional[Path] = None, timeout: int = 30) -> Tuple[int, str, str]:
    """跑子命令,返回 (returncode, stdout, stderr)。"""
    try:
        result = subprocess.run(
            cmd,
            cwd=str(cwd) if cwd else None,
            capture_output=True,
            text=True,
            check=False,
            timeout=timeout,
        )
        return result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired as e:
        return 124, "", f"timeout after {timeout}s: {e}"
    except FileNotFoundError as e:
        return 127, "", f"command not found: {e}"


def _probe_http(url: str, timeout: int = HTTP_TIMEOUT) -> Tuple[bool, str]:
    """HTTP 探针,不引入 requests 依赖(标准库 urllib)。"""
    import urllib.request
    import urllib.error
    import socket

    try:
        with urllib.request.urlopen(url, timeout=timeout) as resp:
            code = resp.getcode()
            if 200 <= code < 300:
                return True, f"HTTP {code}"
            return False, f"HTTP {code}"
    except urllib.error.HTTPError as e:
        return False, f"HTTP {e.code}"
    except urllib.error.URLError as e:
        return False, f"URLError: {e.reason}"
    except (socket.timeout, TimeoutError):
        return False, f"timeout after {timeout}s"
    except ConnectionRefusedError:
        return False, "ConnectionRefused"
    except Exception as e:  # noqa: BLE001
        return False, f"{type(e).__name__}: {e}"


def _find_active_change_ids(project_root: Path) -> List[str]:
    """从 git status --porcelain 找 docs/specs/changes/{id}/ 下有变更的 change IDs。

    备选:扫描目录取子目录名(对应未在 git 跟踪也找得到)。
    """
    ids: List[str] = []
    # 1. git 路径
    rc, out, _ = _run_cmd(["git", "status", "--porcelain"], cwd=project_root, timeout=10)
    if rc == 0 and out:
        for line in out.splitlines():
            # 格式:XY <path>(rename 时 ->  形如 R  old -> new)
            path_part = line[3:].strip()
            if " -> " in path_part:
                path_part = path_part.split(" -> ", 1)[1]
            marker = f"{CHANGES_DIR}/"
            if path_part.startswith(marker):
                rest = path_part[len(marker):]
                if "/" in rest:
                    cid = rest.split("/", 1)[0]
                    if cid and cid not in ids:
                        ids.append(cid)
    # 2. 目录扫描(兜底 — 没 git / 还没 add)
    changes_root = project_root / CHANGES_DIR
    if changes_root.exists():
        for sub in changes_root.iterdir():
            if sub.is_dir() and sub.name not in ids:
                ids.append(sub.name)
    return ids


# ============================================================================
# 4 项检查
# ============================================================================


def check_typecheck(project_root: Path) -> CheckResult:
    """#1 typecheck 0 错 — compileall 全部 .py"""
    # \u5148\u7edf\u8ba1 .py \u6587\u4ef6\u6570(\u5305\u542b\u5b50\u76ee\u5f55)
    py_files = sorted((project_root / "scripts").rglob("*.py"))
    rc, out, err = _run_cmd(COMPILE_CMD + ["scripts/"], cwd=project_root, timeout=60)
    if rc == 0:
        return CheckResult(
            name="typecheck",
            status="pass",
            detail=f"compileall \u5168 .py 0 \u9519({len(py_files)} \u6587\u4ef6)",
            exit_code=0,
            evidence={"py_files": len(py_files), "stderr": err[-500:] if err else ""},
        )
    # rc != 0 \u2192 \u8bed\u6cd5\u9519
    return CheckResult(
        name="typecheck",
        status="fail",
        detail=f"compileall \u5931\u8d25(rc={rc})",
        exit_code=1,
        evidence={"stderr": (err or out)[-1000:], "rc": rc, "py_files": len(py_files)},
    )
    # rc != 0 \u2192 \u8bed\u6cd5\u9519
    return CheckResult(
        name="typecheck",
        status="fail",
        detail=f"compileall \u5931\u8d25(rc={rc})",
        exit_code=1,
        evidence={"stderr": (err or out)[-1000:], "rc": rc},
    )


def check_spot_check(project_root: Path) -> CheckResult:
    """#2 \u5173\u952e 5 \u8def\u7531 spot-check \u2014 \u63a2\u6d4b spot-check.json"""
    ids = _find_active_change_ids(project_root)
    if not ids:
        return CheckResult(
            name="spot-check",
            status="warn",
            detail="\u672a\u627e\u5230 active change ID",
            exit_code=0,
            evidence={"reason": "no-change-dirs"},
        )
    # \u53d6\u6700\u8fd1 1 \u4e2a active change
    cid = ids[0]
    spot = project_root / CHANGES_DIR / cid / SPOT_CHECK_FILE
    if not spot.exists():
        return CheckResult(
            name="spot-check",
            status="warn",
            detail=f"{spot.relative_to(project_root)} \u4e0d\u5b58\u5728(\u9879\u76ee\u53ef\u81ea\u5b9a\u4e49 \u00b7 \u4e0d\u963b\u65ad)",
            exit_code=0,
            evidence={"change_id": cid},
        )
    # \u89e3\u6790 JSON
    try:
        data = json.loads(spot.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        return CheckResult(
            name="spot-check",
            status="fail",
            detail=f"spot-check.json \u89e3\u6790\u5931\u8d25: {e}",
            exit_code=1,
            evidence={"change_id": cid, "path": str(spot)},
        )
    endpoints = data.get("endpoints") or data.get("routes") or []
    if not isinstance(endpoints, list):
        return CheckResult(
            name="spot-check",
            status="fail",
            detail=f"endpoints \u5b57\u6bb5\u7f3a\u5931\u6216\u4e0d\u662f list",
            exit_code=1,
            evidence={"change_id": cid},
        )
    if len(endpoints) == 0:
        return CheckResult(
            name="spot-check",
            status="warn",
            detail=f"endpoints \u4e3a\u7a7a",
            exit_code=0,
            evidence={"change_id": cid, "count": 0},
        )
    # \u7edf\u8ba1 pass / fail
    pass_cnt = sum(1 for e in endpoints if e.get("status") == "pass")
    fail_cnt = sum(1 for e in endpoints if e.get("status") == "fail")
    if fail_cnt > 0:
        return CheckResult(
            name="spot-check",
            status="fail",
            detail=f"{fail_cnt}\u4e2a\u8def\u7531 FAIL({pass_cnt}/{len(endpoints)} PASS)",
            exit_code=1,
            evidence={"change_id": cid, "pass": pass_cnt, "fail": fail_cnt, "total": len(endpoints)},
        )
    return CheckResult(
        name="spot-check",
        status="pass",
        detail=f"{len(endpoints)} \u8def\u7531\u5168 PASS",
        exit_code=0,
        evidence={"change_id": cid, "pass": pass_cnt, "total": len(endpoints)},
    )


def check_admin_probe(project_root: Path, strict: bool = False) -> CheckResult:
    """#3 admin \u63a2\u9488 200 \u2014 \u68c0\u6d4b dev server + /health

    dev server \u672a\u542f \u2192 \u8fdb WARN(exit 2),\u4e0d\u963b\u65ad\u3002
    strict \u6a21\u5f0f \u2192 \u4e25\u91cd:dev server \u672a\u542f \u2192 FAIL(\u963b\u65ad commit)\u3002
    """
    base_url, source = _resolve_base_url(project_root)
    if not base_url:
        return CheckResult(
            name="admin-probe",
            status="warn",
            detail="admin/auth/data \u63a5\u53e3\u672a\u914d\u7f6e base_url(\u8df3\u8fc7)",
            exit_code=0,
            evidence={"reason": "no-config"},
        )
    target = base_url.rstrip("/") + ADMIN_PROBE_PATH
    ok, probe_detail = _probe_http(target, timeout=HTTP_TIMEOUT)
    if ok:
        return CheckResult(
            name="admin-probe",
            status="pass",
            detail=f"{target} {probe_detail}(src={source})",
            exit_code=0,
            evidence={"url": target, "source": source, "detail": probe_detail},
        )
    # \u63a2\u6d4b\u5931\u8d25
    if strict:
        return CheckResult(
            name="admin-probe",
            status="fail",
            detail=f"{target} {probe_detail}(strict=严格阻断)",
            exit_code=1,
            evidence={"url": target, "source": source, "detail": probe_detail, "strict": True},
        )
    return CheckResult(
        name="admin-probe",
        status="warn",
        detail=f"{target} {probe_detail}(dev server \u672a\u542f \u00b7 N/A)",
        exit_code=2,
        evidence={"url": target, "source": source, "detail": probe_detail},
    )


def check_lint_pre_existing(project_root: Path) -> CheckResult:
    """#4 lint \u9884\u5b58\u95ee\u9898\u4e0d\u963b\u65ad \u2014 pyflakes \u6536\u96c6 + \u5199 jsonl"""
    py_files = list((project_root / "scripts").rglob("*.py"))
    if not py_files:
        return CheckResult(
            name="lint-pre-existing",
            status="warn",
            detail="scripts/ \u4e0b\u65e0 .py",
            exit_code=0,
            evidence={"file_count": 0},
        )
    rc, out, err = _run_cmd(PYFLAKES_CMD + ["scripts/"], cwd=project_root, timeout=60)
    # \u5f02\u5e38\u963b\u65ad:pyflakes \u672a\u88c5
    if rc == 127 and "No module named pyflakes" in (err or ""):
        return CheckResult(
            name="lint-pre-existing",
            status="warn",
            detail="pyflakes \u672a\u5b89\u88c5(\u8df3\u8fc7)",
            exit_code=0,
            evidence={"missing_module": "pyflakes"},
        )
    # pyflakes \u8f93\u51fa\u683c\u5f0f: <file>:<line>: <warning>
    warnings_by_file: dict = {}
    for raw_line in (out or "").splitlines():
        line = raw_line.strip()
        if not line or ":" not in line:
            continue
        try:
            file_part, lineno, msg = line.split(":", 2)
        except ValueError:
            continue
        file_part = file_part.strip()
        warnings_by_file.setdefault(file_part, []).append({
            "line": lineno.strip(),
            "warning": msg.strip(),
        })
    # \u6bcf\u4e2a\u6587\u4ef6\u53d6\u524d 5 \u4e2a
    summary = []
    for fp, items in sorted(warnings_by_file.items()):
        summary.append((fp, items[:5]))
    # \u5199 log
    log_path = project_root / LOG_PATH_DEFAULT
    log_path.parent.mkdir(parents=True, exist_ok=True)
    ts = time.strftime("%Y-%m-%dT%H:%M:%S%z", time.localtime())
    with log_path.open("a", encoding="utf-8") as fh:
        for fp, items in summary:
            for it in items:
                fh.write(json.dumps({
                    "timestamp": ts,
                    "file": fp,
                    "line": it["line"],
                    "warning": it["warning"],
                    "category": "lint-pre-existing",
                }, ensure_ascii=False) + "\n")
    total_files = len(summary)
    total_warns = sum(len(items) for _, items in summary)
    return CheckResult(
        name="lint-pre-existing",
        status="warn",
        detail=f"{total_files} \u6587\u4ef6\u524d 5 warnings \u5199\u5165 {LOG_PATH_DEFAULT}",
        exit_code=0,
        evidence={
            "log_path": str(log_path),
            "files_with_warnings": total_files,
            "warnings_logged": total_warns,
        },
    )


# ============================================================================
# 汇总
# ============================================================================


def aggregate(results: List[CheckResult], strict: bool) -> Tuple[str, int]:
    """汇总 4 项结果。

    Returns:
        (summary, exit_code)
        - "PASS" / 0 \u2014 \u5168\u90e8\u901a\u8fc7 \u00b7 \u6216\u524d 3 pass + \u7b2c 4 WARN
        - "FAIL" / 1 \u2014 \u524d 3 \u4efb\u4e00 FAIL(\u963b\u65ad commit)
        - "WARN" / 2 \u2014 dev server \u672a\u542f \u00b7 #3=N/A
    """
    fail = [c for c in results if c.status == "fail"]
    if fail:
        return "FAIL", 1
    # \u524d 3 \u90fd\u662f pass / warn \u2014 \u770b\u662f\u5426 admin #3\u4e3a warn
    admin = next((c for c in results if c.name == "admin-probe"), None)
    if admin and admin.status == "warn" and admin.exit_code == 2:
        return "WARN", 2
    return "PASS", 0


# ============================================================================
# 文本输出
# ============================================================================


def format_text(report: Report) -> str:
    """人类可读输出(PASS \u4fe1\u606f \u2192 stdout)."""
    lines = [f"[v11-commit-min] 4 \u9879\u68c0\u67e5 \u00b7 strict={report.strict}"]
    for i, c in enumerate(report.checks, 1):
        marker = {"pass": "pass", "fail": "FAIL", "warn": "warn", "na": "N/A"}.get(c.status, c.status)
        lines.append(f"[{i}/{len(report.checks)}] {c.name}: {marker} ({c.detail})")
    lines.append(f"\u603b\u7ed3: {report.summary} (WARN \u4e0d\u963b\u65ad)")
    return "\n".join(lines)


def format_json(report: Report) -> str:
    return json.dumps(report.to_dict(), ensure_ascii=False, indent=2)


# ============================================================================
# CLI
# ============================================================================


def main() -> int:
    parser = argparse.ArgumentParser(
        description="V11 commit \u51c6\u5165\u6700\u5c0f\u96c6\u7a0b\u5e8f\u5316\u6821\u9a8c(AUDIT-#13)"
    )
    parser.add_argument(
        "--project-root",
        default=".",
        help="\u9879\u76ee\u6839\u76ee\u5f55(default:.)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="\u4ee5 JSON \u8f93\u51fa",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="\u4e25\u91cd\u6a21\u5f0f:admin \u63a2\u9488\u5931\u8d25 \u2192 FAIL \u963b\u65ad commit",
    )
    args = parser.parse_args()

    project_root = Path(args.project_root).resolve()

    results: List[CheckResult] = [
        check_typecheck(project_root),
        check_spot_check(project_root),
        check_admin_probe(project_root, strict=args.strict),
        check_lint_pre_existing(project_root),
    ]
    summary_str, summary_exit = aggregate(results, strict=args.strict)
    report = Report(
        project_root=str(project_root),
        strict=args.strict,
        checks=results,
        summary=summary_str,
        summary_exit_code=summary_exit,
        warnings_log=str(project_root / LOG_PATH_DEFAULT),
    )

    out = format_json(report) if args.json else format_text(report)
    if summary_exit == 0:
        # PASS / WARN \u2192 stdout(WARN \u4e0d\u963b\u65ad,\u4ecd\u7ed9\u4e3b\u4e0a\u4e0b\u6587\u4e00\u4e2a\u63d0\u793a)
        print(out)
        if summary_str == "WARN":
            # \u989d\u5916\u4e00\u884c\u53bb stderr \u63d0\u9192
            print(
                f"[v11-commit-min] WARN: dev server \u672a\u542f,admin \u63a2\u9488 N/A",
                file=sys.stderr,
            )
    else:
        # FAIL \u2192 stderr
        print(out, file=sys.stderr)
    return summary_exit


if __name__ == "__main__":
    sys.exit(main())
