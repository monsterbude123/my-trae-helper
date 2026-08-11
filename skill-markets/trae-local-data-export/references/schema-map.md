# Trae 数据库 Schema 映射

> 来源: trae-chat-decrypt 实际导出的 schema.sql（39 个表）
> 适用: Trae CN 当前版本（v3.5.x ~ v3.6.x，2026-06 验证）

---

## §1 核心表（导出必用）

### 1.1 `chat_session` — 会话元数据

| 列 | 类型 | 说明 | 导出 JSON 字段 |
|----|------|------|---------------|
| `id` | TEXT PK | UUID | `session_id` |
| `title` | TEXT | 会话标题 | `title` |
| `type` | TEXT | side_chat / inline_chat / background_chat / proactive_chat | `type` |
| `project_id` | TEXT | 关联 project.id | `project` (join) |
| `created_at` | INTEGER | ms epoch | `created_at` (ISO 转换) |
| `updated_at` | INTEGER | ms epoch | `updated_at` (ISO 转换) |

**典型查询**:

```sql
SELECT id, title, type, project_id, created_at, updated_at
FROM chat_session
ORDER BY created_at DESC;
```

### 1.2 `chat_message` — 消息索引

| 列 | 类型 | 说明 |
|----|------|------|
| `id` | TEXT PK | 消息 UUID |
| `session_id` | TEXT FK | → chat_session.id |
| `role` | TEXT | user / assistant / system |
| `type` | TEXT | general / task |
| `index` | INTEGER | 会话内顺序 |
| `created_at` | INTEGER | ms epoch |

### 1.3 `chat_message_general` — 普通消息内容

| 列 | 类型 | 说明 |
|----|------|------|
| `id` | TEXT PK | → chat_message.id |
| `content` | TEXT | 完整文本（可能含 markdown） |
| `context` | TEXT (JSON) | 引用文件、选择范围 |

### 1.4 `chat_message_task` — 任务消息（Agent 输出）

| 列 | 类型 | 说明 |
|----|------|------|
| `id` | TEXT PK | → chat_message.id |
| `summary` | TEXT | 一句话摘要 |
| `content` | TEXT (JSON) | 完整 task 描述 + steps + tool calls |
| `status` | TEXT | pending / running / success / failed |

### 1.5 `chat_turn` — 对话轮次（Agent 信息）

| 列 | 类型 | 说明 |
|----|------|------|
| `session_id` | TEXT | → chat_session.id |
| `turn_index` | INTEGER | 轮次序号 |
| `agent_type` | TEXT | solo_coder / solo_agent / custom_v3 / search_agent / browser_use_agent |
| `model` | TEXT | kimi-k2.5 / glm-5.1 / deepseek-r1 等 |
| `context` | TEXT (JSON) | **token_usage 藏这里** |

### 1.6 `history_v2` — 详细历史 + token 用量

| 列 | 类型 | 说明 |
|----|------|------|
| `id` | TEXT PK | |
| `session_id` | TEXT | |
| `turn_id` | TEXT | |
| `timestamp` | INTEGER | |
| `token_usage` | TEXT (JSON) | prompt/completion/cache_read/cache_write |
| `request_meta` | TEXT (JSON) | 模型、温度、tools |

### 1.7 `server_history_info` — 服务端视角

> 客户端 token 压缩/截断，服务端这里完整记录。
> 通常是 `history_v2` 的 5-15 倍大小。

### 1.8 `project` — 项目元数据

| 列 | 类型 | 说明 |
|----|------|------|
| `id` | TEXT PK | |
| `name` | TEXT | 项目名 |
| `path` | TEXT | 绝对路径（**脱敏重点**） |

---

## §2 导出 JOIN 模板

### 2.1 完整会话（含消息）

```sql
SELECT
    s.id          AS session_id,
    s.title       AS title,
    s.type        AS type,
    p.name        AS project,
    s.created_at  AS created_at,
    m.role        AS role,
    m.type        AS msg_type,
    m.idx         AS idx,
    m.created_at  AS msg_ts,
    COALESCE(g.content, t.content) AS content
FROM chat_session s
LEFT JOIN project p  ON s.project_id = p.id
LEFT JOIN chat_message m ON m.session_id = s.id
LEFT JOIN chat_message_general g ON g.id = m.id AND m.type = 'general'
LEFT JOIN chat_message_task t    ON t.id = m.id AND m.type = 'task'
ORDER BY s.created_at, m.idx;
```

### 2.2 Token 用量统计（按模型）

```sql
SELECT
    json_extract(context, '$.agent.model') AS model,
    COUNT(*) AS calls,
    SUM(CAST(json_extract(context, '$.token_usage.prompt_tokens') AS INTEGER)) AS prompt_total,
    SUM(CAST(json_extract(context, '$.token_usage.completion_tokens') AS INTEGER)) AS completion_total
FROM chat_turn
WHERE context IS NOT NULL
GROUP BY model
ORDER BY prompt_total DESC;
```

### 2.3 按 Agent 类型

```sql
SELECT
    json_extract(context, '$.agent.type') AS agent_type,
    COUNT(*) AS calls
FROM chat_turn
WHERE context IS NOT NULL
GROUP BY agent_type
ORDER BY calls DESC;
```

---

## §3 字段别名差异（跨版本）

| Trae 版本 | chat_message.index 列 | chat_message.general/task 分流 |
|-----------|----------------------|------------------------------|
| v3.4.x 之前 | `index` | type 字段 |
| v3.5.x | `index` 或 `idx` | type 字段 |
| v3.6.x | `index` | type 字段 |

> 兼容方案：导出前用 `PRAGMA table_info(chat_message)` 查实际列名。

---

## §4 不导出的表（辅助类）

| 表 | 用途 | 建议 |
|----|------|------|
| `cache_*` | 缓存 | 跳过 |
| `metrics_*` | 性能指标 | 跳过（除非用户要 APM 数据） |
| `_journal_*` | WAL 残留 | 跳过 |
| `mcp_*` | MCP server 元数据 | 可选导出（用于回溯 agent 用了哪些 MCP） |
| `tool_call_*` | 工具调用详情 | 包含在 `chat_message_task.content` JSON 中 |

---

## §5 字段脱敏清单

> 默认在 §2 JOIN 后、PII 脱敏阶段处理。

| 原始字段 | 脱敏后 |
|---------|--------|
| `project.path`（绝对路径） | `<PROJECT_PATH>` |
| `chat_message_general.context` 内 file 路径 | `<FILE_PATH>` |
| 32+ 字符 hex 串 | `<HEX_32>` |
| 64 字符 hex 串 | `<HEX_64>` |
| email 格式 | `<EMAIL>` |
| IPv4 | `<IP>` |
| 真实姓名 + 邮箱组合 | 整条 `content` 标记 `<PII>` |
