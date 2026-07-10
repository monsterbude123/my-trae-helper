# 错误处理与成本控制

## 常见错误

### 429 Rate Limited

SDK 自动以指数退避重试 429 响应。如果持续出现，可能需要增加并发 session —— 联系支持。

### Session 超时

- 默认 15 分钟无活动超时
- 最长 session 时长 4 小时
- 超时后 session 无法恢复，需重新创建

### 网站封锁

Stealth + 代理默认开启。如果仍被封锁：
1. 使用 profile（含登录态 cookies）
2. 切换代理国家
3. 联系支持

### Task 失败

Task 状态变为 `error` 时，检查：
- `result.output` — agent 最终输出
- `result.status` — `error` / `timed_out` / `stopped`
- Session messages — 查看 agent 在哪一步出错

```python
session = await client.sessions.get(session_id)
if session.status.value == "error":
    msgs = await client.sessions.messages(session_id, limit=50)
    for m in msgs.messages:
        print(f"[{m.role}] {m.summary}")
```

---

## 成本控制策略

### 1. 使用 Deterministic Rerun（缓存脚本）

首次运行全 agent，后续 $0 LLM 成本：

```python
workspace = await client.workspaces.create(name="scraper")

# 首次：全 agent (~$0.10, ~60s)
result = await client.run(
    "Get the top @{{5}} stories from Hacker News as JSON",
    workspace_id=str(workspace.id),
)

# 后续：缓存脚本 ($0 LLM, ~5s)
result2 = await client.run(
    "Get the top @{{10}} stories from Hacker News as JSON",
    workspace_id=str(workspace.id),
)
```

**成本对比**：

| | LLM 成本 | Browser+Proxy | 耗时 |
|---|---|---|---|
| 首次（Agent） | ~$0.05–1.00 | Yes | ~30-120s |
| 缓存命中 | $0 | Yes | ~3-10s |

### 2. 选对模型

| 模型 | 每步成本 | 适用 |
|------|---------|------|
| GPT-5.4 mini | 最低 | 简单任务 |
| Claude Sonnet 4.6 | 中等 | 复杂多步 |
| Claude Opus 4.6 | 最高 | 最难任务 |

### 3. Auto-healing

缓存脚本因网站改版失败时自动修复（限制 1 次尝试）：

| 场景 | LLM 成本 |
|------|---------|
| 缓存成功 | $0 |
| 缓存失败，自动修复 | ~$0.05–1.00 |
| 修复后仍失败 | 同上（返回 best-effort） |

### 4. 及时停止 Session

```python
try:
    result = await client.run("...", session_id=session.id)
finally:
    await client.sessions.stop(session.id)  # 防止资源泄漏
```

### 5. 选择合适粒度的任务

```
❌ 不好："打开每个页面抓一点数据" → 多次短 session = 多次浏览器启动成本
✅ 好："打开列表页，抓取所有数据" → 一次 session 完成所有工作
```

---

## 任务状态监控

```python
session = await client.sessions.get(session_id)
print(session.status.value)  # running / idle / stopped / error / timed_out
print(session.output)         # 最终输出
```

### Webhook 异步通知

参见 `references/webhook-async.md`，在任务状态变更时接收实时通知。

---

## Session 状态码

| 状态 | 含义 |
|------|------|
| `running` | Agent 正在执行 |
| `idle` | Session 就绪，等待新任务 |
| `stopped` | 任务完成 |
| `error` | 执行出错 |
| `timed_out` | 执行超时 |
