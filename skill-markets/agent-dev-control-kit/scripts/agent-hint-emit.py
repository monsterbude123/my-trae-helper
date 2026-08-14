#!/usr/bin/env python3
"""agent-hint-emit.py — 聚合 logs/agent-hints.jsonl,人类可读 + 按 trap 分组

直接对应 ai-short-studio-monster 的 `.learnings/ERRORS.md`:
  - 每个 hint = 一条结构化记录(what / where / minimal_fix / next_skill)
  - agent 拿到聚合输出,按 trap_id 分组决定下一步

用法:
    python scripts/agent-hint-emit.py                # 打印最近 hints
    python scripts/agent-hint-emit.py --group-by trap  # 按 trap 分组
    python scripts/agent-hint-emit.py --reset       # 清空 hints 日志

特性:
  - 标准库 + json + argparse,无外部依赖
  - 永远 exit 0(信息性 CLI,不阻断)
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parents[1]
HINT_LOG = SKILL_ROOT / "logs" / "agent-hints.jsonl"


def load_hints() -> list[dict]:
    if not HINT_LOG.is_file():
        return []
    out: list[dict] = []
    for line in HINT_LOG.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            out.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return out


def render_per_hint(hints: list[dict]) -> None:
    print(f"📋 Agent hints 聚合 — 共 {len(hints)} 条\n")
    for h in hints:
        print(f"🛑 {h['id']} [{h.get('severity', 'HIGH')}] {h.get('trap_id', '?')}")
        print(f"   📍 {h.get('where', '?')}")
        print(f"   💥 {h.get('what', '?')}")
        for i, fix in enumerate(h.get("minimal_fix", []), 1):
            print(f"   🛠 {i}. {fix}")
        if h.get("next_skill"):
            action = f" — {h['next_skill_action']}" if h.get("next_skill_action") else ""
            print(f"   🤖 next: Skill(name='{h['next_skill']}'){action}")
        for ref in h.get("see_also", []):
            print(f"   📚 {ref}")
        print()


def render_grouped(hints: list[dict]) -> None:
    grouped: dict[str, list[dict]] = defaultdict(list)
    for h in hints:
        grouped[h.get("trap_id", "UNKNOWN")].append(h)

    print(f"📋 Agent hints 分组 — {len(grouped)} 个 trap,共 {len(hints)} 条\n")
    for trap_id, items in sorted(grouped.items()):
        print(f"━━━ {trap_id} ({len(items)} 条) ━━━")
        for h in items:
            print(f"  • {h['id']}: {h.get('what', '?')}")
            print(f"    where: {h.get('where', '?')}")
            for fix in h.get("minimal_fix", [])[:2]:
                print(f"      - {fix}")
            if h.get("next_skill"):
                print(f"    next: Skill('{h['next_skill']}')")
        print()


def main() -> int:
    parser = argparse.ArgumentParser(
        description="聚合 logs/agent-hints.jsonl,人类可读 + 按 trap 分组",
    )
    parser.add_argument("--group-by", choices=("trap", "id"), default=None)
    parser.add_argument("--reset", action="store_true", help="清空 hints 日志")
    parser.add_argument("--json", action="store_true", help="以 JSON 输出")
    args = parser.parse_args()

    if args.reset:
        if HINT_LOG.is_file():
            HINT_LOG.unlink()
        print(f"✅ hints 日志已清空({HINT_LOG})")
        return 0

    hints = load_hints()
    if not hints:
        print("📋 当前无 hints")
        return 0

    if args.json:
        print(json.dumps(hints, ensure_ascii=False, indent=2))
    elif args.group_by == "trap":
        render_grouped(hints)
    else:
        render_per_hint(hints)
    return 0


if __name__ == "__main__":
    sys.exit(main())
