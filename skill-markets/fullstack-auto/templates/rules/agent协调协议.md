# Agent 协调协议 — 主上下文只协调不执行

> fullstack + goal-mode 同时激活时生效。

## 铁律

主上下文 = 协调器 + 路由器，不直接执行 coding/spec/doc/sync 工作。所有执行通过 Task 工具委派子代理。

## 决策树

goal-mode + fullstack 激活 → pursuer 按阶段委派：
proposal-writer → spec-writer → planner → implementer → reviewer → doc-updater

## 禁止行为

| 禁止 | 替代方案 |
|------|---------|
| 主上下文直接 Read/Write/Edit 代码 | 委派 implementer agent |
| 主上下文直接写 spec/design/tasks | 委派 spec-writer / planner agent |
| 主上下文调测试框架 | 委派 implementer（TDD 红绿重构） |
| 跳过 DOC SYNC GATE | implementer 启动前 doc-updater 先跑 |
| 执行者自审 | 执行 agent ≠ 审计 agent（goal-mode 硬约束） |
