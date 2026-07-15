"""缺口检测 — 检查 story-design 中有但 asset-manifest 中无的条目"""
import sys
import re
from pathlib import Path


def main(game_key: str):
    base = Path(game_key)
    story = (base / "story-design.md").read_text(encoding="utf-8")
    manifest = (base / "asset-manifest.md").read_text(encoding="utf-8")

    # Extract story characters and scenes
    chars = set(re.findall(r'^- \[(\w+)\]', story, re.MULTILINE))
    bgs = set(re.findall(r'###\s+(\w+)', story))

    # Check against manifest text
    manifest_text = manifest
    missing = []
    for c in chars:
        if c not in manifest_text:
            missing.append(f"character_{c}")
    for b in bgs:
        if b not in manifest_text:
            missing.append(f"bg_{b}")

    if missing:
        print(f"❌ 缺口: {len(missing)} 个条目在 asset-manifest 中缺失")
        for m in missing:
            print(f"  - {m}")
        sys.exit(1)
    else:
        print("✅ 无缺口 — story-design 中所有角色/场景在 asset-manifest 中有对应")


if __name__ == "__main__":
    main(sys.argv[1])
