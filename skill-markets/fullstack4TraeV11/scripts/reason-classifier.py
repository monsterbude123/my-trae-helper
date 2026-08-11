#!/usr/bin/env python3
"""
V11 reason-classifier.py — 6 类抽象理由检测（Article XVI）

Usage:
    python reason-classifier.py [--file <path>] [--project-root <path>]

6 类抽象理由（V10.10 NEW）:
  1. 理解偏差
  2. 流程裁剪
  3. 心理障碍
  4. 概念漂移
  5. 上下文丢失
  6. 权衡取舍

Exit codes:
    0 = PASS（未发现抽象理由）
    1 = FAIL（发现抽象理由）
"""
import sys
import argparse
import pathlib
import json
import re
from datetime import datetime, timezone


REASON_PATTERNS = {
    "理解偏差": r"理解偏差",
    "流程裁剪": r"流程裁剪",
    "心理障碍": r"心理障碍",
    "概念漂移": r"概念漂移",
    "上下文丢失": r"上下文丢失",
    "权衡取舍": r"权衡取舍",
}


def classify_text(text: str) -> list:
    """分类文本中的抽象理由"""
    found = []
    for category, pattern in REASON_PATTERNS.items():
        matches = list(re.finditer(pattern, text))
        for match in matches:
            # 提取上下文（前后各 30 字符）
            start = max(0, match.start() - 30)
            end = min(len(text), match.end() + 30)
            context = text[start:end].replace("\n", " ")
            found.append({
                "category": category,
                "context": context,
            })
    return found


def main():
    parser = argparse.ArgumentParser(description="V11 6 类抽象理由检测")
    parser.add_argument("--file", help="单文件检测")
    parser.add_argument("--project-root", default=".", help="项目级检测")
    parser.add_argument("--json", action="store_true", help="JSON 输出")
    args = parser.parse_args()

    if args.file:
        path = pathlib.Path(args.file)
        if not path.exists():
            print(f"❌ 文件不存在: {path}")
            return 1
        text = path.read_text(encoding="utf-8")
        found = classify_text(text)
        output = {
            "scan_at": datetime.now(timezone.utc).isoformat(),
            "file": str(path),
            "found_count": len(found),
            "matches": found,
            "status": "PASS" if not found else "FAIL",
        }
    else:
        project_root = pathlib.Path(args.project_root).resolve()
        all_found = []
        # 白名单：含"理解偏差"等引用但非真实理由
        filename_whitelist = {
            "SKILL.md",
            "common-anti-patterns.md",
            "common-iron-rules.md",
            "constitution.md",
            "blockage-report.md",
            "stage-card-protocol.md",
            "report-growth.md",
            "ask-question-anti-patterns.md",
            "anti-distortion.md",  # references/ 下反例文档
            "ask-question-anti-patterns.md",
        }
        for md in project_root.rglob("*.md"):
            if any(p in md.parts for p in [
                "node_modules", "__pycache__", ".git",
                "anti-patterns",
                "research",
            ]):
                continue
            if md.name in filename_whitelist:
                continue
            try:
                text = md.read_text(encoding="utf-8")
            except Exception:
                continue
            matches = classify_text(text)
            for m in matches:
                m["file"] = str(md.relative_to(project_root))
                all_found.append(m)

        output = {
            "scan_at": datetime.now(timezone.utc).isoformat(),
            "project_root": str(project_root),
            "found_count": len(all_found),
            "matches": all_found,
            "status": "PASS" if not all_found else "FAIL",
        }

    if args.json:
        print(json.dumps(output, indent=2, ensure_ascii=False))
    else:
        icon = "❌" if output["found_count"] > 0 else "✅"
        print(f"{icon} {output['status']} — {output['found_count']} 个抽象理由")
        for m in output["matches"][:10]:
            file_info = m.get("file", "?")
            print(f"   [{ {m['category']}}] {file_info}: ...{m['context']}...")

    return 0 if output["status"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())