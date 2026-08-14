"""MiniMax 视频生成 — Hailuo-2.3(同步) / MiniMax-H3(异步多模态)。

端点:
  V1(同步) POST /v1/video_generation → POST /v1/query/video_generation
  V2(异步) POST /v1/video/generation  → GET  /v1/query/video/generation

用法:
  # Hailuo-2.3 同步
  python video_generate.py --prompt "猫追蝴蝶" --out cat.mp4
  # MiniMax-H3 异步 + 参考图
  python video_generate.py --model MiniMax-H3 --prompt "保持角色" \\
      --reference-image character.png --out h3.mp4
  # H3 首尾帧
  python video_generate.py --model MiniMax-H3 --prompt "镜头推近" \\
      --first-frame start.png --last-frame end.png --out fl.mp4
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _client  # noqa: E402

# V1(同步,Hailuo-2.3)
V1_CREATE = "/v1/video_generation"
V1_QUERY = "/v1/query/video_generation"
# V2(异步,MiniMax-H3)— 注意是 /v2/ 不是 /v1/
V2_CREATE = "/v2/video_generation"
V2_QUERY = "/v2/query/video_generation"

HAILUO_MODELS = ["MiniMax-Hailuo-2.3", "MiniMax-Hailuo-2.3-Fast", "MiniMax-Hailuo-02"]


def generate_hailuo(
    prompt: str,
    *,
    model: str = "MiniMax-Hailuo-2.3",
    duration: int = 6,
    resolution: str = "768P",
    api_key: str,
    base_url: str,
    timeout: int,
) -> str:
    """Hailuo V1 同步生成,轮询直到完成,返回下载 URL。"""
    headers = _client.auth_headers(api_key)
    body = {
        "model": model,
        "prompt": prompt,
        "duration": duration,  # 6 / 10
        "resolution": resolution,  # 768P / 1080P
    }
    create_resp = _client.request(
        "POST", base_url + V1_CREATE,
        headers=headers, json_body=body, timeout=timeout,
    )
    task_id = create_resp.get("task_id")
    if not task_id:
        raise RuntimeError(f"V1 创建响应缺 task_id:{json.dumps(create_resp, ensure_ascii=False)[:300]}")
    _client.LOG.info("Hailuo V1 task_id=%s — 轮询中", task_id)

    # 轮询 V1 接口
    query_url = f"{base_url}{V1_QUERY}?task_id={task_id}"
    result = _client.poll_task(
        query_url, headers=headers, interval=5.0, timeout=600.0,
        done_status=("Success", "Finished"), fail_status=("Fail", "Failed"),
    )
    # V1 字段:file_id + base_resp.status_code
    file_id = result.get("file_id")
    if not file_id:
        raise RuntimeError(f"V1 响应缺 file_id:{json.dumps(result, ensure_ascii=False)[:300]}")

    # 通过 file 接口获取下载 URL
    file_info = _client.request(
        "GET", f"{base_url}/v1/files/retrieve?file_id={file_id}",
        headers=headers, timeout=timeout,
    )
    # 响应格式:{file: {file_id, bytes, ..., download_url}, base_resp}
    file_obj = file_info.get("file") if isinstance(file_info.get("file"), dict) else file_info
    url = file_obj.get("download_url") or file_info.get("download_url") or file_obj.get("url") or file_info.get("url")
    if not url:
        raise RuntimeError(f"file 接口响应缺 url:{json.dumps(file_info, ensure_ascii=False)[:300]}")
    return url


def generate_h3(
    prompt: str,
    *,
    reference_image: Path | None = None,
    first_frame: Path | None = None,
    last_frame: Path | None = None,
    reference_video: Path | None = None,
    reference_audio: Path | None = None,
    duration: int = 5,
    resolution: str = "768P",
    aspect_ratio: str = "16:9",
    api_key: str,
    base_url: str,
    timeout: int,
) -> str:
    """MiniMax-H3 V2 异步生成,支持多模态 content 输入。"""
    headers = _client.auth_headers(api_key)

    # 构建多模态 content 数组
    # H3 用 image_url/video_url/audio_url + role + 公网 URL(不推荐 base64,会撞 64MB 上限)
    content: list = []
    if reference_image:
        role = "first_frame" if first_frame else "reference_image"
        content.append({
            "type": "image_url",
            "role": role,
            "image_url": _client.file_to_base64(Path(reference_image)),
        })
    if first_frame and not reference_image:
        content.append({
            "type": "image_url",
            "role": "first_frame",
            "image_url": _client.file_to_base64(Path(first_frame)),
        })
    if last_frame:
        content.append({
            "type": "image_url",
            "role": "last_frame",
            "image_url": _client.file_to_base64(Path(last_frame)),
        })
    if reference_video:
        content.append({
            "type": "video_url",
            "role": "reference_video",
            "video_url": _client.file_to_base64(Path(reference_video)),
        })
    if reference_audio:
        content.append({
            "type": "audio_url",
            "role": "reference_audio",
            "audio_url": _client.file_to_base64(Path(reference_audio)),
        })
    content.append({"type": "text", "text": prompt})

    body = {
        "model": "MiniMax-H3",
        "content": content,
        "duration": duration,  # 4 ~ 15 整数
        "resolution": resolution,  # 768P / 2K(必填)
        "ratio": aspect_ratio,  # 注意是 ratio 不是 aspect_ratio
    }

    create_resp = _client.request(
        "POST", base_url + V2_CREATE,
        headers=headers, json_body=body, timeout=timeout,
    )
    task_id = create_resp.get("task_id")
    if not task_id:
        raise RuntimeError(f"H3 V2 创建响应缺 task_id:{json.dumps(create_resp, ensure_ascii=False)[:300]}")
    _client.LOG.info("H3 V2 task_id=%s — 轮询中", task_id)

    query_url = f"{base_url}{V2_QUERY}?task_id={task_id}"
    result = _client.poll_task(
        query_url, headers=headers, interval=8.0, timeout=900.0,
        done_status=("Success", "succeeded"), fail_status=("Fail", "failed"),
    )
    # H3 V2 响应:{"task": {"id":..., "status":"succeeded", "content": {"url": "..."}}}
    task = result.get("task") or result
    inner_content = task.get("content")
    url = None
    if isinstance(inner_content, dict):
        url = inner_content.get("url")
    elif isinstance(inner_content, list) and inner_content:
        url = inner_content[0].get("url")
    if not url:
        raise RuntimeError(f"H3 V2 响应缺 url:{json.dumps(result, ensure_ascii=False)[:300]}")
    return url


def main() -> int:
    _client.setup_logging()
    parser = argparse.ArgumentParser(description="MiniMax 视频生成")
    parser.add_argument("--prompt", required=True)
    parser.add_argument("--model", default="MiniMax-Hailuo-2.3",
                        choices=HAILUO_MODELS + ["MiniMax-H3"])
    parser.add_argument("--duration", type=int, default=6)
    parser.add_argument("--resolution", default="768P", choices=["768P", "1080P", "2K"])
    parser.add_argument("--aspect-ratio", default="16:9",
                        choices=["16:9", "9:16", "1:1"])
    parser.add_argument("--reference-image", help="H3 多模态参考图")
    parser.add_argument("--first-frame", help="H3 首帧图")
    parser.add_argument("--last-frame", help="H3 尾帧图")
    parser.add_argument("--reference-video", help="H3 参考视频")
    parser.add_argument("--reference-audio", help="H3 参考音频")
    parser.add_argument("--out", help="输出文件")
    parser.add_argument("--api-key", default=None)
    args = parser.parse_args()

    cred = _client.get_credentials()
    if args.api_key:
        cred["api_key"] = args.api_key

    try:
        if args.model == "MiniMax-H3":
            url = generate_h3(
                args.prompt,
                reference_image=Path(args.reference_image) if args.reference_image else None,
                first_frame=Path(args.first_frame) if args.first_frame else None,
                last_frame=Path(args.last_frame) if args.last_frame else None,
                reference_video=Path(args.reference_video) if args.reference_video else None,
                reference_audio=Path(args.reference_audio) if args.reference_audio else None,
                duration=args.duration,
                resolution=args.resolution,
                aspect_ratio=args.aspect_ratio,
                api_key=cred["api_key"],
                base_url=cred["base_url"],
                timeout=cred["timeout"],
            )
        else:
            url = generate_hailuo(
                args.prompt,
                model=args.model,
                duration=args.duration,
                resolution=args.resolution,
                api_key=cred["api_key"],
                base_url=cred["base_url"],
                timeout=cred["timeout"],
            )
        print(f"[model={args.model}] video URL: {url}")
        out = _client.output_path("video", "mp4", args.out)
        _client.download_file(url, out, timeout=300)
        print(f"[saved] {out}")
        return 0
    except Exception as e:
        print(f"[ERROR] {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())