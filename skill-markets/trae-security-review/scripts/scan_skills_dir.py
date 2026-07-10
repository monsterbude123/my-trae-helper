"""
TRAE Security Review — Skill 目录静态扫描脚本

对 Skill 目录做 5 类风险静态检测：
- HIGH: 危险删除命令、动态执行代码、硬编码密钥
- MEDIUM: Shell 执行调用、不安全网络请求
- LOW: 信息泄露、宽权限、弱算法

用法:
    python scan_skills_dir.py <skills_dir> [output_dir]
"""

import json
import re
import sys
from datetime import datetime
from pathlib import Path


CHECK_ITEMS = [
    {
        "code": "CMD_RM_RF",
        "name": "危险删除命令",
        "severity": "high",
        "regex": re.compile(r"\brm\s+-rf\b"),
        "message": "检测到无保护递归删除命令",
        "remediation": "限制删除范围并加入路径白名单校验"
    },
    {
        "code": "DYN_EVAL",
        "name": "动态执行代码",
        "severity": "high",
        "regex": re.compile(r"\beval\s*\(|\bexec\s*\("),
        "message": "检测到动态代码执行模式",
        "remediation": "替换为显式分支逻辑，禁止直接 eval/exec"
    },
    {
        "code": "HARDCODED_SECRET",
        "name": "硬编码密钥",
        "severity": "high",
        "regex": re.compile(
            r"(api[_-]?key|token|secret|password|private_key)"
            r"\s*[:=]\s*['\"`].{8,}['\"`]?",
            re.I
        ),
        "message": "检测到疑似硬编码密钥",
        "remediation": "改为环境变量或密钥管理服务注入"
    },
    {
        "code": "SHELL_EXEC",
        "name": "Shell 执行调用",
        "severity": "medium",
        "regex": re.compile(
            r"(child_process\.(exec|execSync|spawn)"
            r"|subprocess\.(call|Popen|run)"
            r"|os\.system)\s*\(",
        ),
        "message": "检测到 Shell 执行调用",
        "remediation": "改用参数化调用并增加命令白名单"
    },
    {
        "code": "HTTP_INSECURE",
        "name": "明文 HTTP 调用",
        "severity": "medium",
        "regex": re.compile(r"http://", re.I),
        "message": "检测到明文 HTTP 链接",
        "remediation": "替换为 HTTPS 并校验证书"
    },
    {
        "code": "SUDO_OPERATION",
        "name": "提权操作",
        "severity": "medium",
        "regex": re.compile(r"\bsudo\b"),
        "message": "检测到提权操作",
        "remediation": "考虑是否需要提权，遵循最小权限原则"
    },
    {
        "code": "STACK_LEAK",
        "name": "栈追踪泄露",
        "severity": "low",
        "regex": re.compile(
            r"(print\(.*traceback|print\(.*stack|console\.(error|log)"
            r".*stack|logging\.exception)",
        ),
        "message": "检测到潜在栈追踪泄露",
        "remediation": "生产环境关闭 DEBUG 输出"
    },
    {
        "code": "WEAK_CRYPTO",
        "name": "弱加密算法",
        "severity": "low",
        "regex": re.compile(r"\b(MD5|SHA1|DES|RC4)\b", re.I),
        "message": "检测到弱加密算法引用",
        "remediation": "升级到 SHA-256 / AES-256"
    },
]

TEXT_FILE_EXTS = {
    ".md", ".txt", ".json", ".js", ".ts", ".py", ".sh",
    ".ps1", ".yaml", ".yml", ".toml", ".cfg", ".conf",
}

IGNORE_DIRS = {"node_modules", ".git", "dist", "build", "coverage", "__pycache__", ".venv"}


def iter_files(root: Path):
    for path in root.rglob("*"):
        if path.is_dir():
            continue
        if any(part in IGNORE_DIRS for part in path.parts):
            continue
        if path.suffix.lower() in TEXT_FILE_EXTS:
            yield path


