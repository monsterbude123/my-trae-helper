"""
06_decision_layer_tag.py — SKILL.md 决策层级 / 反例 / 章节编号标注校验

检查项（关键词 + 正则扫描）：
    必须（含 § 章节编号）
    推荐（决策层级 / 反例 / requires — requires 由 01 校验，本处仅作交叉确认）

CLI:    python 06_decision_layer_tag.py --target <skill-path> [--json]
退出码: 0=PASS  2=WARN  4=BLOCK  5=ARG_ERROR  6=INTERNAL_ERROR
"""

import argparse
import json
import re
import sys
import time
from pathlib import Path


CHECK_ID = "06_decision_layer_tag"
SECTION_RE = re.compile(r"^#{1,3}\s*§", re.M)  # ## §A / ### §0
SECTION_LOOSE_RE = re.compile(r"§[A-Z0-9]")  # 兜底：内联引用 §A/§F 等
DECISION_RE = re.compile(r"决策层级|决策层|decision\s*layer|L[0-9]\b|L[1-9]\b|§B\b")
ANTI_RE = re.compile(r"反例|anti-?pattern|anti\s+pattern|R-[123]\b")


def evaluate(target: Path):
    issues = []
    skill_md = target / "SKILL.md"
    if not skill_md.is_file():
        return {
            "id": CHECK_ID,
            "status": "BLOCK",
            "score": 0,
            "issues": [
                {
                    "code": "SKILL_MD_MISSING",
                    "severity": "HIGH",
                    "message": "SKILL.md 不存在",
                    "file": str(skill_md),
                    "line": None,
                }
            ],
        }

    try:
        text = skill_md.read_text(encoding="utf-8", errors="ignore")
    except OSError as exc:
        return {
            "id": CHECK_ID,
            "status": "BLOCK",
            "score": 0,
            "issues": [
                {
                    "code": "SKILL_MD_UNREADABLE",
                    "severity": "HIGH",
                    "message": f"无法读取 SKILL.md: {exc}",
                    "file": str(skill_md),
                    "line": None,
                }
            ],
        }

    has_section = bool(SECTION_RE.search(text))
    has_section_loose = bool(SECTION_LOOSE_RE.search(text))
    has_decision = bool(DECISION_RE.search(text))
    has_anti = bool(ANTI_RE.search(text))

    if not (has_section or has_section_loose):
        issues.append(
            {
                "code": "SECTION_MISSING",
                "severity": "HIGH",
                "message": "SKILL.md 缺章节编号体系（## §X 形式）",
                "file": str(skill_md),
                "line": None,
            }
        )

    missing = []
    if not has_decision:
        missing.append("decision-layer")
    if not has_anti:
        missing.append("anti-pattern")

    if len(missing) >= 2:
        issues.append(
            {
                "code": "TAGS_MISSING_BOTH",
                "severity": "MEDIUM",
                "message": f"决策层级 + 反例两类标注均缺: {', '.join(missing)}",
                "file": str(skill_md),
                "line": None,
            }
        )
    elif len(missing) == 1:
        issues.append(
            {
                "code": "TAGS_MISSING",
                "severity": "LOW",
                "message": f"缺少标注: {missing[0]}",
                "file": str(skill_md),
                "line": None,
            }
        )

    high = sum(1 for x in issues if x["severity"] == "HIGH")
    medium = sum(1 for x in issues if x["severity"] == "MEDIUM")
    if high > 0:
        status, score = "BLOCK", max(0, 50 - 20 * high)
    elif medium >= 3:
        status, score = "WARN", max(40, 100 - 10 * medium)
    else:
        score = max(0, 100 - 5 * medium)
        status = "PASS"

    return {
        "id": CHECK_ID,
        "status": status,
        "score": score,
        "issues": issues,
        "signals": {
            "section_numbering": has_section,
            "section_loose_ref": has_section_loose,
            "decision_layer": has_decision,
            "anti_pattern": has_anti,
        },
    }


def main():
    parser = argparse.ArgumentParser(description="决策层级 / 反例标注校验")
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
