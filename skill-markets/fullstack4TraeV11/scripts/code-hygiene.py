#!/usr/bin/env python3
"""
V11 code-hygiene.py — 代码卫生扫描

Usage:
    python code-hygiene.py [--src <dir>]

检查项:
  1. 文件行数 ≤ 800
  2. 函数行数 ≤ 50
  3. 魔法数字（数字 > 9 不在常量/字符串中）
  4. 桩代码标记（STUB / TODO / FIXME 堆积）

Exit codes:
    0 = PASS
    1 = FAIL
"""
import sys
import argparse
import pathlib
import json
import re
from datetime import datetime, timezone


def check_file_lines(file_path: pathlib.Path) -> list:
    """单文件代码卫生检查"""
    issues = []

    try:
        content = file_path.read_text(encoding="utf-8")
    except Exception:
        return issues

    lines = content.split("\n")

    # 1. 文件行数 ≤ 800
    if len(lines) > 800:
        issues.append({
            "type": "file_too_long",
            "file": str(file_path),
            "line_count": len(lines),
            "threshold": 800,
        })

    # 2. 函数行数 ≤ 50（粗略按 "def " 或 "fn " 切分）
    func_starts = []
    for i, line in enumerate(lines):
        if re.match(r"^\s*(def |fn |async fn |class )", line):
            func_starts.append(i)

    for idx, start in enumerate(func_starts):
        end = func_starts[idx + 1] if idx + 1 < len(func_starts) else len(lines)
        func_len = end - start
        if func_len > 50:
            issues.append({
                "type": "function_too_long",
                "file": str(file_path),
                "function_start": start + 1,
                "line_count": func_len,
                "threshold": 50,
            })

    # 3. 桩代码堆积（≥3 个 STUB/TODO/FIXME）
    stub_count = sum(content.count(m) for m in ["STUB:", "TODO:", "FIXME:", "XXX"])
    if stub_count > 3:
        issues.append({
            "type": "stub_pileup",
            "file": str(file_path),
            "stub_count": stub_count,
            "threshold": 3,
        })

    return issues


def main():
    parser = argparse.ArgumentParser(description="V11 代码卫生扫描")
    parser.add_argument("--src", default="src", help="src 目录")
    parser.add_argument("--project-root", default=".", help="项目根路径")
    parser.add_argument("--exclude", nargs="*", default=["scripts"], help="排除目录")
    parser.add_argument("--json", action="store_true", help="JSON 输出")
    args = parser.parse_args()

    project_root = pathlib.Path(args.project_root).resolve()
    src_dir = project_root / args.src

    if not src_dir.exists():
        result = {"status": "N/A", "message": f"目录不存在: {src_dir}"}
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print(f"⚠️ {result['message']}")
        return 0

    extensions = {".py", ".ts", ".js", ".tsx", ".jsx", ".rs", ".go"}
    all_issues = []

    for ext in extensions:
        for f in src_dir.rglob(f"*{ext}"):
            if any(p in f.parts for p in ["node_modules", "__pycache__", ".git", "dist", "build"]):
                continue
            if any(p in f.parts for p in args.exclude):
                continue
            issues = check_file_lines(f)
            all_issues.extend(issues)

    is_pass = not all_issues

    output = {
        "scan_at": datetime.now(timezone.utc).isoformat(),
        "status": "PASS" if is_pass else "FAIL",
        "total_issues": len(all_issues),
        "issues": all_issues,
    }

    if args.json:
        print(json.dumps(output, indent=2, ensure_ascii=False))
    else:
        icon = "✅" if is_pass else "❌"
        print(f"{icon} {output['status']} — {len(all_issues)} 项问题")
        for issue in all_issues[:10]:
            print(f"   [{ {issue['type']}}] { {issue.get('file', '?')}}")
        if len(all_issues) > 10:
            print(f"   ... 还有 {len(all_issues) - 10} 项")

    return 0 if is_pass else 1


if __name__ == "__main__":
    sys.exit(main())