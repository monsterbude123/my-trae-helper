#!/usr/bin/env python3
"""
V11 secrets-detector.py — Article XVII Secret Redaction 程序化扫描(P3-4 NEW)

定位:common-iron-rules.md Article XVII 17.1-17.6 6 条 secret redaction rule 程序化落地。
取代分散在 templates/hooks/ 的局部检测,提供 --file / --project-root 统一接口。

Usage:
    python secrets-detector.py --file <path> [--json]
    python secrets-detector.py --project-root <path> [--json]

Exit codes:
    0 = PASS(无 secret 命中)
    1 = FAIL(任一命中 → 输出 hits 列表)

检测 pattern 类别:
  - AWS Access Key (AKIA / ASIA 前缀 + 16 字符)
  - OpenAI API Key (sk- 开头 + 32+ 字符)
  - GitHub Token (ghp_ / ghs_ / gho_ / ghu_ 前缀 + 36 字符)
  - Generic api_key= / token= / password= / secret= (key=value 形式)
  - Authorization: Bearer <jwt>
  - private_key / -----BEGIN <algo> PRIVATE KEY-----
  - JWT-like (eyJ 开头 + base64 段 + dot 分隔)
  - 中国大陆手机号 (1[3-9]xxxxxxxxx)
  - 身份证号 (18 位,末位 X/x 校验)
  - 邮箱 PII (排除 docstring / 注释常见邮箱)
"""
import argparse
import json
import pathlib
import re
import sys
from typing import List, Dict, Tuple


# === 检测 pattern ===
SECRET_PATTERNS = [
    {
        "id": "aws-access-key",
        "name": "AWS Access Key",
        "regex": r"\b(AKIA|ASIA)[0-9A-Z]{16}\b",
        "article": "17.1",
        "severity": "P0",
    },
    {
        "id": "openai-api-key",
        "name": "OpenAI API Key",
        "regex": r"\bsk-[a-zA-Z0-9]{20,}\b",
        "article": "17.1",
        "severity": "P0",
    },
    {
        "id": "github-token",
        "name": "GitHub Token",
        "regex": r"\b(ghp|ghs|gho|ghu)_[a-zA-Z0-9]{36}\b",
        "article": "17.1",
        "severity": "P0",
    },
    {
        "id": "generic-credential-keyvalue",
        "name": "Generic Credential (key=value)",
        # 排除占位符:空 / xxx / placeholder / <VAR> / ${VAR} / REDACTED
        # 兼容三种形式:
        #   - shell:    password=secret123
        #   - YAML:     password: secret123
        #   - JSON:     "password": "secret123"
        "regex": r"(?i)[\"']?(api[_-]?key|token|password|passwd|pwd|secret|access[_-]?key|client[_-]?secret)[\"']?\s*[:=]\s*[\"']?([^\s\"'<>$\{\}]{6,})[\"']?",
        "article": "17.4",
        "severity": "P0",
        "exclude_values": ["xxx", "XXXX", "placeholder", "<VAR>", "${VAR}", "REDACTED", "null", "None", "example", "test"],
    },
    {
        "id": "authorization-bearer",
        "name": "Authorization: Bearer",
        "regex": r"(?i)Authorization:\s*Bearer\s+([A-Za-z0-9\-._~+/]{20,}=*)",
        "article": "17.2",
        "severity": "P0",
    },
    {
        "id": "private-key-block",
        "name": "PEM Private Key Block",
        "regex": r"-----BEGIN (RSA |EC |DSA |PGP |OPENSSH )?PRIVATE KEY-----",
        "article": "17.1",
        "severity": "P0",
    },
    {
        "id": "jwt-like",
        "name": "JWT-like Token",
        # eyJ 开头 + base64 + . + base64 + . + base64
        "regex": r"\beyJ[A-Za-z0-9\-_]{10,}\.[A-Za-z0-9\-_]{10,}\.[A-Za-z0-9\-_]{10,}\b",
        "article": "17.1",
        "severity": "P0",
    },
    {
        "id": "china-mobile-phone",
        "name": "China Mobile Phone (PII)",
        # 1[3-9] 开头 11 位
        "regex": r"(?<![0-9])1[3-9][0-9]{9}(?![0-9])",
        "article": "17.1",
        "severity": "P1",
    },
    {
        "id": "china-id-card",
        "name": "China ID Card (PII)",
        # 18 位,前 17 位数字 + 末位数字或 X
        "regex": r"(?<![0-9])[1-9][0-9]{5}(?:19|20)[0-9]{2}(?:0[1-9]|1[0-2])(?:0[1-9]|[12][0-9]|3[01])[0-9]{3}[0-9Xx](?![0-9])",
        "article": "17.1",
        "severity": "P1",
    },
    {
        "id": "email-pii",
        "name": "Email PII (可疑业务邮箱,非 example/test)",
        # 排除 example.com / test.com 占位
        "regex": r"\b[A-Za-z0-9._%+\-]+@(?!example\.)(?!test\.)[A-Za-z0-9.\-]+\.[A-Za-z]{2,}\b",
        "article": "17.1",
        "severity": "P2",
    },
]


# === 扫描白名单 / 跳过 ===
SKIP_DIR_NAMES = {
    ".git", "node_modules", "__pycache__", "dist", "build",
    "logs", "docs/archive", "tests/fixtures",
}

