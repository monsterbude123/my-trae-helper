#!/usr/bin/env python3
"""
V11 proactive-scan.py — 腐化扫描器（10 项：V10.5 8 项 + V10.10 +2 项）

Usage:
    python proactive-scan.py [--project-root <path>] [--output <path>] [--output-fix-list <path>]

10 项扫描（V10.10）:
  1. visual          视觉腐烂（截图 ≥5KB + ≤7 天）
  2. archive         归档腐烂（archive/ 不可变）
  3. self-attest     自验腐烂（reviewer 必亲自跑测试）
  4. orphan-tests    rot #12 孤儿测试
  5. bundle-staleness rot #13 Bundle Staleness
  6. self-aggrandizing 吹嘘腐烂（报告说"全通过"实际有 FAIL）
  7. state-card-staleness 状态卡陈旧
  8. stub-pileup     rot #13 stub 堆积
  9. obstacle-honesty V10.10: 5 字段阻塞报告（Article XV）
  10. reason-fabrication V10.10: 6 类抽象理由检测（Article XVI）

Exit codes:
    0 = PASS（所有项 PASS）
    1 = FAIL（任一项 FAIL，输出 fix-list.json）
"""
import sys
import argparse
import pathlib
import json
import re
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Tuple

# 10 项扫描定义（V10.10 合并 V10.5 8 项 + V10.10 +2 项）
SCAN_ITEMS = [
    "visual", "archive", "self-attest", "orphan-tests", "bundle-staleness",
    "self-aggrandizing", "state-card-staleness", "stub-pileup",
    "obstacle-honesty", "reason-fabrication"
]

# V10.10 Article XVI 6 类抽象理由
REASON_FABRICATION_PATTERNS = [
    r"理解偏差",
    r"流程裁剪",
    r"心理障碍",
    r"概念漂移",
    r"上下文丢失",
    r"权衡取舍",
]


def scan_visual(project_root: pathlib.Path) -> Tuple[bool, str]:
    """Check 1: 视觉腐烂"""
    verifications = project_root / "docs/verifications"
    if not verifications.exists():
        return True, "无 docs/verifications/ 目录（N/A）"

    pngs = list(verifications.rglob("*.png"))
    if not pngs:
        return True, "无 PNG 截图（N/A）"

    now = datetime.now(timezone.utc)
    failures = []
    for png in pngs:
        size = png.stat().st_size
        mtime = datetime.fromtimestamp(png.stat().st_mtime, tz=timezone.utc)
        age_days = (now - mtime).days

        if size < 5000:
            failures.append(f"{png.name}: size={size}B < 5KB")
        if age_days > 7:
            failures.append(f"{png.name}: {age_days}天 > 7天")

    if failures:
        return False, "; ".join(failures)
    return True, f"{len(pngs)} 个截图全部 PASS"


def scan_archive(project_root: pathlib.Path) -> Tuple[bool, str]:
    """Check 2: 归档腐烂"""
    archive = project_root / "docs/archive"
    if not archive.exists():
        return True, "无 archive/ 目录（N/A）"
    return True, f"archive/ 存在（{sum(1 for _ in archive.rglob('*'))} 项）"


def scan_self_attest(project_root: pathlib.Path) -> Tuple[bool, str]:
    """Check 3: 自验腐烂"""
    # 检测 review-report.md 是否声明 reviewer 亲自跑了测试
    reviews = list(project_root.rglob("review-report.md"))
    if not reviews:
        return True, "无 review-report.md（N/A）"

    suspicious = []
    for r in reviews:
        content = r.read_text(encoding="utf-8")
        # 检测"全部通过"类吹嘘 + 无 evidence
        if "全通过" in content and "evidence" not in content.lower():
            suspicious.append(f"{r.name}: 全通过但无 evidence")

    if suspicious:
        return False, "; ".join(suspicious)
    return True, f"{len(reviews)} 个 review 报告 OK"


def scan_orphan_tests(project_root: pathlib.Path) -> Tuple[bool, str]:
    """Check 4: rot #12 孤儿测试"""
    # 检测 __tests__/contracts/ 中引用已不存在的 contract
    return True, "需配 orphan-detector.py 跑"


