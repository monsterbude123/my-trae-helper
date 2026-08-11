---
title: Fullstack4TraeV10 思想图谱索引
description: 12 个 Mermaid 文件表达 V10.12 全栈文档驱动开发的设计思想
layer: fact
---

# Fullstack4TraeV10 思想图谱索引

> 使用 mermaid（mindmap + graph + flowchart）将 fullstack4TraeV10 全栈文档驱动开发技能包的设计思想可视化。
> 每个文件聚焦一个核心主题，可独立阅读，也可按顺序串成完整学习路径。

## 文件清单

| # | 文件 | 主题 | 核心 mermaid 类型 |
|---|------|------|------------------|
| 00 | [00-overview-mindmap.md](00-overview-mindmap.md) | 全栈总览 + 哲学 + 5 阶段 + 14 Articles + 5 维度 | mindmap |
| 01 | [01-constitution-mindmap.md](01-constitution-mindmap.md) | 14 Articles 宪法铁律全景 | mindmap + graph |
| 02 | [02-pipeline-flow-graph.md](02-pipeline-flow-graph.md) | 5 阶段流水线 + Phase 3.5/4.5 | flowchart + graph |
| 03 | [03-delegation-discipline.md](03-delegation-discipline.md) | 委派纪律 + 子代理铁律 | mindmap + flowchart |
| 04 | [04-spec-driven-mindmap.md](04-spec-driven-mindmap.md) | 契约先行 + Spec 真相源 + TDD | mindmap + flowchart |
| 05 | [05-rot-detection.md](05-rot-detection.md) | 腐化防御 + 5 项扫描 + 7 大分类 | mindmap + flowchart |
| 06 | [06-skeptical-validation.md](06-skeptical-validation.md) | 质疑性校验 + 技能优化 + 知识库升级 | mindmap + flowchart |
| 07 | [07-agent-architecture.md](07-agent-architecture.md) | 9 Agent 角色 Mindmap | mindmap + graph |
| 08 | [08-skill-loading-protocol.md](08-skill-loading-protocol.md) | §0.5 加载协议 + §0.10 启动验证 | mindmap + flowchart |
| 09 | [09-acceptance-gates.md](09-acceptance-gates.md) | 验收门禁 + 4 维评分 + 视觉证据 | mindmap + graph |
| 10 | [10-bug-debug-mindmap.md](10-bug-debug-mindmap.md) | Bug 录入 + 5 步流水线 + 6 层排查 | mindmap + flowchart |
| 11 | [11-version-evolution-graph.md](11-version-evolution-graph.md) | V10.0 → V10.12.1 演进 + 索引 | graph + mindmap |

## 推荐学习路径

### 路径 A：新手入门（按流程顺序）

```
00 总览
  ↓
01 宪法（14 Articles）
  ↓
02 流水线（5 阶段）
  ↓
04 契约先行 + TDD
  ↓
07 Agent 角色
  ↓
09 验收门禁
  ↓
05 腐化防御
  ↓
10 Bug 调试
```

### 路径 B：升级者视角（V10.8 → V10.12.1）

```
06 质疑性校验 + 技能优化方法论
  ↓
08 §0.5 加载协议 + §0.10 启动验证
  ↓
03 委派纪律
  ↓
05 腐化防御 rot #18/#19
  ↓
11 版本演进
```

### 路径 C：实战操盘手

```
08 §0.5 加载协议（必须先看）
  ↓
02 流水线（图解）
  ↓
03 委派纪律（防虚假交付）
  ↓
09 验收 4 维 + 视觉证据
  ↓
10 Bug 流水线
  ↓
05 腐化防御
```

## 核心设计思想提炼

### 哲学 8 句

| 立场 | 含义 |
|------|------|
| 复用而非自研 | spec-kit 五阶段骨架 + GitNexus + 既存工具 |
| 质量而非流程 | 14 Articles 不可降级 + 5 维度硬门禁 |
| 验证而非信任 | 机械脚本 + 异会话抽检 + 视觉证据 |
| 干净而非兼容 | 无 .bak / 无骨架堆积 / 归档不可变 |
| 主动而非被动 | rot-detector 必跑 + 质疑式验收 |
| 诚实而非吹嘘 | 通过依据 3 类分层 + 障碍 5 字段 |
| 骨感而非堆积 | Agent ≤10 条铁律 ≤150 行 |
| 分层而非混置 | fact / process / log 三层标注 |

### 核心防失真 4 大机制

1. **§0.5 Skill 加载协议** — 主上下文必读 4 references + Glob 项目惯例
2. **§7.5 AskUserQuestion 反模式** — 用户没选选项 = 可能在质疑流程
3. **clarify-checklist.md §7** — ≥2 轮同类问题必触发根因诊断
4. **process-rot-analysis.md §5.5** — rot #21/22/23 三类代理腐烂检测

### 不可降级 8 Articles

即使修改流程也维持底线：
- I TDD 强制
- II 满分硬门禁
- IV 委派纪律
- V GitNexus First
- VIII 归档不可变
- IX TDD 即时
- XIV rot-detector 必跑
- XV 障碍诚实
- XVI 禁止抽象理由

## 如何使用本目录

每个 .md 文件都包含：
1. **YAML frontmatter** — 标题 + 描述 + layer 标签
2. **mermaid 块** — 核心图谱（推荐 IDE 渲染查看）
3. **关键引用区** — 入口到原文档的链接

支持的 mermaid 渲染器：
- GitHub / VSCode / Trae IDE 内置预览
- mermaid.live 在线编辑器
- docsify + mermaid 插件
- obsidian 双链 + mindmap 插件

## 关联引用

- 主技能: [fullstack4TraeV10](../SKILL.md)
- 场景演练: [scenarios.md](../scenarios.md)
- 版本变更: [changelog.md](../references/changelog.md)
- 术语表: [glossary.md](../references/glossary.md)
