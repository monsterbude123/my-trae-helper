#!/usr/bin/env python3
"""script-threshold-audit.py — V11.2 NEW 脚本阈值变更审计(蒸馏自 00-03-diagnostic)

蒸馏: visual-content-check.py MIN_QUADRANT_DIFF_DARK 2.5 → 1.5 → 0.9 连续降级无审计
铁律: 修改 MIN_* / pass_count / THRESHOLD_* 常量必审计;连续降级 2 次 → 🛑 REJECT

用法:
    python scripts/script-threshold-audit.py --project-root . [--check-git-diff --base-ref main] [--json]
    python scripts/script-threshold-audit.py --project-root . --scripts visual-content-check.py
"""
import argparse
import json
import pathlib
import re
import subprocess
import sys
from typing import Dict, List


# V11 scripts 阈值常量识别模式(V11.2 NEW) — 合并 MIN_/MAX_/PASS_COUNT/THRESHOLD_* 统一识别
THRESHOLD_PATTERN = re.compile(
    r'^(\s*)((?:MIN_[A-Z_]+|MAX_[A-Z_]+|PASS_COUNT|THRESHOLD_[A-Z_]+|[A-Z_]+_THRESHOLD))\s*=\s*([\d.]+)',
    re.MULTILINE,
)


def scan_thresholds(script_path: pathlib.Path) -> List[Dict]:
    """扫描单个脚本的阈值常量"""
    if not script_path.exists():
        return []
    content = script_path.read_text(encoding="utf-8")
    results = []
    for match in THRESHOLD_PATTERN.finditer(content):
        indent, name, value = match.groups()
        line_num = content[:match.start()].count('\n') + 1
        results.append({
            "script": script_path.name,
            "line": line_num,
            "name": name,
            "value": float(value),
            "context": match.group(0).strip(),
        })
    return results


def detect_git_diff_changes(project_root: pathlib.Path, base_ref: str, scripts: List[pathlib.Path]) -> List[Dict]:
    """比对 git diff,检测常量值变更"""
    changes = []
    for script in scripts:
        try:
            diff_result = subprocess.run(
                ["git", "diff", f"{base_ref}..HEAD", "--", str(script.relative_to(project_root))],
                cwd=str(project_root), capture_output=True, text=True, encoding="utf-8", timeout=10
            )
            if diff_result.returncode != 0:
                continue
            for line in diff_result.stdout.split('\n'):
                m = re.match(r'^[-+]\s*((?:MIN_|MAX_|PASS_COUNT|THRESHOLD_|[A-Z_]+_THRESHOLD)[A-Z_0-9]*)\s*=\s*([\d.]+)', line)
                if m:
                    changes.append({
                        "script": script.name,
                        "name": m.group(1),
                        "new_value": float(m.group(2)),
                        "diff_type": "deletion" if line.startswith('-') else "addition",
                    })
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass
    return changes


def check_consecutive_downgrade(changes: List[Dict], current_thresholds: Dict) -> List[Dict]:
    """V11.2 NEW: 检测连续降级 2 次 → 阻断"""
    blockers = []
    by_name: Dict[str, List[Dict]] = {}
    for change in changes:
        by_name.setdefault(change["name"], []).append(change)

    for name, history in by_name.items():
        if len(history) < 2:
            continue
        values = [c["new_value"] for c in history if c["diff_type"] == "addition"]
        if len(values) < 2:
            continue
        # 连续降级检测:后值 < 前值 两次连续
        downgrade_count = sum(1 for i in range(1, len(values)) if values[i] < values[i-1])
        if downgrade_count >= 2:
            blockers.append({
                "type": "consecutive_downgrade",
                "name": name,
                "history": history,
                "risk": "阈值连续降级 >= 2 次,违反 00-03-diagnostic 反例教训",
                "recommendation": "重新审视验收方法(改测试方法,不是改阈值)",
            })
    return blockers


def main() -> int:
    parser = argparse.ArgumentParser(description="V11.2 脚本阈值变更审计")
    parser.add_argument("--project-root", default=".", help="项目根路径")
    parser.add_argument("--scripts", nargs="*", help="指定脚本名(默认全部)")
    parser.add_argument("--check-git-diff", action="store_true", help="比对 git diff 检测变更")
    parser.add_argument("--base-ref", default="main", help="git 比对基准")
    parser.add_argument("--json", action="store_true", help="JSON 输出")
    args = parser.parse_args()

    project_root = pathlib.Path(args.project_root).resolve()
    scripts_dir = project_root / "scripts" if (project_root / "scripts").exists() else pathlib.Path(__file__).parent

    if args.scripts:
        scripts = [scripts_dir / s for s in args.scripts]
    else:
        scripts = sorted(scripts_dir.glob("*.py"))

    all_thresholds = []
    for script in scripts:
        all_thresholds.extend(scan_thresholds(script))

    result = {
        "scripts_scanned": [s.name for s in scripts if s.exists()],
        "thresholds_found": len(all_thresholds),
        "thresholds": all_thresholds,
    }

    if args.check_git_diff:
        changes = detect_git_diff_changes(project_root, args.base_ref, [s for s in scripts if s.exists()])
        blockers = check_consecutive_downgrade(changes, {t["name"]: t for t in all_thresholds})
        result["git_diff_changes"] = changes
        result["blockers"] = blockers
        result["exit_status"] = 1 if blockers else 0

    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print(f"🔍 脚本阈值审计 — {len(scripts)} 脚本, {len(all_thresholds)} 阈值常量")
        for t in all_thresholds[:10]:
            print(f"  {t['script']}:{t['line']}  {t['name']} = {t['value']}")
        if len(all_thresholds) > 10:
            print(f"  ... 还有 {len(all_thresholds) - 10} 个")
        if result.get("blockers"):
            print(f"\n🛑 {len(result['blockers'])} 个阻断项")
            for b in result["blockers"]:
                print(f"  - {b['name']}: {b['risk']}")
            return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())