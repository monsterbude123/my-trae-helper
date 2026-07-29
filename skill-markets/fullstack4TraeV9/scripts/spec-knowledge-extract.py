"""
Spec 知识提取 — 归档前将 spec 关键知识提取为项目级知识库文件。

用法:
  python scripts/spec-knowledge-extract.py --feature <feature-name> --project-root <路径>
  python scripts/spec-knowledge-extract.py --feature user-auth --project-root . --dry-run

提取内容（按 V8 多文件拆分模式，防单文件膨胀）:
  - API Endpoints    → docs/api-endpoints/{feature}.md
  - Domain Models    → docs/domain-models/{feature}.md
  - Events           → docs/events/{feature}.md
  - INDEX.md         → 将 feature 从 Active 移到 Archived

每个 feature 独立一文件，agent 按需读取，避免遍历 archive/。
确定性执行: 基于文件系统读取合同文件 → 结构化提取 → 写入独立文件。零 LLM 依赖。
"""

import argparse
import re
import sys
from pathlib import Path
from datetime import datetime


# ─── 提取器 ────────────────────────────────────────

def extract_api_endpoints(feature_dir: Path) -> list[dict]:
    """从 contracts/api-contracts.md 提取 API 端点。"""
    api_file = feature_dir / "contracts" / "api-contracts.md"
    if not api_file.exists():
        return []

    text = api_file.read_text(encoding="utf-8")
    endpoints = []

    method_pattern = re.compile(
        r'^[`\*]*(GET|POST|PUT|PATCH|DELETE|HEAD|OPTIONS)\s+(/\S+)',
        re.MULTILINE
    )

    current_method = None
    current_path = None
    current_desc = ""

    for line in text.split('\n'):
        m = method_pattern.match(line.strip().rstrip('`*'))
        if m:
            if current_method and current_path:
                endpoints.append({
                    "method": current_method,
                    "path": current_path,
                    "description": current_desc.strip() or "(no description)"
                })
            current_method = m.group(1)
            current_path = m.group(2)
            current_desc = ""
        elif current_path and line.strip().startswith(('- ', '* ')):
            current_desc += line.strip()[2:] + " "

    if current_method and current_path:
        endpoints.append({
            "method": current_method,
            "path": current_path,
            "description": current_desc.strip() or "(no description)"
        })

    return endpoints


def extract_domain_models(feature_dir: Path) -> list[dict]:
    """从 contracts/domain-models.md 提取领域模型。"""
    model_file = feature_dir / "contracts" / "domain-models.md"
    if not model_file.exists():
        return []

    text = model_file.read_text(encoding="utf-8")
    models = []

    model_header = re.compile(
        r'^###\s+(?:Entity:\s*)?(\w[\w\s]*\w)',
        re.MULTILINE
    )

    for m in model_header.finditer(text):
        name = m.group(1).strip()
        lines_after = text[m.end():].split('\n')
        description = ""
        fields = []
        in_fields = False

        for la in lines_after[:30]:
            ls = la.strip()
            if not ls:
                if in_fields:
                    break
                continue
            if ls.startswith('#') and '##' in ls:
                break
            if ls.startswith('|') and '字段' in ls:
                in_fields = True
                continue
            if ls.startswith('|---') or ls.startswith('|:-'):
                continue
            if in_fields and ls.startswith('|'):
                parts = [p.strip() for p in ls.split('|') if p.strip()]
                if len(parts) >= 2:
                    fields.append({"name": parts[0], "type": parts[1]})
                continue
            if not description and ls and not ls.startswith('|') and not ls.startswith('#'):
                description = ls

        models.append({
            "name": name,
            "description": description,
            "fields": fields
        })

    return models


