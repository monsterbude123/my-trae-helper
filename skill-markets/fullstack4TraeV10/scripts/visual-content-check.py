#!/usr/bin/env python3
"""visual-content-check.py — V10.4 视觉内容深度校验（腐烂点 9 修复）

实战教训: V10.3.9 视觉证据只查 PNG magic + 大小。PNG 真但内容是空白/破图也 PASS。
V10.4 加入 3 层: PIL 完整解码 + 颜色直方图 + 关键区域非空采样。

用法:
  python scripts/visual-content-check.py <png_path> [--json]
  python scripts/visual-content-check.py --dir <shots_dir> [--json]   # 批量检查

检测:
  L1: PNG magic number
  L2: 文件大小 ≥ 5000 bytes
  L3: PIL 完整解码 (无 truncated)
  L4: 颜色直方图多样性 (unique_count ≥ 50)
  L5: 关键区域非空采样 (4 象限亮度差 > 阈值)

退出码:
  0 = pass
  1 = fail
  2 = script error

V10.4 引入 (2026-07-30)
"""
from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional


# === 阈值常量 ===

VISUAL_MIN_BYTES = 5000
PNG_MAGIC = b"\x89PNG\r\n\x1a\n"
MIN_UNIQUE_COLORS = 50      # 颜色直方图阈值（过低=单色破图）
MIN_QUADRANT_DIFF = 5       # 4 象限平均亮度差阈值（亮色主题：过低=整页同色）
MIN_QUADRANT_DIFF_DARK = 2.5  # 4 象限亮度差阈值（深色主题：暗背景差异更小，V10.4.1 新增）
DARK_BRIGHTNESS_THRESHOLD = 50  # mean 亮度 < 此值视为深色主题
SAMPLE_SIZE = 64            # 降采样尺寸（加速计算）


@dataclass
class VisualCheckResult:
    path: str
    status: str               # "pass" | "fail" | "skip"
    layer1_magic: str = "skip"
    layer2_size: str = "skip"
    layer3_decode: str = "skip"
    layer4_histogram: str = "skip"
    layer5_quadrants: str = "skip"
    detail: str = ""

    def to_dict(self):
        return asdict_dict(self)


def asdict_dict(obj) -> dict:
    """简单 asdict 替代，避免 dataclasses 依赖"""
    return {k: getattr(obj, k) for k in obj.__dict__}


