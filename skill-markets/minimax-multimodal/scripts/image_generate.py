"""MiniMax 文生图 / 图生图 — image-01 / image-01-live。

端点:POST /v1/image/generation
支持:T2I(纯文本)、I2I(参考图片 base64 或 URL)、画风(image-01-live)

用法:
  python image_generate.py --prompt "赛博朋克杭州西湖" --out cyber_westlake.png
  python image_generate.py --prompt "日式动漫风格少女" --model image-01-live
  python image_generate.py --prompt "相似风格" --reference-image photo.jpg
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _client  # noqa: E402

ENDPOINT = "/v1/image_generation"

DEFAULT_MODEL = "image-01"
SUPPORTED = ["image-01", "image-01-live"]


def generate(
    prompt: str,
    *,
    model: str = DEFAULT_MODEL,
    aspect_ratio: str = "1:1",
    n: int = 1,
    reference_image: Path | None = None,
    style: str | None = None,
    api_key: str,
    base_url: str,
    timeout: int,
) -> list[str]:
    """生成图像,返回下载 URL 列表。"""
    headers = _client.auth_headers(api_key)
    body: dict = {
        "model": model,
        "prompt": prompt,
        "aspect_ratio": aspect_ratio,
        "n": n,
        "response_format": "url",  # 也可 "base64"
    }
    if reference_image:
        body["subject_reference"] = [{
            "type": "image",
            "image_file": _client.file_to_base64(Path(reference_image)),
        }]
    if style and model == "image-01-live":
        body["style"] = style  # 例如 "日式动漫"、"水墨画"

    data = _client.request(
        "POST", base_url + ENDPOINT,
        headers=headers, json_body=body, timeout=timeout,
    )
    # 响应格式:{"data": {"image_urls": [...]}, "base_resp": {...}}
    # 或旧的:{"image_urls": [...], "metadata": {...}}
    urls = (
        data.get("data", {}).get("image_urls")
        if isinstance(data.get("data"), dict)
        else None
    ) or data.get("image_urls") or data.get("data", [])
    if isinstance(urls, str):
        urls = [urls]
    if not urls:
        raise RuntimeError(f"响应无图像 URL:{json.dumps(data, ensure_ascii=False)[:300]}")
    return urls if isinstance(urls, list) else [urls]


def main() -> int:
    _client.setup_logging()
    parser = argparse.ArgumentParser(description="MiniMax 文生图")
    parser.add_argument("--prompt", required=True)
    parser.add_argument("--model", default=DEFAULT_MODEL, choices=SUPPORTED)
    parser.add_argument("--aspect-ratio", default="1:1",
                        choices=["1:1", "16:9", "9:16", "4:3", "3:4", "16:10"])
    parser.add_argument("--n", type=int, default=1)
    parser.add_argument("--reference-image", help="图生图参考图(本地路径)")
    parser.add_argument("--style", help="画风(仅 image-01-live)")
    parser.add_argument("--out", help="输出文件路径(多张时仅保存第一张)")
    parser.add_argument("--api-key", default=None)
    args = parser.parse_args()

    cred = _client.get_credentials()
    if args.api_key:
        cred["api_key"] = args.api_key

    try:
        urls = generate(
            args.prompt,
            model=args.model,
            aspect_ratio=args.aspect_ratio,
            n=args.n,
            reference_image=Path(args.reference_image) if args.reference_image else None,
            style=args.style,
            api_key=cred["api_key"],
            base_url=cred["base_url"],
            timeout=cred["timeout"],
        )
        print(f"[model={args.model}] 生成 {len(urls)} 张图")
        for i, u in enumerate(urls):
            print(f"  [{i}] {u}")
        # 默认下载第一张
        out = _client.output_path("image", "png", args.out)
        _client.download_file(urls[0], out)
        print(f"[saved] {out}")
        return 0
    except Exception as e:
        print(f"[ERROR] {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())