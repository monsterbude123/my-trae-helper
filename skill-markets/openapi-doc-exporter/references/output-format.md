# Markdown 渲染规范

> 本文档定义 `render_md.py` 的输出格式，确保渲染结果一致可读。
> 单文件模式（single）和分模块模式（split）共用本规范。

## 1. 文档结构

### 1.1 single 模式

```markdown
# {title}

> 版本：v{version} | 生成日期：YYYY-MM-DD | OpenAPI 版本：{openapi_version}
> 接口总数：N | 路径数：M | Schema 数：K

## 目录

- 第 1 章：API 概览
- 第 2 章：通用约定
- 第 3 章：{模块A}（N ops）
- 第 4 章：{模块B}（N ops）
- ...
- 附录：Schema 定义

---

## 第 1 章：API 概览
...

## 第 2 章：通用约定
...

## 第 N 章：{模块名}
...

## 附录：Schema 定义
...
```

### 1.2 split 模式

```
{output-dir}/
├── README.md              # 总览（目录 + 各模块链接 + 统计）
├── 01-overview.md         # API 概览 + 通用约定
├── 02-{module-a}.md       # 模块 A 接口
├── 03-{module-b}.md       # 模块 B 接口
├── ...
├── 99-unclassified.md     # 未匹配前缀的接口
└── appendix-schemas.md    # Schema 定义附录
```

每个模块文件独立可读，通过 README 中的相对链接互相引用。

## 2. 接口标题格式

```markdown
### {METHOD} {path}
```

示例：

```markdown
### GET /api/users/{user_id}

### POST /api/writing/chapters/stream
```

- `METHOD` 大写：GET / POST / PUT / DELETE / PATCH / HEAD / OPTIONS
- `path` 保留原始大小写和参数占位符（`{user_id}`）
- 同一 path 的不同 method 各占一个 `###` 小节

## 3. 请求渲染

### 3.1 元信息

```markdown
**概述**：{description 或 summary}
**Tags**：{tag1, tag2}
**operationId**：`{operationId}`
```

- 若 `description` 缺失，回退到 `summary`
- 若都缺失，写 `（无描述）`
- `Tags` 和 `operationId` 缺失则省略该行

### 3.2 Path 参数表格

```markdown
**Path 参数**：

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| user_id | string | 是 | 用户 ID |
```

- 必填列：`是` / `否`
- 说明列：取 `description`，换行替换为空格

### 3.3 Query 参数表格

同 Path 参数格式。

### 3.4 Header / Cookie 参数

同 Path 参数格式（如有）。

### 3.5 请求体

```markdown
**请求**：
- Content-Type: `application/json`
- Body Schema: `CreateUserRequest`（见附录）
- Body 字段：

  | 字段 | 类型 | 必填 | 说明 |
  |------|------|------|------|
  | name | string | 是 | 用户名 |
  | email | string | 是 | 邮箱 |

- Body 示例：
  ```json
  {
    "name": "string",
    "email": "string"
  }
  ```
```

- 若 schema 是 `$ref`，引用附录中的 Schema 定义
- 若 schema 是 inline object 且有 properties，渲染字段表 + 示例
- 若 schema 是 array，渲染 `array<{item_type}>`
- 多 Content-Type 各占一块

## 4. 响应渲染

```markdown
**响应**：
- `200` 成功响应
  - Content-Type: `application/json`
  - Schema: `UserResponse`（见附录）
- `404` 用户不存在
  - Content-Type: `application/json`
  - Body: `object`
- `422` 校验失败
  - Content-Type: `application/json`
  - Body 字段：

    | 字段 | 类型 | 必填 | 说明 |
    |------|------|------|------|
    | detail | array | 否 | 错误详情 |
```

- 每个状态码一行：`- \`{code}\` {description}`
- 每种 Content-Type 缩进一级
- Schema 引用规则同请求体

## 5. SSE 端点标注

当响应 Content-Type 包含 `text/event-stream` 时：

```markdown
> **SSE 端点**：响应 Content-Type 为 `text/event-stream`，使用 Server-Sent Events 协议推送流式数据。
```

同时在第 2 章通用约定的"流式响应（SSE）"小节列出该端点。

## 6. WebSocket 端点标注

当 operationId 或 summary 包含 `ws://`、`wss://`、`websocket`（不区分大小写）时：

```markdown
> **WebSocket 端点**：使用 ws:// 或 wss:// 协议进行双向通信。
```

同时在第 2 章通用约定的"WebSocket"小节列出该端点。

## 7. Schema 定义附录

```markdown
## 附录：Schema 定义

> 共 N 个 schema，按字母顺序列出。

### CreateUserRequest

**说明**：创建用户请求

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| name | string | 是 | 用户名 |
| email | string | 是 | 邮箱 (默认: `null`) |

---

### UserStatus

类型：`enum(active,inactive,banned)`

---
```

- Schema 按字母序排列
- 每个 schema 一个 `###` 小节
- 若有 `description`，写 `**说明**：{desc}`
- 若有 properties，渲染字段表
- 若是 enum，渲染 `类型：\`enum(v1,v2,...)\``
- 每个 schema 后跟 `---` 分隔线

## 8. 类型渲染规则

| OpenAPI 类型 | 渲染为 |
|-------------|--------|
| `string` | `string` |
| `integer` | `integer` |
| `number` | `number` |
| `boolean` | `boolean` |
| `array` | `array<{item_type}>` |
| `object` (有 properties) | `object` |
| `$ref: #/components/schemas/Foo` | `Foo` |
| `anyOf: [A, B]` | `A \| B` |
| `oneOf: [A, B]` | `A \| B` |
| `allOf: [A, B]` | `A & B` |
| 有 `enum` | `enum(v1,v2,v3)` |
| 无 type 信息 | `any` |

## 9. 章节编号规则

- 第 1 章：API 概览（固定）
- 第 2 章：通用约定（固定）
- 第 3 章起：按 prefix-map 中 `order` 字段升序编号
- 附录：Schema 定义（固定，无章号）

split 模式下：
- `01-overview.md`：包含第 1、2 章
- `02-{module}.md` ~ `99-unclassified.md`：各模块章节
- `appendix-schemas.md`：附录

## 10. 示例 JSON 生成规则

- 优先使用 schema 中的 `example` 字段
- 其次使用 `default` 字段
- 其次使用 `enum` 的第一个值
- 否则按类型生成默认值：
  - `string` → `"string"`
  - `integer` → `0`
  - `number` → `0`
  - `boolean` → `true`
  - `object` → 递归生成
  - `array` → `[示例值]`
- 嵌套深度限制 5 层，超出返回 `null`

## 11. 分隔符与空行

- 章节之间用 `---` 分隔
- 接口小节之间用 `---` 分隔
- 表格前后保留一个空行
- 代码块前后保留一个空行
- 文档末尾保留一个换行符
