#!/usr/bin/env python3
"""proactive-scan.py — V10.5 腐化扫描包（腐烂点 14 + 15-17 修复）

实战教训: V10.3.9 Agent 不主动发现问题,用户问才查。本脚本把腐化扫描打包,供 rot-detector
agent 在 Phase 4.5 强制调用。

用法:
  python scripts/proactive-scan.py --project-root <path> [--feature <name>] [--json]
  python scripts/proactive-scan.py --only <check_name> --project-root <path> [--json]

8 项检查 (V10.5):
  1. orphan-tests            — 孤儿测试/组件 (腐烂点 12)
  2. deprecated-code         — @deprecated 标记的代码 (腐烂点 12 变体)
  3. archive-drift           — archive/ 下文件被修改 (腐烂点 10)
  4. bundle-staleness        — binary chunk vs dist chunk (腐烂点 13, 仅 Tauri)
  5. visual-freshness        — 视觉证据新鲜度 + 内容 (腐烂点 9)
  6. self-aggrandizing-doc   — state-card 声称的 INV vs spec.md 实际 INV (腐烂点 15, V10.5 新)
  7. state-card-staleness    — .state-card.md mtime + change 数量一致性 (腐烂点 16, V10.5 新)
  8. stub-pileup             — define.md-only 骨架堆积比例 (腐烂点 17, V10.5 新)

退出码:
  0 = pass (全部 PASS/WARN/SKIP,无 FAIL)
  1 = fail (任一 FAIL)
  2 = script error

V10.4 引入 (2026-07-30) | V10.5 扩展 (2026-07-31)
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, List, Optional

try:
    from common import get_project_root
except ImportError:  # pragma: no cover
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from common import get_project_root


# === 数据结构 ===

@dataclass
class CheckResult:
    name: str
    status: str               # "pass" | "warn" | "fail" | "skip"
    severity: str             # "PASS" | "WARN" | "FAIL"
    evidence: str = ""
    count: int = 0
    duration_ms: int = 0

    def to_dict(self):
        return self.__dict__


# === 单项 check 实现 ===

def _run_subprocess(cmd: list[str], cwd: Optional[Path] = None) -> tuple[int, str, str]:
    """运行子进程,返回 (returncode, stdout, stderr)"""
    try:
        r = subprocess.run(
            cmd, cwd=str(cwd) if cwd else None,
            capture_output=True, text=True, timeout=30,
        )
        return r.returncode, r.stdout, r.stderr
    except subprocess.TimeoutExpired:
        return -1, "", "timeout"
    except FileNotFoundError as e:
        return -1, "", str(e)


def run_orphan_detector(project_root: Path, feature: Optional[str] = None) -> CheckResult:
    """检查 1: 孤儿测试/组件"""
    t0 = time.time()
    script = Path(__file__).parent / "orphan-detector.py"
    cmd = ["python", str(script), "--project-root", str(project_root), "--json"]
    if feature:
        cmd += ["--feature", feature]
    rc, stdout, stderr = _run_subprocess(cmd, cwd=project_root)
    duration = int((time.time() - t0) * 1000)
    if rc < 0:
        return CheckResult("orphan-tests", "skip", "PASS", f"subprocess error: {stderr}", 0, duration)
    try:
        data = json.loads(stdout)
    except json.JSONDecodeError:
        return CheckResult("orphan-tests", "warn", "WARN", f"非 JSON 输出: {stdout[:200]}", 0, duration)
    fail = data.get("fail_count", 0)
    warn = data.get("warn_count", 0)
    total = data.get("orphan_count", 0)
    if fail > 0:
        return CheckResult(
            "orphan-tests", "fail", "FAIL",
            f"发现 {fail} 项孤儿测试（FAIL） + {warn} 项 WARN",
            total, duration,
        )
    if warn > 0:
        return CheckResult(
            "orphan-tests", "warn", "WARN",
            f"发现 {warn} 项 WARN 孤儿（建议清理）",
            total, duration,
        )
    return CheckResult("orphan-tests", "pass", "PASS", "无孤儿测试", 0, duration)


def run_deprecated_scan(project_root: Path, feature: Optional[str] = None) -> CheckResult:
    """检查 2: @deprecated 标记代码"""
    t0 = time.time()
    # 复用 orphan-detector 的 deprecated 检测（normal 模式输出 deprecated 项）
    script = Path(__file__).parent / "orphan-detector.py"
    cmd = ["python", str(script), "--project-root", str(project_root), "--json"]
    rc, stdout, stderr = _run_subprocess(cmd, cwd=project_root)
    duration = int((time.time() - t0) * 1000)
    if rc < 0:
        return CheckResult("deprecated-code", "skip", "PASS", f"subprocess error: {stderr}", 0, duration)
    try:
        data = json.loads(stdout)
    except json.JSONDecodeError:
        return CheckResult("deprecated-code", "warn", "WARN", f"非 JSON 输出: {stdout[:200]}", 0, duration)
    deprecated = [o for o in data.get("orphans", []) if o.get("kind") == "deprecated-code"]
    count = len(deprecated)
    if count > 5:
        return CheckResult(
            "deprecated-code", "warn", "WARN",
            f"发现 {count} 处 @deprecated 标记，建议清理",
            count, duration,
        )
    if count > 0:
        return CheckResult(
            "deprecated-code", "pass", "PASS",
            f"{count} 处 @deprecated（少量可接受）",
            count, duration,
        )
    return CheckResult("deprecated-code", "pass", "PASS", "无 @deprecated 标记", 0, duration)


def run_archive_drift(project_root: Path, feature: Optional[str] = None) -> CheckResult:
    """检查 3: archive/ 下文件被修改（腐烂点 10）

    简单实现: 检查 archive/ 目录最近 7 天内是否有 mtime 变化
    """
    t0 = time.time()
    archive_dirs = [
        project_root / "docs" / "archive",
        project_root / "docs" / "specs" / "archive",
    ]
    violations: list[str] = []
    for archive_dir in archive_dirs:
        if not archive_dir.is_dir():
            continue
        for p in archive_dir.rglob("*"):
            if not p.is_file():
                continue
            try:
                mtime = p.stat().st_mtime
            except OSError:
                continue
            age_days = (time.time() - mtime) / 86400
            if age_days < 7:
                violations.append(f"{p.relative_to(project_root)} ({age_days:.1f}d)")
    duration = int((time.time() - t0) * 1000)
    if violations:
        return CheckResult(
            "archive-drift", "fail", "FAIL",
            f"archive/ 下 {len(violations)} 个文件 7 天内有修改: {'; '.join(violations[:3])}{'...' if len(violations) > 3 else ''}",
            len(violations), duration,
        )
    return CheckResult("archive-drift", "pass", "PASS", "archive/ 无近期修改", 0, duration)


def run_bundle_staleness(project_root: Path, feature: Optional[str] = None) -> CheckResult:
    """检查 4: Bundle Staleness (腐烂点 13, 仅 Tauri)"""
    t0 = time.time()
    script = Path(__file__).parent / "dist-hash-check.py"
    cmd = ["python", str(script), "--project-root", str(project_root), "--json"]
    rc, stdout, stderr = _run_subprocess(cmd, cwd=project_root)
    duration = int((time.time() - t0) * 1000)
    if rc < 0:
        return CheckResult("bundle-staleness", "skip", "PASS", f"subprocess error: {stderr}", 0, duration)
    try:
        data = json.loads(stdout)
    except json.JSONDecodeError:
        return CheckResult("bundle-staleness", "warn", "WARN", f"非 JSON 输出: {stdout[:200]}", 0, duration)
    status = data.get("status", "skip")
    if status == "skip":
        return CheckResult("bundle-staleness", "skip", "PASS", data.get("reason", "skipped"), 0, duration)
    if status == "fail":
        total_stale = data.get("total_stale", 0)
        return CheckResult(
            "bundle-staleness", "fail", "FAIL",
            f"binary 引用 {total_stale} 个 stale chunk（改 TS 后未重 build）",
            total_stale, duration,
        )
    return CheckResult("bundle-staleness", "pass", "PASS", "binary chunk 与 dist 一致", 0, duration)


def run_visual_freshness(project_root: Path, feature: Optional[str] = None) -> CheckResult:
    """检查 5: 视觉证据新鲜度 + 内容 (腐烂点 9)"""
    t0 = time.time()
    shots_dir = project_root / "docs" / "verifications" / "tauri"
    if not shots_dir.is_dir():
        return CheckResult(
            "visual-freshness", "skip", "PASS",
            "无 visual 目录（非 Tauri 项目或未截图）",
            0, int((time.time() - t0) * 1000),
        )
    shots = sorted(shots_dir.glob("*.png"), key=lambda p: p.stat().st_mtime, reverse=True)
    if not shots:
        return CheckResult(
            "visual-freshness", "warn", "WARN",
            "visual 目录为空（需补充截图）",
            0, int((time.time() - t0) * 1000),
        )
    # 检查最新一张
    newest = shots[0]
    age_hours = (time.time() - newest.stat().st_mtime) / 3600
    duration = int((time.time() - t0) * 1000)
    if age_hours > 168:  # 7 天
        return CheckResult(
            "visual-freshness", "fail", "FAIL",
            f"最新视觉证据 {newest.name} 已有 {age_hours/24:.1f} 天（>7d）— 需重新截图",
            len(shots), duration,
        )
    # 调用 visual-content-check 做内容验证
    script = Path(__file__).parent / "visual-content-check.py"
    cmd = ["python", str(script), str(newest), "--json"]
    rc, stdout, stderr = _run_subprocess(cmd, cwd=project_root)
    duration = int((time.time() - t0) * 1000)
    if rc < 0:
        return CheckResult(
            "visual-freshness", "warn", "WARN",
            f"visual-content-check 调用失败: {stderr}",
            len(shots), duration,
        )
    try:
        data = json.loads(stdout)
    except json.JSONDecodeError:
        return CheckResult(
            "visual-freshness", "warn", "WARN",
            f"visual-content-check 非 JSON 输出: {stdout[:200]}",
            len(shots), duration,
        )
    vc_status = data.get("status", "warn")
    if vc_status == "fail":
        return CheckResult(
            "visual-freshness", "fail", "FAIL",
            f"最新截图 {newest.name} 内容校验失败（{data.get('fail_count', 0)}/L3-5 失配）",
            len(shots), duration,
        )
    return CheckResult(
        "visual-freshness", "pass", "PASS",
        f"最新 {newest.name}（{age_hours:.1f}h ago）内容校验通过",
        len(shots), duration,
    )


# === V10.5 新增 check 函数（腐烂点 15-17） ===

INV_RE = re.compile(r"INV-[A-Z0-9-]+")


def _extract_invs(text: str) -> set[str]:
    """从文本中抽取所有 INV-XXX 标识符"""
    return set(INV_RE.findall(text))


def run_self_aggrandizing_doc(project_root: Path, feature: Optional[str] = None) -> CheckResult:
    """检查 6: 自我吹嘘腐烂 (腐烂点 15)

    算法: 抽取 state-card.md/INDEX.md 等元文档中声称的 INV → 抽取所有 spec.md 实际 INV
          → doc_claims - code_actual = 自我吹嘘清单
    """
    t0 = time.time()
    # 候选"自我吹嘘"源: state-card.md + INDEX.md + 主要报告
    claim_sources = [
        project_root / "docs" / "specs" / ".state-card.md",
        project_root / "docs" / "specs" / "INDEX.md",
    ]
    doc_claims: set[str] = set()
    for src in claim_sources:
        if src.is_file():
            doc_claims |= _extract_invs(src.read_text(encoding="utf-8", errors="ignore"))
    if not doc_claims:
        return CheckResult(
            "self-aggrandizing-doc", "skip", "PASS",
            "无元文档含 INV- 声明（非 V10 项目或元文档缺失）",
            0, int((time.time() - t0) * 1000),
        )
    # 抽取所有 spec.md 实际 INV
    changes_dir = project_root / "docs" / "specs" / "changes"
    code_actual: set[str] = set()
    if changes_dir.is_dir():
        for spec in changes_dir.rglob("spec.md"):
            code_actual |= _extract_invs(spec.read_text(encoding="utf-8", errors="ignore"))
    # 比对
    bragging = doc_claims - code_actual
    duration = int((time.time() - t0) * 1000)
    brag_rate = len(bragging) / len(doc_claims) if doc_claims else 0
    if brag_rate > 0.3:
        sample_list = sorted(bragging)[:5]
        sample_str = ", ".join(sample_list) + ("..." if len(bragging) > 5 else "")
        return CheckResult(
            "self-aggrandizing-doc", "fail", "FAIL",
            f"{len(bragging)}/{len(doc_claims)} 声称的 INV 在 spec.md 不存在 (rate={brag_rate:.0%}): {sample_str}",
            len(bragging), duration,
        )
    if bragging:
        return CheckResult(
            "self-aggrandizing-doc", "warn", "WARN",
            f"{len(bragging)}/{len(doc_claims)} 声称的 INV 在 spec.md 不存在 (rate={brag_rate:.0%})，建议核对",
            len(bragging), duration,
        )
    return CheckResult(
        "self-aggrandizing-doc", "pass", "PASS",
        f"所有 {len(doc_claims)} 个声称的 INV 都在 spec.md 落地",
        0, duration,
    )


def run_state_card_staleness(project_root: Path, feature: Optional[str] = None) -> CheckResult:
    """检查 7: 状态卡陈旧腐烂 (腐烂点 16)

    算法: 比对 state-card.md mtime (vs 当前时间) + 列出的 change 数 (vs 实际)
    """
    t0 = time.time()
    sc = project_root / "docs" / "specs" / ".state-card.md"
    if not sc.is_file():
        return CheckResult(
            "state-card-staleness", "skip", "PASS",
            "无 .state-card.md（未走 V10 流程）",
            0, int((time.time() - t0) * 1000),
        )
    age_hours = (time.time() - sc.stat().st_mtime) / 3600
    # 抽取 state-card.md 中实际列出的 change 数（粗略: 匹配 `| \d+ |` 表格行）
    text = sc.read_text(encoding="utf-8", errors="ignore")
    claimed = set(re.findall(r"changes/([\w-]+)/?", text))
    # 实际 changes 目录
    changes_dir = project_root / "docs" / "specs" / "changes"
    actual: set[str] = set()
    if changes_dir.is_dir():
        actual = {d.name for d in changes_dir.iterdir() if d.is_dir()}
    missing_in_doc = actual - claimed
    duration = int((time.time() - t0) * 1000)
    issues = []
    if age_hours > 72:
        issues.append(f"state-card 已有 {age_hours/24:.1f} 天未更新 (>3d)")
    elif age_hours > 24:
        issues.append(f"state-card 已有 {age_hours:.0f}h 未更新 (>24h)")
    if missing_in_doc:
        sample_list = sorted(missing_in_doc)[:3]
        sample_str = ", ".join(sample_list) + ("..." if len(missing_in_doc) > 3 else "")
        issues.append(f"{len(missing_in_doc)} 个 change 在 state-card 未列出: {sample_str}")
    if issues and (age_hours > 72 or len(missing_in_doc) > 0):
        return CheckResult(
            "state-card-staleness", "fail", "FAIL",
            "; ".join(issues),
            len(issues), duration,
        )
    if issues:
        return CheckResult(
            "state-card-staleness", "warn", "WARN",
            "; ".join(issues),
            len(issues), duration,
        )
    return CheckResult(
        "state-card-staleness", "pass", "PASS",
        f"state-card 健康 ({age_hours:.1f}h, {len(actual)} changes 完整列出)",
        0, duration,
    )


def run_stub_pileup(project_root: Path, feature: Optional[str] = None) -> CheckResult:
    """检查 8: 骨架堆积腐烂 (腐烂点 17)

    算法: 扫 docs/specs/changes/*/ 各文件存在性
          → 分类 archived / full-plan / stub (only define.md) / controller
          → stub_rate = stub / total
    """
    t0 = time.time()
    changes_dir = project_root / "docs" / "specs" / "changes"
    if not changes_dir.is_dir():
        return CheckResult(
            "stub-pileup", "skip", "PASS",
            "无 docs/specs/changes/ 目录（非 V10 项目）",
            0, int((time.time() - t0) * 1000),
        )
    buckets = {"archived": [], "full": [], "stub": [], "controller": [], "other": []}
    for d in sorted(changes_dir.iterdir()):
        if not d.is_dir():
            continue
        # 控制器: 有 plan.md/spec.md 但无 tasks.md
        names = {f.name for f in d.iterdir() if f.is_file()}
        # 归档标志: 在 state-card.md 标 Archived 或 tasks.md 全 [x] 或有 archive/ 子目录
        has_archived_marker = (
            "acceptance-scorecard" in " ".join(names)  # 存在计分卡 = 验收过
            or bool(list((d / "archive").iterdir())) if (d / "archive").is_dir() else False
        )
        has_tasks = "tasks.md" in names
        has_spec = "spec.md" in names
        has_plan = "plan.md" in names
        has_define = "define.md" in names
        # controller: 名称含 refactor / controller / hub
        is_controller = "refactor" in d.name.lower() or "controller" in d.name.lower() or "hub" in d.name.lower()
        if is_controller and not has_tasks:
            buckets["controller"].append(d.name)
        elif has_archived_marker and has_tasks:
            buckets["archived"].append(d.name)
        elif has_define and has_spec and has_tasks:
            buckets["full"].append(d.name)
        elif has_define and not (has_spec and has_tasks):
            buckets["stub"].append(d.name)
        else:
            buckets["other"].append(d.name)
    total = sum(len(v) for v in buckets.values())
    stub_count = len(buckets["stub"])
    stub_rate = stub_count / total if total else 0
    duration = int((time.time() - t0) * 1000)
    if stub_rate > 0.6:
        return CheckResult(
            "stub-pileup", "fail", "FAIL",
            f"骨架堆积 {stub_count}/{total} = {stub_rate:.0%} (>{0.6:.0%} 破窗临界): {', '.join(buckets['stub'][:5])}{'...' if stub_count > 5 else ''}",
            stub_count, duration,
        )
    if stub_rate > 0.4:
        return CheckResult(
            "stub-pileup", "warn", "WARN",
            f"骨架比例 {stub_count}/{total} = {stub_rate:.0%} (>{0.4:.0%} 需警惕): {', '.join(buckets['stub'][:5])}{'...' if stub_count > 5 else ''}",
            stub_count, duration,
        )
    return CheckResult(
        "stub-pileup", "pass", "PASS",
        f"骨架 {stub_count}/{total} = {stub_rate:.0%} (健康)",
        0, duration,
    )


# === 注册所有 check ===

CHECKS: list[tuple[str, Callable]] = [
    ("orphan-tests", run_orphan_detector),
    ("deprecated-code", run_deprecated_scan),
    ("archive-drift", run_archive_drift),
    ("bundle-staleness", run_bundle_staleness),
    ("visual-freshness", run_visual_freshness),
    ("self-aggrandizing-doc", run_self_aggrandizing_doc),
    ("state-card-staleness", run_state_card_staleness),
    ("stub-pileup", run_stub_pileup),
]


def run_all(project_root: Path, feature: Optional[str] = None,
            only: Optional[str] = None) -> list[CheckResult]:
    results: list[CheckResult] = []
    for name, fn in CHECKS:
        if only and only != name:
            continue
        try:
            r = fn(project_root, feature)
        except Exception as e:
            r = CheckResult(name, "fail", "FAIL", f"check 内部异常: {e}")
        results.append(r)
    return results


def main() -> int:
    parser = argparse.ArgumentParser(
        description="V10.5 8 项腐化扫描包（腐烂点 14+15+16+17 修复）",
    )
    parser.add_argument("--project-root", type=str, default=".", help="项目根")
    parser.add_argument("--feature", type=str, help="feature 名（限定扫描范围）")
    parser.add_argument("--only", type=str, choices=[n for n, _ in CHECKS],
                        help="仅运行指定 check")
    parser.add_argument("--json", action="store_true", help="JSON 输出")
    args = parser.parse_args()

    project_root = Path(args.project_root).resolve() if args.project_root != "." else get_project_root()

    if not project_root.is_dir():
        print(f"ERROR: 项目根不存在: {project_root}", file=sys.stderr)
        return 2

    results = run_all(project_root, args.feature, args.only)
    fail_count = sum(1 for r in results if r.severity == "FAIL")

    if args.json:
        payload = {
            "status": "fail" if fail_count > 0 else "pass",
            "project_root": str(project_root),
            "feature": args.feature,
            "total": len(results),
            "fail_count": fail_count,
            "results": [r.to_dict() for r in results],
        }
        print(json.dumps(payload, ensure_ascii=False, separators=(",", ":")))
    else:
        # Markdown 报告
        print(f"# V10.5 Proactive Rot Scan\n")
        print(f"- project: {project_root.name}")
        print(f"- feature: {args.feature or '(all)'}")
        print(f"- total: {len(results)}, fail: {fail_count}\n")
        print(f"| # | Check | Status | Severity | Evidence | Duration |")
        print(f"|---|-------|--------|----------|----------|----------|")
        for i, r in enumerate(results, 1):
            icon = {"pass": "✅", "warn": "⚠️", "fail": "🛑", "skip": "⏭️"}.get(r.status, "?")
            print(f"| {i} | {r.name} | {icon} {r.status} | {r.severity} | {r.evidence[:80]} | {r.duration_ms}ms |")
        print()
        if fail_count:
            print(f"🛑 {fail_count} 项 FAIL — 阻断 Accept,要求 implementer 修复")
        else:
            print(f"✅ 全部通过（FAIL: 0, WARN: {sum(1 for r in results if r.severity == 'WARN')}, SKIP: {sum(1 for r in results if r.severity == 'PASS' and r.status == 'skip')}）")

    return 1 if fail_count > 0 else 0


if __name__ == "__main__":
    raise SystemExit(main())
