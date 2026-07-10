"""TTS 静音检测器：用 pydub 检查每个 flac 后 30% 是否 RMS 偏低。

判定：
- 取音频后 30%
- 计算 RMS
- 若 RMS < max_amp * 0.05 → 该段视为静音
- 若后 30% 全部静音 → 报告"过长静音"

输入：webgal_case02/voice/*.flac
输出：报告到 stdout
"""
import sys
import json
from pathlib import Path
from pydub import AudioSegment
import numpy as np

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", line_buffering=True)
    except Exception:
        pass

ROOT = Path(r"d:\workspace\ai-github\OpenWebGAL\WebGAL_Demo")
VOICE_DIR = ROOT / "webgal_case02" / "voice"
MANIFEST = VOICE_DIR / "manifest.json"


def detect_silence(flac_path: Path, silence_ratio: float = 0.05) -> dict:
    """检测单个 flac 的尾部静音比例。
    silence_ratio: 静音 RMS 阈值（相对于 max_amp 的比例）
    """
    a = AudioSegment.from_file(flac_path)
    arr = np.array(a.get_array_of_samples())
    n = len(arr)
    max_amp = float(np.max(np.abs(arr))) if n > 0 else 0
    if max_amp == 0:
        return {
            "file": flac_path.name,
            "duration_ms": 0,
            "max_amp": 0,
            "tail_rms": 0,
            "tail_silent_ratio": 1.0,
            "is_overly_silent": True,
        }
    # 后 30%
    tail = arr[int(n * 0.7):]
    tail_rms = float(np.sqrt(np.mean(tail.astype(np.float64) ** 2)))
    # 分 100ms 块检查静音
    chunk = int(a.frame_rate * 0.1)
    total = silent = 0
    for i in range(0, n, chunk):
        seg = arr[i:i + chunk]
        r = float(np.sqrt(np.mean(seg.astype(np.float64) ** 2)))
        total += 1
        if r < max_amp * silence_ratio:
            silent += 1
    ratio = silent / total if total > 0 else 0
    return {
        "file": flac_path.name,
        "duration_ms": len(a),
        "max_amp": int(max_amp),
        "tail_rms": round(tail_rms, 1),
        "tail_silent_ratio": round(ratio, 3),
        "is_overly_silent": tail_rms < max_amp * 0.01,  # 后 30% 平均 RMS < 1% max
    }


def main():
    if not MANIFEST.exists():
        print(f"manifest.json 不存在: {MANIFEST}")
        sys.exit(1)
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    lines = manifest.get("lines", [])

    flacs = sorted(VOICE_DIR.glob("*.flac"))
    print(f"检测 {len(flacs)} 个 flac", flush=True)
    if not flacs:
        print("没有 flac 文件")
        return

    results = []
    for f in flacs:
        try:
            r = detect_silence(f)
            results.append(r)
        except Exception as e:
            results.append({"file": f.name, "error": str(e)})

    # 统计
    total = len(results)
    over_silent = [r for r in results if r.get("is_overly_silent")]
    by_spk = {}
    for r in results:
        # 从文件名提取 speaker
        n = r["file"]
        parts = n.replace(".flac", "").split("_")
        if len(parts) >= 4:
            spk = parts[-1]
        else:
            spk = "?"
        by_spk.setdefault(spk, []).append(r)

    print(f"\n总文件: {total}")
    print(f"过长静音（后 30% RMS < 1% max）: {len(over_silent)}")
    print()
    print("各 speaker 统计:")
    for spk, items in sorted(by_spk.items()):
        n = len(items)
        sil = sum(1 for x in items if x.get("is_overly_silent"))
        avg_dur = sum(x.get("duration_ms", 0) for x in items) / n if n else 0
        print(f"  {spk}: {n} 个, 静音 {sil} 个, 平均时长 {avg_dur/1000:.1f}s")
    print()
    if over_silent:
        print("过长静音文件清单（前 30 个）:")
        for r in over_silent[:30]:
            print(f"  {r['file']} dur={r.get('duration_ms',0)}ms tail_rms={r.get('tail_rms',0)}")


if __name__ == "__main__":
    main()
