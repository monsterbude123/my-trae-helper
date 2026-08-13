"""
05_references_size.py — 校验 SKILL.md 与 references/ 体积 + skill 包总大小

阈值（与 AGENTS.md §2 铁律 + §7.6 技能库建设铁律 对齐）：
    SKILL.md                 ≤ 500 行（500~800 = MEDIUM；>800 = HIGH）
    references/ 单文件       ≤ 250 行（250~500 = MEDIUM；>500 = HIGH）
    references/ 总体积       ≤ 200KB
    skill 包总大小           ≤ 1MB（不含 .git / node_modules / __pycache__）
    references/ 内部目录深度 > 5 层 → LOW

CLI:    python 05_references_size.py --target <skill-path> [--json]
退出码: 0=PASS  2=WARN  4=BLOCK  5=ARG_ERROR  6=INTERNAL_ERROR
"""

import argparse
import json
import sys
import time
from pathlib import Path


CHECK_ID = "05_references_size"
SKILL_MD_SOFT = 500
SKILL_MD_HARD = 800
REF_FILE_SOFT = 250
REF_FILE_HARD = 500
REF_TOTAL_KB = 200
PKG_TOTAL_BYTES = 1 * 1024 * 1024
SKIP_DIRS = {".git", "node_modules", "__pycache__", ".venv", ".trae"}


def dir_size(root: Path):
    total = 0
    for p in root.rglob("*"):
        if not p.is_file():
            continue
        if any(part in SKIP_DIRS for part in p.parts):
            continue
        try:
            total += p.stat().st_size
        except OSError:
            pass
    return total


def dir_depth(root: Path):
    if not root.exists():
        return 0
    md = 0
    for p in root.rglob("*"):
        if p.is_dir():
            d = len(p.relative_to(root).parts)
            if d > md:
                md = d
    return md


def evaluate(target: Path):
    issues = []
    skill_md = target / "SKILL.md"
    if skill_md.is_file():
        try:
            text = skill_md.read_text(encoding="utf-8", errors="ignore")
        except OSError as exc:
            issues.append(
                {
                    "code": "SKILL_MD_UNREADABLE",
                    "severity": "HIGH",
                    "message": f"无法读取 SKILL.md: {exc}",
                    "file": str(skill_md),
                    "line": None,
                }
            )
            text = ""
        lines = text.splitlines()
        n = len(lines)
        if n > SKILL_MD_HARD:
            issues.append(
                {
                    "code": "SKILL_MD_TOO_LONG_HARD",
                    "severity": "HIGH",
                    "message": f"SKILL.md {n} 行（>={SKILL_MD_HARD}）",
                    "file": str(skill_md),
                    "line": None,
                }
            )
        elif n > SKILL_MD_SOFT:
            issues.append(
                {
                    "code": "SKILL_MD_TOO_LONG",
                    "severity": "MEDIUM",
                    "message": f"SKILL.md {n} 行（>{SKILL_MD_SOFT}）",
                    "file": str(skill_md),
                    "line": None,
                }
            )

    ref_dir = target / "references"
    if ref_dir.is_dir():
        ref_total = 0
        for p in ref_dir.rglob("*"):
            if not p.is_file():
                continue
            try:
                size = p.stat().st_size
            except OSError:
                continue
            ref_total += size
            try:
                text = p.read_text(encoding="utf-8", errors="ignore")
            except OSError:
                continue
            n = len(text.splitlines())
            if n > REF_FILE_HARD:
                issues.append(
                    {
                        "code": "REF_FILE_TOO_LONG_HARD",
                        "severity": "HIGH",
                        "message": f"references/{p.relative_to(ref_dir).as_posix()} {n} 行（>={REF_FILE_HARD}）",
                        "file": str(p),
                        "line": None,
                    }
                )
            elif n > REF_FILE_SOFT:
                issues.append(
                    {
                        "code": "REF_FILE_TOO_LONG",
                        "severity": "MEDIUM",
                        "message": f"references/{p.relative_to(ref_dir).as_posix()} {n} 行（>{REF_FILE_SOFT}）",
                        "file": str(p),
                        "line": None,
                    }
                )
        if ref_total > REF_TOTAL_KB * 1024:
            issues.append(
                {
                    "code": "REF_TOTAL_TOO_BIG",
                    "severity": "MEDIUM",
                    "message": f"references/ 总体积 {ref_total / 1024:.1f}KB（>{REF_TOTAL_KB}KB）",
                    "file": str(ref_dir),
                    "line": None,
                }
            )
        if dir_depth(ref_dir) > 5:
            issues.append(
                {
                    "code": "REF_DEPTH_DEEP",
                    "severity": "LOW",
                    "message": "references/ 内部目录深度 > 5 层",
                    "file": str(ref_dir),
                    "line": None,
                }
            )

    pkg_bytes = dir_size(target)
    if pkg_bytes > PKG_TOTAL_BYTES:
        issues.append(
            {
                "code": "PKG_TOO_BIG",
                "severity": "MEDIUM",
                "message": f"skill 包总体积 {pkg_bytes / 1024:.1f}KB（>{PKG_TOTAL_BYTES // 1024}KB）",
                "file": str(target),
                "line": None,
            }
        )

    high = sum(1 for x in issues if x["severity"] == "HIGH")
    medium = sum(1 for x in issues if x["severity"] == "MEDIUM")
    if high > 0:
        status, score = "BLOCK", max(0, 50 - 15 * high)
    elif medium >= 3:
        status, score = "WARN", max(40, 100 - 8 * medium)
    else:
        score = max(0, 100 - 5 * medium)
        status = "PASS"

    return {
        "id": CHECK_ID,
        "status": status,
        "score": score,
        "issues": issues,
        "pkg_bytes": pkg_bytes,
    }


def main():
    parser = argparse.ArgumentParser(description="references + 总体积校验")
    parser.add_argument("--target", required=True, help="skill 目录路径")
    parser.add_argument("--json", action="store_true", help="强制 JSON 输出")
    args = parser.parse_args()

    target = Path(args.target).resolve()
    if not target.is_dir():
        sys.stdout.write(
            json.dumps(
                {
                    "id": CHECK_ID,
                    "status": "BLOCK",
                    "score": 0,
                    "issues": [
                        {
                            "code": "TARGET_NOT_DIR",
                            "severity": "HIGH",
                            "message": f"目标不是目录: {target}",
                            "file": str(target),
                            "line": None,
                        }
                    ],
                    "duration_ms": 0,
                },
                ensure_ascii=False,
            )
        )
        sys.stdout.write("\n")
        sys.exit(5)

    t0 = time.time()
    try:
        result = evaluate(target)
    except Exception as exc:  # noqa: BLE001
        sys.stdout.write(
            json.dumps(
                {
                    "id": CHECK_ID,
                    "status": "INTERNAL_ERROR",
                    "score": 0,
                    "issues": [
                        {
                            "code": "EXCEPTION",
                            "severity": "HIGH",
                            "message": f"内部异常: {exc}",
                            "file": str(target),
                            "line": None,
                        }
                    ],
                    "duration_ms": int((time.time() - t0) * 1000),
                },
                ensure_ascii=False,
            )
        )
        sys.stdout.write("\n")
        sys.exit(6)

    result["duration_ms"] = int((time.time() - t0) * 1000)
    sys.stdout.write(json.dumps(result, ensure_ascii=False))
    sys.stdout.write("\n")
    code_map = {"PASS": 0, "WARN": 2, "BLOCK": 4}
    sys.exit(code_map.get(result["status"], 4))


if __name__ == "__main__":
    main()
