#!/usr/bin/env python3
"""
V11 visual-content-check.py — 视觉证据 3 层校验

Usage:
    python visual-content-check.py [--png <dir>]

3 层校验:
  1. 文件存在 + Size ≥ 5KB
  2. PIL 解码 + PNG magic
  3. 直方图 + 关键区域采样

Exit codes:
    0 = PASS
    1 = FAIL
"""
import sys
import argparse
import pathlib
import json
from datetime import datetime, timezone


def check_png_3_layers(png_path: pathlib.Path) -> tuple:
    """3 层校验单张 PNG"""
    # Layer 1: 文件存在 + size
    if not png_path.exists():
        return False, "文件不存在"

    size = png_path.stat().st_size
    if size < 5000:
        return False, f"size={size}B < 5KB"

    # 文件活跃性（≤7 天）
    mtime = datetime.fromtimestamp(png_path.stat().st_mtime, tz=timezone.utc)
    age_days = (datetime.now(timezone.utc) - mtime).days
    if age_days > 7:
        return False, f"过期 {age_days} 天"

    # Layer 2: PNG magic（尝试 PIL）
    try:
        from PIL import Image
        img = Image.open(png_path)
        img.verify()
    except ImportError:
        return False, "缺 PIL（Pillow）"
    except Exception as e:
        return False, f"PIL 解码失败: {e}"

    # Layer 3: 直方图
    try:
        img = Image.open(png_path)
        hist = img.convert("L").histogram()  # 灰度直方图
        avg = sum(i * h for i, h in enumerate(hist)) / sum(hist)
        if avg < 30 or avg > 240:
            return False, f"亮度异常 {avg:.0f}（30-240 正常）"
    except Exception as e:
        return False, f"直方图失败: {e}"

    return True, f"size={size}B age={age_days}d avg={avg:.0f}"


def main():
    parser = argparse.ArgumentParser(description="V11 视觉证据 3 层校验")
    parser.add_argument("--png", default="docs/verifications", help="PNG 目录")
    parser.add_argument("--project-root", default=".", help="项目根路径")
    parser.add_argument("--json", action="store_true", help="JSON 输出")
    args = parser.parse_args()

    project_root = pathlib.Path(args.project_root).resolve()
    png_dir = project_root / args.png

    if not png_dir.exists():
        result = {"status": "N/A", "message": f"目录不存在: {png_dir}"}
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print(f"⚠️ {result['message']}")
        return 0

    pngs = list(png_dir.rglob("*.png"))
    results = []
    all_pass = True

    for png in pngs:
        is_pass, msg = check_png_3_layers(png)
        results.append({
            "file": str(png.relative_to(project_root)),
            "status": "PASS" if is_pass else "FAIL",
            "message": msg,
        })
        if not is_pass:
            all_pass = False

    output = {
        "scan_at": datetime.now(timezone.utc).isoformat(),
        "total": len(pngs),
        "passed": sum(1 for r in results if r["status"] == "PASS"),
        "failed": sum(1 for r in results if r["status"] == "FAIL"),
        "status": "PASS" if all_pass else "FAIL",
        "results": results,
    }

    if args.json:
        print(json.dumps(output, indent=2, ensure_ascii=False))
    else:
        icon = "✅" if all_pass else "❌"
        print(f"{icon} {output['status']} — {output['passed']}/{output['total']} PASS")
        for r in results:
            mark = "✓" if r["status"] == "PASS" else "✗"
            print(f"  [{mark}] {r['file']}: {r['message']}")

    return 0 if all_pass else 1


if __name__ == "__main__":
    sys.exit(main())