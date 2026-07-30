#!/usr/bin/env python3
"""dist-hash-check.py — V10.4 Bundle Staleness 检测器（腐烂点 13 修复）

实战教训: 改 TS 后 cargo build 不重触 pnpm build,frontend bundle 过期,binary chunk hash 仍是旧的。
本脚本验证 binary 内嵌的前端 chunk hash vs dist/assets 当前 hash。

用法:
  python scripts/dist-hash-check.py --project-root <path> [--json]

仅在 src-tauri/tauri.conf.json 存在时启用。Web 项目直接 SKIP。

检测逻辑:
  1. 读 src-tauri/target/release/*.exe bytes
  2. 提取所有类似 SystemSettingsPage-{hash}.js 字符串(Vite chunk naming)
  3. 对比 dist/assets/ 实际文件
  4. binary 引用的 chunk 在 dist 中不存在 → FAIL (stale binary)

退出码:
  0 = pass / skip
  1 = fail (binary stale)
  2 = script error

V10.4 引入 (2026-07-30)
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional

try:
    from common import get_project_root
except ImportError:  # pragma: no cover
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from common import get_project_root


# Vite/Webpack 默认 chunk 命名: {name}-{8charhash}.{ext}
CHUNK_PATTERN = re.compile(
    r"\b([A-Za-z][A-Za-z0-9_]*)-([A-Za-z0-9_-]{6,12})\.(js|mjs)\b"
)

# Vite asset 命名: assets/Page-{hash}.js 或 assets/index-{hash}.js
ASSET_PATTERN = re.compile(
    r"/?assets/([A-Za-z0-9_.-]+)-([A-Za-z0-9_-]{6,12})\.(js|mjs)\b"
)

BIN_SIZE_THRESHOLD = 1024 * 1024  # 1MB


@dataclass
class StaleReport:
    binary: str
    binary_chunks: List[str] = field(default_factory=list)
    dist_chunks: List[str] = field(default_factory=list)
    stale: List[str] = field(default_factory=list)  # binary 引用但 dist 不存在
    new: List[str] = field(default_factory=list)    # dist 有但 binary 没引用

    def to_dict(self):
        return {
            "binary": self.binary,
            "binary_chunks": self.binary_chunks,
            "dist_chunks": self.dist_chunks,
            "stale": self.stale,
            "new": self.new,
            "stale_count": len(self.stale),
            "new_count": len(self.new),
        }


def is_tauri_project(project_root: Path) -> bool:
    return (project_root / "src-tauri" / "tauri.conf.json").is_file()


def find_release_binaries(project_root: Path) -> List[Path]:
    """查找 src-tauri/target/release/ 下的所有 .exe binary"""
    target_release = project_root / "src-tauri" / "target" / "release"
    if not target_release.is_dir():
        return []
    bins = []
    for p in target_release.iterdir():
        if p.is_file() and (p.suffix == ".exe" or p.name.endswith(".app")):
            try:
                if p.stat().st_size >= BIN_SIZE_THRESHOLD:
                    bins.append(p)
            except OSError:
                continue
    return bins


def extract_chunks_from_binary(binary: Path) -> List[str]:
    """从 binary 字节中提取所有 chunk 名称"""
    try:
        data = binary.read_bytes()
    except OSError:
        return []
    text = data.decode("utf-8", errors="ignore")
    chunks = set()
    for m in CHUNK_PATTERN.finditer(text):
        chunks.add(f"{m.group(1)}-{m.group(2)}.{m.group(3)}")
    for m in ASSET_PATTERN.finditer(text):
        chunks.add(f"{m.group(1)}-{m.group(2)}.{m.group(3)}")
    return sorted(chunks)


def extract_chunks_from_dist(project_root: Path) -> List[str]:
    """从 dist/assets/ 读取所有 chunk 文件"""
    dist_assets = project_root / "dist" / "assets"
    if not dist_assets.is_dir():
        # Vite 旧版用 dist/ 根目录
        dist_assets = project_root / "dist"
    if not dist_assets.is_dir():
        return []
    chunks = []
    for p in dist_assets.rglob("*.js"):
        if p.is_file():
            chunks.append(p.name)
    return sorted(set(chunks))


def check_one_binary(binary: Path, dist_chunks: List[str]) -> StaleReport:
    binary_chunks = extract_chunks_from_binary(binary)
    dist_set = set(dist_chunks)
    binary_set = set(binary_chunks)
    stale = sorted(binary_set - dist_set)
    new = sorted(dist_set - binary_set)
    return StaleReport(
        binary=str(binary.name),
        binary_chunks=binary_chunks,
        dist_chunks=dist_chunks,
        stale=stale,
        new=new,
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="V10.4 Bundle Staleness 检测器（腐烂点 13 修复）",
    )
    parser.add_argument("--project-root", type=str, default=".", help="项目根")
    parser.add_argument("--json", action="store_true", help="JSON 输出")
    args = parser.parse_args()

    project_root = Path(args.project_root).resolve() if args.project_root != "." else get_project_root()

    if not project_root.is_dir():
        print(f"ERROR: 项目根不存在: {project_root}", file=sys.stderr)
        return 2

    if not is_tauri_project(project_root):
        if args.json:
            print(json.dumps({
                "status": "skip",
                "reason": "非 Tauri 项目（无 src-tauri/tauri.conf.json）",
                "project_root": str(project_root),
            }, ensure_ascii=False))
        else:
            print(f"⏭️ SKIP: 非 Tauri 项目，跳过 bundle staleness 检查")
        return 0

    bins = find_release_binaries(project_root)
    if not bins:
        if args.json:
            print(json.dumps({
                "status": "skip",
                "reason": "未找到 release binary（src-tauri/target/release/*.exe 缺失）",
                "project_root": str(project_root),
            }, ensure_ascii=False))
        else:
            print(f"⏭️ SKIP: 未找到 release binary（先 cargo build --release）")
        return 0

    dist_chunks = extract_chunks_from_dist(project_root)
    if not dist_chunks:
        if args.json:
            print(json.dumps({
                "status": "fail",
                "reason": "dist/ 下无 JS chunk（需先 pnpm build）",
                "project_root": str(project_root),
            }, ensure_ascii=False))
        else:
            print(f"🛑 FAIL: dist/ 下无 JS chunk（需先 pnpm build）")
        return 1

    reports = [check_one_binary(b, dist_chunks) for b in bins]
    total_stale = sum(len(r.stale) for r in reports)

    if args.json:
        print(json.dumps({
            "status": "fail" if total_stale > 0 else "pass",
            "project_root": str(project_root),
            "reports": [r.to_dict() for r in reports],
            "total_stale": total_stale,
        }, ensure_ascii=False, separators=(",", ":")))
    else:
        for r in reports:
            if r.stale:
                print(f"🛑 STALE binary: {r.binary}")
                print(f"   binary 引用但 dist 中不存在 ({len(r.stale)} 个):")
                for c in r.stale[:10]:
                    print(f"     - {c}")
                if len(r.stale) > 10:
                    print(f"     ... +{len(r.stale) - 10} more")
                if r.new:
                    print(f"   dist 中新增但 binary 未引用 ({len(r.new)} 个):")
                    for c in r.new[:5]:
                        print(f"     + {c}")
                print()
            else:
                print(f"✅ {r.binary}: binary chunk ({len(r.binary_chunks)}) vs dist ({len(r.dist_chunks)}) 一致")
                if r.new:
                    print(f"   ⚠️ dist 中新增 {len(r.new)} 个 chunk,建议重新 build binary")

    return 1 if total_stale > 0 else 0


if __name__ == "__main__":
    raise SystemExit(main())
