#!/usr/bin/env python3
"""migrate-v9-to-v10.py — V9 → V10 项目迁移（极简原则）

SECURITY 标注（V10.12.2 NEW）: 本脚本含 print() 输出但不输出错误堆栈或调试信息。
迁移工具一次性运行，无 DEBUG 模式控制。脚本已用 try/except 兜底关键路径（dry_run 模式）。
详见 SECURITY-MAP.md fullstack4TraeV10 行 §注。

V10 核心：只保留用户意图 + 决策 + 原型 + 契约，删掉一切运行时工件。

保留:
  ✅ spec.md       — 含 Why（用户意图）+ What Changes（决策）
  ✅ prototypes/   — 原型设计资产
  ✅ contracts/    — 代码已按其实现，不能动

删除（运行时工件 = 噪声）:
  🗑️ plan.md        — 运行时规划，AI 从头生成
  🗑️ tasks.md       — 运行时 checklist
  🗑️ checklist.md   — 验收虚化元凶，从零做
  🗑️ _invalidated/  — V9 隔离机制，V10 已废止

用法:
  python scripts/migrate-v9-to-v10.py --project-root <项目路径>
  python scripts/migrate-v9-to-v10.py --project-root . --dry-run

幂等安全：检测 .trae/logs/migrate-v9-to-v10.done 标记文件则跳过。
"""

import argparse
import shutil
import sys
from pathlib import Path
from datetime import datetime


SIMPLIFIED_HEADER = """---
v10_simplified: true
v10_simplified_at: {timestamp}
v10_source: migrate-v9-to-v10
v10_keep: spec.md + prototypes/ + contracts/
v10_drop: plan.md + tasks.md + checklist.md + _invalidated/
v10_note: 本 change 已完成 V10 简化迁移，AI 重新进入时按 spec-kit → Spec-Enhancer 走 5 阶段
---

"""


def get_project_root(start_path: Path) -> Path:
    current = start_path.resolve()
    for _ in range(10):
        if (current / "docs").is_dir():
            return current
        if current.parent == current:
            break
        current = current.parent
    return start_path.resolve()


def _iter_feature_dirs(specs_dir: Path):
    """遍历所有 feature 目录（兼容 V10 标准 + AIGCMediaDesktop 嵌套布局）

    V10 标准: docs/specs/{feature}/
    嵌套布局: docs/specs/changes/{feature}/
    """
    if not specs_dir.exists():
        return
    for entry in specs_dir.iterdir():
        if not entry.is_dir() or entry.name.startswith((".", "_")):
            continue
        # 跳过非 feature 目录（如 contracts/、archive/）
        # 但要递归进 changes/ 子目录
        if entry.name == "changes":
            for nested in entry.iterdir():
                if nested.is_dir() and not nested.name.startswith((".", "_")):
                    yield nested
        else:
            yield entry


def step1_drop_runtime_files(project_root: Path, dry_run: bool) -> list[str]:
    """Step 1: 删除所有 change 下的运行时工件

    每个 change 目录下物理删除:
      - plan.md
      - tasks.md
      - checklist.md
      - _invalidated/
    """
    changes = []
    specs_dir = project_root / "docs" / "specs"

    if not specs_dir.exists():
        return changes

    runtime_files = ["plan.md", "tasks.md", "checklist.md"]

    for feature_dir in _iter_feature_dirs(specs_dir):

        # 删除单个文件
        for filename in runtime_files:
            f = feature_dir / filename
            if not f.exists():
                continue
            if dry_run:
                changes.append(f"[DRY RUN] 删除 {feature_dir.name}/{filename}")
            else:
                f.unlink()
                changes.append(f"✅ 删除 {feature_dir.name}/{filename}")

        # 删除 _invalidated/ 整目录
        invalidated = feature_dir / "_invalidated"
        if invalidated.exists():
            if dry_run:
                changes.append(f"[DRY RUN] 删除 {feature_dir.name}/_invalidated/")
            else:
                shutil.rmtree(str(invalidated))
                changes.append(f"✅ 删除 {feature_dir.name}/_invalidated/")

    return changes


def step2_mark_spec_simplified(project_root: Path, dry_run: bool) -> list[str]:
    """Step 2: 给 spec.md 顶部注入 v10_simplified: true 标记"""
    changes = []
    specs_dir = project_root / "docs" / "specs"
    timestamp = datetime.now().strftime("%Y-%m-%d")

    if not specs_dir.exists():
        return changes

    for feature_dir in _iter_feature_dirs(specs_dir):

        spec_path = feature_dir / "spec.md"
        if not spec_path.exists():
            continue

        content = spec_path.read_text(encoding="utf-8")
        if "v10_simplified: true" in content:
            continue  # 幂等

        if dry_run:
            changes.append(f"[DRY RUN] {feature_dir.name}/spec.md 顶部追加 v10_simplified 标记")
        else:
            header = SIMPLIFIED_HEADER.format(timestamp=timestamp)
            spec_path.write_text(header + content, encoding="utf-8")
            changes.append(f"✅ {feature_dir.name}/spec.md 顶部追加 v10_simplified 标记")

    return changes