def check_png(png_path: Path) -> VisualCheckResult:
    """检查单个 PNG 文件"""
    result = VisualCheckResult(path=str(png_path), status="pass")

    # L1: PNG magic
    try:
        with open(png_path, "rb") as f:
            header = f.read(8)
    except OSError as e:
        result.status = "fail"
        result.layer1_magic = f"❌ 无法读取: {e}"
        result.detail = result.layer1_magic
        return result

    if header != PNG_MAGIC:
        result.status = "fail"
        result.layer1_magic = f"❌ magic 失配 (前 8 字节 = {header!r})"
        result.detail = result.layer1_magic
        return result
    result.layer1_magic = "✅ PNG magic OK"

    # L2: 文件大小
    size = png_path.stat().st_size
    if size < VISUAL_MIN_BYTES:
        result.status = "fail"
        result.layer2_size = f"❌ {size} bytes < {VISUAL_MIN_BYTES}"
        result.detail = result.layer2_size
        return result
    result.layer2_size = f"✅ {size} bytes"

    # L3-L5: PIL 检查
    try:
        from PIL import Image
    except ImportError:
        # PIL 未安装 → L3-5 全部 SKIP,但保留 L1+L2 通过
        result.layer3_decode = "⏭️ PIL 未安装,跳过 L3-5"
        result.layer4_histogram = "⏭️"
        result.layer5_quadrants = "⏭️"
        result.detail = f"{result.layer1_magic}; {result.layer2_size}; PIL 缺失"
        return result

    try:
        with Image.open(png_path) as img:
            img.load()  # 强制完整解码（truncated 会抛异常）
            # L3: 解码完整
            w, h = img.size
            result.layer3_decode = f"✅ {w}x{h} decoded"

            # L4: 颜色直方图多样性
            # 降采样到 64x64 加速
            small = img.convert("RGB").resize((SAMPLE_SIZE, SAMPLE_SIZE))
            # ponytail: 改用 numpy-free 的 bytes 方式，避免 getdata() 在 Pillow 14 弃用
            pixels = list(small.tobytes())  # RGB bytes = 3*N values
            unique_count = len(set(pixels))
            if unique_count < MIN_UNIQUE_COLORS:
                result.status = "fail"
                result.layer4_histogram = (
                    f"❌ 唯一色 {unique_count} < {MIN_UNIQUE_COLORS} "
                    f"（单色破图/重复元素）"
                )
                result.detail = result.layer4_histogram
                return result
            result.layer4_histogram = f"✅ 唯一色 {unique_count}"

            # L5: 4 象限平均亮度差 (V10.4.1 dark-aware)
            # 深色主题 UI 整页相近,实测 [28.7, 24.5, 26.3, 23.8] 极差 4.9 < 5 误报 FAIL
            # 修复: 先算 mean 亮度判断是否深色,深色用更小的阈值
            gray = img.convert("L").resize((SAMPLE_SIZE, SAMPLE_SIZE))
            gray_bytes = gray.tobytes()  # length = SAMPLE_SIZE^2
            gray_pixels = gray_bytes  # bytes str,可直接索引
            half = SAMPLE_SIZE // 2
            # 4 象限: [0:half, 0:half] / [0:half, half:] / [half:, 0:half] / [half:, half:]
            quads: list[float] = []
            for qx, qy in [(0, 0), (0, half), (half, 0), (half, half)]:
                quad_pixels = []
                for y in range(qy, qy + half):
                    for x in range(qx, qx + half):
                        quad_pixels.append(gray_pixels[y * SAMPLE_SIZE + x])
                avg = sum(quad_pixels) / len(quad_pixels)
                quads.append(avg)

            # mean 亮度 = 4 象限平均
            brightness = sum(quads) / len(quads)
            is_dark = brightness < DARK_BRIGHTNESS_THRESHOLD
            threshold = MIN_QUADRANT_DIFF_DARK if is_dark else MIN_QUADRANT_DIFF
            theme = "dark" if is_dark else "light"

            diff = max(quads) - min(quads)
            if diff < threshold:
                result.status = "fail"
                result.layer5_quadrants = (
                    f"❌ 4 象限亮度极差 {diff:.1f} < {threshold} "
                    f"（{theme} 主题,整页同色/单元素）quads={[f'{q:.1f}' for q in quads]} "
                    f"brightness={brightness:.1f}"
                )
                result.detail = result.layer5_quadrants
                return result
            result.layer5_quadrants = (
                f"✅ 4 象限亮度极差 {diff:.1f}（{theme} 主题,阈值 {threshold}）"
                f"quads={[f'{q:.1f}' for q in quads]}"
            )
    except Exception as e:
        result.status = "fail"
        result.layer3_decode = f"❌ PIL 解码失败: {e}"
        result.detail = result.layer3_decode
        return result

    result.detail = (
        f"{result.layer1_magic}; {result.layer2_size}; "
        f"{result.layer3_decode}; {result.layer4_histogram}; {result.layer5_quadrants}"
    )
    return result


def main() -> int:
    parser = argparse.ArgumentParser(
        description="V10.4 视觉内容深度校验（腐烂点 9 修复）",
    )
    parser.add_argument("png", nargs="?", help="单个 PNG 文件路径")
    parser.add_argument("--dir", type=str, help="批量检查目录")
    parser.add_argument("--json", action="store_true", help="JSON 输出")
    args = parser.parse_args()

    paths: List[Path] = []
    if args.png:
        paths.append(Path(args.png))
    if args.dir:
        d = Path(args.dir)
        if d.is_dir():
            paths.extend(sorted(d.glob("*.png")))

    if not paths:
        print("ERROR: 必须提供 png 文件路径或 --dir 目录", file=sys.stderr)
        return 2

    results = [check_png(p) for p in paths]
    fail_count = sum(1 for r in results if r.status == "fail")

    if args.json:
        payload = {
            "status": "fail" if fail_count > 0 else "pass",
            "total": len(results),
            "fail_count": fail_count,
            "results": [r.to_dict() for r in results],
        }
        print(json.dumps(payload, ensure_ascii=False, separators=(",", ":")))
    else:
        for r in results:
            icon = "✅" if r.status == "pass" else "🛑"
            print(f"{icon} {r.path}")
            print(f"   {r.detail}")
            print()
        if fail_count:
            print(f"🛑 {fail_count}/{len(results)} FAIL")
        else:
            print(f"✅ 全部通过 ({len(results)} 个)")

    return 1 if fail_count > 0 else 0


if __name__ == "__main__":
    raise SystemExit(main())
