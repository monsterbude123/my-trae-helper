#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
collect-baseline.py — 一次性采集 daily-vibe-coding 仓库基线

本脚本固化本次(2026-08-14)调研中用到的所有"探查本地项目"的临时指令:
  - 跑安全扫描
  - 解析扫描 JSON 抽 HIGH/MED/LOW/verdict
  - 枚举 SKILL.md frontmatter 头 10 行
  - 抽取 last_git_commit 时间
  - 列 skill 目录
  - 列 implementation-log 三态(若指定历史日期)
  - 跑数字基线 12 项表

输出: logs/daily-vibe-coding/<date>/_baseline.json
agent 直接读 JSON,不再重复跑命令 → 节省 ~80% 探查时间

用法:
  python scripts/daily-vibe-coding/collect-baseline.py                       # 默认今日
  python scripts/daily-vibe-coding/collect-baseline.py --date 2026-08-14
  python scripts/daily-vibe-coding/collect-baseline.py --history-date 2026-08-13  # 含历史消化
  python scripts/daily-vibe-coding/collect-baseline.py --no-scan            # 跳过扫描(快路径)

退出码:
  0 = 成功
  2 = 扫描器未找到(优雅降级,部分字段为 null)
"""

from __future__ import annotations
import argparse
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

# 路径常量(本仓库默认布局)
ROOT = Path(r"d:\workspace\my-trae-helper")
SCAN_SCRIPT = ROOT / "skill-markets" / "trae-security-review" / "scripts" / "scan_skills_dir.py"
SKILL_DIR = ROOT / "skill-markets"
LOG_DIR = ROOT / "logs" / "daily-vibe-coding"
AUTO_REPORTS = ROOT / "auto_reports"

# 时区:Asia/Shanghai(UTC+8)
TZ = timezone(timedelta(hours=8))


def today_str() -> str:
    return datetime.now(TZ).strftime("%Y-%m-%d")


def run(cmd: list[str], cwd: Path | None = ROOT, timeout: int = 120) -> tuple[int, str, str]:
    """执行命令,返回 (exit_code, stdout, stderr)"""
    try:
        r = subprocess.run(
            cmd, cwd=str(cwd), capture_output=True, text=True,
            timeout=timeout, shell=False
        )
        return r.returncode, r.stdout, r.stderr
    except subprocess.TimeoutExpired:
        return 124, "", f"TIMEOUT after {timeout}s"
    except FileNotFoundError as e:
        return 127, "", f"NOT FOUND: {e}"


def find_python() -> str:
    """探测可用的 Python(避免 Git Bash /usr/bin/python3 缺 pip)"""
    candidates = [
        "python", "python3", "py",
        r"C:\ProgramData\miniconda3\python.exe",
        r"C:\Users\septe\AppData\Local\Programs\Python\Python312\python.exe",
    ]
    for c in candidates:
        try:
            r = subprocess.run([c, "--version"], capture_output=True, text=True, timeout=5)
            if r.returncode == 0:
                return c
        except Exception:
            continue
    return "python"  # 兜底


def step_security_scan(py: str) -> dict:
    """步骤 1+2: 跑安全扫描 + 解析 JSON 数字"""
    result = {"scan": None, "verdict": None, "high": None, "medium": None, "low": None,
              "files_scanned": None, "whitelist_lines": None, "report_md": None, "error": None}
    if not SCAN_SCRIPT.exists():
        result["error"] = f"scan_skills_dir.py not found at {SCAN_SCRIPT}"
        return result

    code, out, err = run([py, str(SCAN_SCRIPT), str(SKILL_DIR), "auto_reports"], timeout=180)
    result["scan_exit"] = code
    if code != 0:
        result["error"] = err[:500] or out[:500]
        return result

    # 找最新的 skill-markets_*.json
    json_files = sorted(AUTO_REPORTS.glob("skill-markets_*.json"), key=lambda p: p.stat().st_mtime)
    if not json_files:
        result["error"] = "no skill-markets_*.json generated"
        return result

    latest = json_files[-1]
    result["report_json"] = str(latest.relative_to(ROOT))
    result["report_md"] = str(latest.with_suffix(".md").relative_to(ROOT))

    try:
        data = json.loads(latest.read_text(encoding="utf-8"))
        result["verdict"] = data.get("verdict")
        result["files_scanned"] = data.get("scanned_files")
        # 统计 severity 分布
        sev = {"high": 0, "medium": 0, "low": 0}
        for f in data.get("findings", []):
            s = f.get("severity", "").lower()
            if s in sev:
                sev[s] += 1
        result["high"] = sev["high"]
        result["medium"] = sev["medium"]
        result["low"] = sev["low"]
        # 白名单行数(从 .md 抽,避免依赖扫描器内部字段)
        md_text = latest.with_suffix(".md").read_text(encoding="utf-8", errors="ignore")
        m = re.search(r"行/区块级豁免.*?\n.*?(\d+)", md_text)
        if m:
            result["whitelist_lines"] = int(m.group(1))
    except Exception as e:
        result["error"] = f"parse error: {e}"
    return result


def step_frontmatter_audit() -> dict:
    """步骤 3: 枚举所有 SKILL.md frontmatter 头 10 行,统计 version 缺失"""
    result = {"total_skill_dirs": 0, "has_skill_md": 0, "with_version": 0,
              "missing_version": [], "no_skill_md": [], "error": None}
    if not SKILL_DIR.exists():
        result["error"] = f"skill-markets not found at {SKILL_DIR}"
        return result

    for pkg in sorted(SKILL_DIR.iterdir()):
        if not pkg.is_dir():
            continue
        result["total_skill_dirs"] += 1
        skill_md = pkg / "SKILL.md"
        if not skill_md.exists():
            result["no_skill_md"].append(pkg.name)
            continue
        result["has_skill_md"] += 1
        try:
            head = "\n".join(skill_md.read_text(encoding="utf-8", errors="ignore").splitlines()[:10])
            if re.search(r"(?m)^version:", head):
                result["with_version"] += 1
            else:
                result["missing_version"].append(pkg.name)
        except Exception as e:
            result["error"] = f"read {skill_md}: {e}"
    result["missing_version_count"] = len(result["missing_version"])
    return result


def step_git_log() -> dict:
    """步骤 4: 取 git log 末次 commit 时间"""
    result = {"last_commit_iso": None, "last_commit_short": None, "branch": None, "error": None}
    code, out, err = run(["git", "log", "-1", "--format=%ad|%h|%s", "--date=iso"], timeout=10)
    if code != 0:
        result["error"] = err[:300]
        return result
    parts = out.strip().split("|", 2)
    if len(parts) >= 3:
        result["last_commit_iso"] = parts[0].strip()
        result["last_commit_short"] = parts[1].strip()
        result["last_commit_subject"] = parts[2].strip()
    code2, out2, _ = run(["git", "rev-parse", "--abbrev-ref", "HEAD"], timeout=5)
    if code2 == 0:
        result["branch"] = out2.strip()
    return result


def step_history_digest(history_date: str | None) -> dict:
    """步骤 5: 读历史日期的 INDEX.md + implementation-log.md,统计三态"""
    result = {"history_date": history_date, "total_advices": 0,
              "adopted": 0, "in_progress": 0, "not_started": 0, "stale": 0,
              "open_q_ids": [], "error": None}
    if not history_date:
        return result
    impl_log = LOG_DIR / history_date / "implementation-log.md"
    if not impl_log.exists():
        result["error"] = f"implementation-log.md not found at {impl_log}"
        return result
    text = impl_log.read_text(encoding="utf-8", errors="ignore")
    # 简化解析: 数 ## ID- 出现次数 + 状态行
    id_blocks = re.findall(r"##\s+ID-\d+", text)
    result["total_advices"] = len(id_blocks)
    # 数 ✅ / ⏳ / ❌
    result["adopted"] = len(re.findall(r"- 结果:\s*✅", text))
    result["in_progress"] = len(re.findall(r"- 结果:\s*⏳", text))
    result["not_started"] = len(re.findall(r"- 结果:\s*❌", text))
    # 抓 Q-XX 等待项
    result["open_q_ids"] = re.findall(r"\bQ-\d{2}\b", text)
    return result


def step_baseline_table(date: str, scan: dict, fm: dict, git: dict) -> dict:
    """步骤 6: 输出 daily-vibe-coding 12 项基线表(供 self-audit.md 直接抄)"""
    return {
        "skill_count": fm.get("total_skill_dirs"),
        "skill_md_count": fm.get("has_skill_md"),
        "with_version_count": fm.get("with_version"),
        "missing_version_count": fm.get("missing_version_count"),
        "scan_files": scan.get("files_scanned"),
        "scan_verdict": scan.get("verdict"),
        "scan_high": scan.get("high"),
        "scan_medium": scan.get("medium"),
        "scan_low": scan.get("low"),
        "scan_whitelist_lines": scan.get("whitelist_lines"),
        "last_commit_iso": git.get("last_commit_iso"),
        "git_branch": git.get("branch"),
        "collect_time_iso": datetime.now(TZ).isoformat(timespec="seconds"),
        "collect_date": date,
    }


def main():
    ap = argparse.ArgumentParser(description="daily-vibe-coding 基线采集器")
    ap.add_argument("--date", default=today_str(), help="今日日期(默认今天)")
    ap.add_argument("--history-date", help="历史日期,用于统计三态")
    ap.add_argument("--no-scan", action="store_true", help="跳过安全扫描(快路径)")
    ap.add_argument("--out", help="输出路径(默认 logs/daily-vibe-coding/<date>/_baseline.json)")
    args = ap.parse_args()

    print(f"[collect-baseline] date={args.date} history={args.history_date} no_scan={args.no_scan}")

    py = find_python()
    print(f"[collect-baseline] python={py}")

    # 步骤 1+2: 安全扫描(可选)
    if args.no_scan:
        scan = {"scan": "skipped", "error": "user --no-scan"}
    else:
        print("[collect-baseline] 步骤 1+2: 安全扫描 + 解析 JSON...")
        scan = step_security_scan(py)
        if scan.get("error"):
            print(f"[collect-baseline] WARN: {scan['error']}", file=sys.stderr)

    # 步骤 3: frontmatter 枚举
    print("[collect-baseline] 步骤 3: SKILL.md frontmatter 枚举...")
    fm = step_frontmatter_audit()
    if fm.get("error"):
        print(f"[collect-baseline] WARN: {fm['error']}", file=sys.stderr)

    # 步骤 4: git log
    print("[collect-baseline] 步骤 4: git log 末次 commit...")
    git_log = step_git_log()

    # 步骤 5: 历史消化
    print(f"[collect-baseline] 步骤 5: 历史消化 {args.history_date or '(skip)'}...")
    history = step_history_digest(args.history_date)

    # 步骤 6: 基线表
    baseline = step_baseline_table(args.date, scan, fm, git_log)

    payload = {
        "baseline_table": baseline,
        "scan_detail": scan,
        "frontmatter_detail": fm,
        "git_detail": git_log,
        "history_digest": history,
    }

    # 输出
    out_path = Path(args.out) if args.out else (LOG_DIR / args.date / "_baseline.json")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[collect-baseline] OK -> {out_path}")
    print(f"[collect-baseline] baseline_table:")
    for k, v in baseline.items():
        print(f"  {k}: {v}")

    return 0 if not scan.get("error") else 2


if __name__ == "__main__":
    sys.exit(main())