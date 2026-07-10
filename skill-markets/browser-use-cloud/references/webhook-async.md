# Webhooks & 异步 — 事件通知与签名验证

任务完成时接收实时通知。在 [cloud.browser-use.com/settings?tab=webhooks](https://cloud.browser-use.com/settings?tab=webhooks) 配置 webhook 端点。

---

## 事件类型

| 事件 | 触发时机 |
|------|---------|
| `agent.task.status_update` | 任务状态变化（running / idle / stopped） |
| `test` | Webhook 测试 ping |

## Payload 格式

```json
{
  "type": "agent.task.status_update",
  "timestamp": "2025-01-15T10:30:00Z",
  "payload": {
    "task_id": "task_abc123",
    "session_id": "session_xyz",
    "status": "idle",
    "metadata": {}
  }
}
```

---

## 签名验证

每个 webhook 请求包含两个 header：

- `X-Browser-Use-Signature` — HMAC-SHA256 签名
- `X-Browser-Use-Timestamp` — Unix 时间戳（秒）

签名计算方式：`HMAC-SHA256(secret, "{timestamp}.{body}")`
其中 body 是 JSON 序列化的 payload（key 按字母排序，无多余空格）。

**必须验证签名并拒绝 5 分钟前的请求以防重放攻击。**

### Python 验证函数

```python
import hashlib
import hmac
import json
import time

def verify_webhook(body: bytes, signature: str, timestamp: str, secret: str) -> bool:
    # 拒绝超过 5 分钟的请求
    try:
        ts = int(timestamp)
    except (ValueError, TypeError):
        return False
    if abs(time.time() - ts) > 300:
        return False
    payload = json.loads(body)
    message = f"{timestamp}.{json.dumps(payload, separators=(',', ':'), sort_keys=True)}"
    expected = hmac.new(secret.encode(), message.encode(), hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, signature)
```

---

## FastAPI 完整示例

```python
from fastapi import FastAPI, Request, HTTPException
import hashlib, hmac, json, os, time

app = FastAPI()
WEBHOOK_SECRET = os.environ["WEBHOOK_SECRET"]

@app.post("/webhook")
async def handle_webhook(request: Request):
    body = await request.body()
    signature = request.headers.get("x-browser-use-signature", "")
    timestamp = request.headers.get("x-browser-use-timestamp", "")

    # 防重放
    try:
        ts = int(timestamp)
    except (ValueError, TypeError):
        raise HTTPException(status_code=401, detail="Invalid timestamp")
    if abs(time.time() - ts) > 300:
        raise HTTPException(status_code=401, detail="Request too old")

    # 验证签名
    payload = json.loads(body)
    message = f"{timestamp}.{json.dumps(payload, separators=(',', ':'), sort_keys=True)}"
    expected = hmac.new(WEBHOOK_SECRET.encode(), message.encode(), hashlib.sha256).hexdigest()

    if not hmac.compare_digest(expected, signature):
        raise HTTPException(status_code=401, detail="Invalid signature")

    # 处理事件
    if payload["type"] == "agent.task.status_update":
        task_id = payload["payload"]["task_id"]
        status = payload["payload"]["status"]
        print(f"Task {task_id} is now {status}")

    return {"status": "ok"}
```

---

## Express (Node.js) 完整示例

```typescript
import express from "express";
import { createHmac, timingSafeEqual } from "crypto";

const app = express();
app.use(express.raw({ type: "application/json" }));
const WEBHOOK_SECRET = process.env.WEBHOOK_SECRET!;

function sortKeys(obj: unknown): unknown {
  if (Array.isArray(obj)) return obj.map(sortKeys);
  if (obj !== null && typeof obj === "object") {
    return Object.keys(obj as object).sort().reduce((acc, key) => {
      (acc as Record<string, unknown>)[key] = sortKeys((obj as Record<string, unknown>)[key]);
      return acc;
    }, {} as Record<string, unknown>);
  }
  return obj;
}

app.post("/webhook", (req, res) => {
  const signature = req.headers["x-browser-use-signature"] as string;
  const timestamp = req.headers["x-browser-use-timestamp"] as string;

  if (Math.abs(Date.now() / 1000 - parseInt(timestamp)) > 300) {
    return res.status(401).send("Request too old");
  }

  const body = req.body.toString();
  const payload = JSON.parse(body);
  const message = `${timestamp}.${JSON.stringify(sortKeys(payload))}`;
  const expected = createHmac("sha256", WEBHOOK_SECRET).update(message).digest("hex");

  if (!timingSafeEqual(Buffer.from(expected), Buffer.from(signature))) {
    return res.status(401).send("Invalid signature");
  }

  if (payload.type === "agent.task.status_update") {
    console.log(`Task ${payload.payload.task_id} → ${payload.payload.status}`);
  }

  res.status(200).send("OK");
});

app.listen(3000);
```

---

## 本地开发

使用 ngrok 暴露本地服务：

```bash
ngrok http 3000
```

将 ngrok URL 设置为 Dashboard 中的 webhook endpoint。
