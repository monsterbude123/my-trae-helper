# Agent 任务详解

## client.run() 完整说明

`client.run()` 是最高频使用的方法。它内部做三件事：
1. 创建 session（或复用已有 session_id）
2. 每 2 秒轮询任务状态
3. 完成后返回 Session 对象，`result.output` 是 agent 的最终输出

`client.run()` 接受 [Create Session](https://docs.browser-use.com/cloud/api-v3/sessions/create-session) 的所有参数。

## 结构化输出

用 Pydantic (Python) 或 Zod v4 (TypeScript) 定义输出格式，`result.output` 自动验证并类型转换。

### Python（Pydantic）

```python
from browser_use_sdk.v3 import AsyncBrowserUse
from pydantic import BaseModel

class Post(BaseModel):
    title: str
    points: int
    comments: int

class HNPosts(BaseModel):
    posts: list[Post]

client = AsyncBrowserUse()
result = await client.run(
    "List the top 20 posts on Hacker News today with their points",
    output_schema=HNPosts,
)
for post in result.output.posts:
    print(f"{post.title} ({post.points} pts, {post.comments} comments)")
```

### TypeScript（Zod v4）

> **注意**：TypeScript 需要 Zod v4（`npm install zod@4`），Zod v3 不兼容。

```typescript
import { BrowserUse } from "browser-use-sdk/v3";
import { z } from "zod";

const Post = z.object({
  title: z.string(),
  points: z.number(),
  comments: z.number(),
});

const HNPosts = z.object({
  posts: z.array(Post),
});

const client = new BrowserUse();
const result = await client.run(
  "List the top 20 posts on Hacker News today with their points",
  { schema: HNPosts },
);
for (const post of result.output.posts) {
  console.log(`${post.title} (${post.points} pts, ${post.comments} comments)`);
}
```

## Follow-up 任务（多步工作流）

传入 `session_id` 保持浏览器状态（页面、cookies、标签页）跨任务延续。每个任务运行新的 agent 实例，agent 之间不共享上下文，但浏览器状态保留。

```python
from browser_use_sdk.v3 import AsyncBrowserUse

client = AsyncBrowserUse()

# 创建 session
session = await client.sessions.create()

# 步骤 1
await client.run(
    "Go to amazon.com, search for laptops, open the first result",
    session_id=session.id,
)

# 步骤 2（浏览器保持步骤 1 的状态）
result = await client.run(
    "Extract all customer reviews from this product page",
    session_id=session.id,
)

# 关闭 session
await client.sessions.stop(session.id)
```

- `sessions.create()` 返回 `live_url`，可嵌入 iframe 实时观看任务执行
- Session 默认 15 分钟无活动超时，最长 4 小时

## Live Messages（实时流式消息）

在 agent 工作时流式获取消息，包括推理过程、工具调用、浏览器动作和结果。每条消息有 `role`、`type`、`summary`、`data`、`screenshot_url`。

```python
from browser_use_sdk.v3 import AsyncBrowserUse

client = AsyncBrowserUse()

run = client.run("Find the top story on Hacker News")
async for msg in run:
    print(f"[{msg.role}] {msg.summary}")

# 迭代结束后获取结果
print(run.result.output)
```

输出示例：
```
[user] Find the top story on Hacker News
[assistant] Navigating to https://news.ycombinator.com/
[tool] Browser Navigate: Navigated
[assistant] Analyzing browser state
[tool] Browser Analyze State: The top story is "Coding Agents Could Make Free Software Matter Again"
[tool] Done Autonomous: The top story on Hacker News is "Coding Agents Could Make Free Software Matter Again"
```

### 取消运行中的任务

```python
run = client.run("Find the top story on Hacker News")
async for msg in run:
    if should_cancel():
        await client.sessions.stop(run.session_id, strategy="task")
        break
# Session 回到 idle 状态，可以发送新任务
```

`strategy="task"` 只取消当前任务不销毁 session。

### 手动轮询

完全控制轮询循环：

```python
import asyncio
from browser_use_sdk.v3 import AsyncBrowserUse

client = AsyncBrowserUse()
session = await client.sessions.create(task="Find the top story on Hacker News")

cursor = None
while True:
    msgs = await client.sessions.messages(session.id, after=cursor, limit=100)
    for m in msgs.messages:
        print(f"[{m.role}] {m.summary}")
        cursor = m.id

    s = await client.sessions.get(session.id)
    if s.status.value in ("idle", "stopped", "error", "timed_out"):
        break
    await asyncio.sleep(2)

print(s.output)
```

## 模型选择

```python
result = await client.run("...", model="claude-sonnet-4.6")
```

| 模型 | API 字符串 | Input/1M | Output/1M |
|------|-----------|----------|-----------|
| Claude Sonnet 4.6 | `claude-sonnet-4.6` | $3.60 | $18.00 |
| Claude Opus 4.6 | `claude-opus-4.6` | $6.00 | $30.00 |
| GPT-5.4 mini | `gpt-5.4-mini` | $0.90 | $5.40 |

推荐 **Claude Sonnet 4.6**。

## Agent 能力一览

- **数据提取** — 抓取数千条列表
- **表单填写** — 提交申请、填写问卷
- **多步工作流** — 登录、导航、点击流程、下载文件
- **研究** — 跨站搜索、对比结果、总结发现
- **监控** — 监控网站变化并通知
- **测试** — 自然语言端到端测试
- **定时任务** — 周期性运行
- **1000+ 集成** — Gmail、Calendar、Notion 等