# 默认扫描文件后缀
SCAN_EXTENSIONS = {
    ".py", ".ts", ".tsx", ".js", ".jsx", ".mjs", ".cjs",
    ".json", ".yaml", ".yml", ".env", ".sh", ".bash", ".ps1",
}


def _compile_patterns() -> List[Dict]:
    """编译 regex,返回 [{id, name, regex, article, severity, exclude_values?}]"""
    compiled = []
    for p in SECRET_PATTERNS:
        try:
            p["compiled"] = re.compile(p["regex"])
        except re.error as e:
            sys.stderr.write(f"[secrets-detector] WARN: {p['id']} regex 编译失败: {e}\n")
            continue
        compiled.append(p)
    return compiled


def _is_excluded_value(value: str, exclude_list) -> bool:
    """检查 generic-credential-keyvalue 命中的 value 是否是占位符。"""
    if not exclude_list:
        return False
    v = value.strip().strip("'").strip('"')
    return v in exclude_list


def scan_text(text: str, patterns: List[Dict]) -> List[Dict]:
    """扫描一段文本,返回 hits 列表。"""
    hits = []
    for line_no, line in enumerate(text.splitlines(), start=1):
        for p in patterns:
            for m in p["compiled"].finditer(line):
                # generic-credential-keyvalue:排除占位符
                if "exclude_values" in p:
                    captured = m.group(2) if m.lastindex and m.lastindex >= 2 else m.group(0)
                    if _is_excluded_value(captured, p["exclude_values"]):
                        continue
                hits.append({
                    "pattern_id": p["id"],
                    "pattern_name": p["name"],
                    "article": p["article"],
                    "severity": p["severity"],
                    "line": line_no,
                    "match": m.group(0)[:50] + ("..." if len(m.group(0)) > 50 else ""),
                })
    return hits


def scan_file(path: pathlib.Path) -> Tuple[List[Dict], List[str]]:
    """扫描单个文件。返回 (hits, errors)。"""
    errors = []
    if not path.exists():
        return [], [f"文件不存在: {path}"]
    try:
        content = path.read_text(encoding="utf-8", errors="ignore")
    except Exception as e:
        return [], [f"读取失败 {path}: {e}"]

    patterns = _compile_patterns()
    hits = scan_text(content, patterns)
    return hits, errors


def scan_project(project_root: pathlib.Path) -> Tuple[List[Dict], List[Dict]]:
    """扫描整个项目。

    返回 (files_with_hits, errors)。
    files_with_hits: [{path, hits: [...]}]
    """
    patterns = _compile_patterns()
    files_with_hits = []
    errors = []

    if not project_root.exists():
        return [], [{"path": str(project_root), "error": "项目根不存在"}]

    for path in project_root.rglob("*"):
        if not path.is_file():
            continue
        if any(skip in path.parts for skip in SKIP_DIR_NAMES):
            continue
        # 跳过 .git / 等目录下的所有文件
        if ".git" in path.parts:
            continue

        # 扩展名匹配(覆盖 .env / .env.local / Dockerfile 等无扩展但需检测)
        suffix_ok = path.suffix in SCAN_EXTENSIONS
        name_ok = path.name.startswith(".env") or path.name in {"Dockerfile", ".npmrc", ".pypirc"}
        if not (suffix_ok or name_ok):
            continue

        try:
            content = path.read_text(encoding="utf-8", errors="ignore")
        except Exception as e:
            errors.append({"path": str(path), "error": f"读取失败: {e}"})
            continue

        hits = scan_text(content, patterns)
        if hits:
            files_with_hits.append({"path": str(path), "hits": hits})

    return files_with_hits, errors


def main():
    parser = argparse.ArgumentParser(
        description="V11 secrets-detector.py — Article XVII Secret Redaction 扫描器"
    )
    parser.add_argument("--file", help="扫描单个文件")
    parser.add_argument("--project-root", help="扫描整个项目根目录")
    parser.add_argument("--json", action="store_true", help="JSON 输出")
    args = parser.parse_args()

    if not args.file and not args.project_root:
        parser.error("必须提供 --file 或 --project-root 之一")

    if args.file:
        hits, errors = scan_file(pathlib.Path(args.file))
        result = {
            "scope": "file",
            "path": args.file,
            "hits": hits,
            "errors": errors,
            "hit_count": len(hits),
            "status": "FAIL" if hits else "PASS",
        }
    else:
        files_with_hits, errors = scan_project(pathlib.Path(args.project_root))
        total_hits = sum(len(f["hits"]) for f in files_with_hits)
        result = {
            "scope": "project",
            "project_root": args.project_root,
            "files_with_hits": files_with_hits,
            "errors": errors,
            "file_count": len(files_with_hits),
            "hit_count": total_hits,
            "status": "FAIL" if files_with_hits else "PASS",
        }

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        status = result["status"]
        icon = "❌" if status == "FAIL" else "✅"
        print(f"{icon} {status} — hit_count={result['hit_count']}")
        if args.file:
            for h in result["hits"]:
                print(f"   [{h['severity']}] L{h['line']} {h['pattern_name']}: {h['match']}")
        else:
            for f in result["files_with_hits"]:
                rel = pathlib.Path(f["path"]).relative_to(args.project_root) if args.project_root else f["path"]
                print(f"\n   📄 {rel}")
                for h in f["hits"]:
                    print(f"      [{h['severity']}] L{h['line']} {h['pattern_name']}: {h['match']}")

    return 1 if result["status"] == "FAIL" else 0


if __name__ == "__main__":
    sys.exit(main())