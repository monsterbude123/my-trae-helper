"""
Rigor Reporter — Markdown / JSON 报告输出

输出位置：audit_reports/ 目录（与 auto_reports 平级）
"""

from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path

from rigor_scanner import Finding, ScanResult


SEV_ZH = {"medium": "�� MEDIUM", "low": "�� LOW", "high": "�� HIGH"}


def _safe_name(name: str) -> str:
    return re.sub(r'[<>:"/\\|?*]+', "_", name) or "rigor-scan"


def write_reports(result: ScanResult, skills_dir: Path, output_dir: Path):
    output_dir.mkdir(parents=True, exist_ok=True)
    safe_name = _safe_name(skills_dir.name)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")

    json_path = output_dir / f"{safe_name}_rigor_{ts}.json"
    payload = {
        "skills_dir": str(skills_dir),
        "generated_at": ts,
        "verdict": result.verdict,
        "summary": result.summary,
        "stats": {
            "files_scanned": result.stats.files_scanned,
            "files_skipped": result.stats.files_skipped,
            "lines_whitelisted": result.stats.lines_whitelisted,
        },
        "risk_counts": result.risk_counts,
        "by_category": result.by_category,
        "findings": [
            {
                "file": f.file,
                "line": f.line,
                "col": f.col,
                "code": f.code,
                "category": f.category,
                "severity": f.severity,
                "snippet": f.snippet,
                "message": f.message,
                "suggestion": f.suggestion,
            }
            for f in result.findings
        ],
    }
    json_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    md_path = output_dir / f"{safe_name}_rigor_{ts}.md"
    lines = [
        f"# 严谨用词扫描报告: {skills_dir.name}",
        "",
        f"- 扫描目录: `{skills_dir}`",
        f"- 扫描时间: `{ts}`",
        f"- 扫描文件: `{result.stats.files_scanned}`",
        f"- 判定: `{result.verdict}`",
        "",
        "## 类别统计",
        "",
        "| 类别 | 命中 |",
        "|------|------|",
    ]
    for code, count in sorted(result.by_category.items(), key=lambda x: -x[1]):
        lines.append(f"| {code} | {count} |")

    if result.findings:
        lines += [
            "",
            "## 发现明细",
            "",
            "| 严重度 | 类别 | 行 | 列 | 文件 | 摘要 | 建议 |",
            "|--------|------|---|---|------|------|------|",
        ]
        for f in result.findings[:200]:
            sev = SEV_ZH.get(f.severity, f.severity)
            file_disp = f.file.replace("|", "\\|")
            snippet = f.snippet.replace("|", "\\|")[:80]
            sug = f.suggestion.replace("|", "\\|")
            lines.append(
                f"| {sev} | {f.code} | {f.line} | {f.col} | "
                f"`{file_disp}` | {snippet} | {sug} |"
            )
        if len(result.findings) > 200:
            lines.append("")
            lines.append(f"> 共 {len(result.findings)} 条，仅展示前 200 条")
    else:
        lines += ["", "未发现严谨性问题。"]

    md_path.write_text("\n".join(lines), encoding="utf-8")
    return json_path, md_path
