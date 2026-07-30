#!/usr/bin/env python3
"""phase-gate.py — 阶段转换硬门禁 (V10.4 升级: +3 phases)

V10.4 新增 (2026-07-30):
  python scripts/phase-gate.py --phase orphan-precheck --feature 00-04-system-settings
  python scripts/phase-gate.py --phase bundle-check --project-root <path>
  python scripts/phase-gate.py --phase proactive-scan --project-root <path> [--feature <name>]

用法:
  # V9 兼容（项目级单文件布局）
  python scripts/phase-gate.py --phase plan-to-spec
  python scripts/phase-gate.py --phase spec-to-contract

  # V10 feature-scoped（多 feature 嵌套布局）
  python scripts/phase-gate.py --phase plan-to-spec --feature 00-05-task-queue

  # JSON 输出（机械验证友好）
  python scripts/phase-gate.py --phase spec-to-contract --feature 00-05-task-queue --json

  # 接入契约门禁（V10 新增 2026-07-28）
  python scripts/phase-gate.py --phase integration-contract --project-root /path/to/AIGCMediaDesktop

任意检查失败 = exit 1 + 具体缺失项
"""

import argparse
import os
import re
import sys
from pathlib import Path

# å…è®¸ç›´æŽ¥æ‰§è¡Œæˆ– import
try:
    from common import (
        FeaturePaths,
        get_current_feature,
        get_project_root,
    )
except ImportError:  # pragma: no cover
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from common import (
        FeaturePaths,
        get_current_feature,
        get_project_root,
    )

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent


def _find_review_report(project_root: Path) -> Path | None:
    """æŸ¥æ‰¾ review æŠ¥å‘Šï¼ˆV10 review-latest.md ä¼˜å…ˆ, V9 acceptance-scorecard-*.md fallbackï¼‰
    
    V10_STRICT_REVIEW=1: ç¦æ­¢ fallbackï¼Œå¿…é¡» review-latest.md å­˜åœ¨ï¼ˆç¡¬é—¨ç¦ï¼‰
    é»˜è®¤: V10_STRICT_REVIEW=1ï¼ˆå¼ºåˆ¶ï¼‰

    Returns:
        æ‰¾åˆ°çš„ review æŠ¥å‘Šè·¯å¾„; æ‰¾ä¸åˆ°è¿”å›ž None
    """
    strict_review = os.environ.get("V10_STRICT_REVIEW", "1") == "1"
    reports = project_root / "docs" / "reports"
    if not reports.is_dir():
        return None
    # V10 ä¼˜å…ˆ
    latest = reports / "review-latest.md"
    if latest.is_file():
        return latest
    # V10_STRICT_REVIEW=1 æ—¶ç¦æ­¢ fallback
    if strict_review:
        return None
    # V9 fallback: acceptance-scorecard-{date}.mdï¼ˆæŒ‰æ—¥æœŸå€’åº, æœ€æ–°ä¼˜å…ˆï¼‰
    scorecards = sorted(reports.glob("acceptance-scorecard-*.md"), reverse=True)
    if scorecards:
        return scorecards[0]
    return None


def get_paths(project_root: Path, feature: str | None) -> dict:
    """è§£æžé˜¶æ®µé—¨ç¦æ‰€éœ€çš„è·¯å¾„é›†åˆ"""
    if feature:
        paths = FeaturePaths.from_root(project_root, feature)
        return {
            "mode": "feature-scoped",
            "feature": feature,
            "plan": paths.plan,
            "spec": paths.spec,
            "tasks": paths.tasks,
            "contracts_dir": paths.contracts_dir,
            "test_skel": paths.contracts_dir / "test-skeleton",
            "alt_skel": project_root / "__tests__" / "contracts",
            "review_report": _find_review_report(project_root),
            "doc_sync": project_root / "docs" / "reports" / "doc-sync-latest.md",
        }
    return {
        "mode": "project-level",
        "feature": None,
        "plan": project_root / "docs" / "specs" / "plan.md",
        "spec": project_root / "docs" / "specs" / "spec.md",
        "tasks": project_root / "docs" / "specs" / "tasks.md",
        "contracts_dir": project_root / "docs" / "specs" / "contracts",
        "test_skel": project_root / "docs" / "specs" / "contracts" / "test-skeleton",
        "alt_skel": project_root / "__tests__" / "contracts",
        "review_report": _find_review_report(project_root),
        "doc_sync": project_root / "docs" / "reports" / "doc-sync-latest.md",
    }


