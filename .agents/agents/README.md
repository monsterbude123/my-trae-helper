# .agents/agents/ — 项目级云端可复用 Agent 配置

> **职责**：放置**项目级云端可复用**的 Agent 定义。任何拉取本仓库的人都能直接用。
>
> **不允许**：本地环境级 / 个人隐私 / 一时调试用的 Agent — 这类放 `.trae/agents/`（`.gitignore` 内，不提交）。

## 与 `.trae/agents/` 的边界

| 维度 | `.agents/agents/` | `.trae/agents/` |
|------|--------------------|--------------------|
| 提交状态 | ✅ 随仓库提交 | ❌ `.gitignore` 排除（本地） |
| 内容性质 | 通用、可复用 | 个人/本机/临时 |
| 例子 | role-based specialist、reviewer、planner 等可被多项目复用的角色 | 本机调试 assistant、临时跑通的实验 agent |
| 命名约束 | kebab-case，**不带 `-agent` 后缀** | 无约束 |

## 命名规范

- 文件名：`kebab-case.md` 或 `kebab-case.yaml`
- **不带 `-agent` 后缀**（已在 `agents/` 目录内）
- frontmatter 必带 `name` + `description`，推荐 `model` / `tools`

## 当前状态

> 当前没有提交级 Agent 定义（云端可复用）。后续按需新增。

## 与 `.agents/skills/` 的区分

| 概念 | 目录 | 加载方式 | 何时用 |
|------|------|---------|--------|
| Skill | `.agents/skills/<name>/` | `Skill` 工具 | 改变主 Agent 行为/知识 |
| Agent | `.agents/agents/*.md` | `Task` 工具 | 流水线中的专业化工人 |

详见 AGENTS.md §5。
