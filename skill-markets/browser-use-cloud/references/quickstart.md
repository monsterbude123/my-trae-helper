# Quickstart — Cloud API 快速入门

> ⚠️ 这是 **Cloud API**（`browser-use-sdk`）快速入门。
> **本地版**（开源 `browser-use[core]`）请读 [`references/local-usage.md`](local-usage.md)。

## 安装

```bash
# Python
pip install browser-use-sdk

# TypeScript
npm install browser-use-sdk
```

## 获取 API Key

1. 打开 [cloud.browser-use.com/settings](https://cloud.browser-use.com/settings?tab=api-keys&new=1)
2. 创建 API Key（以 `bu_` 开头）
3. 设置环境变量：

```bash
export BROWSER_USE_API_KEY=bu_your_key_here
```

## Agent 自主注册（无需人类操作）

AI Agent 可以通过以下步骤自主创建免费账号：

### REST 流程

**Step 1: 请求挑战**
```bash
curl -X POST https://api.browser-use.com/cloud/signup \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "name": "User Name"}'
```

响应：
```json
{
  "challenge_id": "uuid",
  "challenge_text": "..."
}
```

**Step 2: 解决数学题**

读取 `challenge_text` 中的数学题，求解后保留两位小数，如 `"144.00"`。

**Step 3: 验证答案**
```bash
curl -X POST https://api.browser-use.com/cloud/signup/verify \
  -H "Content-Type: application/json" \
  -d '{"challenge_id":"uuid","answer":"144.00"}'
```

响应：
```json
{
  "api_key": "bu_..."
}
```

**Step 4: 创建 Claim Link（可选，供人类认领账号）**
```bash
curl -X POST https://api.browser-use.com/cloud/signup/claim \
  -H "X-Browser-Use-API-Key: bu_..."
```

响应：
```json
{
  "claim_url": "https://..."
}
```
Claim URL 有效期 1 小时。

### CLI 方式

```bash
browser-use cloud signup
browser-use cloud signup --verify <challenge-id> <answer>
browser-use cloud signup --claim
```

CLI 将 API key 保存到 `~/.browser-use/config.json`。

## 第一个任务

### Python

```python
import asyncio
from browser_use_sdk.v3 import AsyncBrowserUse

async def main():
    client = AsyncBrowserUse()
    result = await client.run("List the top 20 posts on Hacker News today with their points")
    print(result.output)

asyncio.run(main())
```

### TypeScript

```typescript
import { BrowserUse } from "browser-use-sdk/v3";

const client = new BrowserUse();
const result = await client.run("List the top 20 posts on Hacker News today with their points");
console.log(result.output);
```

### curl（直接调 API）

```bash
curl -X POST https://api.browser-use.com/api/v3/sessions \
  -H "X-Browser-Use-API-Key: YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"task": "List the top 20 posts on Hacker News today with their points"}'
```

## 完整应用示例

参见 [Chat UI tutorial](https://docs.browser-use.com/cloud/tutorials/chat-ui)。

## SDK 说明

SDK 是 [API v3](https://docs.browser-use.com/cloud/api-reference) 的薄封装，所有 API 端点都对应 SDK 方法：

- `client.sessions` — session 管理
- `client.browsers` — 浏览器管理
- `client.profiles` — profile 管理
- `client.workspaces` — workspace 管理
- `client.billing` — 计费查询

`client.run()` 创建 session → 每 2 秒轮询直到完成（最长 4 小时）→ 返回结果。

## v3 vs v2

```python
# v3（推荐）— 更强的复杂任务、文件系统、定时任务
from browser_use_sdk.v3 import AsyncBrowserUse

# v2 — 接近开源体验，纯浏览器自动化
from browser_use_sdk.v2 import AsyncBrowserUse
```

默认用 v3，除非只需要简单的浏览器自动化。
