---
name: gitnexus-guide
description: "GitNexus 工具参考、MCP 资源和知识图谱模式速查。当用户问\"GitNexus 有哪些工具\"、\"GitNexus 怎么用\"、\"schema 是什么\"、\"MCP 资源有哪些\"等 GitNexus 本身的使用问题时加载。即使不直接说 guide，只要在查询 GitNexus 的能力和用法就应加载。"
---

# GitNexus 速查指南

TRAE IDE 环境下的 GitNexus MCP 工具、资源和知识图谱模式快速参考。

## 入口

任何涉及代码理解、调试、影响分析或重构的任务：

1. **检查索引新鲜度** — 运行 `npx gitnexus status` 或读取 context 资源
2. **匹配你的任务到对应技能**并**加载该技能**
3. **按技能的工作流和检查清单执行**

> 如果索引过时，先在终端运行 `npx gitnexus analyze`。

## 技能索引

| 任务 | 加载技能 |
|------|---------|
| 理解架构 / "X 怎么工作" | `gitnexus-exploring` |
| 爆炸半径 / "改 X 会影响什么" | `gitnexus-impact-analysis` |
| 追踪 bug / "为什么 X 失败" | `gitnexus-debugging` |
| 重命名 / 提取 / 拆分 / 重构 | `gitnexus-refactoring` |
| 工具、资源、模式参考 | `gitnexus-guide`（本技能）|
| 索引、状态、清理、wiki 命令 | `gitnexus-cli` |

## 工具参考

所有 GitNexus MCP 工具在 TRAE IDE 中通过 `run_mcp({server_name: "gitnexus", tool_name: "...", args: {...}})` 调用：

| 工具 | 功能 | 调用示例 |
|------|------|---------|
| `query` | 按流程分组代码智能 — 概念相关的执行流 | `run_mcp({server_name: "gitnexus", tool_name: "query", args: {query: "支付"}})` |
| `context` | 符号 360 度视图 — 分类引用、所在流程 | `run_mcp({server_name: "gitnexus", tool_name: "context", args: {name: "validateUser"}})` |
| `impact` | 符号爆炸半径 — 各深度的破坏范围及置信度 | `run_mcp({server_name: "gitnexus", tool_name: "impact", args: {target: "validateUser", direction: "upstream"}})` |
| `detect_changes` | Git diff 影响 — 当前改动影响哪些内容 | `run_mcp({server_name: "gitnexus", tool_name: "detect_changes", args: {}})` |
| `rename` | 多文件协调重命名，编辑带置信度标记 | `run_mcp({server_name: "gitnexus", tool_name: "rename", args: {symbol_name: "oldName", new_name: "newName", dry_run: true}})` |
| `cypher` | 原始图查询（先读 schema 资源） | `run_mcp({server_name: "gitnexus", tool_name: "cypher", args: {query: "MATCH ... RETURN ..."}})` |
| `list_repos` | 发现已索引的仓库 | `run_mcp({server_name: "gitnexus", tool_name: "list_repos", args: {}})` |

## MCP 资源

GitNexus 提供轻量 MCP 资源（约 100-500 token）用于导航：

| 资源 | 内容 |
|------|------|
| `gitnexus://repo/{name}/context` | 统计信息、索引新鲜度检查 |
| `gitnexus://repo/{name}/clusters` | 所有功能区域及内聚度评分 |
| `gitnexus://repo/{name}/cluster/{clusterName}` | 区域成员 |
| `gitnexus://repo/{name}/processes` | 所有执行流 |
| `gitnexus://repo/{name}/process/{processName}` | 逐步执行追踪 |
| `gitnexus://repo/{name}/schema` | Cypher 图模式 |

## 图模式

**节点：** File, Function, Class, Interface, Method, Community, Process
**边（通过 CodeRelation.type）：** CALLS, IMPORTS, EXTENDS, IMPLEMENTS, DEFINES, MEMBER_OF, STEP_IN_PROCESS

Cypher 查询示例：

```cypher
MATCH (caller)-[:CodeRelation {type: 'CALLS'}]->(f:Function {name: "myFunc"})
RETURN caller.name, caller.filePath
```

TRAE 调用方式：

```
run_mcp({server_name: "gitnexus", tool_name: "cypher", args: {query: "MATCH (caller)-[:CodeRelation {type: 'CALLS'}]->(f:Function {name: 'myFunc'}) RETURN caller.name, caller.filePath"}})
```
