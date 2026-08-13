#!/usr/bin/env python3
"""
V11 spec-knowledge-extract.py — 知识沉淀（Stage 5 Accept 必走）

Usage:
    python spec-knowledge-extract.py --change-id <id> [--type api|domain|events]

沉淀:
  - api       → docs/api-endpoints/{endpoint}.md
  - domain    → docs/domain-models/{entity}.md
  - events    → docs/events/{event-name}.md

Exit codes:
    0 = PASS
    1 = FAIL
"""
import sys
import argparse
import pathlib
import json
import re
from datetime import datetime, timezone


def extract_api(change_dir: pathlib.Path, project_root: pathlib.Path) -> list:
    """从 api-contracts.md 提取 API 端点"""
    api_file = change_dir / "contracts/api-contracts.md"
    if not api_file.exists():
        return []

    content = api_file.read_text(encoding="utf-8")
    endpoints = []

    # 提取 - path: /api/v1/... + method
    for m in re.finditer(r"path:\s*([/\w\-]+).*?method:\s*(\w+)", content, re.DOTALL | re.IGNORECASE):
        path = m.group(1)
        method = m.group(2)
        endpoints.append({"path": path, "method": method})

    # 写入 docs/api-endpoints/
    api_dir = project_root / "docs/api-endpoints"
    api_dir.mkdir(parents=True, exist_ok=True)

    extracted = []
    for ep in endpoints:
        slug = ep["path"].replace("/", "_").strip("_") or "root"
        out_path = api_dir / f"{ep['method'].lower()}_{slug}.md"
        out_path.write_text(
            f"# API: {ep['method']} {ep['path']}\n\n> Extracted from {api_file}\n",
            encoding="utf-8",
        )
        extracted.append(str(out_path.relative_to(project_root)))

    return extracted


def extract_domain(change_dir: pathlib.Path, project_root: pathlib.Path) -> list:
    """从 domain-models.md 提取领域实体"""
    domain_file = change_dir / "contracts/domain-models.md"
    if not domain_file.exists():
        return []

    content = domain_file.read_text(encoding="utf-8")

    # 提取 Entity {Name} 标题
    entities = []
    for m in re.finditer(r"^(?:###\s+Entity\s+\d+:\s+|##\s+\d+\.\s+)(\w+)", content, re.MULTILINE):
        entities.append(m.group(1))

    domain_dir = project_root / "docs/domain-models"
    domain_dir.mkdir(parents=True, exist_ok=True)

    extracted = []
    for entity in entities:
        out_path = domain_dir / f"{entity}.md"
        out_path.write_text(
            f"# Domain: {entity}\n\n> Extracted from {domain_file}\n",
            encoding="utf-8",
        )
        extracted.append(str(out_path.relative_to(project_root)))

    return extracted


def extract_events(change_dir: pathlib.Path, project_root: pathlib.Path) -> list:
    """从 events.md 提取事件"""
    events_file = change_dir / "contracts/events.md"
    if not events_file.exists():
        return []

    content = events_file.read_text(encoding="utf-8")

    events = []
    for m in re.finditer(r"^(?:###\s+Event\s+\d+:\s+|##\s+\d+\.\s+)(\w+)", content, re.MULTILINE):
        events.append(m.group(1))

    events_dir = project_root / "docs/events"
    events_dir.mkdir(parents=True, exist_ok=True)

    extracted = []
    for event in events:
        out_path = events_dir / f"{event}.md"
        out_path.write_text(
            f"# Event: {event}\n\n> Extracted from {events_file}\n",
            encoding="utf-8",
        )
        extracted.append(str(out_path.relative_to(project_root)))

    return extracted


def main():
    parser = argparse.ArgumentParser(description="V11 spec-knowledge-extract 知识沉淀")
    parser.add_argument("--change-id", required=True, help="change ID")
    parser.add_argument("--type", default="all", choices=["api", "domain", "events", "all"], help="沉淀类型")
    parser.add_argument("--project-root", default=".", help="项目根路径")
    parser.add_argument("--json", action="store_true", help="JSON 输出")
    args = parser.parse_args()

    project_root = pathlib.Path(args.project_root).resolve()
    change_dir = project_root / f"docs/specs/changes/{args.change_id}"

    if not change_dir.exists():
        result = {"status": "FAIL", "message": f"change 不存在: {change_dir}"}
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print(f"❌ {result['message']}")
        return 1

    extracted = {"api": [], "domain": [], "events": []}

    if args.type in ("api", "all"):
        extracted["api"] = extract_api(change_dir, project_root)
    if args.type in ("domain", "all"):
        extracted["domain"] = extract_domain(change_dir, project_root)
    if args.type in ("events", "all"):
        extracted["events"] = extract_events(change_dir, project_root)

    total = sum(len(v) for v in extracted.values())

    result = {
        "status": "PASS" if total > 0 else "FAIL",
        "change_id": args.change_id,
        "extracted": extracted,
        "total": total,
    }

    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        icon = "✅" if total > 0 else "❌"
        print(f"{icon} {result['status']} — 沉淀 {total} 项")
        for k, v in extracted.items():
            print(f"   {k}: {len(v)} 项")
            for f in v:
                print(f"     - {f}")

    return 0 if total > 0 else 1


if __name__ == "__main__":
    sys.exit(main())