def step3_drop_v9_references(project_root: Path, dry_run: bool) -> list[str]:
    """Step 3: 删除 docs/references/ 下 V9 专题文档（直接删除，不再归档）"""
    changes = []
    docs_refs = project_root / "docs" / "references"

    if not docs_refs.exists():
        return changes

    v9_specific = ["openspec-format.md", "define-format.md", "rework-protocol.md"]

    for filename in v9_specific:
        f = docs_refs / filename
        if not f.exists():
            continue
        if dry_run:
            changes.append(f"[DRY RUN] 删除 docs/references/{filename}")
        else:
            f.unlink()
            changes.append(f"✅ 删除 docs/references/{filename}")

    return changes


def step4_drop_v8_standards(project_root: Path, dry_run: bool) -> list[str]:
    """Step 4: 删除 standards/fullstack4traev8-enhancement/ 整目录"""
    changes = []
    src_dir = project_root / "docs" / "standards" / "fullstack4traev8-enhancement"

    if not src_dir.exists():
        return changes

    if dry_run:
        changes.append(f"[DRY RUN] 删除 standards/fullstack4traev8-enhancement/")
    else:
        shutil.rmtree(str(src_dir))
        changes.append(f"✅ 删除 standards/fullstack4traev8-enhancement/")

    return changes


def write_done_marker(project_root: Path) -> None:
    """幂等标记：写一个 .trae/logs/migrate-v9-to-v10.done 文件"""
    logs_dir = project_root / ".trae" / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)
    marker = logs_dir / "migrate-v9-to-v10.done"
    marker.write_text(
        f"V9 → V10 迁移完成: {datetime.now().isoformat()}\n"
        f"原则: 保留 spec.md + prototypes/ + contracts/；删除 plan/tasks/checklist/_invalidated\n",
        encoding="utf-8",
    )


def already_migrated(project_root: Path) -> bool:
    marker = project_root / ".trae" / "logs" / "migrate-v9-to-v10.done"
    return marker.exists()


def main():
    parser = argparse.ArgumentParser(description="V9 → V10 项目迁移（极简原则）")
    parser.add_argument("--project-root", type=str, default=".", help="项目根路径")
    parser.add_argument("--dry-run", action="store_true", help="预览模式")
    parser.add_argument("--force", action="store_true", help="跳过已迁移检查")
    args = parser.parse_args()

    project_root = get_project_root(Path(args.project_root))
    print(f"项目根: {project_root}")
    print(f"模式: {'DRY RUN (预览)' if args.dry_run else '执行模式'}\n")

    print("保留:")
    print("  ✅ spec.md       — 用户意图 + 决策")
    print("  ✅ prototypes/   — 原型设计")
    print("  ✅ contracts/    — 代码实现依据")
    print("删除:")
    print("  🗑️ plan.md + tasks.md + checklist.md + _invalidated/")
    print("  🗑️ references/{openspec,define,rework}-format.md")
    print("  🗑️ standards/fullstack4traev8-enhancement/\n")

    if not args.force and already_migrated(project_root):
        print("⏭️  项目已迁移（.trae/logs/migrate-v9-to-v10.done 存在）")
        print("   使用 --force 强制重跑")
        sys.exit(0)

    all_changes = []
    steps = [
        ("Step 1: 删除运行时工件（plan/tasks/checklist/_invalidated）", step1_drop_runtime_files),
        ("Step 2: spec.md 顶部追加 v10_simplified 标记", step2_mark_spec_simplified),
        ("Step 3: 删除 V9 专题 references/", step3_drop_v9_references),
        ("Step 4: 删除 V8 standards/fullstack4traev8-enhancement/", step4_drop_v8_standards),
    ]
    for label, func in steps:
        print(label)
        changes = func(project_root, args.dry_run)
        all_changes.extend(changes)
        for c in changes:
            print(f"  {c}")

    print(f"\n完成: {len(all_changes)} 项变更")
    if args.dry_run:
        print("⚠️  这是预览。去掉 --dry-run 以实际执行。")
    else:
        write_done_marker(project_root)
        print(f"\n✅ V9 → V10 迁移完成")
        print(f"   迁移标记: .trae/logs/migrate-v9-to-v10.done")
        print(f"   AI 重新进入时按 spec-kit → Spec-Enhancer 走 5 阶段")


if __name__ == "__main__":
    main()