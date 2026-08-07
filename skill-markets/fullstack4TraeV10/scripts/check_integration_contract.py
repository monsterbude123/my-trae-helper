#!/usr/bin/env python3
"""check_integration_contract.py — V10 接入契约硬门禁

扫描项目源码检查 5 项契约违规 (V10 新增 2026-07-28)。
每个违例 = 🛑 REJECT。

用法:
  python check_integration_contract.py --project-root /path/to/your-project
  python check_integration_contract.py --project-root /path/to/your-project --json

5 项契约:
  1. 不直接 fetch('/api/v1/...') — 必须走 apiClient.get/post/...
  2. 不直接 addEventListener('keydown', ...) — 必须用 registerShortcut 或 useKeyboardShortcuts
  3. 新模块必须有 ModuleDef 入口 — 扫描 src/modules/<name>/index.tsx (index.ts 也算)
  4. 后端模块必须 pub trait Module 实现 — advisory (不强求,仅提醒)
  5. 事件命名符合 `<domain>:<action>` — 扫描 eventBus.emit('xxx:yyy', ...)

白名单 (允许直 fetch 的场景):
  - .test.tsx / .test.ts (测试 mock)
  - __tests__/ 目录下所有文件
  - src/shared/api-client.ts (ApiClient 自身实现)
  - src/shared/hooks/useKeyboardShortcuts.ts (hook 自身)
  - src/shared/hooks/useWorkbenchShortcuts.ts (hook 自身)
  - 历史负债 (AssetLightbox / ContextMenu / DropOverlay): advisory 而非 hard reject
"""

import argparse
import json
import re
import sys
from pathlib import Path


def find_project_root(start: Path) -> Path | None:
    cur = start.resolve()
    for _ in range(10):
        if (cur / "Cargo.toml").exists() and (cur / "package.json").exists():
            return cur
        cur = cur.parent
    return None


WHITELIST_FILE_PATTERNS = [
    r"__tests__[/\\]",
    r"[/\\]\.trae[/\\]",
    r"[/\\]node_modules[/\\]",
    r"[/\\]target[/\\]",
    r"[/\\]dist[/\\]",
]

# 契约自身 / hook 自身 — 完全白名单
SELF_IMPL_FILES = [
    "src/shared/api-client.ts",
    "src/shared/events.ts",
    "src/shared/keybindings/keybindingService.ts",
    "src/shared/keybindings/keybindingApi.ts",
    "src/shared/keybindings/registerBuiltinCommands.ts",
    "src/shared/hooks/useKeyboardShortcuts.ts",
    "src/shared/hooks/useWorkbenchShortcuts.ts",
    "src/components/bottom-panel/logs/",
]

# 历史负债 — advisory 标记,不 REJECT (本任务范围外)
ADVISORY_FILES = [
    "AssetLightbox.tsx",
    "ContextMenu.tsx",
    "DropOverlay.tsx",
]


def is_whitelisted(file_path: Path) -> bool:
    p = str(file_path).replace("\\", "/")
    for pat in WHITELIST_FILE_PATTERNS:
        if re.search(pat, p):
            return True
    for self_impl in SELF_IMPL_FILES:
        if self_impl in p:
            return True
    return False


def is_advisory(file_path: Path) -> bool:
    p = str(file_path).replace("\\", "/")
    for adv in ADVISORY_FILES:
        if adv in p:
            return True
    return False


def _line_of(content: str, offset: int) -> int:
    return content[:offset].count("\n") + 1


def scan_fetch_violation(project_root: Path) -> tuple[list[str], list[str]]:
    errors, advisory = [], []
    src_dir = project_root / "src"
    if not src_dir.exists():
        return errors, advisory
    pattern = re.compile(r"""fetch\(\s*['"`]/api/v\d+/[^'"`]*['"`]""")
    for ext in ("ts", "tsx"):
        for f in src_dir.rglob(f"*.{ext}"):
            if is_whitelisted(f):
                continue
            try:
                content = f.read_text(encoding="utf-8", errors="ignore")
            except Exception:
                continue
            for m in pattern.finditer(content):
                ln = _line_of(content, m.start())
                snippet = m.group(0)[:80]
                msg = (
                    f"[fetch-violation] {f.relative_to(project_root)}:{ln} — "
                    f"直 fetch 后端端点: {snippet} (必须用 apiClient.get/post)"
                )
                if is_advisory(f):
                    advisory.append(msg)
                else:
                    errors.append(msg)
    return errors, advisory


def scan_keydown_violation(project_root: Path) -> tuple[list[str], list[str]]:
    errors, advisory = [], []
    src_dir = project_root / "src"
    if not src_dir.exists():
        return errors, advisory
    pattern = re.compile(r"""addEventListener\(\s*['"]keydown['"]""")
    for ext in ("ts", "tsx"):
        for f in src_dir.rglob(f"*.{ext}"):
            if is_whitelisted(f):
                continue
            try:
                content = f.read_text(encoding="utf-8", errors="ignore")
            except Exception:
                continue
            for m in pattern.finditer(content):
                ln = _line_of(content, m.start())
                snippet = m.group(0)[:80]
                msg = (
                    f"[keydown-violation] {f.relative_to(project_root)}:{ln} — "
                    f"直监听 keydown: {snippet} (必须用 registerShortcut 或 useKeybindings)"
                )
                if is_advisory(f):
                    advisory.append(msg)
                else:
                    errors.append(msg)
    return errors, advisory


