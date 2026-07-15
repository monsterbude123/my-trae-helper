"""外部素材导入 — 扫描目录 → 自动分类 → 注册到 asset-manifest.md"""
import sys, os, hashlib, shutil
from pathlib import Path
from datetime import date

CATEGORY_MAP = {
    '.png': ('sprite', 'assets/sprites/'),
    '.jpg': ('sprite', 'assets/sprites/'),
    '.ogg': ('audio', 'assets/audio/'),
    '.wav': ('audio', 'assets/audio/'),
    '.mp3': ('audio', 'assets/audio/'),
    '.ttf': ('font', 'assets/fonts/'),
    '.otf': ('font', 'assets/fonts/'),
}

def file_hash(path: str) -> str:
    with open(path, 'rb') as f:
        return hashlib.md5(f.read()).hexdigest()

def main(game_key: str, external_dir: str):
    base = Path(game_key)
    manifest_path = base / "asset-manifest.md"

    imported = []
    skipped = []
    duplicates = []

    for f in Path(external_dir).rglob('*'):
        if not f.is_file():
            continue

        ext = f.suffix.lower()
        if ext not in CATEGORY_MAP:
            skipped.append(str(f))
            continue

        category, dest_dir = CATEGORY_MAP[ext]
        dest = base / dest_dir / f.name
        dest.parent.mkdir(parents=True, exist_ok=True)

        if dest.exists() and file_hash(str(f)) == file_hash(str(dest)):
            duplicates.append(str(f))
            continue

        shutil.copy2(str(f), str(dest))

        relative_path = str(dest.relative_to(base)).replace('\\', '/')
        entry = (
            f"\n{relative_path}:\n"
            f'  source: "external"\n'
            f'  imported_at: "{date.today()}"\n'
            f'  status: "imported"\n'
            f'  category: "{category}"\n'
        )

        with open(manifest_path, 'a', encoding='utf-8') as mf:
            mf.write(entry)

        imported.append(relative_path)

    print(f"✅ 已导入: {len(imported)} 个文件")
    if skipped:
        print(f"⚠️ 跳过 (格式不支持): {len(skipped)} 个")
    if duplicates:
        print(f"⏭️ 重复 (已存在): {len(duplicates)} 个")

if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
