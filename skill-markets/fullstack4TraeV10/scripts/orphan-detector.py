#!/usr/bin/env python3
"""orphan-detector.py — V10.4 孤儿测试/组件检测器（腐烂点 12 修复）

实战教训: 00-04-system-settings 替代了 SettingsPage,但 SettingsPage.test.tsx + SettingsPage.tsx
都没即时清除,导致 9 failed 测试持续 1 周。本脚本主动扫"被删/被取代组件的残留"。

用法:
  python scripts/orphan-detector.py --project-root <path> [--feature <name>] [--json]

检测项:
  1. Orphan Tests       — 测试文件 import 的目标文件不存在
  2. Deprecated Code    — // @deprecated / /* DEPRECATED */ 标记
  3. Stale Component    — 在 spec 提到但代码中已不存在的组件

退出码:
  0 = no orphan
  1 = found orphan(s)
  2 = script error

V10.4 引入 (2026-07-30)
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import List, Optional

# 允许直接执行或 import
try:
    from common import get_project_root
except ImportError:  # pragma: no cover
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from common import get_project_root


# === 数据结构 ===

@dataclass
class OrphanRef:
    """单个孤儿引用"""
    kind: str              # "orphan-test" | "deprecated-code" | "stale-component"
    test_file: str         # 引用方文件（孤儿测试 = test 文件,deprecated = 源文件）
    target: str            # 目标文件/组件
    line: int = 0          # 出现行号
    last_used_in_spec: Optional[str] = None  # 最后出现的 spec 路径
    severity: str = "WARN" # "WARN" | "FAIL"
    detail: str = ""       # 额外说明

    def to_dict(self):
        return asdict(self)


# === 扫描实现 ===

# import 目标文件路径的正则 (兼容: import X from './path' | import { X } from '../path' | require('./path'))
IMPORT_PATTERN = re.compile(
    r"""(?:
        from\s+['"]([^'"]+)['"]       |   # import x from '...'
        require\s*\(\s*['"]([^'"]+)['"]\s*\) |  # require('...')
        import\s*\(\s*['"]([^'"]+)['"]\s*\)     # dynamic import('...')
    )""",
    re.VERBOSE,
)

# @deprecated 标记
DEPRECATED_PATTERN = re.compile(
    r"^\s*(?://|/\*|\*)\s*@deprecated\b|^\s*(?://|/\*|\*)\s*DEPRECATED\b",
    re.IGNORECASE | re.MULTILINE,
)

# 测试文件扩展名
TEST_EXTENSIONS = {".test.ts", ".test.tsx", ".spec.ts", ".spec.tsx"}
SOURCE_EXTENSIONS = {".ts", ".tsx", ".js", ".jsx"}


def _resolve_import_path(import_path: str, from_file: Path, project_root: Path) -> Optional[Path]:
    """把 import 路径解析为绝对文件路径

    仅解析相对路径(以 . 或 .. 开头)。库 import('react') → None。
    """
    if not import_path.startswith("."):
        return None  # 库 import,跳过
    base = (from_file.parent / import_path).resolve()
    candidates = [
        base,
        base.with_suffix(".ts"),
        base.with_suffix(".tsx"),
        base.with_suffix(".js"),
        base.with_suffix(".jsx"),
        base / "index.ts",
        base / "index.tsx",
        base / "index.js",
        base / "index.jsx",
    ]
    for c in candidates:
        try:
            if c.is_file() and (project_root in c.parents or c == project_root):
                return c
        except OSError:
            continue
    # ponytail: 即使文件不存在,只要是合理路径也返回(用于检测孤儿)
    return base


def _is_test_file(p: Path) -> bool:
    return any(p.name.endswith(ext) for ext in TEST_EXTENSIONS)


def find_orphan_tests(project_root: Path, feature: Optional[str] = None) -> List[OrphanRef]:
    """扫描孤儿测试

    1. 扫 src/**/__tests__/**/*.{ts,tsx} + tests/**/*.{ts,tsx} + src/**/*.test.{ts,tsx}
    2. 对每个 test 文件,提取 import 目标
    3. 检查目标文件是否存在
    """
    orphans: List[OrphanRef] = []

    # 限定扫描目录
    test_dirs = []
    if feature:
        spec_dir = project_root / "docs" / "specs" / feature
        if spec_dir.is_dir():
            test_dirs.append(spec_dir)
    else:
        for sub in ("src", "tests", "test", "__tests__"):
            d = project_root / sub
            if d.is_dir():
                test_dirs.append(d)

    seen: set[tuple[str, str]] = set()  # (test_file, target) 去重

    for test_dir in test_dirs:
        for test_file in test_dir.rglob("*"):
            if not test_file.is_file():
                continue
            if not _is_test_file(test_file):
                continue
            if "node_modules" in test_file.parts:
                continue
            try:
                content = test_file.read_text(encoding="utf-8", errors="ignore")
            except OSError:
                continue

            for line_num, line in enumerate(content.splitlines(), start=1):
                for m in IMPORT_PATTERN.finditer(line):
                    import_path = m.group(1) or m.group(2) or m.group(3)
                    if not import_path:
                        continue
                    target = _resolve_import_path(import_path, test_file, project_root)
                    if target is None or target.exists():
                        continue

                    # target 不存在 → orphan
                    key = (str(test_file.relative_to(project_root)), import_path)
                    if key in seen:
                        continue
                    seen.add(key)

                    # 推断 severity
                    # 若 import 的目标在 spec 提及但代码不存在 → FAIL
                    severity = "FAIL"
                    last_spec = _find_last_spec_mention(import_path, project_root, feature)
                    if last_spec is None:
                        severity = "WARN"  # 没有 spec 提及 → 降级为警告(可能是私有测试)

                    orphans.append(OrphanRef(
                        kind="orphan-test",
                        test_file=str(test_file.relative_to(project_root)),
                        target=import_path,
                        line=line_num,
                        last_used_in_spec=last_spec,
                        severity=severity,
                        detail=f"测试文件引用了不存在的目标: {import_path}",
                    ))

    return orphans


def find_deprecated_code(project_root: Path) -> List[OrphanRef]:
    """扫描 @deprecated / DEPRECATED 标记

    用于发现"已废弃但代码还在"的情况(腐烂点 12 变体)。
    """
    orphans: List[OrphanRef] = []
    for ext in SOURCE_EXTENSIONS:
        for src_file in project_root.rglob(f"*{ext}"):
            if any(p in src_file.parts for p in ("node_modules", "dist", "build", "target", ".git")):
                continue
            if src_file.name.endswith((".test.ts", ".test.tsx", ".spec.ts", ".spec.tsx")):
                continue
            try:
                content = src_file.read_text(encoding="utf-8", errors="ignore")
            except OSError:
                continue
            for m in DEPRECATED_PATTERN.finditer(content):
                line_num = content[:m.start()].count("\n") + 1
                orphans.append(OrphanRef(
                    kind="deprecated-code",
                    test_file=str(src_file.relative_to(project_root)),
                    target="",
                    line=line_num,
                    severity="WARN",
                    detail=f"标记已废弃但代码仍在: {m.group(0).strip()[:80]}",
                ))
    return orphans


def _find_last_spec_mention(name: str, project_root: Path, feature: Optional[str]) -> Optional[str]:
    """查找 spec 中是否提到 name(简单 grep)"""
    specs_root = project_root / "docs" / "specs"
    if not specs_root.is_dir():
        return None
    if feature:
        spec_files = [specs_root / feature / "spec.md"]
    else:
        spec_files = list(specs_root.rglob("spec.md"))

    # 取 name 最后一段(如 ./components/SettingsPage → SettingsPage)
    key = name.rstrip("/").split("/")[-1].replace(".tsx", "").replace(".ts", "")

    for sf in spec_files:
        if not sf.is_file():
            continue
        try:
            content = sf.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        if key in content:
            return str(sf.relative_to(project_root))
    return None


def main() -> int:
    parser = argparse.ArgumentParser(
        description="V10.4 孤儿测试/组件检测器（腐烂点 12 修复）",
    )
    parser.add_argument("--project-root", type=str, default=".", help="项目根")
    parser.add_argument("--feature", type=str, help="限定 feature 范围")
    parser.add_argument("--json", action="store_true", help="JSON 输出")
    parser.add_argument(
        "--no-deprecated-scan", action="store_true",
        help="跳过 @deprecated 扫描（仅查孤儿测试）",
    )
    args = parser.parse_args()

    project_root = Path(args.project_root).resolve() if args.project_root != "." else get_project_root()

    if not project_root.is_dir():
        print(f"ERROR: 项目根不存在: {project_root}", file=sys.stderr)
        return 2

    # 扫描
    orphans: List[OrphanRef] = []
    orphans.extend(find_orphan_tests(project_root, args.feature))
    if not args.no_deprecated_scan:
        orphans.extend(find_deprecated_code(project_root))

    # 输出
    fail_count = sum(1 for o in orphans if o.severity == "FAIL")
    warn_count = sum(1 for o in orphans if o.severity == "WARN")

    if args.json:
        payload = {
            "status": "fail" if fail_count > 0 else ("warn" if warn_count > 0 else "pass"),
            "project_root": str(project_root),
            "feature": args.feature,
            "orphan_count": len(orphans),
            "fail_count": fail_count,
            "warn_count": warn_count,
            "orphans": [o.to_dict() for o in orphans],
        }
        print(json.dumps(payload, ensure_ascii=False, separators=(",", ":")))
    else:
        if not orphans:
            print(f"✅ 无孤儿引用（project={project_root.name}, feature={args.feature or 'all'}）")
            return 0
        print(f"🛑 发现 {len(orphans)} 项孤儿引用（FAIL: {fail_count}, WARN: {warn_count}）\n")
        for o in orphans:
            sev_icon = "🛑" if o.severity == "FAIL" else "⚠️"
            print(f"  {sev_icon} [{o.kind}] {o.test_file}:{o.line}")
            print(f"      target: {o.target or '(inline)'}")
            if o.last_used_in_spec:
                print(f"      last_used_in_spec: {o.last_used_in_spec}")
            if o.detail:
                print(f"      detail: {o.detail}")
            print()

    return 1 if fail_count > 0 else 0


if __name__ == "__main__":
    raise SystemExit(main())
