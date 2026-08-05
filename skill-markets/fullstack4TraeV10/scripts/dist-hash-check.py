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


# Vite/Webpack 默认 chunk 命名: {Name}-{8charhash}.{ext}
# V10.4.1 修复: 加 PascalCase 守卫(首字母大写 + 至少 1 个小写字符在后),避免 1 字符前缀误报
#   V10.4.1 升级 (regex 收紧):
#     旧 regex `[A-Z][A-Za-z0-9_]*` 会匹配 1 字符前缀如 `C-5YGVCf.js`(误报: Vite 不会生成
#     这么短的 chunk 名,这是 CSS background-image hash 之类)
#     新 regex 要求 PascalCase chunk 前缀 ≥ 2 字符且必须含小写
#     拒绝: C-5YGVCf.js / A-DOcbj12u.js (单字符 chunk 前缀)
#     保留: ActivityBar-DOcbj12u.js (PascalCase) / useBaseUiId-BnDuWhvb.js (camelCase)
#   camelCase 分支也加 `+` 要求至少 1 字符的小写前缀(原 `*` 允许 0 字符,与 PascalCase
#   分支冲突时会让 1 字符情况漏过 → 升级为 `+`)
CHUNK_PATTERN = re.compile(
    r"\b([A-Z][a-z][A-Za-z0-9_]*|[a-z][a-z0-9]*[A-Z][A-Za-z0-9_]+)-([A-Za-z0-9_-]{6,12})\.(js|mjs)\b"
)

# Vite asset 命名: assets/Page-{hash}.js 或 assets/index-{hash}.js
ASSET_PATTERN = re.compile(
    r"/?assets/([A-Za-z0-9_.-]+)-([A-Za-z0-9_-]{6,12})\.(js|mjs)\b"
)

BIN_SIZE_THRESHOLD = 1024 * 1024  # 1MB

# V10.4.1 修复 (self-diagnose generic-heuristics WARN): 把硬编码 10 提到模块顶部常量
#   原代码直接用 `r.stale[:10]` 和 `len(r.stale) > 10` 触发 self-diagnose 启发式 2 误报
#   实际语义: 报告展示用截断上限(超过的标 "+N more"),不影响 stale 判定本身
#   V10.4.1 起改用常量,后续要调整截断长度只改一处
STALE_DISPLAY_LIMIT = 10  # stale 列表展示上限(超出标 "+N more")

# Tauri Rust 内嵌的 JS 桥文件 (不是 Vite 产物,永远不应在 dist/ 中)
# V10.4.1 新增: 避免 "ipc-message-fn.js" 等 Tauri 内部 chunk 触发 stale 误报
TAURI_INTERNAL_JS: set[str] = {
    "ipc-message-fn.js",       # Tauri IPC 桥(被 Rust 内嵌)
    "tauri-plugin-api.js",     # Tauri 插件 API (如有)
    "tauri-runtime.js",        # Tauri 运行时
}


@dataclass
class StaleReport:
    binary: str
    binary_chunks: List[str] = field(default_factory=list)
    dist_chunks: List[str] = field(default_factory=list)
    stale: List[str] = field(default_factory=list)  # binary 引用但 dist 不存在
    new: List[str] = field(default_factory=list)    # dist 有但 binary 没引用
    filtered_internal: int = 0  # V10.4.1: 被 TAURI_INTERNAL_JS 白名单过滤的数量

    def to_dict(self):
        return {
            "binary": self.binary,
            "binary_chunks": self.binary_chunks,
            "dist_chunks": self.dist_chunks,
            "stale": self.stale,
            "new": self.new,
            "stale_count": len(self.stale),
            "new_count": len(self.new),
            "filtered_internal": self.filtered_internal,
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
    # V10.4.1: 过滤 Tauri 内部 JS(白名单),它们永远不应在 dist/ 中
    raw_stale = sorted(binary_set - dist_set)
    stale = [c for c in raw_stale if c not in TAURI_INTERNAL_JS]
    filtered_count = len(raw_stale) - len(stale)
    new = sorted(dist_set - binary_set)
    return StaleReport(
        binary=str(binary.name),
        binary_chunks=binary_chunks,
        dist_chunks=dist_chunks,
        stale=stale,
        new=new,
        filtered_internal=filtered_count,  # V10.4.1: 记录被白名单过滤的数量
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
                for c in r.stale[:STALE_DISPLAY_LIMIT]:
                    print(f"     - {c}")
                if len(r.stale) > STALE_DISPLAY_LIMIT:
                    print(f"     ... +{len(r.stale) - STALE_DISPLAY_LIMIT} more")
                if r.filtered_internal:
                    print(f"   ⏭️  {r.filtered_internal} 个 Tauri 内部 JS 已白名单过滤(非 stale)")
                if r.new:
                    print(f"   dist 中新增但 binary 未引用 ({len(r.new)} 个):")
                    for c in r.new[:5]:
                        print(f"     + {c}")
                print()
            else:
                print(f"✅ {r.binary}: binary chunk ({len(r.binary_chunks)}) vs dist ({len(r.dist_chunks)}) 一致")
                if r.filtered_internal:
                    print(f"   ⏭️  {r.filtered_internal} 个 Tauri 内部 JS 已白名单过滤(非 stale)")
                if r.new:
                    print(f"   ⚠️ dist 中新增 {len(r.new)} 个 chunk,建议重新 build binary")

    return 1 if total_stale > 0 else 0


if __name__ == "__main__":
    raise SystemExit(main())
