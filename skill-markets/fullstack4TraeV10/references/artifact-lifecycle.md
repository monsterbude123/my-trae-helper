# 工件生命周期

> 文档分层 + 文件体积约束 + 状态卡重置规则。

---

## 文档分层标签（V10.6 — 子代理可机械判定）

> 根因：历史档案/changelog/fix_result 等"过程文档"被当"事实文档"喂给子代理，
> 导致上下文噪音淹没、旧 agent 错误判断成为幻觉种子。
> 治理：显式 `layer:` 标签，子代理按层判定"现在能不能读"。

| layer | 含义 | 典型文档 | 子代理任务执行时 | 复盘时 |
|:-----:|------|---------|:---------------:|:-----:|
| `fact` | 项目真相源 | contracts/、spec.md、ARCHITECTURE.md、模块文档、AGENTS.md | **必读** | 必读 |
| `process` | 过程产物 | diagnose.md、fix_result.md、分析手记、v1v2v3 修复记录、evidence JSON | **禁读** | 可读 |
| `log` | 操作日志 | changelog、commit log、state-card 历史、review 报告 | **不作验收依据** | 可读 |

### 判定规则（子代理执行）

```
子代理启动时:
  1. 主上下文在委派 prompt 中注入 [DOC_WHITELIST]（路径前缀列表）
  2. 子代理只能读白名单内的文件
  3. 白名单只含 layer=fact 的文档
  4. layer=process/log 的文档:
     - 子代理不主动遍历、不主动读
     - 主上下文从中提取"事实摘要"（≤5 行）注入到委派 prompt
     - 子代理拿到的永远是"过滤后的事实点"，不是"历史文件路径"
```

### 分层标签示例

文档头部 YAML frontmatter 加 `layer` 字段：
```yaml
---
layer: fact     # 事实文档 — 任务执行时必读
---
```

无 `layer` 字段的文档默认 `layer: process`（保守策略，防止噪音泄漏）。

### spec 领域 layer 分配（V10.6）

| 文件 | layer | 说明 |
|------|:-----:|------|
| `plan.md` | fact | 意向声明（Why + Capabilities + Impact） |
| `define.md` | fact | 意向边界（Non-Goals + Out of Scope） |
| `spec.md` | fact | 行为规格 + 验收标准 |
| `design.md` | fact | 技术方案 + 架构决策 |
| `contracts/*.md` | fact | 接口契约 + 领域模型 |
| `tasks.md` | fact | 当前实现清单（checkbox） |
| `prototypes/*` | fact | UI 视觉原型 |
| `.state-card.md` | process | 状态快照（阶段性，非真相源） |
| `_invalidated/` | process | 回流隔离旧产物 |
| `docs/reports/review-*.md` | log | 审查报告 |
| `docs/bugs/` | process | Bug 修复记录 |
| `changelog` / `commit log` | log | 操作日志 |

---

## 体积硬上限

| 文件类型 | 上限 | 超出动作 |
|---------|:---:|---------|
| 单源码文件 | 800 行 | 拆分为多文件 |
| 状态卡 (.state-card.md) | 80 行 | 执行重置（从模板重建） |
| Spec 文件 | 200 行 | 拆分为父文件 + 子文件 |
| define.md | 80 行 | 精简 Non-Goals + Out of Scope |
| Contract 单文件 | 200 行 | 拆分为子契约 |

---

## 状态卡四态重置

```
正常 (< 80 行) → 继续使用
接近上限 (70-80 行) → 修剪历史记录
超标 (> 80 行) → 重置：从模板重建，保留 phase/health/blocked
```

---

## 禁止写入状态卡的内容

- 实现细节（放代码注释）
- Review 评分（放审查报告）
- DOC SYNC 时间戳（放 git log）
- Bug 修复过程（放 commit message）

---

## 文档治理原则

- 修剪/迁移文档时，操作前编目事实 → 操作后逐项验证 → 缺失 = 回退
- `archive/` 目录下文件不可修改（归档 = 只读）
- 过程文档（layer=process）不进 `contracts/` 或 `specs/changes/`，放 `docs/bugs/` 或 `docs/reports/`

---

## Single Source of Truth（V10.6）

- 每个知识点只在 1 个文件出现，其他文件只放指针 + 摘要
- state-card.md 是版本号/健康度的唯一权威源，其他文档只引用 state-card 的版本号 + 章节链接
- 禁止在 spec.md / design.md / tasks.md 之间复制粘贴同一段内容

## 事实块沉淀（V10.6）

- MCP 抓取的事实（GitNexus context / Chrome DevTools network / 抽帧数据）必须作为完整段落写进 reference 文件
- 同一 session 内不重复跑同一 MCP 分析——已沉淀的事实直接 Read
- reference 文件 layer: fact，任务执行时可读
