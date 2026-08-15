#!/usr/bin/env python3
"""
V11 ac-gate.py — Stage 4 AC 核销门禁(Guard/Gate 层,V11.6.0 取代评分制)

模型: 验收 = 逐 AC 核销,任一 FAIL/缺失 = BLOCK。无评分、无权重、无 N/A 降级。

Usage:
    python ac-gate.py --review-report <path> [--spec <spec.md>] [--test-plan <test-plan.md>] [--json]

Guards:
    G1  review-report 必含 "## AC 核销矩阵" 段
    G2  核销矩阵 ≥ 1 行有效 AC 行(6 列: AC-ID|类型|TC-ID|TC结果|UI证据|状态)
    G3  每行 TC 结果=PASS 且 状态=✅ 才算行 PASS;任一 ❌/FAIL → BLOCK
    G4  --spec 提供时: spec 每个 AC-ID 必须被核销(防漏核销)
    G5  --test-plan 提供时: 矩阵每个 TC-ID 必须存在于 test-plan(防编造测试)

Exit codes:
    0 = GATE PASS(全部 AC 核销 ✅)
    1 = GATE BLOCK(任一 AC ❌ / 漏核销 / 基准缺失 / 编造 TC)
"""
import sys
import argparse
import pathlib
import json
import re

MATRIX_HEADING = "AC 核销矩阵"
AC_ID_RE = re.compile(r"^AC-[A-Za-z0-9][A-Za-z0-9\-]*$")
STATUS_PASS = {"✅", "PASS"}
STATUS_FAIL = {"❌", "FAIL"}


def extract_matrix_rows(content: str) -> list:
    """解析 review-report 的 AC 核销矩阵段,返回行 dict 列表。"""
    rows = []
    in_matrix = False
    for line in content.splitlines():
        stripped = line.strip()
        if stripped.startswith("#") and MATRIX_HEADING in stripped:
            in_matrix = True
            continue
        if in_matrix:
            if stripped.startswith("#"):  # 下一个段落标题 → 结束
                break
            if not stripped.startswith("|") or set(stripped) <= {"|", "-", " ", ":"}:
                continue  # 跳过分隔行/空行
            cells = [c.strip() for c in stripped.strip("|").split("|")]
            if len(cells) < 6:
                continue
            ac_id, dim, tc_id, tc_result, ui_evidence, status = cells[:6]
            if ac_id.upper().startswith("AC-ID"):  # 表头
                continue
            if not AC_ID_RE.match(ac_id):
                continue
            rows.append({
                "ac": ac_id,
                "type": dim,
                "tc": tc_id,
                "tc_result": tc_result.upper(),
                "ui_evidence": ui_evidence,
                "status": status,
            })
    return rows


def extract_spec_ac_ids(spec_path: pathlib.Path) -> list:
    """从 spec.md 提取全部 AC-ID(标题或行首定义)。"""
    if not spec_path.exists():
        return []
    ac_ids = []
    for line in spec_path.read_text(encoding="utf-8").splitlines():
        m = re.match(r"^(?:#{1,6}\s*)?(AC-[A-Za-z0-9][A-Za-z0-9\-]*)\s*[:：]", line.strip())
        if m and m.group(1) not in ac_ids:
            ac_ids.append(m.group(1))
    return ac_ids


def run(review_path: pathlib.Path, spec_path, test_plan_path) -> dict:
    violations = []
    stats = {"rows": 0, "pass": 0, "fail": 0}

    if not review_path.exists():
        return {"verdict": "BLOCK", "violations": [f"G1: review-report 不存在: {review_path}"]}

    content = review_path.read_text(encoding="utf-8")

    # G1 — 矩阵段存在
    if MATRIX_HEADING not in content:
        violations.append("G1: review-report 缺少 '## AC 核销矩阵' 段(无基准 = 无法验收 = BLOCK)")

    rows = extract_matrix_rows(content)

    # G2 — 至少 1 行有效核销
    if not rows:
        violations.append("G2: AC 核销矩阵无有效行(每行 6 列: AC-ID|类型|TC-ID|TC结果|UI证据|状态)")
    stats["rows"] = len(rows)

    # G3 — 逐行核销判定
    for r in rows:
        ok = (r["tc_result"] in STATUS_PASS) and (r["status"] in STATUS_PASS)
        if ok:
            stats["pass"] += 1
        else:
            stats["fail"] += 1
            violations.append(
                f"G3: {r['ac']} 未核销通过(tc={r['tc']}, tc_result={r['tc_result']}, status={r['status']})"
            )

    # G4 — spec AC 全覆盖(防漏核销)
    spec_acs = []
    if spec_path:
        spec_acs = extract_spec_ac_ids(spec_path)
        if not spec_acs:
            violations.append("G4: spec.md 未提取到任何 AC-ID(基准文件异常)")
        covered = {r["ac"] for r in rows}
        for ac in spec_acs:
            if ac not in covered:
                violations.append(f"G4: {ac} 在 spec 中定义但未核销(漏核销)")

    # G5 — TC 防编造
    if test_plan_path:
        if not test_plan_path.exists():
            violations.append(f"G5: test-plan 不存在: {test_plan_path}")
        else:
            tp_text = test_plan_path.read_text(encoding="utf-8")
            for r in rows:
                tc = r["tc"].strip()
                if tc and tc != "—" and tc not in tp_text:
                    violations.append(f"G5: {r['ac']} 引用 TC '{tc}' 不存在于 test-plan(疑似编造)")

    return {
        "verdict": "PASS" if not violations else "BLOCK",
        "stats": stats,
        "spec_acs": spec_acs,
        "violations": violations,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="AC 核销门禁(V11.6.0+)")
    ap.add_argument("--review-report", required=True, type=pathlib.Path)
    ap.add_argument("--spec", type=pathlib.Path, default=None)
    ap.add_argument("--test-plan", type=pathlib.Path, default=None)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    result = run(args.review_report, args.spec, args.test_plan)

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        s = result["stats"]
        print(f"[AC-GATE] {result['verdict']} — 核销 {s['pass']}/{s['rows']} 行 AC 通过")
        for v in result["violations"]:
            print(f"  ❌ {v}")
        if not result["violations"]:
            print("  ✅ 全部 AC 核销通过,门禁放行")

    return 0 if result["verdict"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
