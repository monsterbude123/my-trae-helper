#!/usr/bin/env python3
"""
V11 dist-hash-check.py — Bundle Staleness 检测（rot #13 修复）

Usage:
    python dist-hash-check.py [--src <dir>] [--dist <dir>]

Exit codes:
    0 = PASS（src/ 与 dist/ 时序一致）
    1 = FAIL（src/ 更新但 dist/ 未重生成）
"""
import sys
import argparse
import pathlib
import hashlib
import json
from datetime import datetime, timezone


def hash_dir(dir_path: pathlib.Path) -> str:
    """计算目录下所有文件 hash"""
    if not dir_path.exists():
        return ""

    h = hashlib.sha256()
    for f in sorted(dir_path.rglob("*")):
        if f.is_file() and not any(p in f.parts for p in ["node_modules", "__pycache__", ".git"]):
            h.update(str(f.relative_to(dir_path)).encode())
            try:
                h.update(f.read_bytes())
            except Exception:
                pass
    return h.hexdigest()[:16]


def main():
    parser = argparse.ArgumentParser(description="V11 Bundle Staleness 检测")
    parser.add_argument("--src", default="src", help="src 目录")
    parser.add_argument("--dist", default="dist", help="dist 目录")
    parser.add_argument("--project-root", default=".", help="项目根路径")
    parser.add_argument("--json", action="store_true", help="JSON 输出")
    args = parser.parse_args()

    project_root = pathlib.Path(args.project_root).resolve()
    src_dir = project_root / args.src
    dist_dir = project_root / args.dist

    if not src_dir.exists():
        result = {"status": "N/A", "message": f"src 目录不存在: {src_dir}"}
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print(f"⚠️ {result['message']}")
        return 0

    src_hash = hash_dir(src_dir)
    dist_hash = hash_dir(dist_dir)

    src_mtime = max((f.stat().st_mtime for f in src_dir.rglob("*") if f.is_file()), default=0)
    dist_mtime = max((f.stat().st_mtime for f in dist_dir.rglob("*") if f.is_file()), default=0) if dist_dir.exists() else 0

    is_stale = src_mtime > dist_mtime and dist_hash != src_hash

    result = {
        "src_hash": src_hash,
        "dist_hash": dist_hash,
        "src_mtime": datetime.fromtimestamp(src_mtime, tz=timezone.utc).isoformat() if src_mtime else None,
        "dist_mtime": datetime.fromtimestamp(dist_mtime, tz=timezone.utc).isoformat() if dist_mtime else None,
        "status": "FAIL" if is_stale else "PASS",
        "message": "src 更新但 dist 未重生成" if is_stale else "src/ vs dist/ 时序一致",
    }

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        icon = "❌" if is_stale else "✅"
        print(f"{icon} {result['status']} — {result['message']}")
        print(f"   src hash: {src_hash}")
        print(f"   dist hash: {dist_hash}")

    return 0 if not is_stale else 1


if __name__ == "__main__":
    sys.exit(main())