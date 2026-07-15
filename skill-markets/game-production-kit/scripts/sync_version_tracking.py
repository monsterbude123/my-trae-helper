"""
sync_version_tracking.py — 设计版本 vs 素材版本自动对比

功能:
  1. 读取 {game_key}/story-design.md → 提取当前设计版本号
  2. 读取 {game_key}/asset-manifest.md → 提取每个素材的 source_version
  3. 对比: source_version < 当前版本 → 标记 ⚠️ stale
  4. 输出 JSON Lines + Markdown 表格
  5. 自动计算影响范围（素材文件名前缀匹配到角色/场景/BGM/TTS）

用法:
  python sync_version_tracking.py [{game_key}]
  game_key 默认当前目录，也可指定子目录名（如 "my-vn-game"）
"""

import sys
import re
import json
from pathlib import Path


def extract_version(content: str) -> str:
    """从 story-design.md 头部提取版本号: 版本: v{N}"""
    m = re.search(r'版本:\s*(v\d+)', content)
    return m.group(1) if m else "v0"


def parse_version_num(version: str) -> int:
    """解析版本号为整数: v0→0, v1→1, v2→2"""
    m = re.search(r'v(\d+)', version)
    return int(m.group(1)) if m else 0


def extract_source_versions(content: str) -> dict:
    """
    从 asset-manifest.md 提取素材→source_version 映射。
    支持两种格式:
      YAML-like:  character_elise_01.png:\n  source_version: "v2"
      Markdown 表格: | name | source_version | ... |
    """
    assets = {}

    # 格式1: YAML-like 块
    # 匹配: asset_name:\n  source_version: "v{N}"
    yaml_pattern = re.compile(
        r'^([^\s:][^:]*?):\s*$\n^\s+source_version:\s*"(v\d+)"',
        re.MULTILINE,
    )
    for m in yaml_pattern.finditer(content):
        name = m.group(1).strip()
        ver = m.group(2)
        assets[name] = ver

    # 格式2: Markdown 表格
    # | asset_name | source_version | ... |
    # 找到表头行确定列位置
    lines = content.split("\n")
    in_table = False
    col_name = -1
    col_ver = -1

    for line in lines:
        stripped = line.strip()
        if stripped.startswith("|") and "source_version" in stripped.lower():
            # 表头行
            in_table = True
            cols = [c.strip().lower() for c in stripped.strip("|").split("|")]
            for i, c in enumerate(cols):
                if c == "source_version":
                    col_ver = i
                elif c in ("asset", "name", "filename", "素材", "文件名"):
                    col_name = i
            continue

        if in_table and stripped.startswith("|"):
            # 跳过分隔行
            if re.match(r'^\|[\s\-:]*\|', stripped):
                continue
            cols = [c.strip().strip('"') for c in stripped.strip("|").split("|")]
            if col_name >= 0 and col_ver >= 0 and len(cols) > max(col_name, col_ver):
                name = cols[col_name]
                ver = cols[col_ver]
                if name and ver and re.match(r'v\d+', ver):
                    assets[name] = ver

    return assets


def match_impact(asset_name: str) -> str:
    """
    根据素材文件名前缀自动匹配影响范围。
    
    命名规范:
      立绘: {角色}_*.png      → 立绘: {角色}
      背景: bg_{场景}_*.png   → 背景: {场景}
      BGM:  bgm_{名称}.mp3    → BGM: {名称}
      TTS:  voice_{场景}.wav  → TTS: {场景}
      UI:   ui_{元素}.png     → UI: {元素}
      其他:                    → General
    """
    name = Path(asset_name).stem.lower()

    # 背景: bg_开头
    if name.startswith("bg_"):
        scene = name[3:].split("_")[0] if "_" in name[3:] else name[3:]
        return f"背景: {scene}"

    # BGM: bgm_开头
    if name.startswith("bgm_"):
        track = name[4:]
        return f"BGM: {track}"

    # TTS/语音: voice_开头
    if name.startswith("voice_"):
        scene = name[6:].split("_")[0] if "_" in name[6:] else name[6:]
        return f"TTS: {scene}"

    # UI: ui_开头
    if name.startswith("ui_"):
        element = name[3:]
        return f"UI: {element}"

    # 立绘/角色: {角色}_* 格式 (如 character_elise_01, elise_smile)
    # 提取第一个下划线前的部分作为角色名
    parts = name.split("_")
    if len(parts) >= 2:
        # character_elise_01 → 取 elise
        # 常见前缀过滤
        skip_prefixes = {"character", "sprite", "figure"}
        if parts[0] in skip_prefixes and len(parts) >= 2:
            return f"立绘: {parts[1]}"
        else:
            return f"立绘: {parts[0]}"

    return "General"