def check_plan_to_spec(project_root: Path, feature: str | None = None) -> tuple[bool, list[str]]:
    errors = []
    paths = get_paths(project_root, feature)
    plan_path = paths["plan"]
    if not plan_path.exists():
        errors.append(f"ç¼ºå¤±: {plan_path.relative_to(project_root)}")
        return False, errors
    content = plan_path.read_text(encoding="utf-8")
    if not re.search(
        r"^#{1,6}\s+(Closure|Closing|Closure Criteria|Acceptance Criteria)",
        content,
        re.MULTILINE | re.IGNORECASE,
    ):
        errors.append(f"{plan_path.name} ç¼º '## Closure' æ ‡é¢˜æ®µï¼ˆæˆ– '## Acceptance Criteria'ï¼‰")
    if "P0" not in content:
        errors.append(f"{plan_path.name} ç¼º P0 ä¼˜å…ˆçº§ä»»åŠ¡")
    return len(errors) == 0, errors


def check_spec_to_contract(project_root: Path, feature: str | None = None) -> tuple[bool, list[str]]:
    errors = []
    paths = get_paths(project_root, feature)
    spec_path = paths["spec"]
    if not spec_path.exists():
        errors.append(f"ç¼ºå¤±: {spec_path.relative_to(project_root)}")
        return False, errors
    content = spec_path.read_text(encoding="utf-8")
    req_count = len(re.findall(
        r"### ((?:Functional |Non-Functional )?Requirements?[: ]|REQ-\d+[: ])",
        content,
    ))
    if req_count < 3:
        errors.append(f"{spec_path.name} Requirement æ•° = {req_count}ï¼ˆè¦æ±‚ â‰¥ 3ï¼‰")
    if "Invariants" not in content and "Invariant" not in content:
        errors.append(f"{spec_path.name} ç¼º Invariants æ®µ")
    return len(errors) == 0, errors


def check_contract_to_implement(project_root: Path, feature: str | None = None) -> tuple[bool, list[str]]:
    errors = []
    paths = get_paths(project_root, feature)
    contracts_dir = paths["contracts_dir"]
    if not contracts_dir.exists():
        errors.append(f"ç¼ºå¤±ç›®å½•: {contracts_dir.relative_to(project_root)}")
    md_files = list(contracts_dir.rglob("*.md")) if contracts_dir.exists() else []
    if contracts_dir.exists() and not md_files:
        errors.append(f"contracts/ ä¸‹æ—  .md æ–‡ä»¶")

    test_skel = paths["test_skel"]
    alt_skel = paths["alt_skel"]

    def _has_tests(p: Path) -> bool:
        if not p.exists():
            return False
        if p.is_file() and p.suffix == ".md":
            return True
        return any(
            p.rglob(f"*.{ext}") for ext in ("ts", "py", "md", "feature")
        )

    has_skel = False
    if test_skel.exists() and _has_tests(test_skel):
        has_skel = True
    if alt_skel.exists() and _has_tests(alt_skel):
        has_skel = True

    if not has_skel:
        errors.append(
            f"ç¼ºå¤±æµ‹è¯•éª¨æž¶ã€‚è¯·åœ¨ä»¥ä¸‹ä¸¤ä¸ªè·¯å¾„ä¹‹ä¸€åˆ›å»ºæµ‹è¯•æ–‡ä»¶ï¼š\n"
            f"  é€‰é¡¹ 1: docs/specs/{{feature}}/contracts/test-skeleton/  (V10 æ ‡å‡†)\n"
            f"  é€‰é¡¹ 2: __tests__/contracts/  (Vitest/Jest é¡¹ç›®æƒ¯ä¾‹)"
        )

    return len(errors) == 0, errors


