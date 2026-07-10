# MCP Server

## 从 MCP 市场添加

设置 → MCP → 添加 → 从市场添加 → 找到所需 MCP → `+` → 填入配置（替换 API Key 等） → 确认。

## 手动配置

设置 → MCP → 添加 → 手动添加 → 填入 JSON 配置。

可在其他 IDE 已配置的 MCP 中复制 JSON 粘贴到 TRAE。

## stdio 类型

| 字段 | 必填 | 说明 |
|------|------|------|
| command | 是 | 可执行命令（不能含空格） |
| args | 否 | 命令参数列表 |
| env | 否 | 环境变量 |

```json
{
  "mcpServers": {
    "mcp_name": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": { "API_Key": "value" }
    }
  }
}
```

## HTTP 类型

| 字段 | 必填 | 说明 |
|------|------|------|
| url | 是 | 远程 MCP Server 地址 |
| headers | 否 | 自定义请求头（鉴权信息等） |

```json
{
  "mcpServers": {
    "mcp_name": {
      "url": "https://example.com/mcp",
      "headers": { "Authorization": "Bearer xxxx" }
    }
  }
}
```

## 超时配置

| 类型 | 位置 | 参数 |
|------|------|------|
| stdio | `env` | `START_MCP_TIMEOUT_MS`、`RUN_MCP_TIMEOUT_MS` (ms) |
| HTTP | `headers` | 同上 |

## 项目级 MCP Server

项目根目录 `.trae/mcp.json` 声明配置。设置 → MCP → 开启"启用项目级 MCP"。

> 确保所有项目文件可信，避免恶意配置文件。

## 变量引用

支持 `${workspaceFolder}`，启动时替换为项目根目录路径。
