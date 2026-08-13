#!/usr/bin/env python3
"""
scan_rigor.py — 严谨用词扫描 CLI

用法:
    python scan_rigor.py <skills_dir> [output_dir]
    python scan_rigor.py --self-test
    python scan_rigor.py --emit-empty

退出码:
    0 = PASS
    1 = WARNING（命中过多；默认不阻断）
    2 = 调用错误
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# 允许 `python scan_rigor.py` 直接调用（路径注入 scripts 根）
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from rigor_scanner import scan  # noqa: E402
from rigor_reporter import write_reports  # noqa: E402


def _print(result, json_path, md_path, quiet=False):
    payload = {
        "verdict": result.verdict,
        "summary": result.summary,
        "stats": {
            "files_scanned": result.stats.files_scanned,
            "files_skipped": result.stats.files_skipped,
            "lines_whitelisted": result.stats.lines_whitelisted,
        },
        "risk_counts": result.risk_counts,
        "by_category": result.by_category,
        "report_files": {"json": str(json_path), "md": str(md_path)},
    }
    if quiet:
        print(json.dumps(payload, ensure_ascii=False))
    else:
        print(json.dumps(payload, ensure_ascii=False, indent=2))


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="scan_rigor",
        description="扫描 Skill 目录是否存在情绪化 / 死角 / 模糊用词",
    )
    parser.add_argument("skills_dir", nargs="?", help="Skill 目录路径")
    parser.add_argument("output_dir", nargs="?", help="报告输出目录")
    parser.add_argument(
        "--self-test", action="store_true",
        help="用内置 fixture 验证模式库与判定阈值",
    )
    parser.add_argument(
        "--emit-empty", action="store_true",
        help="无 skills_dir 时不报错，仅打印空结果（供 pre-commit 探测）",
    )
    parser.add_argument(
        "--quiet", action="store_true",
        help="单行 JSON 输出（供 shell pipe 解析）",
    )
    args = parser.parse_args(argv)

    if args.self_test:
        return _self_test()

    if not args.skills_dir:
        if args.emit_empty:
            print(json.dumps({
                "verdict": "PASS", "summary": "no input", "findings": [],
            }, ensure_ascii=False))
            return 0
        parser.error("缺少 skills_dir 参数")

    skills_dir = Path(args.skills_dir).resolve()
    if not skills_dir.exists() or not skills_dir.is_dir():
        print(json.dumps({"error": f"Invalid directory: {skills_dir}"},
                         ensure_ascii=False))
        return 2

    output_dir = (
        Path(args.output_dir).resolve()
        if args.output_dir
        else (Path.cwd() / "audit_reports")
    )

    result = scan(skills_dir)
    json_path, md_path = write_reports(result, skills_dir, output_dir)
    _print(result, json_path, md_path, quiet=args.quiet)

    return 0 if result.verdict == "PASS" else 1


def _self_test() -> int:
    """用临时目录构造含各类模式的样本，验证扫描器。"""
    import tempfile
    import textwrap

    samples = {
        "emotional.md": "本工具非常好用，极致完美。",
        "absolute.md": "100% 安全，零风险，绝对可靠。",
        "vague.md": "大量文件被处理，很多脚本被扫描。",
        "inclusive.md": "支持 Python、JS、TS 等等。",
        "undefined.md": "在特殊情况下，需要特殊处理。",
        "dead_angle.md": "一般情况下，直接执行即可。",
        "opinion.md": "我觉得这是一个好工具。",
        "prohibited.md": "显而易见，这是最佳实践。",
        "over_promise.md": "一键搞定，轻松实现。",
        "unmeasured.md": "显著提升效率，改善体验。",
        "clean.md": "本工具覆盖 8 类风险，命中率 0 时输出 PASS。",
    }
    with tempfile.TemporaryDirectory() as tmp:
        tmp_dir = Path(tmp)
        for name, content in samples.items():
            (tmp_dir / name).write_text(content, encoding="utf-8")
        result = scan(tmp_dir)
        # 至少应命中 8 类
        detected = set(result.by_category.keys())
        expected = {
            "EMOTIONAL_TONE", "ABSOLUTE_CLAIM", "VAGUE_QUANTIFIER",
            "INCLUSIVE_HEDGE", "UNDEFINED_TERM", "DEAD_ANGLE_MARKER",
            "PERSONAL_OPINION", "PROHIBITED_PHRASE", "OVER_PROMISE",
            "UNMEASURED_BENEFIT",
        }
        missing = expected - detected
        if missing:
            print(json.dumps({
                "self_test": "FAIL",
                "missing": sorted(missing),
                "detected": sorted(detected),
            }, ensure_ascii=False, indent=2))
            return 1
        print(json.dumps({
            "self_test": "PASS",
            "detected_classes": sorted(detected),
            "total_findings": len(result.findings),
            "verdict": result.verdict,
        }, ensure_ascii=False, indent=2))
        return 0


if __name__ == "__main__":
    sys.exit(main())
