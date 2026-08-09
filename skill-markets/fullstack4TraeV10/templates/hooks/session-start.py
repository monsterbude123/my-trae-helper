#!/usr/bin/env python3
"""session-start.py — V10.1 知识发现协议 + 状态注入
每次会话启动加载，输出项目上下文供 agent 读取。

V10.1 变更:
  - 检测 docs/constitution.md + v10_simplified 标记
  - _invalidated_ 机制已废止，改用 archive/out/spec-purge/ 路径
"""

import sys
from pathlib import Path
from datetime import datetime

project_root = Path(__file__).resolve().parent.parent.parent  # .trae 的父目录

print("[Fullstack V10.1] Session Start — Knowledge Discovery")
print(f"  Project: {project_root.name}")
print(f"  Time: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
print()

# ── Step 1: 驾驶舱 ──
state_card = project_root / "docs" / "specs" / ".state-card.md"
if state_card.exists():
    print("  ✅ .state-card.md found — drive from cockpit")
else:
    print("  ⚠️ .state-card.md missing — run intake to initialize")

# ── Step 1.5: V10 Constitution 检测 ──
constitution = project_root / "docs" / "constitution.md"
if constitution.exists():
    try:
        text = constitution.read_text(encoding="utf-8")
        if "v10_simplified" in text:
            print("  ✅ docs/constitution.md + v10_simplified 标记 — V10 满分硬门禁生效")
        else:
            print("  ⚠️ docs/constitution.md 存在但缺 v10_simplified 标记")
    except Exception:
        print("  ⚠️ docs/constitution.md 存在但无法读取")
else:
    print("  ⚠️ docs/constitution.md missing — V10 硬门禁未初始化")

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

# ── Step 3: spec-purge 历史检测（V10.1 取代 V9.2 _invalidated/）──
print()
spec_purge_dir = project_root / "docs" / "archive" / "out" / "spec-purge"
if spec_purge_dir.exists():
    purged = [d.name for d in spec_purge_dir.iterdir() if d.is_dir()]
    if purged:
        print("  🧹 Spec Purge History Detected (V10 spec-purge):")
        for p in purged:
            print(f"    ℹ️ {p} — history 已迁移到 archive/out/spec-purge/")
        print("    Action: agent 应忽略 archive/out/ 下旧 spec，仅看当前 active spec")
else:
    print("  ✅ No spec-purge history detected")

# ── Step 4: prototypes 完整性 ──
print()
proto_missing = []
specs_dir = project_root / "docs" / "specs"
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
# V10.10 提示同步: gitnexus-session-check.py (SessionStart ①) 已自动后台触发 analyze（如过期）
# 无需手动跑 `npx gitnexus analyze` — 手动跑会和后台 analyze 撞写竞争
print()
print("  ⑤ GitNexus: index staleness check 已由 SessionStart ① 自动后台完成（见 gitnexus-session-check 输出）")
print("     → impact() before any code change")
print("     → detect_changes() before any commit")
print("     → 禁止手动跑 `npx gitnexus analyze`（与后台 analyze 撞写竞争）")

print()
print("[Fullstack V10.1] Session context loaded — 6 layers available")
sys.exit(0)
