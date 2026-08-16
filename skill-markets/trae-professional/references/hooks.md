# Hook 钩子系统

> v3.5.66 新增功能（2026-06-10）
>
> **📚 知识源**：[Hook 配置详解 — docs.trae.cn](https://docs.trae.cn/ide_hook-configuration-reference)
> （TraeCode / AI 编程核心 / 钩子（Hook）/ Hook 配置详解）
> **最后同步**：2026-08-16（基于上述官方文档补全事件 schema / stdin / stdout / 退出码）
>
> ⚠️ 本 skill 是通过检索 Trae 官方文档站点（[docs.trae.cn](https://docs.trae.cn)）学习构建。任何字段、事件、退出码行为若与官方页面不一致，以官方为准并修订本文件。

Hook（钩子）允许你在智能体执行过程中的特定事件节点运行自定义 Shell 命令，实现对智能体行为的确定性控制。

## 核心概念

- **Hook** 是用户定义（user-defined）的 Shell 命令
- 在 TRAE 智能体生命周期的**特定阶段/事件节点**自动触发执行
- 确保某些操作**始终自动执行**，无需手动干预
- 提供对智能体行为的**确定性控制**

## 配置文件位置

| Hook 类型 | 操作系统 | 路径 | 作用范围 |
|----------|---------|------|---------|
| **全局 Hook** | macOS / Linux | `~/.trae-cn/hooks.json` | 当前用户所有工作区 |
| 全局 Hook | Windows | `%userprofile%/.trae-cn/hooks.json` | 当前用户所有工作区 |
| **项目 Hook** | macOS / Linux | `$PROJECT_FOLDER/.trae/hooks.json` | 仅当前项目 |
| 项目 Hook | Windows | `$PROJECT_FOLDER/.trae/hooks.json` | 仅当前项目 |

**多 Hook 共存行为**：
- 多项目根目录：TraeCode 读取各项目的 Hook 配置并合并执行
- Claude Code Hook + TraeCode Hook 同时启用：所有已启用 Hook 配置被读取并合并执行

## 与其它机制的区别

| 机制 | 触发方式 | 执行内容 | 用途 |
|------|----------|----------|------|
| **Hook** | 生命周期事件节点自动触发 | Shell 命令 | 自动化控制智能体行为 |
| 规则 (Rules) | 对话开始时注入 | 文本约束 | 规范 AI 输出风格和标准 |
| 技能 (Skills) | 任务匹配时按需加载 | 指令集 + 资源 | 赋予专业能力 |
| 命令 (Commands) | 用户手动 `/` 调用 | 封装的操作 | 简化重复操作 |

## 典型使用场景

- 在智能体执行命令前进行安全检查
- 在文件写入后自动运行格式化工具
- 在对话开始时初始化项目环境变量
- 在智能体读取文件前验证权限
- 自动记录智能体的工具调用日志

---

## Hook 配置格式（官方 schema）

```json
{
  "version": 1,
  "hooks": {
    "<EventName>": [
      {
        "matcher": "<ToolPattern>",
        "loop_limit": 5,
        "hooks": [
          {
            "type": "command",
            "command": "<shell command>",
            "timeout": 30
          }
        ]
      }
    ]
  }
}
```

### 顶层结构

| 字段 | 类型 | 必填 | 描述 |
|------|------|:---:|------|
| `version` | number | 否 | schema 版本，默认 `1`，当前仅支持 `1` |
| `hooks` | object | ✅ | Hook 事件名 → Hook 组列表的映射 |

### 事件层（`hooks.<EventName>`）

| 字段 | 类型 | 必填 | 描述 |
|------|------|:---:|------|
| `<EventName>` | array | ✅ | 该事件下的 Hook 组列表 |

### Hook 组层

| 字段 | 类型 | 必填 | 描述 |
|------|------|:---:|------|
| `matcher` | string | 否 | 正则匹配工具名（`Edit\|Write`、`mcp.*`）。`*` / 空 / 省略 = 匹配所有。**仅对 `PreToolUse` / `PostToolUse` / `Notification` 有效** |
| `loop_limit` | number | 否 | 循环次数限制。`loop_count` ≥ `loop_limit` 时跳过该 Hook 组。**仅对 `Stop` 事件有效**，默认 `5` |
| `hooks` | array | ✅ | 该 Hook 组下要执行的 Hook 列表 |

### Hook 定义层

| 字段 | 类型 | 必填 | 描述 |
|------|------|:---:|------|
| `type` | string | 否 | 类型，默认 `command`，当前仅支持 `command` |
| `command` | string | ✅ | 要执行的 Shell 命令 |
| `timeout` | number | 否 | 超时（秒），默认 `30` |

---

## Hook 输入输出协议

所有 Hook 命令遵循标准 I/O 机制：通过 **stdin** 接收 JSON 输入，通过 **stdout** + 退出码控制智能体行为。

### stdin 通用字段

每个 Hook 事件 stdin 都包含：

```json
{
  "session_id": "string",
  "cwd": "/path/to/workspace",
  "hook_event_name": "PreToolUse",
  "workspace_roots": ["/path/to/workspace"]
}
```

### stdout 通用字段

Hook 命令可通过 stdout 输出两种格式：
- **JSON**：结构化控制智能体执行
- **纯文本**：作为附加上下文给模型（**仅 `SessionStart` / `UserPromptSubmit` 事件适用**）

JSON 通用字段：

```json
{
  "continue": true,
  "stopReason": "string"
}
```

| 字段 | 类型 | 默认 | 描述 |
|------|------|:---:|------|
| `continue` | boolean | `true` | 智能体是否在 Hook 执行后继续。`false` = 停止。优先于任何事件特定的 `decision` 字段 |
| `stopReason` | string | — | 当 `continue: false` 时展示给用户的停止原因 |

### 退出码行为

| 退出码 | 行为 |
|:------:|------|
| `0` | 正常。`stdout` 按事件类型解析为 JSON 或纯文本 |
| `2` | **阻断性错误**。`stderr` 作为错误信息传给模型上下文。**不同事件行为不同**（见下文） |
| 其他 | 非阻断错误。`stderr` 和 `stdout` 被忽略 |

---

## Hook 执行环境

### Shell

- macOS / Linux：默认 **Bash**
- Windows：默认 **PowerShell**

### 环境变量

| 环境变量 | 描述 |
|---------|------|
| `TRAE_PROJECT_DIR` | 当前 Hook 工作目录（与 `stdin.cwd` 一致） |
| `CLAUDE_PROJECT_DIR` | 兼容 Claude Code 的工作目录变量（与 `stdin.cwd` 一致） |

**`SessionStart` 事件额外注入**：

| 环境变量 | 描述 |
|---------|------|
| `TRAE_ENV_FILE` | TraeCode 环境变量文件路径（仅 SessionStart 注入） |
| `CLAUDE_ENV_FILE` | 兼容 Claude Code 的环境变量文件路径（仅 SessionStart 注入） |

### 环境变量文件（SessionStart 独有）

向 `$TRAE_ENV_FILE` 写入环境变量 → 当前会话后续 Hook + `RunCommand` 工具调用生效（不影响当前 SessionStart Hook 进程）。

支持三种格式：
- **Bash**：`export NODE_ENV=production`
- **PowerShell**：`$env:NODE_ENV=production`
- **Dotenv**：`NODE_ENV=production`

### 工作目录

| Hook 命令类型 | 工作目录 |
|-------------|---------|
| 全局 Hook | 单工作区 = 工作区根；多工作区 = 第一个工作区根 |
| 项目 Hook | 该 Hook 配置文件所在项目的根目录 |

### 运行方式（沙箱 vs 本地）

- **沙箱运行**：Hook 命令在沙箱中执行，文件访问和系统权限受沙箱限制
- **本地自动运行**：Hook 命令在沙箱外执行，可访问本地环境（更高安全风险）

设置方法：参考 [设置 Hook 命令的运行方式](https://docs.trae.cn/ide/automate-actions-with-hooks#bb41f71f)。

---

## Hook 事件清单（官方支持）

### SessionStart

- **触发时机**：创建 Session 后、发起第一个对话之前
- **作用**：初始化环境、注入上下文、设置环境变量
- **stdin 专有字段**：`source`（`startup` = 新建会话）
- **stdout 纯文本**：作为附加上下文给模型
- **stdout JSON**：`hookSpecificOutput.additionalContext`
- **退出码 2 行为**：不影响会话流程
- **支持 `loop_limit` 的事件**：**❌ 否**
- **支持 `matcher` 的事件**：**❌ 否**

### UserPromptSubmit

- **触发时机**：用户发送消息后、智能体开始处理前
- **作用**：拦截不允许请求、向模型附加上下文
- **stdin 专有字段**：`prompt`
- **stdout JSON**：`decision: "block"` + `reason` + `hookSpecificOutput.additionalContext`
- **退出码 2 行为**：等价 `decision: "block"`，禁止执行 Prompt，`stderr` 展示给用户
- **支持 `loop_limit`**：❌ 否
- **支持 `matcher`**：❌ 否

### PreToolUse

- **触发时机**：智能体发起工具调用后、实际执行前
- **作用**：校验或拦截工具调用、修改工具参数、要求用户确认
- **stdin 专有字段**：
  - `tool_use_id`：工具调用唯一 ID
  - `tool_name`：标准化的工具名
  - `llm_tool_name`：传给 LLM 的原始工具名
  - `tool_input`：工具输入参数
- **stdout JSON**：
  - `permissionDecision`：`allow` / `deny` / `ask`（多 Hook 并行优先级：`deny` > `ask` > `allow`）
  - `permissionDecisionReason`：决策原因
  - `updatedInput`：整体替换（**非合并**）的工具输入参数
  - `additionalContext`
- **退出码 2 行为**：等价 `permissionDecision: "deny"`，拒绝执行，`stderr` 作为原因附加给模型
- **支持 `loop_limit`**：❌ 否
- **支持 `matcher`**：**✅ 是**（匹配 `tool_name`）

### PostToolUse

- **触发时机**：工具调用实际执行完成后
- **作用**：校验执行结果或附加上下文
- **stdin 专有字段**：`tool_use_id` + `tool_name` + `llm_tool_name` + `tool_input` + `tool_response`
- **stdout JSON**：`decision: "block"` + `reason` + `hookSpecificOutput.additionalContext`
- **退出码 2 行为**：`stderr` 传递给模型上下文
- **支持 `loop_limit`**：❌ 否
- **支持 `matcher`**：**✅ 是**（匹配 `tool_name`）

### Stop

- **触发时机**：智能体完成输出、准备结束当前查询时
- **作用**：阻止智能体结束当前任务，要求其继续执行
- **stdin 专有字段**：
  - `stop_hook_active`：当前查询是否已被该事件 Hook 阻断过
  - `loop_count`：当前查询被该事件 Hook 阻断的次数（从 0 累加）
  - `last_assistant_message`：LLM 最终输出的文本
- **stdout JSON**：`decision: "block"` + `reason`（`reason` 作为新的用户请求让智能体继续）
- **退出码 2 行为**：等价 `decision: "block"`，阻断停止，`stderr` 作为新 Query
- **支持 `loop_limit`**：**✅ 是**（默认 `5`）
- **支持 `matcher`**：❌ 否
- **决策控制流程**：
  ```
  智能体准备停止
    │
    ▼
  检查 loop_count ≥ loop_limit？──── 是 ──► 跳过 Hook，允许停止
    │
   否
    ▼
  执行 Stop Hook 脚本
    │
    ├── 退出码 0 + decision 为空 ──────────► 允许停止
    ├── 退出码 0 + decision = "block" ─────► 阻断停止，reason 作为新 Query
    ├── 退出码 2 ───────────────────────► 阻断停止，stderr 作为新 Query
    └── 其他退出码 ──────────────────────► 忽略错误，允许停止
  ```

### Notification

- **触发时机**：工具调用等待用户确认时 / 智能体完成任务时（**异步，不阻塞主流程**）
- **作用**：发送通知，不改变智能体执行流程
- **matcher 匹配**：基于 `notification_type`（非 `tool_name`）
- **stdin 专有字段**：`notification_type`（通知类别）+ `message`（通知正文）+ `tool_use_id`（关联的工具调用 ID，可选）
- **支持 `loop_limit`**：❌ 否
- **支持 `matcher`**：**✅ 是**（匹配 `notification_type`）

### `matcher` / `loop_limit` 适用性速查

| 事件 | matcher 适用 | loop_limit 适用 |
|------|:----------:|:--------------:|
| SessionStart | ❌ | ❌ |
| UserPromptSubmit | ❌ | ❌ |
| PreToolUse | ✅ | ❌ |
| PostToolUse | ✅ | ❌ |
| Stop | ❌ | ✅ |
| Notification | ✅ | ❌ |

---

## 已知未覆盖内容（待下次同步）

- [Hook 事件支持的工具清单](https://docs.trae.cn/ide/reference-for-hooks-configuration#hVL37mbtD)（`PreToolUse` / `PostToolUse` 的 `tool_name` 合法值）
- Claude Code Hook 导入流程 — 详见 [导入 Claude Code 中的 Hook](https://docs.trae.cn/ide/automate-actions-with-hooks#4c6238cd)