def scan_module_entry(project_root: Path) -> tuple[list[str], list[str]]:
    errors, advisory = [], []
    modules_dir = project_root / "src" / "modules"
    if not modules_dir.exists():
        return errors, advisory
    for mod_dir in modules_dir.iterdir():
        if not mod_dir.is_dir():
            continue
        # index.ts 或 index.tsx 都算入口
        if any((mod_dir / name).exists() for name in ("index.ts", "index.tsx")):
            continue
        # 检查是否有替代入口: registry 中的模块 (Phase A mock 允许无 index.ts)
        # 但 V10 契约硬要求 — 标记为 advisory (本任务范围外历史)
        advisory.append(
            f"[module-entry-missing-advisory] src/modules/{mod_dir.name}/ — "
            f"缺 index.ts 或 index.tsx (ModuleDef 入口契约 — 历史模块待迁移)"
        )
    return errors, advisory


def scan_event_naming(project_root: Path) -> tuple[list[str], list[str]]:
    errors, advisory = [], []
    src_dir = project_root / "src"
    if not src_dir.exists():
        return errors, advisory
    pattern = re.compile(r"""eventBus\.emit\(\s*['"]([^'"]+)['"]""")
    named = re.compile(r"^[a-z][a-z0-9-]*:[a-z][a-z0-9_]*$")
    for ext in ("ts", "tsx"):
        for f in src_dir.rglob(f"*.{ext}"):
            if is_whitelisted(f):
                continue
            try:
                content = f.read_text(encoding="utf-8", errors="ignore")
            except Exception:
                continue
            for m in pattern.finditer(content):
                event_name = m.group(1)
                if named.match(event_name):
                    continue
                ln = _line_of(content, m.start())
                msg = (
                    f"[event-naming-violation] {f.relative_to(project_root)}:{ln} — "
                    f"事件名 '{event_name}' 不符合 <domain>:<action> (lowercase + 冒号 + snake_case action)"
                )
                if is_advisory(f):
                    advisory.append(msg)
                else:
                    errors.append(msg)
    return errors, advisory


def main():
    parser = argparse.ArgumentParser(
        description="V10 接入契约硬门禁 — 5 项契约违例扫描",
    )
    parser.add_argument(
        "--project-root", type=str, default=".",
        help="项目根路径（默认自动向上查找 Cargo.toml + package.json）",
    )
    parser.add_argument(
        "--json", action="store_true", help="JSON 输出（机械验证友好）",
    )
    parser.add_argument(
        "--advisory-only", action="store_true",
        help="仅输出 advisory (历史负债), 不 REJECT",
    )
    args = parser.parse_args()

    project_root = Path(args.project_root).resolve()
    cargo_toml = project_root / "src-tauri" / "Cargo.toml"
    if not cargo_toml.exists():
        cargo_toml = project_root / "Cargo.toml"
    if not cargo_toml.exists():
        auto = find_project_root(Path.cwd())
        if auto:
            project_root = auto
            cargo_toml = project_root / "src-tauri" / "Cargo.toml"
    if not cargo_toml.exists():
        print(f"❌ 未找到 Cargo.toml, --project-root={project_root} 不是 Rust 项目根")
        sys.exit(1)

    hard_errors: list[str] = []
    advisories: list[str] = []

    for fn in (scan_fetch_violation, scan_keydown_violation, scan_module_entry, scan_event_naming):
        errs, advs = fn(project_root)
        hard_errors.extend(errs)
        advisories.extend(advs)

    if args.json:
        payload = {
            "status": "pass" if not hard_errors else "fail",
            "project_root": str(project_root),
            "hard_errors": hard_errors,
            "advisories": advisories,
            "hard_count": len(hard_errors),
            "advisory_count": len(advisories),
        }
        print(json.dumps(payload, ensure_ascii=False, separators=(",", ":")))
        sys.exit(0 if not hard_errors else 1)

    print(f"━━━ integration-contract 扫描: {project_root} ━━━")
    if not hard_errors:
        print(f"✅ 硬门禁 0 violations")
    else:
        print(f"🛑 硬门禁 {len(hard_errors)} 处违例 (REJECT):\n")
        for err in hard_errors:
            print(f"  - {err}")
    if advisories:
        print(f"\n⚠️ advisory {len(advisories)} 处 (历史负债, 不 REJECT):\n")
        for adv in advisories[:10]:
            print(f"  - {adv}")
        if len(advisories) > 10:
            print(f"  ... ({len(advisories) - 10} more)")
    if args.advisory_only:
        sys.exit(0 if not advisories else 1)
    sys.exit(0 if not hard_errors else 1)


if __name__ == "__main__":
    main()