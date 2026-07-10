"""单文件：webgal_case02 资产质量检查。
- figures/*.png: RGBA，尺寸合理 (>256x256)，文件 > 20KB
- backgrounds/*.webp: 1216x832.webp，文件 > 30KB
- bgm/*.mp3: mp3，文件 > 100KB
- 每张图 Pillow 程序化检查：
    * 不是大面积纯色（HSV 饱和度均值 < 5% 视为废图）
    * 主体像素 > 30%（非黑/非白的有效像素比例）
"""
import sys
from pathlib import Path
from collections import defaultdict
from PIL import Image

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

ROOT = Path(r"d:\workspace\ai-github\OpenWebGAL\WebGAL_Demo")
CASE = ROOT / "webgal_case02"
FIG = CASE / "figure"
BG = CASE / "background"
BGM = CASE / "bgm"

results = defaultdict(list)
summary = {"figures_ok": 0, "figures_fail": 0,
           "backgrounds_ok": 0, "backgrounds_fail": 0,
           "bgm_ok": 0, "bgm_fail": 0}


def check_image_quality(path: Path):
    """Pillow 程序化检查。
    返回 (passed: bool, reason: str, sat: float, main: float)
    """
    try:
        im = Image.open(path).convert("RGB")
    except Exception as e:
        return False, f"open fail: {e}", 0.0, 0.0
    # 缩略采样加速
    small = im.copy()
    small.thumbnail((256, 256))
    px = small.load()
    w, h = small.size
    sat_sum = 0.0
    sat_n = 0
    main_n = 0
    for y in range(0, h, 2):
        for x in range(0, w, 2):
            r, g, b = px[x, y]
            mx, mn = max(r, g, b), min(r, g, b)
            sat = (mx - mn) / mx if mx > 0 else 0.0
            sat_sum += sat
            sat_n += 1
            # 主体像素：非黑非白，且有一定饱和度或亮度差异
            if not (mx < 15 or mn > 245):
                if sat > 0.05 or (mx - mn) > 15:
                    main_n += 1
    sat_avg = sat_sum / sat_n if sat_n else 0.0
    main_ratio = main_n / sat_n if sat_n else 0.0
    if sat_avg < 0.05:
        return False, f"low_saturation={sat_avg:.3f}", sat_avg, main_ratio
    if main_ratio < 0.30:
        return False, f"low_main_pixels={main_ratio:.3f}", sat_avg, main_ratio
    return True, "ok", sat_avg, main_ratio


def hr(label):
    print(f"\n{'='*60}\n[{label}]\n{'='*60}", flush=True)


# ---------- figures ----------
hr("FIGURES (RGBA, >20KB, sat>5%, main>30%)")
if not FIG.exists():
    print("no figure dir")
else:
    for p in sorted(FIG.glob("*.png")):
        size_kb = p.stat().st_size // 1024
        ok = True
        reasons = []
        if size_kb < 20:
            ok = False
            reasons.append(f"size<20KB({size_kb}KB)")
        try:
            im = Image.open(p)
            if im.mode != "RGBA":
                reasons.append(f"mode={im.mode}(need RGBA)")
                ok = False
            w, h = im.size
            if w < 256 or h < 256:
                reasons.append(f"size={w}x{h}(<256)")
                ok = False
        except Exception as e:
            reasons.append(f"open:{e}")
            ok = False
        if ok:
            q_ok, q_reason, sat, main = check_image_quality(p)
            if not q_ok:
                ok = False
                reasons.append(f"quality:{q_reason}")
            print(f"  {'PASS' if ok else 'FAIL'} {p.name:30s} {size_kb}KB  sat={sat:.3f} main={main:.3f}  {' '.join(reasons)}", flush=True)
        else:
            print(f"  {'PASS' if ok else 'FAIL'} {p.name:30s} {size_kb}KB  {' '.join(reasons)}", flush=True)
        if ok:
            results['figures_ok'].append(p.name)
            summary['figures_ok'] += 1
        else:
            results['figures_fail'].append({"name": p.name, "reason": reasons})
            summary['figures_fail'] += 1

# ---------- backgrounds ----------
hr("BACKGROUNDS (1216x832 webp, >30KB, sat>5%, main>30%)")
if not BG.exists():
    print("no background dir")
else:
    for p in sorted(BG.glob("*.webp")):
        size_kb = p.stat().st_size // 1024
        ok = True
        reasons = []
        if size_kb < 30:
            ok = False
            reasons.append(f"size<30KB({size_kb}KB)")
        try:
            im = Image.open(p)
            if im.size != (1216, 832):
                reasons.append(f"size={im.size}(need 1216x832)")
                ok = False
        except Exception as e:
            reasons.append(f"open:{e}")
            ok = False
        if ok:
            q_ok, q_reason, sat, main = check_image_quality(p)
            if not q_ok:
                ok = False
                reasons.append(f"quality:{q_reason}")
            print(f"  {'PASS' if ok else 'FAIL'} {p.name:30s} {size_kb}KB  sat={sat:.3f} main={main:.3f}  {' '.join(reasons)}", flush=True)
        else:
            print(f"  {'PASS' if ok else 'FAIL'} {p.name:30s} {size_kb}KB  {' '.join(reasons)}", flush=True)
        if ok:
            results['backgrounds_ok'].append(p.name)
            summary['backgrounds_ok'] += 1
        else:
            results['backgrounds_fail'].append({"name": p.name, "reason": reasons})
            summary['backgrounds_fail'] += 1

# ---------- bgm ----------
hr("BGM (mp3, >100KB)")
if not BGM.exists():
    print("no bgm dir")
else:
    for p in sorted(BGM.glob("*.mp3")):
        size_kb = p.stat().st_size // 1024
        ok = True
        reasons = []
        if p.suffix.lower() != ".mp3":
            ok = False
            reasons.append("not mp3")
        if size_kb < 100:
            ok = False
            reasons.append(f"size<100KB({size_kb}KB)")
        print(f"  {'PASS' if ok else 'FAIL'} {p.name:30s} {size_kb}KB  {' '.join(reasons)}", flush=True)
        if ok:
            results['bgm_ok'].append(p.name)
            summary['bgm_ok'] += 1
        else:
            results['bgm_fail'].append({"name": p.name, "reason": reasons})
            summary['bgm_fail'] += 1

# ---------- summary ----------
hr("SUMMARY")
for k, v in summary.items():
    print(f"  {k:20s} = {v}", flush=True)

total_ok = summary['figures_ok'] + summary['backgrounds_ok'] + summary['bgm_ok']
total_fail = summary['figures_fail'] + summary['backgrounds_fail'] + summary['bgm_fail']
print(f"\n  TOTAL ok   = {total_ok}", flush=True)
print(f"  TOTAL fail = {total_fail}", flush=True)

# 输出失败清单
if any(results[k] for k in results if k.endswith('_fail')):
    hr("FAILED ITEMS")
    for cat in ('figures_fail', 'backgrounds_fail', 'bgm_fail'):
        for item in results[cat]:
            print(f"  [{cat}] {item['name']}: {item['reason']}", flush=True)
print("DONE", flush=True)
