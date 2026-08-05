#!/usr/bin/env python3
"""self-diagnose.py — V10.4 检测器自身腐烂点诊断

实战教训: AIGCMediaDesktop 实测时发现 proactive-scan 的子检测器有 2 个自身腐烂点:
  - dist-hash-check.py regex 太贪婪(把 icon kebab-name 误当 chunk)
  - visual-content-check.py L5 阈值硬编码 5(深色主题误报)
本脚本作为 V10 自我反思机制,在 release 前跑一遍。

用法:
  python scripts/self-diagnose.py [--json]
  python scripts/self-diagnose.py --only dist-hash-regex-guard [--json]

3 项检查:
  1. dist-hash-regex-guard — CHUNK_PATTERN 须有 CamelCase 守卫或 icon 前缀黑名单
  2. visual-l5-dark-aware  — L5 阈值须 dark-aware(mean 亮度分支或 dark 注释)
  3. generic-heuristics    — 扫所有 detector_*.py / *-check.py
                              启发式: 缺 \\b 锚定 regex / 硬编码单阈值 / PASS 缺 evidence
  4. proactive-v105-coverage (V10.5) — 验 proactive-scan.py 含 rot #15-17 三个新 check 函数

退出码: 0=pass(无 FAIL), 1=fail, 2=script error
V10.4.1 引入 (2026-07-31) | V10.5.0 新增 check 4 (2026-07-31)
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

try:
    from common import get_project_root
except ImportError:  # pragma: no cover
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from common import get_project_root


@dataclass
class CheckResult:
    name: str
    status: str               # pass | warn | fail | skip
    severity: str             # PASS | WARN | FAIL
    evidence: str = ""
    line: int = 0
    suggestion: str = ""

    def to_dict(self):
        return self.__dict__


# V10.4.1 已知 icon-style kebab 前缀 (dist-hash-check 黑名单候选)
ICON_PREFIXES = (
    "bar-chart-", "list-checks-", "external-link-", "chevron-right-",
    "chevron-left-", "chevron-down-", "chevron-up-", "pen-line-",
    "pencil-", "folder-open-", "folder-", "wand-sparkles-", "circle-",
    "circle-x-", "rotate-ccw-", "maximize-2-", "image-", "video-",
    "user-", "zap-", "ban-", "star-", "filter-", "settings-",
    "dialog-", "input-", "key-", "loader-", "owner-", "palette-",
    "package-", "tags-", "dedupe-",
)

SCRIPTS_DIR = Path(__file__).parent
DIST_HASH_PATH = SCRIPTS_DIR / "dist-hash-check.py"
VISUAL_PATH = SCRIPTS_DIR / "visual-content-check.py"


# === 检查 1: dist-hash-check regex 守卫 ===

def check_dist_hash_regex_guard() -> CheckResult:
    if not DIST_HASH_PATH.is_file():
        return CheckResult("dist-hash-regex-guard", "skip", "PASS", f"文件不存在: {DIST_HASH_PATH}", 0, "")
    text = DIST_HASH_PATH.read_text(encoding="utf-8")
    m = re.search(r"CHUNK_PATTERN\s*=\s*re\.compile\(\s*r?(['\"])(.+?)\1\s*\)", text, re.DOTALL)
    if not m:
        return CheckResult("dist-hash-regex-guard", "fail", "FAIL", "未找到 CHUNK_PATTERN 定义", 0, "在 dist-hash-check.py 顶部定义 CHUNK_PATTERN")
    pattern = m.group(2)
    line_no = text[: m.start()].count("\n") + 1
    # 守卫 A: 首字母大写
    guard_a = bool(re.search(r"\[A-Z\]\[A-Za-z0-9_", pattern))
    # 守卫 B: hardcode icon 前缀黑名单
    guard_b = any(p in text for p in ICON_PREFIXES)
    if guard_a or guard_b:
        ev = f"守卫 A(CamelCase 首字母大写)={'✅' if guard_a else '❌'}; 守卫 B(icon 前缀黑名单)={'✅' if guard_b else '❌'}; pattern={pattern[:60]}..."
        return CheckResult("dist-hash-regex-guard", "pass", "PASS", ev, line_no, "")
    return CheckResult(
        "dist-hash-regex-guard", "fail", "FAIL",
        f"CHUNK_PATTERN 缺守卫(regex 贪婪匹配 icon kebab-name); pattern={pattern[:60]}...",
        line_no, "加守卫: 1) `[A-Z][A-Za-z0-9_]*` 首字母大写; 或 2) hardcode ICON_PREFIXES 黑名单",
    )


# === 检查 2: visual-content-check L5 dark-aware ===

def check_visual_l5_dark_aware() -> CheckResult:
    if not VISUAL_PATH.is_file():
        return CheckResult("visual-l5-dark-aware", "skip", "PASS", f"文件不存在: {VISUAL_PATH}", 0, "")
    text = VISUAL_PATH.read_text(encoding="utf-8")
    has_branch = bool(re.search(r"(brightness\s*=|mean_brightness\s*=|avg_brightness\s*=)", text))
    has_dark = bool(re.search(r"(dark\s*theme|dark-theme|深色主题|is_dark)", text, re.IGNORECASE))
    if has_branch or has_dark:
        line_no = next((text[: m.start()].count("\n") + 1 for m in re.finditer(r"(brightness|is_dark|dark)", text, re.IGNORECASE)), 0)
        ev = f"亮度判断分支={'✅' if has_branch else '❌'}; dark 主题注释/条件={'✅' if has_dark else '❌'}"
        return CheckResult("visual-l5-dark-aware", "pass", "PASS", ev, line_no, "")
    return CheckResult(
        "visual-l5-dark-aware", "fail", "FAIL",
        "L5 阈值硬编码单值(无 dark theme 兼容,深色 UI 整页相近会误报)", 0,
        "加 `brightness = sum(quads)/len(quads)` 判断,深色用 MIN_QUADRANT_DIFF_DARK(如 2.5)",
    )


# === 检查 3: 通用启发式 ===

def _is_evidence_missing(text: str) -> bool:
    """找返回 CheckResult(... "PASS" ...) 但缺 evidence= 的调用"""
    matches = list(re.finditer(r'return\s+CheckResult\([^)]*"PASS"', text))
    if not matches:
        return False
    for m in matches:
        before = text[max(0, m.start() - 300): m.start()]
        if "evidence=" in before or "evidence:" in before:
            return False
    return len(matches) > 0


def _find_hardcoded_thresholds(text: str) -> list[tuple[int, str]]:
    """找 `if xxx <op> 数字:` 形式(硬编码单阈值)"""
    out = []
    for i, line in enumerate(text.splitlines(), 1):
        s = line.strip()
        if s.startswith("#") or re.match(r"^if\s+.+\s+([<>=!]=?)\s+\d+\s*:", s) is None:
            continue
        out.append((i, s))
    return out


def _find_unanchored_regex(text: str) -> list[tuple[int, str]]:
    """找 `r"..."` 形如 `name-hash.ext` 但无 \b/^/$ 锚定"""
    out = []
    for i, line in enumerate(text.splitlines(), 1):
        s = line.strip()
        if s.startswith("#"):
            continue
        m = re.search(r'r["\']([^"\']+)["\']', s)
        if not m or not re.search(r"[A-Za-z0-9_\[\]]", m.group(1)):
            continue
        p = m.group(1)
        if r"\b" in p or p.startswith("^") or p.endswith("$"):
            continue
        if "-" in p and re.search(r"[A-Za-z0-9_]+-[A-Za-z0-9_]+", p):
            out.append((i, s))
    return out


def check_generic_heuristics() -> CheckResult:
    """扫所有 detector_*.py / *-check.py / *-detector.py

    启发式 1: 缺 \b 锚定 regex
    启发式 2: 硬编码单阈值
    启发式 3: PASS 缺 evidence
    """
    patterns = ("detector_*.py", "*-check.py", "*-detector.py")
    scripts = sorted({p for pat in patterns for p in SCRIPTS_DIR.glob(pat)})
    if not scripts:
        return CheckResult("generic-heuristics", "skip", "PASS", f"未找到 detector/check 脚本({SCRIPTS_DIR})", 0, "")
    findings: list[str] = []
    for sp in scripts:
        try:
            text = sp.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        rel = sp.name
        for ln, sn in _find_unanchored_regex(text):
            findings.append(f"{rel}:{ln} 缺锚定 regex → {sn[:80]}")
        for ln, sn in _find_hardcoded_thresholds(text):
            findings.append(f"{rel}:{ln} 硬编码阈值 → {sn[:80]}")
        if _is_evidence_missing(text):
            findings.append(f"{rel} 多个 PASS 返回缺 evidence 字段")
    if not findings:
        return CheckResult("generic-heuristics", "pass", "PASS", f"扫描 {len(scripts)} 个 detector 脚本,无腐烂点", 0, "")
    if len(findings) <= 2:
        return CheckResult(
            "generic-heuristics", "warn", "WARN",
            f"扫描 {len(scripts)} 个脚本,发现 {len(findings)} 处疑似腐烂点: {'; '.join(findings[:3])}",
            0, "建议: 1) regex 加 \\b 锚定; 2) 阈值改常量; 3) PASS 路径补 evidence",
        )
    return CheckResult(
        "generic-heuristics", "fail", "FAIL",
        f"扫描 {len(scripts)} 个脚本,发现 {len(findings)} 处腐烂点: {'; '.join(findings[:3])}",
        0, "建议: 1) regex 加 \\b 锚定; 2) 阈值改常量; 3) PASS 路径补 evidence",
    )


# === 检查 4: proactive-scan 新 check 的元腐烂（V10.5 腐烂点 15-17 修复） ===

PROACTIVE_PATH = SCRIPTS_DIR / "proactive-scan.py"

# 腐烂点 15-17 新 check 必含的函数名 / 阈值常量
REQUIRED_V105_FUNCTIONS = (
    "run_self_aggrandizing_doc",
    "run_state_card_staleness",
    "run_stub_pileup",
)
# 腐烂点 15 必含 INV_RE 锚定 + 阈值 0.3
REQUIRED_V105_ANCHORS = (
    (r"INV-[A-Z0-9-]+", "INV- 锚定 regex"),
    (r"brag_rate\s*>\s*0\.[0-9]+", "自我吹嘘阈值 0.3"),
    (r"stub_rate\s*>\s*0\.[0-9]+", "骨架堆积阈值 0.4/0.6"),
    (r"age_hours\s*>\s*7[02]", "state-card 时间阈值 24/72"),
)


def check_proactive_v105_coverage() -> CheckResult:
    """V10.5: 检查 proactive-scan.py 是否含 rot #15-17 三个新 check 函数

    防止 rot-reinforcer 升级时漏写 check 函数,或者把 INV_RE/阈值删了导致静默失效。
    """
    if not PROACTIVE_PATH.is_file():
        return CheckResult(
            "proactive-v105-coverage", "skip", "PASS",
            f"proactive-scan.py 不存在: {PROACTIVE_PATH}", 0, "",
        )
    text = PROACTIVE_PATH.read_text(encoding="utf-8")
    missing: list[str] = []
    for fn in REQUIRED_V105_FUNCTIONS:
        if f"def {fn}" not in text:
            missing.append(f"缺函数 {fn}()")
    for pattern, desc in REQUIRED_V105_ANCHORS:
        if not re.search(pattern, text):
            missing.append(f"缺 {desc}")
    if not missing:
        return CheckResult(
            "proactive-v105-coverage", "pass", "PASS",
            f"proactive-scan.py 含 rot #15-17 三个新 check (3 函数 + 4 锚定)",
            0, "",
        )
    return CheckResult(
        "proactive-v105-coverage", "fail", "FAIL",
        f"proactive-scan.py V10.5 升级不完整: {'; '.join(missing[:4])}",
        0, "V10.5 rot-reinforcer 升级必须含 3 个新 check 函数 + INV_RE 锚定 + 阈值常量",
    )


# === 注册所有 check ===

CHECKS = {
    "dist-hash-regex-guard": check_dist_hash_regex_guard,
    "visual-l5-dark-aware": check_visual_l5_dark_aware,
    "generic-heuristics": check_generic_heuristics,
    "proactive-v105-coverage": check_proactive_v105_coverage,
}


def run_all(only: Optional[str] = None) -> list[CheckResult]:
    results: list[CheckResult] = []
    for name, fn in CHECKS.items():
        if only and only != name:
            continue
        try:
            r = fn()
        except Exception as e:
            r = CheckResult(name, "fail", "FAIL", f"check 内部异常: {e}")
        results.append(r)
    return results


def main() -> int:
    parser = argparse.ArgumentParser(description="V10.5 检测器自身腐烂点诊断 (4 项 check)")
    parser.add_argument("--only", type=str, choices=list(CHECKS.keys()), help="仅运行指定 check")
    parser.add_argument("--json", action="store_true", help="JSON 输出")
    args = parser.parse_args()

    results = run_all(args.only)
    fail_count = sum(1 for r in results if r.severity == "FAIL")
    if args.json:
        payload = {
            "status": "fail" if fail_count > 0 else "pass",
            "total": len(results), "fail_count": fail_count,
            "results": [r.to_dict() for r in results],
        }
        print(json.dumps(payload, ensure_ascii=False, separators=(",", ":")))
    else:
        print(f"# V10.4 Detector Self-Diagnose\n\n- checks: {len(results)}, fail: {fail_count}\n")
        for i, r in enumerate(results, 1):
            icon = {"pass": "✅", "warn": "⚠️", "fail": "🛑", "skip": "⏭️"}.get(r.status, "?")
            line_info = f":L{r.line}" if r.line else ""
            print(f"| {i} | {r.name}{line_info} | {icon} {r.severity} | {r.evidence[:100]} |")
            if r.suggestion and r.status != "pass":
                print(f"   💡 {r.suggestion}")
        print()
        if fail_count:
            print(f"🛑 {fail_count} 项 FAIL — 检测器自身有腐烂点,要求 implementer 修复")
        else:
            warn_n = sum(1 for r in results if r.severity == "WARN")
            skip_n = sum(1 for r in results if r.severity == "PASS" and r.status == "skip")
            print(f"✅ 检测器自身无腐烂点(FAIL: 0, WARN: {warn_n}, SKIP: {skip_n})")
    return 1 if fail_count > 0 else 0


if __name__ == "__main__":
    raise SystemExit(main())
