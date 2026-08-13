"""
04_scripts_boundary.py — 校验 <skill>/scripts/ 边界

• 单脚本 ≤150 行（>200 硬上限 = HIGH；150~200 = MEDIUM）
• 根目录不得出现非 SKILL.md/README.md/LICENSE 的可执行文件
• scripts 内禁止 ../ 或 ../../ 越界相对路径
• 禁止裸 shell 字符串（bash -c / eval / exec，与 scan_skills_dir 的 SHELL_EXEC 区分：
  这里指完全脱离 subprocess 的字符串调用）

CLI:    python 04_scripts_boundary.py --target <skill-path> [--json]
退出码: 0=PASS  2=WARN  4=BLOCK  5=ARG_ERROR  6=INTERNAL_ERROR
"""

import argparse
import json
import re
import sys
import time
from pathlib import Path


CHECK_ID = "04_scripts_boundary"
ROOT_ALLOWED = {"SKILL.md", "README.md", "LICENSE", "LICENSE.md", "CHANGELOG.md"}
SCRIPT_EXTS = {".py", ".mjs", ".ps1", ".sh", ".js", ".ts"}
SKIP_DIRS = {"__pycache__", "node_modules", ".git", "audit_reports", "auto_reports"}
BARE_SHELL_RES = [
    re.compile(r"\beval\s*\("),
    re.compile(r"\bexec\s*\("),
    re.compile(r"\bbash\s+-c\s+"),
    re.compile(r"\bsh\s+-c\s+"),
    re.compile(r"os\.system\s*\("),
]
PATH_ESCAPE_RE = re.compile(r"['\"][^'\"]*\.\./[^'\"]*['\"]")
DOCSTRING_TRIPLE = re.compile(r'^\s*(?:[ru]?["\']{3}|["\']{3})')


def evaluate(target: Path):
    issues = []
    scripts_dir = target / "scripts"

    if scripts_dir.is_dir():
        for path in sorted(scripts_dir.rglob("*")):
            if not path.is_file():
                continue
            if path.suffix.lower() not in SCRIPT_EXTS:
                continue
            if any(part in SKIP_DIRS for part in path.parts):
                continue
            try:
                content = path.read_text(encoding="utf-8", errors="ignore")
            except OSError:
                continue
            lines = content.splitlines()
            total = len(lines)
            if total > 200:
                issues.append(
                    {
                        "code": "SCRIPT_TOO_LONG_HARD",
                        "severity": "HIGH",
                        "message": f"脚本超过 200 行（{total} 行）",
                        "file": str(path),
                        "line": None,
                    }
                )
            elif total > 150:
                issues.append(
                    {
                        "code": "SCRIPT_TOO_LONG",
                        "severity": "MEDIUM",
                        "message": f"脚本超过 150 行（{total} 行）",
                        "file": str(path),
                        "line": None,
                    }
                )

            # 跳过 docstring / 注释行：粗略识别以 """ 或 ''' 开头的块
            in_docstring = False
            quote = None
            for i, line in enumerate(lines, start=1):
                stripped = line.lstrip()
                if not in_docstring:
                    if DOCSTRING_TRIPLE.match(stripped):
                        in_docstring = True
                        # 同行收尾
                        rest = stripped[3:]
                        if (rest.count('"""') >= 1 and stripped.startswith('"""')) or (
                            rest.count("'''") >= 1 and stripped.startswith("'''")
                        ):
                            in_docstring = False
                        continue
                else:
                    if '"""' in line or "'''" in line:
                        in_docstring = False
                    continue
                # 注释行
                if stripped.startswith("#"):
                    continue
                if PATH_ESCAPE_RE.search(line):
                    issues.append(
                        {
                            "code": "PATH_ESCAPE",
                            "severity": "HIGH",
                            "message": f"越界 ../ 相对路径引用: {line.strip()[:80]}",
                            "file": str(path),
                            "line": i,
                        }
                    )
                for rgx in BARE_SHELL_RES:
                    if rgx.search(line):
                        issues.append(
                            {
                                "code": "BARE_SHELL",
                                "severity": "HIGH",
                                "message": f"裸 shell 字符串: {rgx.pattern}",
                                "file": str(path),
                                "line": i,
                            }
                        )
                        break
            del content, lines

    # 根目录可执行文件
    for child in target.iterdir():
        if not child.is_file():
            continue
        if child.name in ROOT_ALLOWED:
            continue
        suffix = child.suffix.lower()
        if suffix in {".py", ".mjs", ".ps1", ".sh", ".bat", ".cmd"}:
            issues.append(
                {
                    "code": "ROOT_EXECUTABLE",
                    "severity": "MEDIUM",
                    "message": f"skill 根目录存在可执行文件: {child.name}",
                    "file": str(child),
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
    return {"id": CHECK_ID, "status": status, "score": score, "issues": issues}


def main():
    parser = argparse.ArgumentParser(description="scripts/ 边界校验")
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
