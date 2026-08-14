"""MiniMax 文本对话 — MiniMax-M3 / M2.7 / M2.5 / M2。

端点:POST /v1/text/chatcompletion_v2
兼容 Anthropic SDK 的 /anthropic/v1/messages(参考 README,本脚本仅走自家接口)。

用法:
  python text_chat.py --message "你好"
  python text_chat.py --model MiniMax-M3 --message "写七言绝句" --stream
  python text_chat.py --message "1+1=?" --system "只回答数字"
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _client  # noqa: E402

ENDPOINT = "/v1/text/chatcompletion_v2"

DEFAULT_MODEL = "MiniMax-M2.7"
SUPPORTED = [
    "MiniMax-M3", "MiniMax-M2.7", "MiniMax-M2.7-highspeed",
    "MiniMax-M2.5", "MiniMax-M2.5-highspeed",
    "MiniMax-M2.1", "MiniMax-M2.1-highspeed", "MiniMax-M2",
]


def chat(
    message: str,
    *,
    model: str = DEFAULT_MODEL,
    system: str | None = None,
    max_tokens: int = 512,
    temperature: float = 0.7,
    stream: bool = False,
    api_key: str,
    base_url: str,
    timeout: int,
) -> dict:
    """单轮对话。返回完整响应 dict;stream=True 时只打印到 stdout,返回 None。"""
    headers = _client.auth_headers(api_key)
    messages: list = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": message})

    body = {
        "model": model,
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": temperature,
    }

    if stream:
        body["stream"] = True
        # 流式单独走(复用 request 但仅取增量)
        import requests
        with requests.post(
            base_url + ENDPOINT,
            headers=headers,
            json=body,
            timeout=timeout,
            stream=True,
        ) as r:
            r.raise_for_status()
            collected: list[str] = []
            for line in r.iter_lines():
                if not line:
                    continue
                s = line.decode("utf-8", errors="ignore")
                if s.startswith("data:"):
                    s = s[5:].strip()
                if s in ("[DONE]", ""):
                    continue
                try:
                    chunk = json.loads(s)
                    delta = (
                        chunk.get("choices", [{}])[0]
                        .get("delta", {})
                        .get("content")
                    )
                    if delta:
                        print(delta, end="", flush=True)
                        collected.append(delta)
                except json.JSONDecodeError:
                    pass
            print()
        return {"content": "".join(collected), "model": model}

    return _client.request(
        "POST", base_url + ENDPOINT,
        headers=headers, json_body=body, timeout=timeout,
    )


def _check_business_error(data: dict) -> None:
    """MiniMax 业务错误:200 OK + base_resp.status_code != 0。"""
    base_resp = data.get("base_resp") if isinstance(data.get("base_resp"), dict) else {}
    err_code = base_resp.get("status_code")
    if err_code is not None and err_code != 0:
        raise RuntimeError(
            f"调用失败:status_code={err_code} {base_resp.get('status_msg', '')}"
        )


def _extract_content(data: dict) -> str:
    """提取模型回复内容。

    MiniMax M 系列默认带 chain-of-thought:
      - message.content: 最终答案(主用)
      - message.reasoning_content: 推理文本(CoT 思考过程,非答案)
      - message.reasoning_details[]: 结构化推理段

    正常情况下 content 会有值;若 content 为空,通常是 max_tokens 不够导致
    模型只来得及输出 reasoning 就被截断(响应里 finish_reason="length")。
    调用方应提高 max_tokens(默认建议 ≥512)。

    本函数返回 content;若为空返回空串 + 通过 finish_reason 提示问题。
    """
    msg = (
        data.get("choices", [{}])[0]
        .get("message", {})
    )
    return msg.get("content") or ""


def main() -> int:
    _client.setup_logging()
    parser = argparse.ArgumentParser(description="MiniMax 文本对话")
    parser.add_argument("--message", required=True, help="用户消息")
    parser.add_argument("--model", default=DEFAULT_MODEL, choices=SUPPORTED)
    parser.add_argument("--system", default=None, help="系统提示词")
    parser.add_argument("--max-tokens", type=int, default=512)
    parser.add_argument("--temperature", type=float, default=0.7)
    parser.add_argument("--stream", action="store_true")
    parser.add_argument("--api-key", default=None, help="覆盖环境变量")
    args = parser.parse_args()

    cred = _client.get_credentials()
    if args.api_key:
        cred["api_key"] = args.api_key

    print(f"[model={args.model}] user: {args.message}")
    if args.system:
        print(f"[system] {args.system}")
    print("-" * 50)

    try:
        result = chat(
            args.message,
            model=args.model,
            system=args.system,
            max_tokens=args.max_tokens,
            temperature=args.temperature,
            stream=args.stream,
            api_key=cred["api_key"],
            base_url=cred["base_url"],
            timeout=cred["timeout"],
        )
        if not args.stream:
            _check_business_error(result)
            content = _extract_content(result)
            print(f"assistant: {content}")
        return 0
    except Exception as e:
        print(f"[ERROR] {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())