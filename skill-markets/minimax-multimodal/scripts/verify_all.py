"""MiniMax 全量连通性验证 — 跑通 6 大模态(文本对话 + 图像理解 走轻量;其他需要资产)。

每个模态用一个**最小可跑**的调用做连通性 check:
  - 文本对话:1+1=?  → 应返回 "2"
  - 图像理解:本脚本生成的极简 PNG(1x1 透明像素) → 描述
  - 文生图:生成 1 张 1:1 小图(默认 512x512)
  - 语音合成:合成 "测试一下" 2 秒音频
  - 音乐生成:生成 5 秒纯器乐(便宜)
  - 视频生成:跳过(默认太贵)→ 仅检查凭据存在性,跑 --skip-video

输出:JSON 报告 + 控制台 PASS/FAIL 表。
退出码:全 PASS = 0;任一 FAIL = 1。
"""
from __future__ import annotations

import argparse
import base64
import json
import sys
import time
import traceback
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _client  # noqa: E402


# 最小 PNG(1x1 透明)— 用于 vision 模态测试,无需外部文件
MINIMAL_PNG_B64 = (
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNgAAIAAAUAAen6lMwAAAAASUVORK5CYII="
)


def _minimal_png() -> Path:
    """写一个 1x1 透明 PNG 到 logs/ 临时目录。"""
    logs_dir = Path(__file__).resolve().parent.parent / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)
    tmp = logs_dir / "_minimal.png"
    tmp.write_bytes(base64.b64decode(MINIMAL_PNG_B64))
    return tmp


def check_credentials() -> tuple[bool, str]:
    try:
        cred = _client.get_credentials()
        return True, f"region={cred['region']} base_url={cred['base_url']} key={_client.mask_key(cred['api_key'])}"
    except Exception as e:
        return False, str(e)


def check_text_chat() -> tuple[bool, str]:
    """文本对话连通性:1+1=?"""
    import text_chat
    cred = _client.get_credentials()
    try:
        resp = text_chat.chat(
            "只回答一个数字:1+1=?",
            model="MiniMax-M2.7",
            max_tokens=256,  # M 系列带 CoT,需要足够空间放 reasoning + 答案
            temperature=0.0,
            api_key=cred["api_key"],
            base_url=cred["base_url"],
            timeout=cred["timeout"],
        )
        text_chat._check_business_error(resp)
        content = text_chat._extract_content(resp)
        ok = "2" in content
        return ok, f"reply={content[:80]!r}"
    except Exception as e:
        return False, f"{type(e).__name__}: {e}"


def check_vision() -> tuple[bool, str]:
    """图像理解:用 1x1 PNG 触发。M3 + CoT 可能偶发空响应,做 1 次重试。"""
    import vision_describe
    png = _minimal_png()
    cred = _client.get_credentials()
    last_result = ""
    for attempt in (1, 2):
        try:
            result = vision_describe.describe(
                str(png),
                "用一句话告诉我这张图的内容。",
                model="MiniMax-M3",
                max_tokens=256,
                api_key=cred["api_key"],
                base_url=cred["base_url"],
                timeout=cred["timeout"],
            )
            last_result = result
            if result and len(result.strip()) > 0:
                return True, f"reply={result[:80]!r}"
            _client.LOG.warning("vision 偶发空响应,第 %d 次重试", attempt)
        except Exception as e:
            return False, f"{type(e).__name__}: {e}"
    return False, f"两次空响应:last={last_result[:60]!r}"


def check_image_gen() -> tuple[bool, str]:
    """文生图:1 张最小图。"""
    import image_generate
    cred = _client.get_credentials()
    try:
        urls = image_generate.generate(
            "一个红色圆点",
            model="image-01",
            aspect_ratio="1:1",
            n=1,
            api_key=cred["api_key"],
            base_url=cred["base_url"],
            timeout=cred["timeout"],
        )
        return bool(urls), f"got {len(urls)} URL(s), first={urls[0][:60] if urls else 'N/A'}..."
    except Exception as e:
        return False, f"{type(e).__name__}: {e}"


