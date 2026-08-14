"""MiniMax 图像理解(看图说话) — 走 M3 多模态对话。

端点:复用 /v1/text/chatcompletion_v2,content 传入图片(URL 或 base64 data URI)。

用法:
  python vision_describe.py --image photo.jpg --prompt "图里有什么?"
  python vision_describe.py --image https://example.com/photo.jpg --prompt "这是什么品种?"
  python vision_describe.py --image photo.png --prompt "用中文描述这张图" \\
      --system "只描述主要对象,不展开背景"
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _client  # noqa: E402

ENDPOINT = "/v1/text/chatcompletion_v2"
DEFAULT_MODEL = "MiniMax-M3"


def describe(
    image: str,
    prompt: str,
    *,
    model: str = DEFAULT_MODEL,
    system: str | None = None,
    max_tokens: int = 1024,
    api_key: str,
    base_url: str,
    timeout: int,
) -> str:
    """图片理解:本地路径 → data URI;URL 直传。"""
    headers = _client.auth_headers(api_key)

    # 决定图片来源
    image_input: str
    if image.startswith(("http://", "https://")):
        image_input = image
    else:
        p = Path(image)
        if not p.exists():
            raise FileNotFoundError(f"图片不存在:{p}")
        image_input = _client.file_to_base64(p)

    messages: list = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({
        "role": "user",
        "content": [
            {"type": "text", "text": prompt},
            {
                "type": "image_url",
                "image_url": {"url": image_input},
            },
        ],
    })

    body = {
        "model": model,
        "messages": messages,
        "max_tokens": max_tokens,
    }
    data = _client.request(
        "POST", base_url + ENDPOINT,
        headers=headers, json_body=body, timeout=timeout,
    )
    # 检查 base_resp.status_code(MiniMax 业务错误,200 OK 但状态码非 0)
    base_resp = data.get("base_resp") if isinstance(data.get("base_resp"), dict) else {}
    err_code = base_resp.get("status_code")
    if err_code is not None and err_code != 0:
        raise RuntimeError(
            f"vision 调用失败:status_code={err_code} {base_resp.get('status_msg', '')}"
        )
    # 返回 message.content;若空(CoT 被 max_tokens 截断),调用方应提高 max_tokens
    msg = data.get("choices", [{}])[0].get("message", {})
    return msg.get("content") or ""


def main() -> int:
    _client.setup_logging()
    parser = argparse.ArgumentParser(description="MiniMax 图像理解")
    parser.add_argument("--image", required=True, help="本地路径或 URL")
    parser.add_argument("--prompt", default="请详细描述这张图片。",
                        help="针对图片的提问")
    parser.add_argument("--model", default=DEFAULT_MODEL,
                        choices=["MiniMax-M3", "MiniMax-M2.7", "MiniMax-M2.5"])
    parser.add_argument("--system", help="系统提示词")
    parser.add_argument("--max-tokens", type=int, default=1024)
    parser.add_argument("--api-key", default=None)
    args = parser.parse_args()

    cred = _client.get_credentials()
    if args.api_key:
        cred["api_key"] = args.api_key

    try:
        result = describe(
            args.image,
            args.prompt,
            model=args.model,
            system=args.system,
            max_tokens=args.max_tokens,
            api_key=cred["api_key"],
            base_url=cred["base_url"],
            timeout=cred["timeout"],
        )
        print(f"[model={args.model}] {args.prompt}")
        print("-" * 50)
        print(result)
        return 0
    except Exception as e:
        print(f"[ERROR] {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())