def check_implement_to_review(project_root: Path, feature: str | None = None) -> tuple[bool, list[str]]:
    errors = []
    paths = get_paths(project_root, feature)
    tasks_path = paths["tasks"]
    if not tasks_path.exists():
        errors.append(f"ç¼ºå¤±: {tasks_path.relative_to(project_root)}")
        return False, errors

    content = tasks_path.read_text(encoding="utf-8")
    unchecked = re.findall(r"- \[ \]", content)
    if unchecked:
        errors.append(f"{tasks_path.name} è¿˜æœ‰ {len(unchecked)} é¡¹æœªå‹¾é€‰")

    import os
    import subprocess
    last_commit = os.environ.get("V10_LAST_REVIEWED_COMMIT", "HEAD~1")
    result = subprocess.run(
        [
            "python",
            str(Path(__file__).parent / "code-hygiene.py"),
            "--diff-base",
            last_commit,
            "--project-root",
            str(project_root),
        ],
        cwd=project_root,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        errors.append(f"code-hygiene å¤±è´¥ï¼ˆbase={last_commit}ï¼‰:\n{result.stdout}")

    return len(errors) == 0, errors


def check_review_to_accept(project_root: Path, feature: str | None = None) -> tuple[bool, list[str]]:
    errors = []
    paths = get_paths(project_root, feature)
    review_report = paths["review_report"]
    if review_report is None or not review_report.is_file():
        errors.append(
            f"ç¼ºå¤± review æŠ¥å‘Šï¼ˆdocs/reports/review-latest.md æˆ– acceptance-scorecard-*.mdï¼‰"
        )
        return False, errors

    content = review_report.read_text(encoding="utf-8")
    # ponytail: 兼容 markdown bold 格式 `- **code_dimension**: PASS` 与 raw `code_dimension: PASS` 双名 (2026-07-29)
    for dim in ["code_dimension", "api_dimension", "uiux_dimension", "boundary_dimension"]:
        if dim not in content or not re.search(
            rf"(?:\*\*{dim}\*\*|{dim}):\s*PASS", content
        ):
            errors.append(f"{dim} éž PASS")

    if "total_score: 5.0" not in content:
        errors.append("total_score â‰  5.0ï¼ˆè¦æ±‚æ»¡åˆ†ï¼‰")

    doc_sync = paths["doc_sync"]
    if not doc_sync.exists():
        errors.append(f"ç¼ºå¤± DOC SYNC æŠ¥å‘Š: {doc_sync.relative_to(project_root)}")

    return len(errors) == 0, errors


def check_integration_contract(project_root: Path, feature: str | None = None) -> tuple[bool, list[str]]:
    """æŽ¥å…¥å¥‘çº¦é—¨ç¦ (V10 æ–°å¢ž 2026-07-28) â€” å§”æ‰˜ç»™ check_integration_contract.py
    è§ skill-markets/fullstack4TraeV10/scripts/check_integration_contract.py
    """
    import subprocess
    script = Path(__file__).parent / "check_integration_contract.py"
    if not script.exists():
        return False, [f"ç¼ºå¤±æ£€æŸ¥è„šæœ¬: {script}"]
    result = subprocess.run(
        ["python", str(script), "--project-root", str(project_root)],
        cwd=project_root,
        capture_output=True,
        text=True,
    )
    # é€ä¼ è„šæœ¬è¾“å‡º
    if result.stdout:
        print(result.stdout, end='')
    if result.returncode != 0:
        return False, [result.stderr.strip() or "integration-contract å¤±è´¥"]
    return True, []

def check_orphan_precheck(project_root: Path, feature: str | None = None) -> tuple[bool, list[str]]:
    """V10.4 孤儿测试预检 (腐烂点 12 修复)

    在 Contract/Implement 阶段开始前扫历史孤儿测试。
    委托给 orphan-detector.py。
    """
    import subprocess
    script = Path(__file__).parent / "orphan-detector.py"
    if not script.exists():
        return False, [f"missing check script: {script}"]
    cmd = ["python", str(script), "--project-root", str(project_root)]
    if feature:
        cmd += ["--feature", feature]
    result = subprocess.run(cmd, cwd=project_root, capture_output=True, text=True)
    if result.stdout:
        print(result.stdout, end='')
    if result.returncode == 1:
        return False, ["orphan tests found, must clean up before next phase (see output above)"]
    if result.returncode != 0:
        return False, [f"orphan-detector abnormal exit ({result.returncode}): {result.stderr.strip()}"]
    return True, []


def check_bundle_check(project_root: Path, feature: str | None = None) -> tuple[bool, list[str]]:
    """V10.4 Bundle 一致性检查 (腐烂点 13 修复)

    验证 binary 嵌入的 JS chunk hash vs dist/assets 当前 hash。
    委托给 dist-hash-check.py (仅 Tauri 项目启用)。
    """
    import subprocess
    script = Path(__file__).parent / "dist-hash-check.py"
    if not script.exists():
        return False, [f"missing check script: {script}"]
    result = subprocess.run(
        ["python", str(script), "--project-root", str(project_root)],
        cwd=project_root, capture_output=True, text=True,
    )
    if result.stdout:
        print(result.stdout, end='')
    if result.returncode == 1:
        return False, ["binary references stale chunks, rebuild needed (see output above)"]
    if result.returncode != 0:
        return False, [f"dist-hash-check abnormal exit ({result.returncode}): {result.stderr.strip()}"]
    return True, []


def check_proactive_scan(project_root: Path, feature: str | None = None) -> tuple[bool, list[str]]:
    """V10.4 5 项腐化扫描 (腐烂点 14 修复)

    在 Review 末尾 + Accept 之前由 rot-detector 强制调用。
    委托给 proactive-scan.py。
    """
    import subprocess
    script = Path(__file__).parent / "proactive-scan.py"
    if not script.exists():
        return False, [f"missing check script: {script}"]
    cmd = ["python", str(script), "--project-root", str(project_root)]
    if feature:
        cmd += ["--feature", feature]
    result = subprocess.run(cmd, cwd=project_root, capture_output=True, text=True)
    if result.stdout:
        print(result.stdout, end='')
    if result.returncode == 1:
        return False, ["rot FAIL found, must fix before Accept (see report above)"]
    if result.returncode != 0:
        return False, [f"proactive-scan abnormal exit ({result.returncode}): {result.stderr.strip()}"]
    return True, []




GATES = {
    "plan-to-spec": check_plan_to_spec,
    "spec-to-contract": check_spec_to_contract,
    "contract-to-implement": check_contract_to_implement,
    "implement-to-review": check_implement_to_review,
    "review-to-accept": check_review_to_accept,
    "integration-contract": check_integration_contract,
    # V10.4 新增 (2026-07-30)
    "orphan-precheck": check_orphan_precheck,
    "bundle-check": check_bundle_check,
    "proactive-scan": check_proactive_scan,
}


def main():
    parser = argparse.ArgumentParser(
        description="V10 é˜¶æ®µè½¬æ¢ç¡¬é—¨ç¦ï¼ˆæ”¯æŒ feature-scopedï¼‰",
    )
    parser.add_argument(
        "--project-root", type=str, default=".",
        help="é¡¹ç›®æ ¹è·¯å¾„ï¼ˆé»˜è®¤è‡ªåŠ¨å‘ä¸ŠæŸ¥æ‰¾ V10 é”šç‚¹ï¼‰",
    )
    parser.add_argument(
        "--feature", type=str,
        help="feature åï¼ˆå¦‚ 00-05-task-queueï¼‰ï¼›ä¸ä¼ åˆ™æ£€æŸ¥é¡¹ç›®çº§å•æ–‡ä»¶å¸ƒå±€ï¼ˆV9 å…¼å®¹ï¼‰",
    )
    parser.add_argument(
        "--phase", required=True, choices=list(GATES.keys()),
        help="é˜¶æ®µè½¬æ¢åï¼ˆå¦‚ spec-to-contractï¼‰/ æŽ¥å…¥å¥‘çº¦é—¨ç¦ï¼ˆintegration-contractï¼‰",
    )
    parser.add_argument(
        "--json", action="store_true", help="JSON è¾“å‡ºï¼ˆæœºæ¢°éªŒè¯å‹å¥½ï¼‰",
    )
    args = parser.parse_args()

    if args.project_root and args.project_root != ".":
        project_root = Path(args.project_root).resolve()
    else:
        project_root = get_project_root()

    feature = args.feature or get_current_feature() or None

    check_fn = GATES[args.phase]
    ok, errors = check_fn(project_root, feature)

    if args.json:
        import json
        payload = {
            "status": "pass" if ok else "fail",
            "phase": args.phase,
            "feature": feature,
            "project_root": str(project_root),
            "errors": errors,
        }
        print(json.dumps(payload, ensure_ascii=False, separators=(",", ":")))
    elif ok:
        scope = f"feature={feature}" if feature else "project-level"
        print(f"âœ… {args.phase} é˜¶æ®µè½¬æ¢é—¨ç¦é€šè¿‡ï¼ˆ{scope}ï¼‰")
    else:
        scope = f"feature={feature}" if feature else "project-level"
        print(f"ðŸ›‘ {args.phase} é˜¶æ®µè½¬æ¢é—¨ç¦å¤±è´¥ï¼ˆ{scope}ï¼‰ï¼š\n")
        for err in errors:
            print(f"  - {err}")
        print(f"\nä¿®å¤åŽå†è¯•ã€‚ä»»ä¸€ FAIL = ðŸ›‘ REJECT")

    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()