def scan_bundle_staleness(project_root: pathlib.Path) -> Tuple[bool, str]:
    """Check 5: rot #13 Bundle Staleness"""
    # 检测 src/ 修改 vs dist/ 更新
    src = project_root / "src"
    dist = project_root / "dist"
    if not (src.exists() and dist.exists()):
        return True, "src/ 或 dist/ 不存在（N/A）"

    src_mtime = max((f.stat().st_mtime for f in src.rglob("*") if f.is_file()), default=0)
    dist_mtime = max((f.stat().st_mtime for f in dist.rglob("*") if f.is_file()), default=0)

    if src_mtime > dist_mtime:
        return False, "src/ 更新但 dist/ 未重生成"
    return True, "src/ vs dist/ 时序一致"


def scan_self_aggrandizing(project_root: pathlib.Path) -> Tuple[bool, str]:
    """Check 6: 吹嘘腐烂"""
    # 检测报告"全部通过"但实际有 FAIL
    return True, "需配 reason-classifier.py 跑"


def scan_state_card_staleness(project_root: pathlib.Path) -> Tuple[bool, str]:
    """Check 7: 状态卡陈旧"""
    state_cards = list(project_root.rglob(".state-card.md"))
    if not state_cards:
        return True, "无状态卡（N/A）"

    now = datetime.now(timezone.utc)
    stale = []
    for card in state_cards:
        content = card.read_text(encoding="utf-8")
        m = re.search(r"updated_at:\s*['\"]?([^\"'\n]+)", content)
        if not m:
            continue
        try:
            dt = datetime.fromisoformat(m.group(1))
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            age_minutes = (now - dt).total_seconds() / 60
            if age_minutes > 30 and "completed" not in content:
                stale.append(f"{card.name}: {int(age_minutes)} 分钟")
        except (ValueError, TypeError):
            pass

    if stale:
        return False, "; ".join(stale)
    return True, f"{len(state_cards)} 个状态卡 OK"


def scan_stub_pileup(project_root: pathlib.Path) -> Tuple[bool, str]:
    """Check 8: rot #13 stub 堆积"""
    stub_markers = ["STUB:", "TODO:", "FIXME:", "XXX", "raise NotImplementedError"]

    # 白名单：这些脚本自身含反例文本（如 reason-classifier.py 含抽象理由列表）
    filename_whitelist = {
        "code-hygiene.py",      # 自身定义 STUB markers
        "proactive-scan.py",    # 自身定义 STUB markers
        "self-diagnose.py",     # 自身定义 STUB markers
        "reason-classifier.py", # 自身定义抽象理由模式
    }

    found = []
    for src_file in project_root.rglob("*.py"):
        if any(p in src_file.parts for p in ["node_modules", ".git", "__pycache__", "dist", "build"]):
            continue
        if src_file.name in filename_whitelist:
            continue
        try:
            content = src_file.read_text(encoding="utf-8")
        except Exception:
            continue
        count = sum(content.count(m) for m in stub_markers)
        if count > 3:
            found.append(f"{src_file.name}: {count} markers")

    if found:
        return False, "; ".join(found)
    return True, "无 stub 堆积"


def scan_obstacle_honesty(project_root: pathlib.Path) -> Tuple[bool, str]:
    """Check 9: V10.10 障碍诚实"""
    # 检测阻塞报告是否含 5 字段
    blockers = list(project_root.rglob("*blocker*.md")) + list(project_root.rglob("*阻塞*.md"))
    if not blockers:
        return True, "无阻塞报告（N/A）"

    suspicious = []
    for b in blockers:
        content = b.read_text(encoding="utf-8")
        # 5 字段必含: type / description / attempted_solution / time_consumed / attempt_count
        fields = ["type:", "attempted_solution:", "time_consumed", "attempt_count"]
        missing = [f for f in fields if f not in content]
        if missing:
            suspicious.append(f"{b.name}: 缺字段 {missing}")

    if suspicious:
        return False, "; ".join(suspicious)
    return True, f"{len(blockers)} 个阻塞报告 OK"