def extract_story_characters(content: str) -> list[str]:
    """从 story-design.md 提取角色名列表"""
    chars = re.findall(r'^- \[(\w+)\].*Want:', content, re.MULTILINE)
    return chars


def extract_story_backgrounds(content: str) -> list[str]:
    """从 story-design.md 提取场景名列表"""
    bgs = re.findall(r'^- \*\*场景\s*(\w+)\*\*', content, re.MULTILINE)
    return bgs


def extract_manifest_entries(content: str) -> list[dict]:
    """从 asset-manifest.md 提取条目为 dict 列表，用于格式校验"""
    entries = []
    yaml_pattern = re.compile(
        r'^([^\s:][^:]*?):\s*$',
        re.MULTILINE,
    )
    lines = content.split("\n")
    i = 0
    while i < len(lines):
        m = yaml_pattern.match(lines[i])
        if m:
            name = m.group(1).strip()
            entry = {"name": name}
            j = i + 1
            while j < len(lines) and lines[j].startswith("  "):
                kv = re.match(r'^\s+(\w+):\s*"?(v?\d+[^"]*)"?', lines[j])
                if kv:
                    entry[kv.group(1)] = kv.group(2).strip('"')
                j += 1
            if len(entry) > 1:
                entries.append(entry)
            i = j
        else:
            i += 1
    return entries


def main(game_key: str = "."):
    base = Path(game_key)
    if not base.is_dir():
        print(f"[ERROR] 目录不存在: {base}", file=sys.stderr)
        sys.exit(1)

    story_path = base / "story-design.md"
    manifest_path = base / "asset-manifest.md"

    if not story_path.exists():
        print(f"[ERROR] story-design.md 不存在: {story_path}", file=sys.stderr)
        sys.exit(1)
    if not manifest_path.exists():
        print(f"[ERROR] asset-manifest.md 不存在: {manifest_path}", file=sys.stderr)
        sys.exit(1)

    story_content = story_path.read_text(encoding="utf-8")
    manifest_content = manifest_path.read_text(encoding="utf-8")

    current_version_str = extract_version(story_content)
    current_version_num = parse_version_num(current_version_str)
    assets = extract_source_versions(manifest_content)

    if not assets:
        print(f"[WARN] 未从 asset-manifest.md 提取到任何素材版本信息", file=sys.stderr)
        print("\n✅ 未检测到素材版本信息，跳过对比")
        return

    # 找出 stale 素材
    stale = []
    for name, ver in assets.items():
        ver_num = parse_version_num(ver)
        if ver_num < current_version_num:
            stale.append({
                "asset": name,
                "source_version": ver,
                "current_version": current_version_str,
                "version_gap": current_version_num - ver_num,
                "impact": match_impact(name),
                "status": "⚠️ stale"
            })

    # 按影响范围排序
    stale.sort(key=lambda x: x["impact"])

    # 输出 JSON Lines（程序消费）
    for s in stale:
        print(json.dumps(s, ensure_ascii=False))

    # 输出 Markdown 表格（人类可读）
    if stale:
        print(f"\n## 受影响素材 ({len(stale)} 项)")
        print("| 素材 | source_version | 当前设计版本 | 版本差 | 影响范围 |")
        print("|------|---------------|-------------|--------|---------|")
        for s in stale:
            print("| {} | {} | {} | {} | {} |".format(
                s["asset"],
                s["source_version"],
                s["current_version"],
                s["version_gap"],
                s["impact"],
            ))
    else:
        print(f"\n✅ 所有素材版本与当前设计版本 ({current_version_str}) 一致")

    # M10 修复: 校验 asset-manifest 格式一致性
    manifest_entries = extract_manifest_entries(manifest_content)
    expected_keys = {"source_version", "category", "asset"}
    for entry in manifest_entries:
        if missing_keys := expected_keys - set(entry.keys()):
            print(f"⚠️ 格式不一致: {entry.get('name','unknown')} 缺少字段 {missing_keys}")

    # M9 修复: 缺口检测 — story-design 中有但 asset-manifest 中没有的角色/场景
    story_chars = extract_story_characters(story_content)
    story_bgs = extract_story_backgrounds(story_content)

    manifest_asset_names = set(assets.keys())
    missing_chars = [c for c in story_chars if not any(c in m for m in manifest_asset_names)]
    missing_bgs = [b for b in story_bgs if not any(b in m for m in manifest_asset_names)]

    if missing_chars:
        print(f"⚠️ 缺口: {len(missing_chars)} 个角色在 asset-manifest 中无素材: {', '.join(missing_chars)}")
    if missing_bgs:
        print(f"⚠️ 缺口: {len(missing_bgs)} 个场景在 asset-manifest 中无素材: {', '.join(missing_bgs)}")


if __name__ == "__main__":
    game_key = sys.argv[1] if len(sys.argv) > 1 else "."
    main(game_key)
