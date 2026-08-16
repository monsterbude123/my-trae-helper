---
description: Trae 五机制速查 — agents / skills / rules / hooks / mcp 文件路径 + 加载时机 + 何时用
alwaysApply: false
enabled: true
updatedAt: 2026-08-16
provider: trae
---

# Trae 机制速查

> **范围**：Trae 官方机制 + 本项目（my-trae-helper）兼容约定,只列与开发相关的核心事实。
> 一句话：**agents 工人 / skills 能力 / rules 规章 / hooks 门禁 / mcp 外接**。

---

## agents — 自定义智能体

### 官方机制

| 维度 | 说明 |
|------|------|
| 配置/调用 | 输入框 `@` → 选智能体；头像 → 设置 → 智能体（创建/修改/分享/删除）|
| 工具 | MCP Server + 内置工具（阅读/文件系统/终端/联网搜索/预览）|
| 跨智能体调用 | 仅 SOLO Agent 可调,需配英文标识名 + 调用场景 |

### 本项目约定

| 文件 | 用途 |
|------|------|
| `.agents/agents/<name>.md` | 项目级云端可复用（提交）|
| `skill-markets/<pkg>/agents/<name>.md` | skill 自带的流水线角色 |
| `.trae/agents/<name>.md` | 本机临时,**不提交** |

**何时用**：复杂多步 / 需要并行 / 需要隔离上下文 → 委派子 agent。
**何时不用**：单文件几步 / 需要主 agent 实时反馈 → 直接干。

---

## skills — 技能（赋予专业能力）

### 官方机制

| 维度 | 说明 |
|------|------|
| 结构 | `skill-name/SKILL.md`（必）+ `examples/` `templates/` `resources/`（可选）|
| 加载 | **按需加载** — 智能体先扫所有 skill 的 description,匹配才加载详情（省 Token）|
| 路径 | 项目级 `.trae/skills/` / 全局 `~/.trae-cn/skills`（Windows: `%userprofile%/.trae-cn/skills`）|
| 调用 | `/` 选 skill / 自然语言"用 X 技能..." / AI 自动按 description 匹配 |

### 本项目约定

| 文件 | 用途 |
|------|------|
| `.agents/skills/<name>/SKILL.md` | 项目级云端可复用 skill |
| `skill-markets/<name>/SKILL.md` | skill 市场发布包（含可选 agents/ references/ scripts/）|
| `~/.trae-cn/skills/<name>/` | 全局安装的 skill（本机）|

**何时用**：需要赋予专业能力 / 自动化重复工作流 / 保证输出一致性。
**何时不用**：约束行为 → rules；确定性自动执行 → hooks；提供可调工具 → mcp。

---

## rules — 规则系统

### 官方机制（**全量加载**,对话开启即注入上下文,持续占用）

| 类型 | 路径 |
|------|------|
| **全局规则** | `~/.trae-cn/user_rules` |
| **项目规则** | 项目内 `.trae/rules/*.md` |
| 兼容导入（仅桌面版）| 根目录 `AGENTS.md` / `CLAUDE.md` / `CLAUDE.local.md` |

> ⚠️ Trae **没有** `alwaysApply` 字段 — 项目级 rules 全部全量加载。子目录最多 3 层。

### 本项目约定

| 文件 | 用途 |
|------|------|
| `.agents/rules/*.md` | 本项目项目级 rules |
| `.trae/rules/*.md` | 项目级 rules |

**何时用**：约束 AI 行为 / 代码风格 / 交互方式。
**何时不用**：赋予能力 → skills；自动执行 → hooks。

---

## hooks — 钩子（v3.5.66+）

### 官方机制

| 维度 | 说明 |
|------|------|
| 触发 | 智能体生命周期**特定事件节点自动触发** |
| 执行 | **Shell 命令**（非文本指令）|
| 事件名 | `SessionStart` / `UserPromptSubmit` / `PreToolUse` / `PostToolUse` / `Stop` 等 |
| 顶层字段 | `version: 1` + `hooks: { <EventName>: [{matcher, hooks: [{type: "command", command, timeout}]}] }` |

### 本项目约定

| 文件 | 触发场景 |
|------|----------|
| `.trae/hooks.json` / `.agents/hooks.json` | 项目级 Trae IDE hook 配置 |
| `.husky/pre-commit` / `pre-push` / `post-commit` | git 事件（husky 自带）|
| `.github/workflows/*.yml` | GitHub 事件（CI）|

### 四机制对比

| 机制 | 触发方式 | 执行内容 | 用途 |
|------|----------|----------|------|
| **Hook** | 生命周期事件自动触发 | Shell 命令 | 自动化控制 |
| Rules | 对话开始注入 | 文本约束 | 规范 AI 输出 |
| Skills | 任务匹配按需加载 | 指令集 + 资源 | 赋予专业能力 |
| Commands | 用户手动 `/` 调用 | 封装的操作 | 简化重复操作 |

**何时用**：想让提交前自动跑检查 / 工具调用后自动做事 / 把重复操作脚本化。
**何时不用**：让 agent 学能力 → skills；约束 AI 行为 → rules；用户主动触发 → commands（`/plan` `/spec` `/browser_use`）。

> 改 hook 看 `.trae/identity/protected-paths.yaml` Tier 3/4 — 多数 gate 文件禁止普通 agent 改。

---

## mcp — Model Context Protocol

### 官方机制

| 类型 | 必填字段 |
|------|----------|
| **stdio** | `command`（可执行命令,不能含空格）+ 可选 `args` / `env` |
| **HTTP** | `url`（远程 MCP Server 地址）+ 可选 `headers` |

**项目级**：根目录 `.trae/mcp.json`。
**变量**：支持 `${workspaceFolder}` 启动时替换。

### 本项目调用方式

**调用前必做**：`LS` + `Read` 读 `c:\Users\septe\.trae-cn\mcps\<server>\tools\<tool>.json` 的 schema。
**参数传递**：所有 tool-specific 参数全部塞 `args` 字段。

**何时用**：需要查 GitHub / 飞书 / 数据库 / 浏览器自动化 / 外部 API。
**何时不用**：项目本地文件用 `Read`/`Write`/`Glob`；项目本地命令用 `RunCommand`。

---

## 一句话铁律

> **agents 调度、skills 赋能、rules 约束、hooks 自动化、mcp 接外**。