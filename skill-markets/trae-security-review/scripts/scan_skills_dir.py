"""
TRAE Security Review — Skill 目录静态扫描脚本（V2.0 +白名单机制）

对 Skill 目录做 8 类风险静态检测：
- HIGH: 危险删除命令、动态执行代码、硬编码密钥
- MEDIUM: Shell 执行调用、不安全网络请求、提权操作
- LOW: 栈追踪泄露、弱加密算法

V2.0 新增（2026-08-10）：白名单机制（解决文档引用误报）
  三层优先级（高 → 低）：
    1. 文件级白名单：扫描根目录放 `.scanignore` 文件，glob 模式匹配
    2. 区块级白名单：HTML 注释 `<!-- scan-whitelist:CODE -->` ... `<!-- /scan-whitelist -->`
       Markdown 注释：`<!-- scan-ignore -->` ... `<!-- /scan-ignore -->`
    3. 行级白名单：单行 `<!-- scan-ignore-line -->` / `# scan-ignore-line`

  注：白名单只豁免**真实误报**（文档描述规则 / 示例代码 / 教程引用）。
     豁免**实际可执行风险**（如某 .py 真调用 `os.system()`）= 白名单失效。

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
            r"(print\(.*\btraceback\b|print\(.*\bstack\b|console\.(error|log)"
            r".*\bstack\b|logging\.exception)",
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

# 白名单机制配置
BLOCK_WHITELIST_START = re.compile(
    r"<!--\s*(?:scan-whitelist(?::[A-Z_,\s]+)?|scan-ignore)\s*-->"
)
BLOCK_WHITELIST_END = re.compile(
    r"<!--\s*/(?:scan-whitelist|scan-ignore)\s*-->"
)
LINE_WHITELIST = re.compile(
    r"(?:<!--\s*scan-ignore-line\s*-->|#\s*scan-ignore-line)"
)


def iter_files(root: Path):
    """递归遍历 root 下的可扫描文件（按 IGNORE_DIRS 过滤）"""
    for path in root.rglob("*"):
        if path.is_dir():
            continue
        if any(part in IGNORE_DIRS for part in path.parts):
            continue
        if path.suffix.lower() in TEXT_FILE_EXTS:
            yield path


def load_file_whitelist(skills_dir: Path) -> list[str]:
    """读取 skills_dir/.scanignore（gitignore 格式 glob 列表）

    支持行内注释（# 开头）和空行忽略。
    """
    ignore_file = skills_dir / ".scanignore"
    patterns = []
    if not ignore_file.is_file():
        return patterns
    try:
        for line in ignore_file.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            patterns.append(line)
    except OSError:
        pass
    return patterns


def is_file_whitelisted(file_path: Path, file_patterns: list[str]) -> bool:
    """判断 file_path 是否被文件级白名单匹配"""
    if not file_patterns:
        return False
    rel = str(file_path).replace("\\", "/")
    for pat in file_patterns:
        # glob 模式匹配（fnmatch 语义）
        if Path(rel).match(pat) or rel.endswith(pat.lstrip("/")):
            return True
        # 简化：basename 包含也算
        basename = file_path.name
        if pat in basename:
            return True
    return False


def build_line_whitelist_mask(content: str, file_ext: str = "") -> dict:
    """构造与 content 行一一对应的白名单遮罩 + 当前 CODE 限定

    返回 dict：
      - "mask": list[bool] 行级遮罩
      - "block_codes": set[str] 区块级 CODE 限定（None = 豁免全部）

    处理三种白名单：
    1. 区块级：<!-- scan-whitelist:CODE --> ... <!-- /scan-whitelist -->
              支持指定 CODE（仅豁免该 CODE）
              文档文件（.md/.txt）忽略 CODE 限定（默认全部豁免）
    2. 区块级：<!-- scan-ignore --> ... <!-- /scan-ignore -->（全部豁免）
    3. 行级：<!-- scan-ignore-line --> 或 # scan-ignore-line
    """
    lines = content.split("\n")
    mask = [False] * len(lines)
    in_block = False
    block_codes = None  # None = 豁免全部；set = 仅豁免指定 CODE

    for i, line in enumerate(lines):
        # 检查区块结束
        if in_block and BLOCK_WHITELIST_END.search(line):
            in_block = False
            mask[i] = True
            continue
        # 检查区块开始
        if not in_block:
            start_match = BLOCK_WHITELIST_START.search(line)
            if start_match:
                in_block = True
                mask[i] = True
                # 解析可选 CODE 列表
                full_match = start_match.group(0)
                if ":" in full_match:
                    codes_str = (
                        full_match.split(":", 1)[1].split("-->")[0].strip()
                    )
                    if codes_str:
                        parsed = {
                            c.strip() for c in codes_str.split(",") if c.strip()
                        }
                        # 文档文件忽略 CODE 限定（默认全部豁免）
                        if file_ext in {".md", ".txt"}:
                            block_codes = None
                        else:
                            block_codes = parsed
                continue
        # 行级豁免
        if LINE_WHITELIST.search(line):
            mask[i] = True
            continue
        # 区块内：标记 mask
        if in_block:
            mask[i] = True

    return {"mask": mask, "block_codes": block_codes}


def scan(skills_dir: Path):
    findings = []
    scanned = 0
    file_patterns = load_file_whitelist(skills_dir)
    whitelist_stats = {
        "files_skipped": 0,
        "lines_whitelisted": 0,
        "by_code": {},
    }

    for file_path in iter_files(skills_dir):
        # 文件级白名单：整个文件跳过
        if is_file_whitelisted(file_path, file_patterns):
            whitelist_stats["files_skipped"] += 1
            continue

        scanned += 1
        try:
            content = file_path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue

        # 行级 / 区块级白名单遮罩
        wl = build_line_whitelist_mask(content, file_path.suffix.lower())
        line_mask = wl["mask"]
        block_codes = wl["block_codes"]
        lines = content.split("\n")
        whitelist_stats["lines_whitelisted"] += sum(line_mask)

        for item in CHECK_ITEMS:
            pattern = item["regex"]
            code = item["code"]
            for line_idx, line in enumerate(lines):
                # 行级白名单遮罩
                if line_idx < len(line_mask) and line_mask[line_idx]:
                    # 区块级 CODE 限定：代码文件需检查 code 是否在限定内
                    if block_codes is not None and code not in block_codes:
                        continue
                    continue
                if pattern.search(line):
                    findings.append({
                        "file": str(file_path),
                        "line": line_idx + 1,
                        "severity": item["severity"],
                        "code": code,
                        "name": item["name"],
                        "message": item["message"],
                        "remediation": item["remediation"],
                    })
                    whitelist_stats["by_code"].setdefault(code, 0)
                    whitelist_stats["by_code"][code] += 1

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
        "whitelist_stats": whitelist_stats,
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

    json_path = output_dir / f"{safe_name}_{ts}.json"
    json_path.write_text(
        json.dumps({**result, "skills_dir": str(skills_dir), "generated_at": ts},
                   ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

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

    # 白名单透明报告
    ws = result.get("whitelist_stats", {})
    if ws.get("files_skipped", 0) > 0 or ws.get("lines_whitelisted", 0) > 0:
        lines += [
            "",
            "## 白名单豁免（V2.0 NEW）",
            "",
            "| 维度 | 数量 |",
            "|------|------|",
            f"| 文件级跳过 | {ws.get('files_skipped', 0)} |",
            f"| 行/区块级豁免 | {ws.get('lines_whitelisted', 0)} |",
            "",
            "> 注：白名单只豁免**真实误报**（文档规则 / 示例代码 / 教程引用），"
            "豁免**实际可执行风险** = 白名单失效。",
        ]

    if result["findings"]:
        lines += [
            "",
            "## 发现明细",
            "",
            "| 级别 | 行 | 类型 | 描述 | 文件 | 建议 |",
            "|------|---|------|------|------|------|",
        ]
        for f in result["findings"]:
            f_sev = sev_zh.get(f["severity"], f["severity"])
            f_file = str(f["file"]).replace("|", "\\|")
            f_msg = f["message"].replace("|", "\\|")
            f_name = f["name"].replace("|", "\\|")
            f_fix = f["remediation"].replace("|", "\\|")
            f_line = f.get("line", 0)
            lines.append(f"| {f_sev} | {f_line} | {f_name} | {f_msg} | `{f_file}` | {f_fix} |")
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

    # --quiet：单行 JSON，给 pre-commit hook 调用
    if "--quiet" in sys.argv:
        print(json.dumps(result, ensure_ascii=False))
    else:
        print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()