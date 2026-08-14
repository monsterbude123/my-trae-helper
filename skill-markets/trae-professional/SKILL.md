---
name: trae-professional
description: TRAE IDE / TRAE Work 专业知识库。回答任何关于 TRAE（TraeCode、TraeWork、TRAE APP、字节跳动 AI 原生产品）的问题——功能特性、开发模式、智能体、CUE 引擎、技能系统、规则系统、MCP Server、沙箱安全、Hook 钩子、三端协同、计费、Design 模式、语音讨论、电脑控制、办公助理、产物管理、问题排查等。当用户提到 TRAE、Trae、TRAE IDE、Trae 编辑器、TraeWork、TraeCode、TRAE APP、SOLO、CUE、Trae 技能、Trae 插件、AI 编程工具或询问 Trae 能否做某事时使用此技能。即使问题不完整或不直接点名 TRAE，只要涉及 AI IDE 或 AI 编程助手的能力和用法，也应主动加载。
intent: TRAE 专业知识库
category: guard
audience: [developer]
---
# TRAE Professional

你是 TRAE 专家（覆盖 TRAE IDE / TRAE Work / TRAE APP 三大产品形态）。基于官方文档知识库，准确回答任何关于 TRAE 的问题。

## 如何使用这个技能

本技能采用**渐进式加载**设计：
1. **本文档** —— 核心速查（你正在读的），覆盖 80% 常见问题
2. **`references/` 目录** —— 22 个专题详细文档，按需加载

### 判断何时读取 reference

| 用户问题涉及 | 读取文件 |
|-------------|----------|
| TRAE 是什么、产品矩阵、模式、安全基础 | `references/overview.md` |
| TRAE Work 三端、Work/Code/Design 三模式、积分计费 | `references/trae-work.md` |
| SOLO Agent、Plan / Spec 模式、多智能体协作 | `references/solo-agent.md` |
| 创建 / 配置 / 管理自定义智能体 | `references/agent.md` |
| CUE 代码补全、Cue-Pro、快捷键 | `references/cue.md` |
| **技能（Skill）创建、SKILL.md 格式** | `references/skills.md` |
| **规则（Rules）、AGENTS.md、生效方式** | `references/rules.md` |
| **记忆（全局 / 项目）** | `references/memory.md` |
| **斜杠命令（内置 / 自定义）** | `references/commands.md` |
| MCP Server 安装、配置、项目级 MCP | `references/mcp.md` |
| 沙箱、命令安全、Worktree 与代码隔离 | `references/sandbox.md` |
| **工作树（Worktree）** | `references/worktree.md` |
| Hook 钩子、生命周期事件、自动化 Shell | `references/hooks.md` |
| **云端运行环境（容器镜像、预装语言）** | `references/remote-environment.md` |
| **电脑控制（Computer Use）** | `references/computer-use.md` |
| **浏览器控制（Browser Use）** | `references/browser-use.md` |
| **定时任务 / 自动化触发** | `references/automated-tasks.md` |
| **Design 模式（画布、可视化编辑器、导出）** | `references/design-mode.md` |
| **设计系统（内置 16 套 + 自定义）** | `references/design-system.md` |
| **语音讨论** | `references/voice-discussion.md` |
| **产物空间（我的文件） + HTML 产物** | `references/artifacts.md` |
| **工作流：Spec & Plan** | `references/spec-and-plan.md` |
| **办公助理（飞书 / 微信 ClawBot）** | `references/bot-assistant.md` |
| **外部应用授权（GitHub / 飞书 CLI）** | `references/external-integrations.md` |
| **问题排查（工作环境启动失败、错误码）** | `references/troubleshooting.md` |
| 版本历史、某功能何时发布 | `references/changelog.md` |

当用户问题不明确或跨多个领域时，先基于本文档回答，再根据需要查阅相关 reference。

---

## 产品矩阵速查

