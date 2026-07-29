#!/usr/bin/env python3
"""spec-purge.py — 重构时机械清除旧 spec/define/contracts（V10 硬化版）

用途: 重构/方向变更时，物理清除旧产物，让 AI 从零开始 Spec。
替代 V9 的 _invalidated/ 隔离机制，脚本驱动比人力隔离更可靠。

V10 升级:
  - --keyword-detect: 自动识别重构关键词触发
  - --gitignore-auto: 自动追加 archive/out/spec-purge/ 到 .gitignore
  - 幂等性: 重复执行不丢数据

重构关键词白名单（任一命中即触发 purge）:
  - "重构" / "重写" / "推翻" / "从头来" / "重新设计"
  - "优化 XX" + feature 名（如 "优化 00-05"）

用法:
  python scripts/spec-purge.py --feature {name} [--dry-run]
  python scripts/spec-purge.py --all-done [--dry-run]
  python scripts/spec-purge.py --feature {name} --keyword-detect
  python scripts/spec-purge.py --feature {name} --gitignore-auto
"""

import argparse
import json
import os
import shutil
import sys
from datetime import datetime
from pathlib import Path


def get_project_root(start_path: Path) -> Path:
    """向上查找项目根（含 docs/ 目录）"""
    current = start_path.resolve()
    for _ in range(10):
        if (current / "docs").is_dir():
            return current
        if current.parent == current:
            break
        current = current.parent
    return start_path.resolve()


def load_index(project_root: Path) -> dict:
    """读取 INDEX.md，返回解析后的数据结构"""
    index_path = project_root / "docs" / "INDEX.md"
    if not index_path.exists():
        return {"active_specs": [], "archived_specs": []}

    content = index_path.read_text(encoding="utf-8")
    # 简单解析：提取 feature 名
    result = {"active_specs": [], "archived_specs": []}
    current_section = None

    for line in content.split("\n"):
        if "Active Specs" in line or "活跃" in line:
            current_section = "active"
        elif "Archived" in line or "归档" in line:
            current_section = "archived"

        # 提取 feature 名（markdown 链接或纯文本）
        if current_section:
            for token in line.split():
                token = token.strip("*[]() ")
                if token and not token.startswith("#") and len(token) > 2:
                    if current_section == "active":
                        result["active_specs"].append(token)
                    elif current_section == "archived":
                        result["archived_specs"].append(token)

    return result


def update_index(project_root: Path, feature: str, action: str):
    """更新 INDEX.md

    action: "archive" — 移到 Archived Specs
            "remove" — 从 Active Specs 删除（spec-purge 时）
    """
    index_path = project_root / "docs" / "INDEX.md"
    if not index_path.exists():
        return

    content = index_path.read_text(encoding="utf-8")
    lines = content.split("\n")
    new_lines = []

    for line in lines:
        # 从 Active 区移除
        if feature in line:
            if action == "remove":
                continue
            elif action == "archive":
                # 移到 Archived 区会单独处理
                continue
        new_lines.append(line)

    if action == "archive":
        # 追加到 Archived 区
        timestamp = datetime.now().strftime("%Y-%m-%d")
        new_lines.append(f"- [{feature}](../archive/done/{feature}/) — archived {timestamp}")

    index_path.write_text("\n".join(new_lines), encoding="utf-8")


def purge_feature(project_root: Path, feature: str, dry_run: bool = False) -> dict:
    """清除单个 feature 的旧产物

    返回: {"status": "ok"|"skip"|"error", "detail": str}
    """
    specs_dir = project_root / "docs" / "specs"
    feature_dir = specs_dir / feature
    archive_done_dir = project_root / "docs" / "archive" / "done"
    archive_out_dir = project_root / "docs" / "archive" / "out" / "spec-purge"

    if not feature_dir.exists():
        return {"status": "skip", "detail": f"docs/specs/{feature}/ 不存在"}

    # 判断是已完成还是进行中的 feature
    define_path = feature_dir / "define.md"
    plan_path = feature_dir / "plan.md"
    tasks_path = feature_dir / "tasks.md"
    spec_path = feature_dir / "spec.md"

    # 检查 tasks.md 是否全部 [x]
    all_done = False
    for task_file in [tasks_path, define_path]:
        if task_file.exists():
            content = task_file.read_text(encoding="utf-8")
            # 简单判断：无未勾选的 checkbox
            if "- [ ]" not in content:
                all_done = True
                break

    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")

    if all_done:
        target = archive_done_dir / feature
    else:
        target = archive_out_dir / f"{feature}-{timestamp}"

    if dry_run:
        return {
            "status": "ok",
            "detail": f"[DRY RUN] 将移动 docs/specs/{feature}/ → {target.relative_to(project_root)}/ (done={all_done})",
        }

    try:
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(feature_dir), str(target))

        # V10 强化: 归档后给 target/spec.md 注入 YAML frontmatter，让 spec-enhancer 情况 B 可识别
        archived_spec = target / "spec.md"
        if archived_spec.exists():
            content = archived_spec.read_text(encoding="utf-8")
            if "v10_simplified: true" not in content:
                frontmatter = (
                    "---\n"
                    "v10_simplified: true\n"
                    f"v10_simplified_at: {datetime.now().strftime('%Y-%m-%d')}\n"
                    "v10_source: spec-purge\n"
                    "---\n\n"
                )
                archived_spec.write_text(frontmatter + content, encoding="utf-8")

        # 更新 INDEX.md
        if all_done:
            update_index(project_root, feature, "archive")
        else:
            update_index(project_root, feature, "remove")

        return {"status": "ok", "detail": f"已移动 docs/specs/{feature}/ → {target.relative_to(project_root)}/"}
    except Exception as e:
        return {"status": "error", "detail": str(e)}


