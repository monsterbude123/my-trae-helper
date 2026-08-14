"""MiniMax 语音合成 — speech-2.8-hd / speech-2.8-turbo / speech-2.6 系列。

端点:POST /v1/t2a_v2
能力:300+ 系统音色、复刻音色、音量/语调/语速、mp3/pcm/flac/wav 格式、流式输出。

用法:
  python speech_synthesize.py --text "你好世界" --out hello.mp3
  python speech_synthesize.py --text "Hello world" --voice English_magnetic_voiced_man \\
      --speed 1.2 --format mp3
  python speech_synthesize.py --text "Hi" --stream
"""
from __future__ import annotations

import argparse
import base64
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _client  # noqa: E402

ENDPOINT = "/v1/t2a_v2"

DEFAULT_MODEL = "speech-2.8-hd"
SUPPORTED = [
    "speech-2.8-hd", "speech-2.8-turbo",
    "speech-2.6-hd", "speech-2.6-turbo",
    "speech-02-hd", "speech-02-turbo",
]

# 常用音色(更多用 --voices 查询)
DEFAULT_VOICES = {
    "zh": "male-qn-qingse",   # 中文青年男声
    "en": "English_magnetic_voiced_man",
    "jp": "Japanese_Graceful_Lady",
}


def list_voices(api_key: str, base_url: str, timeout: int, language: str | None = None) -> list:
    """列出可用音色。GET /v1/voice/list?language=en"""
    headers = _client.auth_headers(api_key)
    url = f"{base_url}/v1/voice/list"
    if language:
        url += f"?language={language}"
    data = _client.request("GET", url, headers=headers, timeout=timeout)
    return data.get("voice_list") or data.get("voices") or data.get("data") or []


def synthesize(
    text: str,
    *,
    model: str = DEFAULT_MODEL,
    voice: str = DEFAULT_VOICES["zh"],
    speed: float = 1.0,
    vol: float = 1.0,
    pitch: int = 0,
    fmt: str = "mp3",
    sample_rate: int = 32000,
    bitrate: int = 128000,
    channels: int = 1,
    stream: bool = False,
    api_key: str,
    base_url: str,
    timeout: int,
) -> bytes:
    """调用 /v1/t2a_v2,返回音频 bytes(MP3/PCM/FLAC/WAV)。"""
    headers = _client.auth_headers(api_key)
    body = {
        "model": model,
        "text": text,
        "stream": stream,
        "voice_setting": {
            "voice_id": voice,
            "speed": speed,
            "vol": vol,
            "pitch": pitch,
        },
        "audio_setting": {
            "format": fmt,
            "sample_rate": sample_rate,
            "bitrate": bitrate,
            "channel": channels,
        },
    }

    if stream:
        # 流式:逐 chunk 收集 hex
        import requests
        chunks: list[bytes] = []
        with requests.post(
            base_url + ENDPOINT,
            headers=headers,
            json=body,
            timeout=timeout,
            stream=True,
        ) as r:
            r.raise_for_status()
            for line in r.iter_lines():
                if not line:
                    continue
                s = line.decode("utf-8", errors="ignore")
                if s.startswith("data:"):
                    payload = s[5:].strip()
                else:
                    payload = s
                if payload in ("[DONE]", ""):
                    continue
                try:
                    obj = json.loads(payload)
                    chunk_hex = (
                        obj.get("data", {}).get("audio")
                        or obj.get("audio")
                        or ""
                    )
                    if chunk_hex:
                        chunks.append(bytes.fromhex(chunk_hex))
                except (json.JSONDecodeError, ValueError):
                    pass
        return b"".join(chunks)

    # 非流式:标准 JSON 响应,音频在 data.audio(hex)
    data = _client.request(
        "POST", base_url + ENDPOINT,
        headers=headers, json_body=body, timeout=timeout,
    )
    audio_hex = (
        data.get("data", {}).get("audio")
        or data.get("audio")
        or ""
    )
    if not audio_hex:
        raise RuntimeError(f"TTS 响应缺 audio:{json.dumps(data, ensure_ascii=False)[:300]}")
    return bytes.fromhex(audio_hex)


def main() -> int:
    _client.setup_logging()
    parser = argparse.ArgumentParser(description="MiniMax 语音合成")
    parser.add_argument("--text", help="要合成的文本(与 --text-file 二选一)")
    parser.add_argument("--text-file", help="从文件读取文本(长文本用这个)")
    parser.add_argument("--model", default=DEFAULT_MODEL, choices=SUPPORTED)
    parser.add_argument("--voice", default=DEFAULT_VOICES["zh"])
    parser.add_argument("--speed", type=float, default=1.0)
    parser.add_argument("--vol", type=float, default=1.0)
    parser.add_argument("--pitch", type=int, default=0)
    parser.add_argument("--format", default="mp3", choices=["mp3", "pcm", "flac", "wav"])
    parser.add_argument("--sample-rate", type=int, default=32000)
    parser.add_argument("--bitrate", type=int, default=128000)
    parser.add_argument("--channels", type=int, default=1, choices=[1, 2])
    parser.add_argument("--stream", action="store_true")
    parser.add_argument("--out", help="输出文件")
    parser.add_argument("--list-voices", action="store_true", help="列出可用音色后退出")
    parser.add_argument("--language", default=None, help="筛选音色语言(zh/en/jp/...)")
    parser.add_argument("--api-key", default=None)
    args = parser.parse_args()

    cred = _client.get_credentials()
    if args.api_key:
        cred["api_key"] = args.api_key

    if args.list_voices:
        voices = list_voices(
            cred["api_key"], cred["base_url"], cred["timeout"], args.language,
        )
        print(f"[voices] {len(voices)} 个音色:")
        for v in voices[:50]:
            if isinstance(v, dict):
                vid = v.get("voice_id") or v.get("id") or v.get("name")
                vlang = v.get("language") or "?"
                print(f"  - {vlang}: {vid}")
            else:
                print(f"  - {v}")
        return 0

    if not args.text and not args.text_file:
        parser.error("需要 --text 或 --text-file")
    text = args.text
    if args.text_file:
        text = Path(args.text_file).read_text(encoding="utf-8")

    try:
        audio_bytes = synthesize(
            text,
            model=args.model,
            voice=args.voice,
            speed=args.speed,
            vol=args.vol,
            pitch=args.pitch,
            fmt=args.format,
            sample_rate=args.sample_rate,
            bitrate=args.bitrate,
            channels=args.channels,
            stream=args.stream,
            api_key=cred["api_key"],
            base_url=cred["base_url"],
            timeout=cred["timeout"],
        )
        out = _client.output_path("speech", args.format, args.out)
        out.write_bytes(audio_bytes)
        print(f"[model={args.model} voice={args.voice}] {len(audio_bytes)} bytes")
        print(f"[saved] {out}")
        return 0
    except Exception as e:
        print(f"[ERROR] {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())