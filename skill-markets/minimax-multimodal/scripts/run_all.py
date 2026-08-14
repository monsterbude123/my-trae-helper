"""MiniMax 编排入口 — 一次性跑完 6 大模态演示(用于冒烟测试 + demo)。

与 verify_all.py 的区别:
  - verify_all.py:连通性 + 最小开销,只确认 6 个端点能 ping 通
  - run_all.py:展示性 demo,各模态跑真实内容,产物全部落 output/

用法:
  python run_all.py                    # 默认跑 5 个模态(跳过视频)
  python run_all.py --include-video    # 6 个全跑
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _client  # noqa: E402


def run_text_chat(cred: dict) -> bool:
    import text_chat
    try:
        resp = text_chat.chat(
            "用一句话介绍 MiniMax 平台。",
            model="MiniMax-M2.7",
            api_key=cred["api_key"], base_url=cred["base_url"], timeout=cred["timeout"],
        )
        content = resp.get("choices", [{}])[0].get("message", {}).get("content", "")
        print(f"[text_chat] {content[:100]}")
        return bool(content)
    except Exception as e:
        print(f"[text_chat FAIL] {e}")
        return False


def run_image_gen(cred: dict) -> bool:
    import image_generate
    try:
        urls = image_generate.generate(
            "一只可爱的卡通小猫",
            model="image-01",
            aspect_ratio="1:1",
            api_key=cred["api_key"], base_url=cred["base_url"], timeout=cred["timeout"],
        )
        out = _client.output_path("image", "png")
        _client.download_file(urls[0], out)
        print(f"[image_generate] {out}")
        return True
    except Exception as e:
        print(f"[image_generate FAIL] {e}")
        return False


def run_speech(cred: dict) -> bool:
    import speech_synthesize
    try:
        audio = speech_synthesize.synthesize(
            "你好,这是 MiniMax 语音合成演示。",
            model="speech-2.8-turbo",
            voice="male-qn-qingse",
            api_key=cred["api_key"], base_url=cred["base_url"], timeout=cred["timeout"],
        )
        out = _client.output_path("speech", "mp3")
        out.write_bytes(audio)
        print(f"[speech_synthesize] {out} ({len(audio)} bytes)")
        return True
    except Exception as e:
        print(f"[speech_synthesize FAIL] {e}")
        return False


def run_music(cred: dict) -> bool:
    import music_generate
    try:
        audio_bytes, _ = music_generate.generate(
            "轻快流行,夏日海边",
            lyrics="[verse]\n阳光洒在海面上\n浪花拍打着脚丫\n[chorus]\n夏天夏天你来啦",
            model="music-3.0",
            output_format="hex",
            api_key=cred["api_key"], base_url=cred["base_url"], timeout=300,
        )
        out = _client.output_path("music", "mp3")
        out.write_bytes(audio_bytes)
        print(f"[music_generate] {out} ({len(audio_bytes)} bytes)")
        return True
    except Exception as e:
        print(f"[music_generate FAIL] {e}")
        return False


def run_vision(cred: dict) -> bool:
    """跑视觉需要图片,用刚生成的图(image_generate 跑成功的话)。"""
    import vision_describe
    # 找最新的一张图
    out_dir = Path(__file__).resolve().parent.parent / "output"
    imgs = sorted(out_dir.glob("image_*.png"), key=lambda p: p.stat().st_mtime, reverse=True)
    if not imgs:
        print("[vision_describe SKIP] 没找到图(image_generate 失败?)")
        return False
    try:
        result = vision_describe.describe(
            str(imgs[0]),
            "用中文描述这张图。",
            model="MiniMax-M3",
            api_key=cred["api_key"], base_url=cred["base_url"], timeout=cred["timeout"],
        )
        print(f"[vision_describe] {result[:100]}")
        return True
    except Exception as e:
        print(f"[vision_describe FAIL] {e}")
        return False


def run_video(cred: dict) -> bool:
    import video_generate
    try:
        url = video_generate.generate_hailuo(
            "a cat playing with a ball",
            model="MiniMax-Hailuo-2.3",
            duration=6,
            resolution="768P",
            api_key=cred["api_key"], base_url=cred["base_url"], timeout=cred["timeout"],
        )
        out = _client.output_path("video", "mp4")
        _client.download_file(url, out, timeout=300)
        print(f"[video_generate] {out}")
        return True
    except Exception as e:
        print(f"[video_generate FAIL] {e}")
        return False


def main() -> int:
    parser = argparse.ArgumentParser(description="MiniMax 6 大模态 demo 编排")
    parser.add_argument("--include-video", action="store_true")
    args = parser.parse_args()

    _client.setup_logging()

    try:
        cred = _client.get_credentials()
    except Exception as e:
        print(f"[FATAL] {e}")
        return 1

    print(f"region={cred['region']} key={_client.mask_key(cred['api_key'])}\n")

    results = {}
    results["text_chat"] = run_text_chat(cred)
    results["image_generate"] = run_image_gen(cred)
    results["vision_describe"] = run_vision(cred)
    results["speech_synthesize"] = run_speech(cred)
    results["music_generate"] = run_music(cred)
    if args.include_video:
        results["video_generate"] = run_video(cred)

    print("\n" + "=" * 50)
    print("SUMMARY")
    for k, v in results.items():
        print(f"  {'✅' if v else '❌'} {k}")
    print("=" * 50)
    return 0 if all(results.values()) else 1


if __name__ == "__main__":
    sys.exit(main())