def extract_events(feature_dir: Path) -> list[dict]:
    """从 contracts/events.md 提取事件。"""
    events_file = feature_dir / "contracts" / "events.md"
    if not events_file.exists():
        return []

    text = events_file.read_text(encoding="utf-8")
    events = []

    event_header = re.compile(
        r'(?:^###\s+|^[-*]\s+\*\*)(\w[\w.]*\w)\*\*?',
        re.MULTILINE
    )

    for m in event_header.finditer(text):
        name = m.group(1).strip()
        next_lines = text[m.end():].split('\n')

        payload = ""
        description = ""
        emit_by = ""

        for nl in next_lines[:20]:
            strip = nl.strip()
            if strip.startswith('#') and '##' in strip:
                break
            if 'payload' in strip.lower() or '字段' in strip.lower():
                payload += strip + " "
            elif 'emit' in strip.lower() or '触发' in strip.lower() or '由' in strip.lower():
                emit_by = strip
            elif not description and strip and not strip.startswith('#') and not strip.startswith('-') and not strip.startswith('|'):
                description = strip

        events.append({
            "name": name,
            "description": description,
            "payload": payload.strip(),
            "emitted_by": emit_by
        })

    return events


# ─── 文件生成器（一个 feature 一个文件）───────────

def write_endpoints_file(endpoints: list[dict], feature_name: str, target_dir: Path) -> str:
    """写入 docs/api-endpoints/{feature}.md。"""
    if not endpoints:
        return "跳过（无数据）"

    file_path = target_dir / f"{feature_name}.md"
    content = f"# {feature_name} — API Endpoints\n\n"
    content += "| Method | Path | Description |\n"
    content += "|--------|------|-------------|\n"
    for ep in endpoints:
        content += f"| {ep['method']} | `{ep['path']}` | {ep['description']} |\n"

    target_dir.mkdir(parents=True, exist_ok=True)
    file_path.write_text(content, encoding="utf-8")
    return f"api-endpoints/{feature_name}.md ({len(endpoints)} 端点)"


def write_models_file(models: list[dict], feature_name: str, target_dir: Path) -> str:
    """写入 docs/domain-models/{feature}.md。"""
    if not models:
        return "跳过（无数据）"

    file_path = target_dir / f"{feature_name}.md"
    content = f"# {feature_name} — Domain Models\n\n"
    for model in models:
        content += f"### {model['name']}\n"
        if model['description']:
            content += f"{model['description']}\n\n"
        if model['fields']:
            content += "| 字段 | 类型 |\n|------|------|\n"
            for f in model['fields']:
                content += f"| {f['name']} | {f['type']} |\n"
        content += "\n"

    target_dir.mkdir(parents=True, exist_ok=True)
    file_path.write_text(content, encoding="utf-8")
    return f"domain-models/{feature_name}.md ({len(models)} 模型)"


def write_events_file(events: list[dict], feature_name: str, target_dir: Path) -> str:
    """写入 docs/events/{feature}.md。"""
    if not events:
        return "跳过（无数据）"

    file_path = target_dir / f"{feature_name}.md"
    content = f"# {feature_name} — Events\n\n"
    content += "| Event | Description | Emitted By |\n"
    content += "|-------|-------------|------------|\n"
    for ev in events:
        desc = ev['description'] or ev['payload'] or '-'
        emit = ev['emitted_by'] or '-'
        content += f"| `{ev['name']}` | {desc} | {emit} |\n"

    target_dir.mkdir(parents=True, exist_ok=True)
    file_path.write_text(content, encoding="utf-8")
    return f"events/{feature_name}.md ({len(events)} 事件)"


# ─── INDEX.md 更新 ─────────────────────────────────

def update_index(project_root: Path, feature_name: str, dry_run: bool = False) -> str:
    """将 feature 从 Active Specs 移到 Archived Specs。"""
    index_path = project_root / "docs" / "INDEX.md"
    if not index_path.exists():
        return "SKIP: docs/INDEX.md 不存在"

    content = index_path.read_text(encoding="utf-8")
    today = datetime.now().strftime("%Y-%m-%d")

    feature_pattern = re.compile(
        rf'^\|\s*.*?\|\s*{re.escape(feature_name)}/\s*\|.*$',
        re.MULTILINE
    )

    match = feature_pattern.search(content)
    if not match:
        if f"| {feature_name}/" in content and "## Archived" in content:
            return "SKIP: 已在 Archived Specs 中"
        return f"WARN: INDEX.md 中未找到 {feature_name}"

    active_line = match.group(0)

    if dry_run:
        return f"MOVE: {feature_name} → Archived ({today})"

    new_archived_line = active_line.strip().rstrip('|') + f" | {today} |"
    new_content = content.replace(active_line, "")

    archived_header = "## Archived Specs"
    if archived_header in new_content:
        archived_pos = new_content.find(archived_header) + len(archived_header)
        table_section = new_content[archived_pos:]
        next_section = re.search(r'\n## ', table_section)
        insert_at = archived_pos + (next_section.start() if next_section else len(table_section))
        new_content = (
            new_content[:insert_at].rstrip() + "\n" +
            new_archived_line + "\n" +
            new_content[insert_at:].lstrip()
        )
    else:
        new_content += (
            f"\n\n## Archived Specs\n\n"
            f"| Feature | Directory | Archived |\n"
            f"|---------|-----------|----------|\n"
            f"{new_archived_line}\n"
        )

    index_path.write_text(new_content, encoding="utf-8")
    return f"MOVE: {feature_name} → Archived ({today})"


