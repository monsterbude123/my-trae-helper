#!/usr/bin/env python3
"""session-start.py — V9.2 知识发现协议 + 状态注入
每次会话启动加载，输出项目上下文供 agent 读取。
"""

import sys
from pathlib import Path
from datetime import datetime

project_root = Path(__file__).resolve().parent.parent.parent  # .trae 的父目录

print("[Fullstack V9.2] Session Start — Knowledge Discovery")
print(f"  Project: {project_root.name}")
print(f"  Time: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
print()

# ── Step 1: 驾驶舱 ──
state_card = project_root / "docs" / "specs" / ".state-card.md"
if state_card.exists():
    print("  ✅ .state-card.md found — drive from cockpit")
else:
    print("  ⚠️ .state-card.md missing — run intake to initialize")

# ── Step 2: 知识发现协议（铁律 11 延伸）──
index_md = project_root / "docs" / "INDEX.md"
arch_md = project_root / "docs" / "ARCHITECTURE.md"
decisions_md = project_root / "docs" / "DECISIONS.md"

print()
print("  Knowledge Discovery Protocol (6 layers):")
for label, path in [
    ("① .state-card.md", state_card),
    ("② INDEX.md      ", index_md),
    ("③ ARCHITECTURE   ", arch_md),
    ("④ DECISIONS      ", decisions_md),
]:
    status = "✅" if path.exists() else "⚠️ MISSING"
    print(f"    {status}  {label}")

if not index_md.exists():
    print("    💡 INDEX.md missing → intake should auto-generate")
if not arch_md.exists():
    print("    💡 ARCHITECTURE.md missing → define initial architecture first")

# ── Step 3: 干净重置检测 ──
print()
specs_dir = project_root / "docs" / "specs"
reset_features = []
if specs_dir.exists():
    for feat_dir in specs_dir.iterdir():
        if not feat_dir.is_dir():
            continue
        invalidated = feat_dir / "_invalidated"
        if invalidated.exists():
            subdirs = [d.name for d in invalidated.iterdir() if d.is_dir()]
            if subdirs:
                reset_features.append(f"{feat_dir.name} ({len(subdirs)} resets)")

if reset_features:
    print("  🧹 Clean Reset Detected (铁律 11):")
    for rf in reset_features:
        print(f"    ⚠️ {rf} — _invalidated/ exists, history is dead")
    print("    Action: agent must read ONLY current artifacts, never _invalidated/")
else:
    print("  ✅ No clean reset state detected")

# ── Step 4: prototypes 完整性 ──
print()
proto_missing = []
if specs_dir.exists():
    for feat_dir in specs_dir.iterdir():
        if not feat_dir.is_dir() or feat_dir.name.startswith('.') or feat_dir.name.startswith('_'):
            continue
        if feat_dir.name in ("archive", "changes"):
            continue
        proto_dir = feat_dir / "prototypes"
        has_design = (proto_dir / "design-prompt.md").exists()
        has_ux = (proto_dir / "ui-ux-logic.md").exists()
        if not has_design or not has_ux:
            proto_missing.append(
                f"{feat_dir.name}: missing "
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

# ── Step 5: GitNexus ──
print()
print("  ⑤ GitNexus: run `npx gitnexus list` to verify index")
print("     → impact() before any code change")
print("     → detect_changes() before any commit")

print()
print("[Fullstack V9.2] Session context loaded — 6 layers available")
sys.exit(0)