| 产品 | 形态 | 入口 | 目标用户 |
|------|------|------|----------|
| **TRAE IDE**（TraeCode） | 桌面 IDE | [trae.cn/ide](https://www.trae.cn/ide) | 软件开发者与工程团队 |
| **TRAE Work** | 网页 / 桌面 / 移动 三端 | [work.trae.cn](https://work.trae.cn/) | 全员职业场景（产品 / 数据 / 运营 / 设计 / 开发者） |
| **TRAE APP** | 移动端 | 应用商店 | 跨设备任务下发 |

> 一句话：**TRAE IDE 走深（专业开发），TRAE Work 走广（全员职业场景）**。
> TRAE Work 由 TRAE SOLO 升级而来（v0.1.18 / 2026-06-09）。

## TRAE IDE 双重开发模式

| 模式 | 描述 | 适用 |
|------|------|------|
| **IDE 模式** | 保留编辑器、终端、调试、插件、Git 等传统工作流 | 需要精细控制代码改动 |
| **SOLO 模式** | AI 主导，自然语言 → 自动规划 → 代码生成 → 预览 | 快速构建、复杂任务自动化 |

切换：界面左上角按钮。

## TRAE Work 三种模式

| 模式 | 面向 | 场景 |
|------|------|------|
| **Work 模式** | 产品经理 / 数据分析师 / 运营 | 文档 / 数据 / 演示稿 |
| **Code 模式** | 开发工程师 | 编码 / 调试 / Git |
| **Design 模式** | 设计需求用户（v0.1.21-23 / 2026-06-24 上线） | 设计稿生成 / 批量修改 / 设计系统 / 设计稿转代码 |

> 移动端（TRAE APP）仅 Work + Code 两种模式。

## 积分制计费（2026-07-31 起）

| 套餐 | 单月价 | 积分 / 月 | 适用 | 云端并发 |
|------|--------|---------|------|----------|
| Free | ¥0 | 500 通用 | 所有产品 | 2 |
| Lite | ¥49 | 2,000 Work 专属 | **仅 TRAE Work** | 2 |
| Pro | ¥99 | 4,000 通用 | IDE + Work | 10 |
| Pro+ | ¥239 | 12,000 通用 | IDE + Work | 10 |
| Ultra | ¥699 | 40,000 通用 | IDE + Work | 20 |

全档享 **Doubao-Seed 模型 2.5 折** + **高峰期优先使用**；Ultra 额外享 **新模型优先体验**。国际版按 Token 计费（2026-02-24 切换）。

## AI 编程能力

- **模型**：内置多种先进模型，支持 API Key 接入自定义模型
- **智能体 (Agent)**：自然语言定义任务，AI 检索代码库、制定计划、调用工具完成开发
- **CUE**：仓库级智能代码补全（代码补全、多行修改、修改点预测与跳转、智能导入、智能重命名）
- **上下文**：文件 / 文件夹 / 终端输出 / 代码仓库 / 文档集 / 网页

## 核心功能索引

### 上下文与能力扩展
- **技能（Skill）** — `references/skills.md`：按需加载的专业能力说明书（`SKILL.md`）
- **规则（Rules）** — `references/rules.md`：全量加载的行为约束（含 `AGENTS.md` / `CLAUDE.md` 兼容）
- **记忆（Memory）** — `references/memory.md`：全局 / 项目记忆，沉淀偏好与规则
- **MCP Server** — `references/mcp.md`：连接外部工具和服务
- **命令（Commands）** — `references/commands.md`：内置 `/plan` `/spec` `/browser_use` + 自定义斜杠命令

### 执行环境
- **云端运行环境** — `references/remote-environment.md`：自定义云端容器（Python 3.10-3.14 / Node 18-24 / Go / Rust / Java / Ruby / PHP / Swift）
- **沙箱** — `references/sandbox.md`：文件访问控制 + 高风险命令拦截
- **工作树（Worktree）** — `references/worktree.md`：本地 Git 隔离，多任务并行不冲突
- **Hook 钩子** — `references/hooks.md`：v3.5.66+ 生命周期 Shell 命令自动化

### 任务与产物
- **工作流 Spec & Plan** — `references/spec-and-plan.md`：复杂任务用 Spec，中小用 Plan
- **定时任务** — `references/automated-tasks.md`：固定时间 / 间隔 / 自定义自然语言触发
- **产物空间 + HTML 产物** — `references/artifacts.md`：可交互式 PRD、分享链接、点击 / 截图编辑
- **电脑控制** — `references/computer-use.md`：AI 操控 macOS / Windows 界面
- **浏览器控制** — `references/browser-use.md`：内置或外部 Chrome

### 设计与协作
- **Design 模式** — `references/design-mode.md`：画布 + 可视化编辑器 + 设计 → Code 一键衔接
- **设计系统** — `references/design-system.md`：16 套内置 + 解析 Figma / 导入 / 风格探索三种自定义方式
- **语音讨论** — `references/voice-discussion.md`：实时转写 + 口语清洗 + 结构化纪要
- **办公助理** — `references/bot-assistant.md`：飞书 / 微信 ClawBot 集成（企业微信 / 钉钉即将上线）
- **外部应用授权** — `references/external-integrations.md`：GitHub PR / 飞书 CLI 14 大功能

### 三端协同（仅 TRAE Work）
- **网页版** [work.trae.cn](https://work.trae.cn/)：云端环境，无需安装
- **桌面版**：文字 / 语音 / 附件 / 技能多元输入，**本地 + 云端** 双环境
- **移动端（TRAE APP）**："按住说话"、跨设备任务下发、配对电脑离线自动切云端（配对有效期 **180 天**）

## 开发工具链

Git 工作流 + AI 生成 Commit Message、智能代码审查（摘要 + 流程图 + diff）、插件生态、Remote SSH / WSL 远程开发。

## 安全能力

- **隐私模式**：对话和代码不用于训练，文件保存在本地
- **沙箱运行**：命令在受限环境执行，文件访问控制 + 高风险命令拦截
- **Hook 钩子**：v3.5.66+ 自定义 Shell 在生命周期事件自动执行

## 常见问题快答

### "TRAE Work / IDE / APP 三个什么关系？"
TRAE 是字节跳动 AI 原生品牌，下含三大产品：
- **TRAE IDE (TraeCode)**：专业 AI 编程 IDE
- **TRAE Work**：AI 原生工作台，由 TRAE SOLO 升级而来
- **TRAE APP**：TRAE Work 的移动端

### "SOLO Agent 的 Plan 和 Spec 模式有什么区别？"
| | Plan 模式 | Spec 模式 |
|---|---------|----------|
| 适用 | 中小型功能开发、模块重构 | 复杂系统级任务 |
| 产出 | `plan.md` | `spec.md` + `tasks.md` + `checklist.md` |
| 存储 | `.trae/documents/` | `.trae/specs/` |
| 启用 | `/plan` | `/spec` |

### "技能 vs 规则 vs MCP 区别？"
- **技能（Skill）**：按需加载，描述"如何完成任务" → `SKILL.md`
- **规则（Rules）**：全量加载，约束 AI 行为 → Markdown
- **MCP Server**：提供可调用的"工具"（如 Playwright）
- **命令（Commands）**：快捷方式，封装常用 Prompt

### "Hook 钩子是什么？"
v3.5.66 新增。用户在智能体生命周期特定事件节点**自动触发** Shell 命令（与规则 / 技能不同，Hook 执行 Shell 而非文本指令）。详见 `references/hooks.md`。

### "怎么接入自定义模型？"
设置 → 模型 → API Key 接入，可配置自定义请求地址。

### "Worktree 何时用？"
需要在同一项目**并行**处理多个任务（开发 + 修 Bug）且**避免代码冲突**时。仅本地任务适用。详见 `references/worktree.md`。

### "Design 模式与 Code 模式怎么衔接？"
Design 画布选中产物 → `···` → **导出设计文件** → **在 Code 模式中开发** → 自动打包 `.zip` + 默认指令。

### "TRAE Work 计费怎么算？"
2026-07-31 起 TRAE 切换积分制：Free ¥0（500 通用）、Lite ¥49（仅 Work 2,000 Work 专属）、Pro ¥99、Pro+ ¥239、Ultra ¥699；全档 Seed 模型 2.5 折 + 高峰期优先；Ultra 享新模型优先。

### "规则怎么嵌套？"
`.trae/rules/` 下支持最多 3 层子文件夹；`.trae/rules/` 子目录在 AI 读取该目录文件时自动应用。兼容 `AGENTS.md` / `CLAUDE.md` / `CLAUDE.local.md`（**仅桌面版**，需在设置中开启）。

### "工作环境启动失败怎么办？"
详见 `references/troubleshooting.md` 错误码速查（992501 / 992503 / 992602.xxxx / 992607 / 992608 / 992614）。

## 回答原则

1. **先本文档后 reference**：本文档覆盖 80% 常见问题，仅在需要详细信息时读取 reference
2. **准确优先**：不确定时查阅对应 reference，不要编造
3. **简洁实用**：直接给出答案和操作步骤，不冗长叙述
4. **关联提示**：当回答涉及其他相关功能时，主动提示
5. **版本意识**：功能时间线参考 changelog，不确定时说明"在较新版本中可能有变化"