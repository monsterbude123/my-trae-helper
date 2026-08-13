"""
Rigor Scanner — 严谨用词扫描核心库

功能：
- 遍历目录，对 .md/.txt/.json/.yaml/.yml/.py/.js/.ts/.sh 文件作行级扫描
- 复用 scan_skills_dir.py 的三层白名单语义（文件级 / 区块级 / 行级）
- 豁免代码块（```...```）与内联代码（`...`）
- 输出 findings + 统计 + 判定（PASS / WARNING）

判定阈值（见 references/rigor-patterns.md §2）：
  - 总命中 ≥ 30 → WARNING
  - EMOTIONAL_TONE / PROHIBITED_PHRASE 总数 ≥ 10 → WARNING
  - 其它任一类别 ≥ 5 → WARNING
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Iterable, List, Set, Tuple

from lib.rigor_patterns import RIGOR_RULES, RigorRule


IGNORE_DIRS = {"node_modules", ".git", "dist", "build", "coverage",
               "__pycache__", ".venv", ".publish", ".gitnexus", ".husky",
               "auto_reports", "logs"}

TEXT_FILE_EXTS = {".md", ".txt", ".json", ".js", ".ts", ".py",
                  ".sh", ".ps1", ".yaml", ".yml", ".toml", ".cfg"}

# 复用 scan_skills_dir.py 的白名单语法
BLOCK_WL_START = re.compile(
    r"<!--\s*(?:scan-whitelist(?::[A-Z_,\s]+)?|scan-ignore)\s*-->"
)
BLOCK_WL_END = re.compile(
    r"<!--\s*/(?:scan-whitelist|scan-ignore)\s*-->"
)
LINE_WL = re.compile(
    r"(?:<!--\s*scan-ignore-line\s*-->|#\s*scan-ignore-line)"
)


@dataclass
class Finding:
    file: str
    line: int
    col: int
    code: str
    category: str
    severity: str
    snippet: str
    message: str
    suggestion: str


@dataclass
class ScanStats:
    files_scanned: int = 0
    files_skipped: int = 0
    lines_whitelisted: int = 0


@dataclass
class ScanResult:
    findings: List[Finding] = field(default_factory=list)
    stats: ScanStats = field(default_factory=ScanStats)
    risk_counts: Dict[str, int] = field(default_factory=dict)
    by_category: Dict[str, int] = field(default_factory=dict)
    verdict: str = "PASS"
    summary: str = ""


def iter_files(root: Path) -> Iterable[Path]:
    for path in root.rglob("*"):
        if path.is_dir():
            continue
        if any(part in IGNORE_DIRS for part in path.parts):
            continue
        if path.suffix.lower() in TEXT_FILE_EXTS:
            yield path


def _strip_code_blocks(lines: List[str]) -> List[bool]:
    """返回与 lines 等长的 mask，True 表示该行被代码块或行内代码豁免。

    豁免三种结构：
    1. 围栏代码块（```...```）
    2. 行内代码（`...`）
    3. Python 原始字符串字面量内的模式串（r"..." / r'...'）
       —— 用作"模式库"本身时不应被自身的扫描器命中
    """
    mask = [False] * len(lines)
    in_code_block = False
    raw_string_re = re.compile(r'r(?:"[^"\n]*"|\'[^\'\n]*\')')
    for i, line in enumerate(lines):
        # 围栏代码块切换
        if re.match(r"^\s*```", line):
            in_code_block = not in_code_block
            mask[i] = True
            continue
        if in_code_block:
            mask[i] = True
            continue
        # 行内代码 `...`
        if "`" in line:
            mask[i] = True
            continue
        # Python 原始字符串字面量（模式库自身豁免）
        if raw_string_re.search(line):
            mask[i] = True
            continue
    return mask


def _strip_whitelist(lines: List[str]) -> List[bool]:
    """三层白名单 mask；与 scan_skills_dir.py 保持兼容。"""
    mask = [False] * len(lines)
    in_block = False
    for i, line in enumerate(lines):
        if in_block and BLOCK_WL_END.search(line):
            in_block = False
            mask[i] = True
            continue
        if not in_block:
            if BLOCK_WL_START.search(line):
                in_block = True
                mask[i] = True
                continue
        if LINE_WL.search(line):
            mask[i] = True
            continue
        if in_block:
            mask[i] = True
    return mask


def _combined_mask(lines: List[str]) -> List[bool]:
    code_mask = _strip_code_blocks(lines)
    wl_mask = _strip_whitelist(lines)
    return [a or b for a, b in zip(code_mask, wl_mask)]


def _match_rule(rule: RigorRule, line: str) -> List[Tuple[int, str]]:
    """返回 (column, matched_text) 列表。"""
    hits = []
    for pattern in rule.patterns:
        for m in pattern.finditer(line):
            hits.append((m.start(), m.group(0)))
    return hits


def scan(skills_dir: Path) -> ScanResult:
    result = ScanResult()

    for file_path in iter_files(skills_dir):
        result.stats.files_scanned += 1
        try:
            content = file_path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            result.stats.files_skipped += 1
            continue

        lines = content.split("\n")
        mask = _combined_mask(lines)
        result.stats.lines_whitelisted += sum(mask)

        for line_idx, line in enumerate(lines):
            if line_idx >= len(mask) or mask[line_idx]:
                continue
            for rule in RIGOR_RULES:
                hits = _match_rule(rule, line)
                for col, _ in hits:
                    result.findings.append(Finding(
                        file=str(file_path),
                        line=line_idx + 1,
                        col=col,
                        code=rule.code,
                        category=rule.category,
                        severity=rule.severity,
                        snippet=line.strip()[:120],
                        message=f"{rule.description}：{rule.code}",
                        suggestion=rule.suggestion,
                    ))
                    result.by_category[rule.code] = (
                        result.by_category.get(rule.code, 0) + 1
                    )

    # 统计风险分布
    for f in result.findings:
        result.risk_counts[f.severity] = result.risk_counts.get(f.severity, 0) + 1

    # 判定阈值
    total = len(result.findings)
    em = result.by_category.get("EMOTIONAL_TONE", 0)
    pp = result.by_category.get("PROHIBITED_PHRASE", 0)
    high = result.by_category

    warning = False
    if total >= 30:
        warning = True
    if (em + pp) >= 10:
        warning = True
    for code, count in high.items():
        if code in {"EMOTIONAL_TONE", "PROHIBITED_PHRASE"}:
            continue
        if count >= 5:
            warning = True

    result.verdict = "WARNING" if warning else "PASS"
    result.summary = (
        f"扫描 {result.stats.files_scanned} 文件 | "
        f"总命中 {total} | "
        f"MEDIUM {result.risk_counts.get('medium', 0)} | "
        f"LOW {result.risk_counts.get('low', 0)} | "
        f"判定 {result.verdict}"
    )
    return result