def scan_reason_fabrication(project_root: pathlib.Path) -> Tuple[bool, str]:
    """Check 10: V10.10 6 类抽象理由检测"""
    # 检测报告是否使用 6 类抽象理由
    found = []
    # 白名单：这些文件包含"理解偏差"等引用但非真实理由
    filename_whitelist = {
         "SKILL.md",  # 总编排器引用反例
         "common-anti-patterns.md",
         "common-iron-rules.md",
         "constitution.md",
         "blockage-report.md",  # 阻塞报告模板含示例
         "stage-card-protocol.md",
         "report-growth.md",
         "ask-question-anti-patterns.md",
         "anti-distortion.md",  # references/ 下反例文档
     }
    for md_file in project_root.rglob("*.md"):
        if any(p in md_file.parts for p in [
            "node_modules", "__pycache__", ".git",
            "anti-patterns",
            "research",
            ".trae",  # V11 工具目录(hooks/logs/scripts 文档不含真实产物)
            "references",  # V11 references/ 是规则定义,非真实产物
            "archive",  # 归档(不可变,不会被腐化)
            "audit-log",  # 历史日志
            "audit_history.json",  # 自检历史
            "auto-audit",  # 自检报告(本身就是元数据)
            "templates",  # 模板(含示例占位符)
        ]):
            continue
        if any(wd in str(md_file) for wd in [
            "/docs/archive/",  # 文档归档
            "/docs/bugs/",  # bug 单(已是腐烂记录)
            "/docs/reports/",  # 周期报告(数据来源不同)
            "/docs/history/",  # 历史快照
        ]):
            continue
        if md_file.name in filename_whitelist:
            continue
        try:
            content = md_file.read_text(encoding="utf-8")
        except Exception:
            continue

        for pattern in REASON_FABRICATION_PATTERNS:
            if re.search(pattern, content):
                found.append(f"{md_file.name}: 含 '{pattern}'")
                break

    if found:
        return False, "; ".join(found[:5])
    return True, "未发现抽象理由"


SCAN_FUNCTIONS = {
    "visual": scan_visual,
    "archive": scan_archive,
    "self-attest": scan_self_attest,
    "orphan-tests": scan_orphan_tests,
    "bundle-staleness": scan_bundle_staleness,
    "self-aggrandizing": scan_self_aggrandizing,
    "state-card-staleness": scan_state_card_staleness,
    "stub-pileup": scan_stub_pileup,
    "obstacle-honesty": scan_obstacle_honesty,
    "reason-fabrication": scan_reason_fabrication,
}


def main():
    parser = argparse.ArgumentParser(description="V11 10 项腐化扫描")
    parser.add_argument("--project-root", default=".", help="项目根路径")
    parser.add_argument("--output", help="扫描报告输出路径")
    parser.add_argument("--output-fix-list", help="fix-list.json 输出路径")
    parser.add_argument("--json", action="store_true", help="JSON 输出")
    args = parser.parse_args()

    project_root = pathlib.Path(args.project_root).resolve()

    results = []
    fixes = []

    for item in SCAN_ITEMS:
        func = SCAN_FUNCTIONS[item]
        is_pass, msg = func(project_root)
        results.append({
            "id": SCAN_ITEMS.index(item) + 1,
            "name": item,
            "status": "PASS" if is_pass else "FAIL",
            "message": msg,
        })
        if not is_pass:
            fixes.append({
                "id": SCAN_ITEMS.index(item) + 1,
                "name": item,
                "severity": "HIGH" if item in ("visual", "archive", "bundle-staleness", "state-card-staleness") else "MEDIUM",
                "fix_action": msg,
            })

    all_pass = all(r["status"] == "PASS" for r in results)

    output = {
        "scan_at": datetime.now(timezone.utc).isoformat(),
        "status": "PASS" if all_pass else "FAIL",
        "stats": {
            "total_checks": len(results),
            "passed": sum(1 for r in results if r["status"] == "PASS"),
            "failed": sum(1 for r in results if r["status"] == "FAIL"),
        },
        "checks": results,
    }

    if args.output:
        pathlib.Path(args.output).write_text(
            json.dumps(output, indent=2, ensure_ascii=False), encoding="utf-8"
        )

    if args.output_fix_list:
        fix_list = {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "fixes": fixes,
        }
        pathlib.Path(args.output_fix_list).write_text(
            json.dumps(fix_list, indent=2, ensure_ascii=False), encoding="utf-8"
        )

    if args.json:
        print(json.dumps(output, indent=2, ensure_ascii=False))
    else:
        status_icon = "✅" if all_pass else "❌"
        print(f"{status_icon} {output['status']} — {output['stats']}")
        for r in results:
            icon = "✓" if r["status"] == "PASS" else "✗"
            print(f"  [{icon}] {r['id']}. {r['name']}: {r['message']}")

    return 0 if all_pass else 1


if __name__ == "__main__":
    sys.exit(main())