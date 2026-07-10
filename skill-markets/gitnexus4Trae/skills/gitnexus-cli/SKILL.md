---
name: gitnexus-cli
description: "用于运行 GitNexus CLI 命令——索引/分析项目、检查状态、清理索引、生成 wiki、列出已索引仓库。当用户说\"索引这个项目\"、\"重新分析代码库\"、\"生成 wiki\"、\"清理 GitNexus\"、\"检查索引状态\"时加载。"
---

# GitNexus CLI 命令

所有命令通过 `npx` 运行，无需全局安装。在 TRAE 终端中执行。

## 使用场景

- 首次在项目中使用 GitNexus
- 代码重大变更后需要重建索引
- 检查索引是否过期
- 清理损坏的索引
- 生成项目文档

## 命令

### analyze — 构建或刷新索引

```bash
npx gitnexus analyze
```

在项目根目录运行。解析所有源文件，构建知识图谱，写入 `.gitnexus/`，并生成 AGENTS.md 上下文文件。

| 参数 | 效果 |
|------|------|
| `--force` | 强制全量重建索引 |
| `--embeddings` | 启用向量嵌入生成（默认关闭） |
| `--drop-embeddings` | 重建时丢弃已有嵌入 |

**何时运行：** 首次使用、重大代码变更后、或索引报告过时时。

### status — 检查索引新鲜度

```bash
npx gitnexus status
```

显示当前仓库是否有 GitNexus 索引、最后更新时间、符号数和关系数。

### clean — 删除索引

```bash
npx gitnexus clean
```

删除 `.gitnexus/` 目录并从全局注册表中取消注册。

| 参数 | 效果 |
|------|------|
| `--force` | 跳过确认提示 |
| `--all` | 清理所有已索引仓库 |

### wiki — 从图谱生成文档

```bash
npx gitnexus wiki
```

使用 LLM 从知识图谱生成仓库文档。首次使用需提供 API Key（保存至 `~/.gitnexus/config.json`）。

| 参数 | 效果 |
|------|------|
| `--force` | 强制全量重新生成 |
| `--model <model>` | LLM 模型（默认: minimax/minimax-m2.5） |
| `--base-url <url>` | LLM API 地址 |
| `--api-key <key>` | LLM API Key |
| `--concurrency <n>` | 并行调用数（默认: 3） |
| `--gist` | 发布为 GitHub Gist |

### list — 显示所有已索引仓库

```bash
npx gitnexus list
```

列出 `~/.gitnexus/registry.json` 中注册的所有仓库。

## 索引完成后

1. 用 `npx gitnexus status` 验证索引加载成功
2. 使用其他 GitNexus 技能（`exploring`、`debugging`、`impact-analysis`、`refactoring`）

## 故障排查

- **"Not inside a git repository"**：在 git 仓库内运行
- **重建后索引仍显示过时**：重启 TRAE IDE 重新加载 MCP Server
- **嵌入生成慢**：去掉 `--embeddings`（默认关闭）或设置 `OPENAI_API_KEY`
