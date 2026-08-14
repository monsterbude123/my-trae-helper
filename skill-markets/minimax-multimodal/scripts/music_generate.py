"""MiniMax 音乐生成 — music-3.0 / music-2.6 / music-cover。

端点:POST /v1/music_generation
能力:文生歌(prompt + lyrics)、纯器乐(is_instrumental)、自动歌词(lyrics_optimizer)、
     翻唱(music-cover,需参考音频)、结构化 prompt(vocals/genre/mood/bpm/key)。

用法:
  python music_generate.py --prompt "轻快流行" --lyrics "[verse] 阳光洒海面" --out song.mp3
  python music_generate.py --prompt "电影管弦乐" --instrumental --out bgm.mp3
  python music_generate.py --prompt "Indie folk" --audio-file original.mp3 --out cover.mp3
  python music_generate.py --prompt "Indie folk, melancholic" --lyrics-optimizer --out song.mp3
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _client  # noqa: E402

ENDPOINT = "/v1/music_generation"

DEFAULT_MODEL = "music-3.0"
SUPPORTED = [
    "music-3.0", "music-3.0-free",
    "music-2.6", "music-2.6-free",
    "music-cover", "music-cover-free",
]


def generate(
    prompt: str,
    *,
    lyrics: str | None = None,
    lyrics_optimizer: bool = False,
    is_instrumental: bool = False,
    vocals: str | None = None,
    genre: str | None = None,
    mood: str | None = None,
    instruments: str | None = None,
    bpm: int | None = None,
    key: str | None = None,
    audio_file: Path | None = None,
    cover_feature_id: str | None = None,
    model: str = DEFAULT_MODEL,
    output_format: str = "url",
    api_key: str,
    base_url: str,
    timeout: int,
) -> tuple[bytes, str | None]:
    """生成音乐,返回 (audio_bytes, mime_type)。"""
    headers = _client.auth_headers(api_key)

    # 翻唱
    if model.startswith("music-cover") or audio_file:
        if not prompt:
            raise ValueError("翻唱模式需要 --prompt 描述风格")
        body: dict = {
            "model": model if model.startswith("music-cover") else "music-cover-free",
            "prompt": prompt,
            "output_format": output_format,
        }
        if audio_file:
            body["audio_url"] = _client.file_to_base64(Path(audio_file))
        if cover_feature_id:
            body["cover_feature_id"] = cover_feature_id
        if lyrics:
            body["lyrics"] = lyrics
    else:
        # 普通音乐生成
        body = {
            "model": model,
            "prompt": prompt,
            "output_format": output_format,  # url / hex
            "audio_setting": {
                "sample_rate": 44100,
                "bitrate": 256000,
                "format": "mp3",
            },
        }
        if is_instrumental:
            body["is_instrumental"] = True
        else:
            if lyrics:
                body["lyrics"] = lyrics
            if lyrics_optimizer:
                body["lyrics_optimizer"] = True
        # 结构化字段(music-3.0 推荐)
        if any([vocals, genre, mood, instruments, bpm, key]):
            body["structured_prompt"] = {
                k: v for k, v in {
                    "vocals": vocals,
                    "genre": genre,
                    "mood": mood,
                    "instruments": instruments,
                    "bpm": bpm,
                    "key": key,
                }.items() if v is not None
            }

    # 异步 or 同步?音乐走同步轮询
    data = _client.request(
        "POST", base_url + ENDPOINT,
        headers=headers, json_body=body, timeout=300,
    )

    # 解析:可能直接返回 audio bytes 也可能返回 URL
    status = data.get("base_resp", {}).get("status_code", 0)
    if status and status != 0:
        raise RuntimeError(f"音乐生成失败:status={status} {data.get('base_resp', {}).get('status_msg')}")

    # 响应格式:{data: {audio: hex, status: 2}, extra_info: {...}, base_resp: {...}}
    # 或 url 模式:{data: {audio_url: "..."}}
    data_obj = data.get("data") if isinstance(data.get("data"), dict) else {}

    if output_format == "url":
        url = data_obj.get("audio_url") or data.get("audio_url") or data.get("audio")
        if not url:
            raise RuntimeError(f"响应缺 audio_url:{json.dumps(data, ensure_ascii=False)[:300]}")
        # 下载
        import requests
        with requests.get(url, timeout=120) as r:
            r.raise_for_status()
            return r.content, "audio/mpeg"
    else:
        # hex 格式
        hex_audio = data_obj.get("audio") or data.get("audio") or ""
        if not hex_audio:
            raise RuntimeError(f"响应缺 audio hex:{json.dumps(data, ensure_ascii=False)[:300]}")
        return bytes.fromhex(hex_audio), "audio/mpeg"


def main() -> int:
    _client.setup_logging()
    parser = argparse.ArgumentParser(description="MiniMax 音乐生成")
    parser.add_argument("--prompt", required=True, help="音乐风格/灵感描述")
    parser.add_argument("--lyrics", help="歌词文本([verse]/[chorus] 等标签)")
    parser.add_argument("--lyrics-optimizer", action="store_true",
                        help="自动从 prompt 生成歌词")
    parser.add_argument("--instrumental", action="store_true", help="纯器乐(无人声)")
    parser.add_argument("--vocals", help="结构化:人声描述")
    parser.add_argument("--genre", help="结构化:流派")
    parser.add_argument("--mood", help="结构化:情绪")
    parser.add_argument("--instruments", help="结构化:乐器")
    parser.add_argument("--bpm", type=int, help="结构化:速度")
    parser.add_argument("--key", help="结构化:调性")
    parser.add_argument("--audio-file", help="翻唱参考音频(本地)")
    parser.add_argument("--cover-feature-id", help="翻唱预处理 ID")
    parser.add_argument("--model", default=DEFAULT_MODEL, choices=SUPPORTED)
    parser.add_argument("--output-format", default="url", choices=["url", "hex"])
    parser.add_argument("--out", help="输出文件")
    parser.add_argument("--api-key", default=None)
    args = parser.parse_args()

    cred = _client.get_credentials()
    if args.api_key:
        cred["api_key"] = args.api_key

    try:
        audio_bytes, mime = generate(
            args.prompt,
            lyrics=args.lyrics,
            lyrics_optimizer=args.lyrics_optimizer,
            is_instrumental=args.instrumental,
            vocals=args.vocals,
            genre=args.genre,
            mood=args.mood,
            instruments=args.instruments,
            bpm=args.bpm,
            key=args.key,
            audio_file=Path(args.audio_file) if args.audio_file else None,
            cover_feature_id=args.cover_feature_id,
            model=args.model,
            output_format=args.output_format,
            api_key=cred["api_key"],
            base_url=cred["base_url"],
            timeout=cred["timeout"],
        )
        out = _client.output_path("music", "mp3", args.out)
        out.write_bytes(audio_bytes)
        print(f"[model={args.model}] {len(audio_bytes)} bytes ({mime})")
        print(f"[saved] {out}")
        return 0
    except Exception as e:
        print(f"[ERROR] {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())