# ─── 主流程 ─────────────────────────────────────────

def extract(feature_name: str, project_root: Path, dry_run: bool = False) -> dict:
    """从指定 feature 提取知识，写入项目级知识库目录。"""
    project_root = project_root.resolve()
    feature_dir = project_root / "docs" / "specs" / feature_name
    docs_dir = project_root / "docs"

    if not feature_dir.exists():
        return {"error": f"Spec 目录不存在: {feature_dir}"}

    report = {
        "feature": feature_name,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "dry_run": dry_run,
        "extracted": {},
        "written": {},
    }

    # 提取
    endpoints = extract_api_endpoints(feature_dir)
    models = extract_domain_models(feature_dir)
    events = extract_events(feature_dir)

    report["extracted"] = {
        "api_endpoints": len(endpoints),
        "domain_models": len(models),
        "events": len(events),
    }

    if dry_run:
        report["written"] = {
            f"api-endpoints/{feature_name}.md": f"将写入 {len(endpoints)} 端点",
            f"domain-models/{feature_name}.md": f"将写入 {len(models)} 模型",
            f"events/{feature_name}.md": f"将写入 {len(events)} 事件",
            "INDEX.md": update_index(project_root, feature_name, dry_run=True),
        }
    else:
        report["written"]["api-endpoints"] = write_endpoints_file(
            endpoints, feature_name, docs_dir / "api-endpoints"
        )
        report["written"]["domain-models"] = write_models_file(
            models, feature_name, docs_dir / "domain-models"
        )
        report["written"]["events"] = write_events_file(
            events, feature_name, docs_dir / "events"
        )
        report["written"]["INDEX.md"] = update_index(project_root, feature_name)

    # 日志
    log_dir = project_root / ".trae" / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / f"knowledge-extract-{feature_name}-{datetime.now().strftime('%Y%m%d-%H%M%S')}.log"
    log_lines = [f"[{report['timestamp']}] Knowledge Extract: {feature_name} {'(DRY-RUN)' if dry_run else ''}"]
    log_lines.append(f"  提取: API={report['extracted']['api_endpoints']} Models={report['extracted']['domain_models']} Events={report['extracted']['events']}")
    for k, v in report["written"].items():
        log_lines.append(f"  写入: {k}: {v}")
    if not dry_run:
        log_file.write_text("\n".join(log_lines), encoding="utf-8")
    report["log_file"] = str(log_file)

    return report


# ─── CLI ────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Spec 知识提取 — 归档前合并到项目级知识库")
    parser.add_argument("--feature", required=True, help="Feature 名称（docs/specs/{feature}/）")
    parser.add_argument("--project-root", required=True, help="项目根目录")
    parser.add_argument("--dry-run", action="store_true", help="仅预览")
    args = parser.parse_args()

    report = extract(args.feature, Path(args.project_root), dry_run=args.dry_run)

    if "error" in report:
        print(f"❌ {report['error']}")
        sys.exit(1)

    mode = "(DRY-RUN)" if args.dry_run else ""
    print(f"Spec 知识提取 {mode}")
    print(f"Feature: {report['feature']}")
    print(f"提取: API={report['extracted']['api_endpoints']} | "
          f"Models={report['extracted']['domain_models']} | "
          f"Events={report['extracted']['events']}")
    print()

    for file, result in report["written"].items():
        print(f"  {file}: {result}")

    if not args.dry_run:
        print(f"\n日志: {report.get('log_file', 'N/A')}")


if __name__ == "__main__":
    main()