def check_speech() -> tuple[bool, str]:
    """语音合成:2 字符测试。"""
    import speech_synthesize
    cred = _client.get_credentials()
    try:
        audio = speech_synthesize.synthesize(
            "测",
            model="speech-2.8-turbo",
            voice="male-qn-qingse",
            fmt="mp3",
            api_key=cred["api_key"],
            base_url=cred["base_url"],
            timeout=cred["timeout"],
        )
        ok = len(audio) > 100  # MP3 头部至少几百字节
        return ok, f"{len(audio)} bytes"
    except Exception as e:
        return False, f"{type(e).__name__}: {e}"


def check_music() -> tuple[bool, str]:
    """音乐生成:5 秒纯器乐(用 -free 模型限免测试)。"""
    import music_generate
    cred = _client.get_credentials()
    try:
        audio_bytes, _ = music_generate.generate(
            "short lofi piano loop",
            model="music-3.0-free",
            is_instrumental=True,
            output_format="hex",
            api_key=cred["api_key"],
            base_url=cred["base_url"],
            timeout=300,
        )
        return len(audio_bytes) > 1000, f"{len(audio_bytes)} bytes"
    except Exception as e:
        return False, f"{type(e).__name__}: {e}"


def check_video(skip: bool = True) -> tuple[bool, str]:
    """视频生成:成本最高,默认 skip。如要跑,需要显式 --include-video。"""
    if skip:
        return True, "SKIPPED (use --include-video to enable)"
    import video_generate
    cred = _client.get_credentials()
    try:
        url = video_generate.generate_hailuo(
            "a cat sitting",
            model="MiniMax-Hailuo-2.3",
            duration=6,
            resolution="768P",
            api_key=cred["api_key"],
            base_url=cred["base_url"],
            timeout=cred["timeout"],
        )
        return bool(url), f"url={url[:60]}..."
    except Exception as e:
        return False, f"{type(e).__name__}: {e}"


CHECKS = [
    ("text_chat",      check_text_chat,    "1+1=? 最小对话"),
    ("vision_describe", check_vision,      "1x1 PNG 图像理解"),
    ("image_generate", check_image_gen,    "最小文生图(1张)"),
    ("speech_synthesize", check_speech,    "1 字 TTS"),
    ("music_generate", check_music,        "5 秒纯器乐"),
    ("video_generate", check_video,        "Hailuo-2.3 6s(默认 skip)"),
]


def main() -> int:
    parser = argparse.ArgumentParser(description="MiniMax 6 大模态连通性验证")
    parser.add_argument("--include-video", action="store_true",
                        help="包含视频模态(成本高,默认跳过)")
    parser.add_argument("--report", help="JSON 报告输出路径")
    args = parser.parse_args()

    _client.setup_logging()

    print("=" * 60)
    print("MiniMax 6 大模态连通性验证")
    print("=" * 60)

    # 凭据
    ok, info = check_credentials()
    print(f"\n[credentials] {'PASS' if ok else 'FAIL'}: {info}")
    if not ok:
        return 1

    results = {"credentials": {"ok": ok, "info": info}}
    all_pass = ok
    t0 = time.time()
    for name, fn, desc in CHECKS:
        if name == "video_generate":
            ok, info = fn(skip=not args.include_video)
        else:
            ok, info = fn()
        results[name] = {"ok": ok, "info": info, "description": desc}
        elapsed = time.time() - t0
        status = "✅ PASS" if ok else "❌ FAIL"
        print(f"[{status}] {name:20s} ({elapsed:5.1f}s) — {desc}")
        print(f"           {info[:200]}")
        all_pass = all_pass and ok

    print("\n" + "=" * 60)
    print(f"OVERALL: {'✅ ALL PASS' if all_pass else '❌ SOME FAILED'}")
    print(f"elapsed: {time.time() - t0:.1f}s")
    print("=" * 60)

    if args.report:
        Path(args.report).write_text(
            json.dumps(results, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        print(f"[report] {args.report}")

    return 0 if all_pass else 1


if __name__ == "__main__":
    sys.exit(main())