def scan(skills_dir: Path):
    findings = []
    scanned = 0
    for file_path in iter_files(skills_dir):
        scanned += 1
        try:
            content = file_path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        for item in CHECK_ITEMS:
            if item["regex"].search(content):
                findings.append({
                    "file": str(file_path),
                    "severity": item["severity"],
                    "code": item["code"],
                    "name": item["name"],
                    "message": item["message"],
                    "remediation": item["remediation"],
                })

    risk_counts = {"high": 0, "medium": 0, "low": 0}
    for f in findings:
        risk_counts[f["severity"]] += 1

    triggered_codes = {f["code"] for f in findings}
    detection_items = [
        {"code": item["code"], "name": item["name"], "severity": item["severity"]}
        for item in CHECK_ITEMS
        if item["code"] in triggered_codes
    ]

    severity_rank = {"high": 0, "medium": 1, "low": 2}
    remediation_map = {}
    for f in findings:
        key = f["code"]
        if key not in remediation_map:
            remediation_map[key] = {
                "severity": f["severity"],
                "name": f["name"],
                "advice": f["remediation"],
            }
    remediation = sorted(remediation_map.values(), key=lambda x: severity_rank[x["severity"]])

    total = risk_counts["high"] + risk_counts["medium"] + risk_counts["low"]
    if risk_counts["high"] > 0:
        verdict = "BLOCKED"
    elif risk_counts["medium"] > 2:
        verdict = "WARNING"
    else:
        verdict = "PASS"

    return {
        "scanned_files": scanned,
        "findings": findings,
        "risk_counts": risk_counts,
        "detection_items": detection_items,
        "remediation": remediation,
        "verdict": verdict,
        "summary": (
            f"扫描文件 {scanned} 个 | "
            f"HIGH {risk_counts['high']} | "
            f"MEDIUM {risk_counts['medium']} | "
            f"LOW {risk_counts['low']} | "
            f"判定: {verdict}"
        ),
    }


def write_reports(result, skills_dir: Path, output_dir: Path):
    output_dir.mkdir(parents=True, exist_ok=True)
    safe_name = re.sub(r'[<>:"/\\|?*]+', "_", skills_dir.name) or "skills-scan"
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")

    # JSON
    json_path = output_dir / f"{safe_name}_{ts}.json"
    json_path.write_text(
        json.dumps({**result, "skills_dir": str(skills_dir), "generated_at": ts},
                   ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    # Markdown
    md_path = output_dir / f"{safe_name}_{ts}.md"
    sev_zh = {"high": "🔴 HIGH", "medium": "🟠 MEDIUM", "low": "🔵 LOW"}
    lines = [
        f"# 安全扫描报告: {skills_dir.name}",
        f"",
        f"- 扫描目录: `{skills_dir}`",
        f"- 扫描时间: `{ts}`",
        f"- 扫描文件: `{result['scanned_files']}`",
        f"- 判定: `{result['verdict']}`",
        f"",
        "## 风险统计",
        f"",
        f"| 级别 | 数量 |",
        f"|------|------|",
        f"| HIGH | {result['risk_counts']['high']} |",
        f"| MEDIUM | {result['risk_counts']['medium']} |",
        f"| LOW | {result['risk_counts']['low']} |",
    ]
    if result["findings"]:
        lines += [
            "",
            "## 发现明细",
            "",
            "| 级别 | 类型 | 描述 | 文件 | 建议 |",
            "|------|------|------|------|------|",
        ]
        for f in result["findings"]:
            f_sev = sev_zh.get(f["severity"], f["severity"])
            f_file = str(f["file"]).replace("|", "\\|")
            f_msg = f["message"].replace("|", "\\|")
            f_name = f["name"].replace("|", "\\|")
            f_fix = f["remediation"].replace("|", "\\|")
            lines.append(f"| {f_sev} | {f_name} | {f_msg} | `{f_file}` | {f_fix} |")
    lines += [
        "",
        "## 整改建议",
        "",
    ]
    if result["remediation"]:
        for i, item in enumerate(result["remediation"], 1):
            lines.append(f"{i}. {sev_zh.get(item['severity'], item['severity'])} {item['name']}: {item['advice']}")
    else:
        lines.append("- 未发现风险项，无需整改")
    md_path.write_text("\n".join(lines), encoding="utf-8")

    return json_path, md_path


def main():
    if len(sys.argv) < 2:
        print("Usage: python scan_skills_dir.py <skills_dir> [output_dir]")
        sys.exit(1)

    skills_dir = Path(sys.argv[1]).resolve()
    output_dir = Path(sys.argv[2]).resolve() if len(sys.argv) > 2 else (Path.cwd() / "auto_reports")

    if not skills_dir.exists() or not skills_dir.is_dir():
        print(json.dumps({"error": f"Invalid directory: {skills_dir}"}))
        sys.exit(1)

    result = scan(skills_dir)
    json_path, md_path = write_reports(result, skills_dir, output_dir)

    result["report_files"] = {"json": str(json_path), "md": str(md_path)}
    result["skills_dir"] = str(skills_dir)
    result["generated_at"] = datetime.now().isoformat()

    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
