#!/usr/bin/env python3
"""V11 session-start.py — SessionStart Hook（蒸馏自 V10）

6 层知识发现协议 + 状态卡注入 + spec-purge 历史检测 + prototypes 完整性。

V11 简化:
  - 不含 v10_simplified 标记检测（V11 改用 common-iron-rules.md）
  - 增强 Article XVII secret 路径检查
  - 增加 gitnexus 双端提示（已由 gitnexus-session-check.py 处理）

SECURITY 标注: print() 仅状态信息。无外网、无破坏性命令。
"""

import sys
from pathlib import Path
from datetime import datetime


def resolve_project_root() -> Path:
    """从 __file__ 推算项目根（避免 .trae/ 软链）"""
    cursor = Path(__file__).resolve().parent
    while cursor != cursor.parent:
        if (cursor / ".trae").exists() or (cursor / "docs").exists():
            return cursor
        cursor = cursor.parent
    return Path(__file__).resolve().parent.parent.parent


project_root = resolve_project_root()

print("[Fullstack V11] Session Start — Knowledge Discovery")
print(f"  Project: {project_root.name}")
print(f"  Time: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
print()

# ── Step 1: 状态卡门禁 ──
state_card = project_root / "docs" / "specs" / ".state-card.md"
if state_card.exists():
    print("  ✅ docs/specs/.state-card.md found — drive from cockpit")
else:
    print("  ⚠️ docs/specs/.state-card.md missing — run intake to initialize")

# ── Step 2: 知识发现协议（6 层）──
print()
print("  Knowledge Discovery Protocol (6 layers):")
for label, sub_path in [
    ("① state-card.md", "docs/specs/.state-card.md"),
    ("② INDEX.md      ", "docs/INDEX.md"),
    ("③ ARCHITECTURE   ", "docs/ARCHITECTURE.md"),
    ("④ DECISIONS      ", "docs/DECISIONS.md"),
    ("⑤ gitnexus       ", ".gitnexus/meta.json"),
    ("⑥ spec           ", "docs/specs/changes/{change-id}/.state-card.md"),
]:
    full = project_root / sub_path
    status = "✅" if full.exists() else "⚠️ MISSING"
    print(f"    {status}  {label}  ({sub_path})")

# ── Step 3: V11 Article XVII secret 路径检查 ──
print()
secret_paths = [".env", ".env.local", "secrets/", "credentials/"]
print("  Article XVII Secret Path Check:")
for sp in secret_paths:
    full = project_root / sp
    if full.exists():
        print(f"    🚫 {sp} EXISTS — ensure forbidden_paths contains it")
    else:
        print(f"    ✅ {sp} absent (forbidden_paths ok)")

# ── Step 4: prototypes 完整性 ──
print()
proto_missing = []
specs_dir = project_root / "docs" / "specs" / "changes"
if specs_dir.exists():
    for change_dir in specs_dir.iterdir():
        if not change_dir.is_dir() or change_dir.name.startswith('.'):
            continue
        spec_path = change_dir / "spec.md"
        if not spec_path.exists():
            continue
        proto_dir = change_dir / "prototypes"
        has_design = (proto_dir / "design-prompt.md").exists()
        has_ux = (proto_dir / "ui-ux-logic.md").exists()
        if not has_design or not has_ux:
            proto_missing.append(
                f"{change_dir.name}: missing "
                + ("" if has_design else "design-prompt.md ")
                + ("" if has_ux else "ui-ux-logic.md")
            )

if proto_missing:
    print("  ⚠️ Missing prototypes/ documents:")
    for pm in proto_missing:
        print(f"    - {pm}")
    print("    → Route: spec-writer backfill mode")
else:
    print("  ✅ All prototypes/ documents present")

# ── Step 5: V11 gitnexus 状态 ──
print()
gitnexus_dir = project_root / ".gitnexus"
if gitnexus_dir.exists():
    print("  ✅ .gitnexus/ found — gitnexus-session-check.py will verify freshness")
else:
    print("  ℹ️ .gitnexus/ missing — run `gitnexus analyze` to initialize")

print()
print("[Fullstack V11] SessionStart complete — agent may proceed")
sys.exit(0)