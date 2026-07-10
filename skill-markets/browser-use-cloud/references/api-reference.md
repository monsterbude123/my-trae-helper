# API Reference — 完整速查

## 认证

所有请求需要 API Key header：

```
X-Browser-Use-API-Key: bu_your_key_here
```

## Base URL

```
https://api.browser-use.com/api/v3
```

## Sessions（Agent 任务）

### 创建 Session

```bash
curl -X POST https://api.browser-use.com/api/v3/sessions \
  -H "X-Browser-Use-API-Key: bu_..." \
  -H "Content-Type: application/json" \
  -d '{
    "task": "Find the top 3 trending repos on GitHub today",
    "model": "claude-sonnet-4.6"
  }'
```

### 获取 Session

```bash
curl https://api.browser-use.com/api/v3/sessions/SESSION_ID \
  -H "X-Browser-Use-API-Key: bu_..."
```

### 停止 Session

```bash
curl -X POST https://api.browser-use.com/api/v3/sessions/SESSION_ID/stop \
  -H "X-Browser-Use-API-Key: bu_..." \
  -H "Content-Type: application/json" \
  -d '{"strategy": "session"}'   # "session" 销毁 / "task" 只取消当前任务
```

### 获取 Session Messages

```bash
curl "https://api.browser-use.com/api/v3/sessions/SESSION_ID/messages?limit=100" \
  -H "X-Browser-Use-API-Key: bu_..."
```

`after` 参数用于分页（传 message id）。

## Browsers（裸浏览器）

### 创建浏览器

```bash
curl -X POST https://api.browser-use.com/api/v3/browsers \
  -H "X-Browser-Use-API-Key: bu_..." \
  -H "Content-Type: application/json" \
  -d '{}'
```

### 停止浏览器

```bash
curl -X POST https://api.browser-use.com/api/v3/browsers/BROWSER_ID/stop \
  -H "X-Browser-Use-API-Key: bu_..."
```

## Workspaces（文件管理）

### 创建 Workspace

```bash
curl -X POST https://api.browser-use.com/api/v3/workspaces \
  -H "X-Browser-Use-API-Key: bu_..." \
  -H "Content-Type: application/json" \
  -d '{"name": "my-workspace"}'
```

### 上传文件

SDK 方式（推荐）：
```python
await client.workspaces.upload(workspace.id, "file.csv")
```

### 列出文件

```bash
curl https://api.browser-use.com/api/v3/workspaces/WORKSPACE_ID/files \
  -H "X-Browser-Use-API-Key: bu_..."
```

## Skills（可复用自动化）

### 创建 Skill

```python
skill = await client.skills.create(
    goal="Extract the top X posts from HackerNews...",
    agent_prompt="Go to https://news.ycombinator.com, scroll to load posts.",
)
```

### 执行 Skill

```python
result = await client.skills.execute(skill.id, parameters={"X": 10})
```

### 优化 Skill

```python
await client.skills.refine(skill.id, feedback="Also extract the product description")
```

### Marketplace

```python
skills = await client.marketplace.list()
my_skill = await client.marketplace.clone(skill_id)
result = await client.marketplace.execute(skill_id, parameters={...})
```

## Profiles（浏览器配置）

```bash
# 创建 profile
curl -X POST https://api.browser-use.com/api/v3/profiles \
  -H "X-Browser-Use-API-Key: bu_..." \
  -H "Content-Type: application/json" \
  -d '{"name": "my-profile"}'
```

## 代理配置

创建 session 时指定代理：

```json
{
  "task": "...",
  "proxy": {
    "url": "http://user:pass@proxy.example.com:8080"
  }
}
```

或使用 residential proxy：
```json
{
  "task": "...",
  "use_residential_proxy": true
}
```

## 录制

创建 session 时启用录制：

```json
{
  "task": "...",
  "recording": true
}
```

录制视频在 session 完成后可通过 API 下载。

## 状态码

| 状态 | 含义 |
|------|------|
| `idle` | Session 就绪，等待任务 |
| `running` | Agent 正在执行 |
| `stopped` | 已完成 |
| `error` | 执行出错 |
| `timed_out` | 执行超时 |

## Session 限制

- 默认 15 分钟无活动超时
- 最长 4 小时
- Task 最长 50000 字符

## 完整文档

- [API v3 完整参考](https://docs.browser-use.com/cloud/api-reference)
- [Create Session](https://docs.browser-use.com/cloud/api-v3/sessions/create-session)
- [Create Browser Session](https://docs.browser-use.com/cloud/api-v3/browsers/create-browser-session)
