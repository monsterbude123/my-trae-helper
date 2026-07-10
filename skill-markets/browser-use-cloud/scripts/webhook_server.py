#!/usr/bin/env python3
"""Browser Use Cloud — Webhook 接收服务器

接收 Browser Use Cloud 的 webhook 通知，验证 HMAC-SHA256 签名，处理事件。

用法:
    # 启动服务器
    export WEBHOOK_SECRET=your_webhook_secret
    python webhook_server.py --port 8000

    # 开发测试（用 ngrok 暴露）
    ngrok http 8000
    # 将 ngrok URL 设为 Dashboard 中的 webhook endpoint

    # 测试 ping
    curl -X POST http://localhost:8000/webhook \
      -H "Content-Type: application/json" \
      -d '{"type":"test","timestamp":"2025-01-01T00:00:00Z","payload":{}}'

依赖:
    pip install fastapi uvicorn
    export WEBHOOK_SECRET=your_webhook_secret
"""

import argparse
import hashlib
import hmac
import json
import os
import time

from fastapi import FastAPI, Request, HTTPException

app = FastAPI(title="Browser Use Webhook Receiver")

WEBHOOK_SECRET = os.environ.get("WEBHOOK_SECRET", "")

# 事件存储（生产环境应替换为数据库）
event_log: list[dict] = []


def verify_signature(body: bytes, signature: str, timestamp: str, secret: str) -> bool:
    """验证 HMAC-SHA256 签名并防重放攻击。

    Args:
        body: 请求体（原始 bytes）
        signature: X-Browser-Use-Signature header
        timestamp: X-Browser-Use-Timestamp header（Unix 秒）
        secret: Webhook secret

    Returns:
        bool: 签名有效且时间戳在 5 分钟内
    """
    # 防重放：拒绝 5 分钟前的请求
    try:
        ts = int(timestamp)
    except (ValueError, TypeError):
        return False
    if abs(time.time() - ts) > 300:
        return False

    # 验证签名
    payload = json.loads(body)
    message = f"{timestamp}.{json.dumps(payload, separators=(',', ':'), sort_keys=True)}"
    expected = hmac.new(secret.encode(), message.encode(), hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, signature)


@app.post("/webhook")
async def handle_webhook(request: Request):
    """接收并验证 webhook 事件。"""
    if not WEBHOOK_SECRET:
        raise HTTPException(status_code=500, detail="WEBHOOK_SECRET not configured")

    body = await request.body()
    signature = request.headers.get("x-browser-use-signature", "")
    timestamp = request.headers.get("x-browser-use-timestamp", "")

    # 验证签名
    if not verify_signature(body, signature, timestamp, WEBHOOK_SECRET):
        raise HTTPException(status_code=401, detail="Invalid signature or expired request")

    payload = json.loads(body)
    event_type = payload.get("type", "unknown")
    event_data = payload.get("payload", {})

    # 存储事件
    event_log.append({
        "type": event_type,
        "timestamp": payload.get("timestamp"),
        "payload": event_data,
    })
    # 只保留最近 1000 条
    if len(event_log) > 1000:
        event_log.pop(0)

    # 处理不同类型事件
    if event_type == "agent.task.status_update":
        task_id = event_data.get("task_id", "?")
        session_id = event_data.get("session_id", "?")
        status = event_data.get("status", "?")
        metadata = event_data.get("metadata", {})
        print(f"📡 Task {task_id} → {status} (session: {session_id})")
        if metadata:
            print(f"   Metadata: {metadata}")

    elif event_type == "test":
        print("🧪 Webhook test ping received")

    else:
        print(f"📦 Unknown event type: {event_type}")

    return {"status": "ok", "event_type": event_type}


@app.get("/events")
async def list_events(limit: int = 50):
    """列出最近的 webhook 事件。"""
    return event_log[-limit:]


@app.get("/health")
async def health_check():
    """健康检查端点。"""
    return {
        "status": "ok",
        "events_received": len(event_log),
        "secret_configured": bool(WEBHOOK_SECRET),
    }


if __name__ == "__main__":
    import uvicorn

    parser = argparse.ArgumentParser(description="Browser Use Webhook 接收服务器")
    parser.add_argument("--port", "-p", type=int, default=8000, help="监听端口（默认 8000）")
    parser.add_argument("--host", type=str, default="0.0.0.0", help="监听地址（默认 0.0.0.0）")
    args = parser.parse_args()

    if not WEBHOOK_SECRET:
        print("⚠️  WEBHOOK_SECRET 未设置！请设置环境变量:")
        print("   export WEBHOOK_SECRET=your_webhook_secret")
        print("   获取: cloud.browser-use.com/settings?tab=webhooks\n")

    print(f"🚀 Webhook 服务器启动: http://{args.host}:{args.port}")
    print(f"   Webhook 端点: POST /webhook")
    print(f"   事件列表:    GET /events")
    print(f"   健康检查:    GET /health")
    print(f"   本地测试:    curl -X POST http://localhost:{args.port}/webhook -d '{{\"type\":\"test\",\"timestamp\":\"...\",\"payload\":{{}}}}'\n")

    uvicorn.run(app, host=args.host, port=args.port)
