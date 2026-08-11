#!/usr/bin/env python3
"""reason-classifier.py — V10.10 Article XVI 抽象理由检测（腐烂点 19）

6 类抽象理由（禁词列表，二次再犯 = 🛑 REJECT）:
  1. 理解偏差 — 把 X 当成 Y / 我理解错了
  2. 流程裁剪 — 把 X 当成可省略 / 跳过了 X
  3. 心理障碍 — 进度焦虑 / 时间压力 / 急于完成
  4. 概念漂移 — 概念 X 变 Y / 重新定义 X
  5. 上下文丢失 — 上下文窗口击穿 / 记忆丢失
  6. 权衡取舍 — 两难权衡 / 不得不牺牲 X

正确替代模板（3 字段）:
  - "我错了"
  - "未执行的规则（Article 编号）"
  - "立即补救方案（命令 + 期望输出）"

用法:
  python scripts/reason-classifier.py --input <markdown_file>
  python scripts/reason-classifier.py --input <dir>          # 递归扫描 .md
  python scripts/reason-classifier.py --input "字符串内容"  # 直接传字符串
  python scripts/reason-classifier.py --input ... --json    # JSON 输出

退出码:
  0 = 无抽象理由
  1 = 检测到抽象理由（WARN，需用户裁决）
  2 = 参数错误
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

# 6 类抽象理由模式
REASON_PATTERNS: dict[str, list[str]] = {
    "理解偏差": [
        r"理解偏差",
        r"我理解错了",
        r"理解错了",
        r"理解错了你的意思",
        r"没理解到位",
        r"理解不到位",
        r"(?:误|错)读了\s*\w+",
        r"以为.{1,20}(?:是|为)",
    ],
    "流程裁剪": [
        r"流程裁剪",
        r"跳过.{0,5}流程",
        r"裁剪.{0,5}阶段",
        r"(?:把|将)\s*\w+\s*当成?\s*(?:可|可以)\s*(?:省略|跳过|延后)",
        r"(?:简化|省略).{0,8}流程",
        r"步骤裁剪",
    ],
    "心理障碍": [
        r"心理障碍",
        r"进度焦虑",
        r"时间压力",
        r"急于完成",
        r"焦虑导致",
        r"压力下",
    ],
    "概念漂移": [
        r"概念漂移",
        r"概念.{1,5}(?:变|变|改)成",
        r"重新定义",
        r"扩展定义",
        r"重新理解",
    ],
    "上下文丢失": [
        r"上下文.{0,5}(?:丢失|击穿|溢出|截断|不清)",
        r"记忆.{0,3}(?:丢失|不清|错误)",
        r"context.{0,5}(?:lost|overflow|truncated)",
    ],
    "权衡取舍": [
        r"权衡.{0,5}取舍",
        r"两难权衡",
        r"不得不.{0,5}牺牲",
        r"取舍",
        r"trade[-_]off",
    ],
}

# 正确替代模板检测（标记"诚实承认"以减低 WARN 严重度）
HONEST_PATTERNS = [
    r"我错了",
    r"未执行的规则",
    r"Article\s+[IVX]+",
    r"立即补救",
    r"违反.{0,8}Article",
]


def classify_text(text: str) -> list[dict]:
    """扫描文本，返回检测到的抽象理由列表。"""
    findings = []
    for category, patterns in REASON_PATTERNS.items():
        for pattern in patterns:
            for match in re.finditer(pattern, text, re.MULTILINE):
                # 取上下文行（±1 行）
                lines = text.split("\n")
                match_line = text[: match.start()].count("\n")
                context_start = max(0, match_line - 1)
                context_end = min(len(lines), match_line + 2)
                context = "\n".join(lines[context_start:context_end])

                # 检测同段是否有"诚实承认"
                has_honest = any(
                    re.search(pat, context, re.IGNORECASE)
                    for pat in HONEST_PATTERNS
                )

                findings.append(
                    {
                        "category": category,
                        "pattern": pattern,
                        "match": match.group(0),
                        "context": context,
                        "has_honest_pattern": has_honest,
                        "severity": "LOW" if has_honest else "WARN",
                    }
                )
    return findings


def scan_file(path: Path) -> dict:
    """扫描单个 .md 文件。"""
    text = path.read_text(encoding="utf-8")
    findings = classify_text(text)
    return {
        "file": str(path),
        "findings_count": len(findings),
        "findings": findings,
    }


def scan_directory(path: Path) -> list[dict]:
    """递归扫描目录所有 .md 文件。"""
    results = []
    for md_file in path.rglob("*.md"):
        # 跳过 V10.11 process 层（process-rot-analysis.md 等含禁词自身）
        if any(
            part in md_file.parts
            for part in [
                "process-rot-analysis.md",
                "skeptical-validation-protocol.md",  # 反例库含禁词
            ]
        ):
            continue
        results.append(scan_file(md_file))
    return results


def main() -> int:
    parser = argparse.ArgumentParser(
        description="V10.10 Article XVI 抽象理由检测（腐烂点 19）"
    )
    parser.add_argument(
        "--input",
        type=str,
        required=True,
        help="输入: 文件路径 / 目录路径 / 直接字符串",
    )
    parser.add_argument("--json", action="store_true", help="JSON 输出")
    args = parser.parse_args()

    input_path = Path(args.input)
    if input_path.is_file():
        results = [scan_file(input_path)]
    elif input_path.is_dir():
        results = scan_directory(input_path)
    else:
        # 当作字符串直接扫描
        findings = classify_text(args.input)
        results = [
            {
                "file": "<inline-string>",
                "findings_count": len(findings),
                "findings": findings,
            }
        ]

    # 汇总
    total_findings = sum(r["findings_count"] for r in results)
    warn_findings = sum(
        f["severity"] == "WARN"
        for r in results
        for f in r["findings"]
    )

    if args.json:
        output = {
            "total_files": len(results),
            "total_findings": total_findings,
            "warn_findings": warn_findings,
            "results": results,
        }
        print(json.dumps(output, ensure_ascii=False, indent=2))
    else:
        print(f"📋 reason-classifier 扫描结果: {len(results)} 文件")
        print(f"   总发现: {total_findings} 个抽象理由")
        print(f"   ⚠️  WARN 级: {warn_findings} 个")
        if total_findings > 0:
            print()
            for r in results:
                if r["findings_count"] > 0:
                    print(f"📄 {r['file']} — {r['findings_count']} 处")
                    for f in r["findings"]:
                        severity_icon = "⚠️ " if f["severity"] == "WARN" else "ℹ️ "
                        print(
                            f"   {severity_icon}[{f['category']}] "
                            f"匹配: {f['match']!r} "
                            f"(severity={f['severity']})"
                        )

    # 退出码
    if warn_findings > 0:
        # WARN 不算硬失败，但提示用户裁决
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())