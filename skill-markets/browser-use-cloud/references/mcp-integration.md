# MCP 集成 — AI 编码助手直连

Browser Use Cloud 通过 MCP Server 接入 Claude Code、Cursor、Windsurf 等 AI 编码助手。

**MCP 端点**：`https://api.browser-use.com/v3/mcp`

---

## 配置各客户端

### Claude Code

```bash
claude mcp add -t http -H "x-browser-use-api-key: YOUR_API_KEY" browser-use https://api.browser-use.com/v3/mcp
```

### Claude Desktop

编辑 `claude_desktop_config.json`：

```json
{
  "mcpServers": {
    "browser-use": {
      "url": "https://api.browser-use.com/v3/mcp",
      "headers": {
        "x-browser-use-api-key": "YOUR_API_KEY"
      }
    }
  }
}
```

### Cursor

编辑 `.cursor/mcp.json`：

```json
{
  "mcpServers": {
    "browser-use": {
      "url": "https://api.browser-use.com/v3/mcp",
      "headers": {
        "x-browser-use-api-key": "YOUR_API_KEY"
      }
    }
  }
}
```

### Windsurf

编辑 `~/.codeium/windsurf/mcp_config.json`：

```json
{
  "mcpServers": {
    "browser-use": {
      "serverUrl": "https://api.browser-use.com/v3/mcp",
      "headers": {
        "x-browser-use-api-key": "YOUR_API_KEY"
      }
    }
  }
}
```

---

## 可用 Tools

| Tool | 说明 |
|------|------|
| `run_session` | 创建 session 并运行任务。支持 `keep_alive`、`model`、`output_schema`、`profile_id` |
| `get_session` | 轮询 session 状态和输出。返回状态、步骤数、费用明细、live URL |
| `send_task` | 向 idle 状态（keep_alive）的 session 发送 follow-up 任务 |
| `stop_session` | 停止 session。`strategy: "task"` 只停任务，`strategy: "session"` 销毁沙箱 |
| `get_session_messages` | 获取 agent 消息——浏览器动作、推理过程、结果 |
| `list_sessions` | 列出最近的 session，含状态和费用 |
| `list_browser_profiles` | 列出浏览器 profile（用于认证任务） |

---

## 使用场景

```
"帮我登录 GitHub 然后 star browser-use 仓库"
→ AI 编码助手通过 MCP 调用 run_session → agent 执行 → 返回结果

"监控 example.com 的价格变化"
→ run_session 设定监控任务 → get_session 轮询结果

"批量抓取这 10 个页面的数据"
→ send_task 逐个发送 follow-up 任务到同一个 keep_alive session
```

---

## 获取 API Key

在 [cloud.browser-use.com/settings](https://cloud.browser-use.com/settings?tab=api-keys&new=1) 创建 key（以 `bu_` 开头）。
