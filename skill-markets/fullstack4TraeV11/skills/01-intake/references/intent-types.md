# 5 种意图类型详解 — 总览

> Stage -1 Intake 的核心分类。所有用户输入必归类到这 5 种意图之一。
>
> **本文件为索引**，按 5 意图拆分到 `intent-types-detail/` 子文件。所有内容保真保留。

---

## 意图总览

| # | 意图 | 路由目标 | 状态卡类型 | 用户确认 |
|:---:|------|---------|-----------|:---:|
| 1 | **project-init** | Stage 0 Plan → Stage 5 Accept | project | 🛑 |
| 2 | **change-start** (feature/refactor) | Stage 0 Plan → Stage 5 Accept | change | 🛑 |
| 3 | **change-start** (doc-sync) | Stage 1 Spec → Stage 5 Accept (lite) | change | ⚙ |
| 4 | **bug-fix** | Stage 6 Bug Fix（独立支线）| bug | 🛑 |
| 5 | **project-health** | Stage 7 Project Health（异步自检）| project | ⚙ |

---

## 5 意图章节指针

| # | 意图 | 文件 |
|:---:|------|------|
| 1 | project-init（项目 0→1 初始化） | [01-project-init.md](./intent-types-detail/01-project-init.md) |
| 2 | change-start（feature / refactor） | [02-change-start.md](./intent-types-detail/02-change-start.md) |
| 3 | change-start (doc-sync)（文档同步） | [03-change-start-doc-sync.md](./intent-types-detail/03-change-start-doc-sync.md) |
| 4 | bug-fix（Bug 修复） | [04-bug-fix.md](./intent-types-detail/04-bug-fix.md) |
| 5 | project-health（项目健康度自检）+ 速查表 + 模糊处理 | [05-project-health.md](./intent-types-detail/05-project-health.md) |

---

## 必读

- 识别到具体意图后只 Read 对应子文件，避免 context 击穿
- 速查表 + 模糊处理集中在 `05-project-health.md`

---

## 关联引用

- [SKILL.md](../SKILL.md) — 阶段入口
- [intent-routing.md](../workflows/intent-routing.md) — 意图路由工作流
- [routing-decision-tree.md](routing-decision-tree.md) — 路由决策树
- [bug-state-machine.md](bug-state-machine.md) — Bug 单状态机
- [bug-intake-flow.md](../workflows/bug-intake-flow.md) — Bug 录入工作流