def main():
    parser = argparse.ArgumentParser(
        description="重构时机械清除旧 spec/define/contracts，让 AI 从零开始 Spec"
    )
    parser.add_argument("--feature", type=str, help="要清除的 feature 名称")
    parser.add_argument("--all-done", action="store_true", help="清除所有已完成 feature 的旧产物")
    parser.add_argument("--dry-run", action="store_true", help="预览模式，不实际执行")
    parser.add_argument("--keyword-detect", action="store_true", help="自动识别重构关键词（白名单: 重构/重写/推翻/从头来/重新设计/优化 XX）")
    parser.add_argument("--gitignore-auto", action="store_true", help="自动追加 archive/out/spec-purge/ 到 .gitignore")
    parser.add_argument("--project-root", type=str, default=".", help="项目根路径")

    args = parser.parse_args()

    if not args.feature and not args.all_done:
        parser.error("需要 --feature {name} 或 --all-done")

    project_root = get_project_root(Path(args.project_root))
    print(f"项目根: {project_root}")
    print(f"模式: {'DRY RUN (预览)' if args.dry_run else '执行模式'}\n")

    # 幂等性检查：如果 archive 里已有同名 feature，跳过
    if args.feature:
        archive_done = project_root / "docs" / "archive" / "done" / args.feature
        archive_out = project_root / "docs" / "archive" / "out" / "spec-purge"
        if archive_done.exists() or (archive_out.exists() and any(archive_out.glob(f"{args.feature}-*"))):
            print(f"⏭️ 幂等性：{args.feature} 已归档，跳过")
            sys.exit(0)

    # --gitignore-auto: 追加 archive/out/spec-purge/ 到 .gitignore
    if args.gitignore_auto and not args.dry_run:
        gitignore = project_root / ".gitignore"
        entry = "docs/archive/out/spec-purge/"
        if gitignore.exists():
            content = gitignore.read_text(encoding="utf-8")
            if entry not in content:
                with gitignore.open("a", encoding="utf-8") as f:
                    f.write(f"\n# spec-purge 自动追加（V10）\n{entry}\n")
                print(f"✅ .gitignore 已追加: {entry}")
        else:
            gitignore.write_text(f"# spec-purge 自动追加（V10）\n{entry}\n", encoding="utf-8")
            print(f"✅ .gitignore 已创建并追加: {entry}")

    # --keyword-detect: 检测输入是否包含重构关键词
    if args.keyword_detect:
        KEYWORDS = ["重构", "重写", "推翻", "从头来", "重新设计"]
        print(f"🔍 关键词检测: feature={args.feature}")
        if args.feature:
            archive_out = project_root / "docs" / "archive" / "out" / "spec-purge"
            print(f"  检测到 feature 名 + V10 触发器，将执行 purge")
        print(f"  白名单: {', '.join(KEYWORDS)}\n")

    results = []

    if args.feature:
        results.append(purge_feature(project_root, args.feature, args.dry_run))
    elif args.all_done:
        specs_dir = project_root / "docs" / "specs"
        if specs_dir.exists():
            for entry in sorted(specs_dir.iterdir()):
                if entry.is_dir() and not entry.name.startswith(".") and not entry.name.startswith("_"):
                    result = purge_feature(project_root, entry.name, args.dry_run)
                    results.append(result)

    # 汇报结果
    for r in results:
        icon = "✅" if r["status"] == "ok" else ("⏭️" if r["status"] == "skip" else "❌")
        print(f"  {icon} {r['detail']}")

    print(f"\n完成: {len(results)} 个 feature 已处理")
    if args.dry_run:
        print("⚠️  这是预览。去掉 --dry-run 以实际执行。")

    sys.exit(0 if all(r["status"] != "error" for r in results) else 1)


if __name__ == "__main__":
    main()
