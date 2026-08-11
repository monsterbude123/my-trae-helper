#!/usr/bin/env python3
"""
V11 acceptance-audit.py — Stage 4 4 维评分 + 通过依据 3 类分层

Usage:
    python acceptance-audit.py --review-report <path>

Exit codes:
    0 = PASS（总分 ≥ 4.0）
    1 = FAIL（任一维度 0 分 或 总分 < 4.0）
"""
import sys
import argparse
import pathlib
import json
import re

# 4 维度
DIMENSIONS = ["code", "api", "uiux", "marginal"]
WEIGHTS = {"code": 0.25, "api": 0.30, "uiux": 0.25, "marginal": 0.20}

# 通过依据 3 类
EVIDENCE_LAYERS = ["backend_compile", "ui_render", "user_view"]


def parse_review_report(path: pathlib.Path) -> dict:
    """解析 review-report.md
    期望格式：
    - 4 维评分表: | 代码 | 25% | [0-5] | [evidence] |
    - 必填字段: current_total_score
    """
    if not path.exists():
        return {"error": f"报告文件不存在: {path}"}

    content = path.read_text(encoding="utf-8")
    result = {"scores": {}, "evidence": {}, "total": None}

    # 解析 4 维评分表
    for dim in DIMENSIONS:
        pattern = rf"\|\s*{dim}\s*\|\s*\d+%\s*\|\s*([0-9](?:\.[0-9])?)\s*\|\s*([^\|]+)\|"
        m = re.search(pattern, content, re.IGNORECASE)
        if m:
            try:
                score = float(m.group(1))
                evidence = m.group(2).strip()
                result["scores"][dim] = score
                result["evidence"][dim] = evidence
            except ValueError:
                result["scores"][dim] = None

    # 解析总分
    total_pattern = r"总分[::]\s*([0-9](?:\.[0-9])?)"
    m = re.search(total_pattern, content)
    if m:
        try:
            result["total"] = float(m.group(1))
        except ValueError:
            pass

    return result


def calculate_score(parsed: dict) -> dict:
    """计算加权总分"""
    if "error" in parsed:
        return parsed

    errors = []

    if not parsed["scores"]:
        return {"error": "缺失 4 维评分"}

    for dim in DIMENSIONS:
        if dim not in parsed["scores"]:
            errors.append(f"缺失维度: {dim}")
        elif parsed["scores"][dim] == 0:
            errors.append(f"维度 {dim} = 0（REJECT 自动）")

    if errors:
        return {"error": "; ".join(errors)}

    # 加权总分
    total = sum(parsed["scores"][dim] * WEIGHTS[dim] for dim in DIMENSIONS) / sum(WEIGHTS.values()) * 5.0 / 5.0
    # 实际公式: total = Σ(score × weight) / Σ(weight) × 5.0（保留满分 5.0）
    total = sum(parsed["scores"][dim] * WEIGHTS[dim] for dim in DIMENSIONS) * (5.0 / sum(WEIGHTS.values()))
    # 简化版: 各维度独立评分（0-5），加权平均
    total = sum(parsed["scores"][dim] * WEIGHTS[dim] for dim in DIMENSIONS) / sum(WEIGHTS.values())

    parsed["calculated_total"] = round(total, 2)

    if total < 4.0:
        errors.append(f"总分 {total} < 4.0（PASS 门槛）")
    if any(parsed["scores"][dim] == 0 for dim in DIMENSIONS):
        errors.append("任一维度 0 分 = REJECT")

    parsed["errors"] = errors
    parsed["is_pass"] = len(errors) == 0

    return parsed


def main():
    parser = argparse.ArgumentParser(description="V11 Stage 4 acceptance-audit")
    parser.add_argument("--review-report", required=True, help="review-report.md 路径")
    parser.add_argument("--json", action="store_true", help="JSON 输出")
    args = parser.parse_args()

    path = pathlib.Path(args.review_report)
    parsed = parse_review_report(path)
    result = calculate_score(parsed)

    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        if "error" in result:
            print(f"❌ FAIL: {result['error']}")
            return 1

        if result["is_pass"]:
            print(f"✅ PASS — 总分 {result['calculated_total']}")
            for dim in DIMENSIONS:
                print(f"   {dim}: {result['scores'][dim]} ({WEIGHTS[dim]*100:.0f}%)")
        else:
            print(f"❌ FAIL — 总分 {result['calculated_total']}（PASS 门槛 4.0）")
            for e in result["errors"]:
                print(f"   - {e}")
            return 1

    return 0 if result.get("is_pass") else 1


if __name__ == "__main__":
    sys.exit(main())