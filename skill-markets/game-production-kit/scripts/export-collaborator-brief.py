"""外部合作需求导出 — 读 asset-manifest + story-design → 渲染为外行可读的 Markdown"""
import sys, re
from pathlib import Path
from datetime import date

def extract_asset_entries(manifest_path: Path, category: str):
    """从 asset-manifest.md 提取指定类别的素材条目"""
    content = manifest_path.read_text(encoding='utf-8')
    entries = []
    current_name = None

    for line in content.split('\n'):
        entry_match = re.match(r'^(assets/[\w/]+\.\w+):$', line)
        if entry_match:
            current_name = entry_match.group(1)
            entries.append({'name': current_name, 'fields': {}})
        elif current_name and ':' in line:
            key_match = re.match(r'\s+(\w+):\s*"([^"]*)"', line)
            if key_match:
                entries[-1]['fields'][key_match.group(1)] = key_match.group(2)

    if category != 'all':
        entries = [e for e in entries if e['fields'].get('category') == category]
    return entries

def export_composer_brief(game_key: str):
    base = Path(game_key)
    manifest = base / 'asset-manifest.md'
    if not manifest.exists():
        return "asset-manifest.md 不存在，先完成 Phase 2"
    entries = extract_asset_entries(manifest, 'bgm')
    lines = [f"# BGM 需求 — {game_key}", ""]
    lines.append("| # | 曲名 | 时长 | 情绪 | 使用场景 |")
    lines.append("|---|------|------|------|---------|")
    for i, e in enumerate(entries, 1):
        name = Path(e['name']).stem
        mood = e['fields'].get('mood', '—')
        desc = e['fields'].get('description', '—')
        lines.append(f"| {i} | {name} | — | {mood} | {desc} |")
    lines.append("")
    lines.append(f"**交付格式**: 48kHz WAV + 320kbps MP3")
    lines.append(f"**导出日期**: {date.today()}")
    output = base / f"BGM-{game_key}-brief.md"
    output.write_text('\n'.join(lines), encoding='utf-8')
    return f"✅ 已导出: {output}"

def export_artist_brief(game_key: str):
    base = Path(game_key)
    manifest = base / 'asset-manifest.md'
    if not manifest.exists():
        return "asset-manifest.md 不存在，先完成 Phase 2"
    entries = extract_asset_entries(manifest, 'sprite')
    lines = [f"# 美术需求 — {game_key}", ""]
    lines.append("| # | 角色/素材 | 数量 | 风格 | 格式 | 备注 |")
    lines.append("|---|----------|------|------|------|------|")
    chars = {}
    for e in entries:
        name = Path(e['name']).stem
        char = name.split('_')[1] if '_' in name else name
        chars.setdefault(char, []).append(name)
    for i, (char, sprites) in enumerate(chars.items(), 1):
        lines.append(
            f"| {i} | {char} | {len(sprites)}张 | — | PNG | "
            f"{', '.join(sprites[:3])}{'...' if len(sprites)>3 else ''} |"
        )
    lines.append("")
    lines.append(f"**导出日期**: {date.today()}")
    output = base / f"Art-{game_key}-brief.md"
    output.write_text('\n'.join(lines), encoding='utf-8')
    return f"✅ 已导出: {output}"

def main():
    if len(sys.argv) < 2:
        print("用法: python export-collaborator-brief.py {game_key} [--composer|--artist|--voice|--all]")
        return
    game_key = sys.argv[1]
    flag = sys.argv[2] if len(sys.argv) > 2 else '--all'
    results = []
    if flag in ('--composer', '--all'):
        results.append(export_composer_brief(game_key))
    if flag in ('--artist', '--all'):
        results.append(export_artist_brief(game_key))
    print('\n'.join(results))

if __name__ == '__main__':
    main()
