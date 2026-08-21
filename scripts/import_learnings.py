#!/usr/bin/env python3
"""
scripts/import_learnings.py — 把 JSON 数据按 self-improving-agent LEARNINGS.md 模板格式追加写入目标文件

设计目的:
  跨会话蒸馏的经验(LRN 条目)持久化到全局 LEARNINGS.md,格式与 self-improving-agent
  skill assets/LEARNINGS.md 模板一致。脚本化导入避免手工复制粘贴格式漂移。

用法:
  python scripts/import_learnings.py --data <json> --target <md> [--dry-run]
  python scripts/import_learnings.py  # 默认读 references/learnings-2026-08-21.json
                                       # 默认写 example/ai-short-studio-monster/.learnings/LEARNINGS.md

数据格式(JSON 数组,每条):
  {
    "id": "LRN-YYYYMMDD-NNN",
    "category": "best_practice|correction|knowledge_gap|...",
    "priority": "low|medium|high|critical",
    "summary": "一句话摘要",
    "details": "详细描述",
    "trigger": "触发场景",
    "action": "建议行动",
    "related_files": ["file1", "file2"],
    "tags": ["tag1", "tag2"],
    "promote_to": "Promote 目标"
  }

退出码:
  0 = PASS(已追加或 dry-run 完成)
  1 = ERROR(数据格式错 / 目标文件不可写)
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from datetime import datetime, timezone, timedelta

# Windows cp1252 兜底(AGENTS.md §4.1.3)
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_DATA = REPO_ROOT / "references" / "learnings-2026-08-21.json"
DEFAULT_TARGET = (
    REPO_ROOT / "example" / "ai-short-studio-monster" / ".learnings" / "LEARNINGS.md"
)


def now_iso() -> str:
    """ISO-8601 +08:00(用户本地时区,Asia/Shanghai)"""
    tz = timezone(timedelta(hours=8))
    return datetime.now(tz).isoformat(timespec="seconds")


def render_entry(entry: dict) -> str:
    """渲染单条 LRN 为 markdown 段"""
    lines = []
    lines.append(f"## [{entry['id']}] {entry['category']}")
    lines.append("")
    lines.append(f"**Logged**: {now_iso()}")
    lines.append(f"**Priority**: {entry['priority']}")
    lines.append("**Status**: pending")
    lines.append(f"**Area**: {entry.get('area', 'workflow')}")
    lines.append("")
    lines.append("### Summary")
    lines.append(entry["summary"])
    lines.append("")
    lines.append("### Details")
    lines.append(entry["details"])
    lines.append("")
    if "trigger" in entry:
        lines.append("### Trigger")
        lines.append(entry["trigger"])
        lines.append("")
    if "action" in entry:
        lines.append("### Suggested Action")
        lines.append(entry["action"])
        lines.append("")
    lines.append("### Metadata")
    lines.append(f"- Source: conversation")
    if entry.get("related_files"):
        rel = ", ".join(entry["related_files"])
        lines.append(f"- Related Files: {rel}")
    if entry.get("tags"):
        lines.append(f"- Tags: {', '.join(entry['tags'])}")
    if entry.get("promote_to"):
        lines.append(f"- Promote To: {entry['promote_to']}")
    lines.append("")
    lines.append("---")
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="导入 LRN 条目到全局 LEARNINGS.md")
    parser.add_argument("--data", type=Path, default=DEFAULT_DATA,
                        help=f"JSON 数据文件 (默认: {DEFAULT_DATA.relative_to(REPO_ROOT)})")
    parser.add_argument("--target", type=Path, default=DEFAULT_TARGET,
                        help=f"目标 LEARNINGS.md (默认: {DEFAULT_TARGET.relative_to(REPO_ROOT)})")
    parser.add_argument("--dry-run", action="store_true",
                        help="只打印不写盘")
    args = parser.parse_args()

    if not args.data.exists():
        print(f"❌ 数据文件不存在: {args.data}", file=sys.stderr)
        return 1

    try:
        entries = json.loads(args.data.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        print(f"❌ JSON 解析失败: {e}", file=sys.stderr)
        return 1

    if not isinstance(entries, list):
        print(f"❌ 数据格式错: 期望 list, 实际 {type(entries).__name__}", file=sys.stderr)
        return 1

    # 必填字段校验
    required = {"id", "category", "priority", "summary", "details"}
    for i, entry in enumerate(entries):
        missing = required - set(entry.keys())
        if missing:
            print(f"❌ 第 {i+1} 条缺字段 {missing}: {entry.get('id', '?')}", file=sys.stderr)
            return 1

    rendered = "\n".join(render_entry(e) for e in entries)

    def _relpath(p: Path) -> str:
        try:
            return str(p.relative_to(REPO_ROOT))
        except ValueError:
            return str(p)

    print(f"📦 数据源: {_relpath(args.data)} ({len(entries)} 条)")
    print(f"📝 目标: {_relpath(args.target)}")
    print()

    if args.dry_run:
        print("🔍 DRY RUN — 不会写盘")
        print("=" * 60)
        print(rendered)
        print("=" * 60)
        return 0

    if not args.target.parent.exists():
        print(f"⚠️  目标目录不存在: {args.target.parent}")
        print(f"   自动创建: {args.target.parent}")
        args.target.parent.mkdir(parents=True, exist_ok=True)

    # 写盘(追加,头部留空行)
    header_check = ""
    if args.target.exists():
        existing = args.target.read_text(encoding="utf-8")
        if "## [" in existing and "---" in existing:
            # 已存在 LEARNINGS, 追加到末尾
            sep = "" if existing.endswith("\n") else "\n"
            new_content = existing + sep + "\n" + rendered
            header_check = "append"
        else:
            # 空文件 / 只有标题, 加入分隔后追加
            sep = "" if existing.endswith("\n") else "\n\n"
            new_content = existing + sep + rendered
            header_check = "append-after-header"
    else:
        # 新文件 — 加顶部标题
        header = "# Learnings\n\n跨会话蒸馏的经验/反例/知识缺口(本批为 2026-08-21 my-trae-helper 工作流)。\n\n---\n\n"
        new_content = header + rendered
        header_check = "create-new"

    args.target.write_text(new_content, encoding="utf-8")
    print(f"✅ 写入成功({header_check}) — {len(entries)} 条 LRN 已追加")
    print(f"   路径: {args.target}")
    return 0


if __name__ == "__main__":
    sys.exit(main())