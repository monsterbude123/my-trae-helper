# 工件依赖图（Artifact Schema）

> 内化自 OpenSpec `schemas/spec-driven/schema.yaml`
> 定义各工件之间的依赖关系与创建顺序。依赖是"使能器"（enablers），非硬锁阶段。

---

## 一、依赖图

```
                 plan.md
                (root node)
                    │
        ┌───────────┴───────────┐
        │                       │
        ▼                       ▼
    spec.md                  design.md
  (requires:                  (requires:
   plan.md)                  plan.md)
        │                       │
        └───────────┬───────────┘
                    │
                    ▼
                tasks.md
             (requires:
             spec.md,
             design.md)
                    │
                    ▼
                implement
             (requires:
              tasks.md)
```

---

## 二、工件定义

| ID | 文件 | 依赖 | 描述 |
|----|------|------|------|
| `proposal` | `plan.md` | — | Why + Capabilities + Impact（意向声明） |
| `define` | `define.md` | `proposal` | 精简 Non-Goals + Out of Scope |
| `specs` | `spec.md` | `proposal` | 行为规格（Delta 或全量）+ 验收标准 |
| `design` | `design.md` | `proposal` | 技术方案 + 架构决策 + 风险 |
| `prototype` | `prototypes/` | `define` | UI 视觉原型（design-prompt + ui-ux-logic） |
| `tasks` | `tasks.md` | `specs`, `design` | 实现清单（checkbox 格式） |
| `contract` | `contracts/` | `specs` | 接口契约 + 领域模型 + 测试骨架 |
| `implement` | 代码 + 测试 | `tasks`, `contract` | TDD 实现 |
| `review` | `docs/reports/review-latest.md` | `implement` | 满分硬门禁 4 维度（**不接受 scorecard 替代**） |

---

## 三、核心规则

### Enablers, Not Gates

```
工件依赖回答"可以创建什么"，不回答"必须按什么顺序创建"

✅ 可并行: specs 和 design 都只依赖 proposal → 可同时创建
✅ 可跳过: 不涉及架构变更 → design 可精简或跳过
✅ 可回退: 实现中发现 design 错了 → 编辑 design.md 继续，不锁死
❌ 禁止: 等待"阶段批准"后才允许下一步
```

### 创建顺序约束

```
必须按依赖: proposal → specs → design → tasks → implement
灵活执行: 可以在 proposal 已批准后并行创建 specs + design
最小约束: 只检查依赖存在性，不检查"阶段审批状态"
```

### 实现就绪判定

当以下条件全部满足时，change 进入可实现状态：

```
[ ] plan.md 的 tasks 字段非空（或独立 tasks.md 存在）
[ ] spec.md 存在且门禁通过
[ ] contracts/ 存在（Contract-First 铁律）
[ ] 以上任一缺失 → 🛑 不可进入 Implement
```

---

## 四、与阶段门禁的关系

| 门禁类型 | 语义 | 示例 |
|---------|------|------|
| 工件依赖 | "必须先有 A 才能创建 B"（软依赖） | 没有 spec 写不了 tasks |
| 质量门禁 | "B 必须满足标准才能移交给 C"（硬检查） | TDD RED→GREEN、5 维度 ≥ 4.0 |
| 不可跳过 | "必须执行，不能优化掉" | Contract-First、Review、Accept |

工件依赖是软的（可以跳过 design 如果不需要），质量门禁和不可跳过阶段是硬的。

---

## 五、禁止写入 spec 领域文档的内容（V10.6）

> 腐烂根因：spec.md / define.md / tasks.md / contracts/ 被当"垃圾桶"——
> 验收状态、修复记录、review 报告、commit log 全往里塞。
> 治理：每类文件只含 fact 层内容，process/log 层内容去该去的地方。

### spec.md（layer: fact — 行为规格）

| 禁止写入 | 去哪里 |
|---------|--------|
| 验收状态历史（"v1 PASS→v2 FAIL"） | commit message / review 报告（layer: log） |
| Bug 修复记录 / diagnose 结论 | docs/bugs/ 或 commit message（layer: process） |
| Review 评分 / 审查报告 | docs/reports/（layer: log） |
| 实现细节（代码片段、函数签名） | 代码注释 / contracts/ |
| 历史版本 diff（"v1→v2 改了什么"） | changelog / commit log（layer: log） |

### define.md（layer: fact — 意向边界）

| 禁止写入 | 去哪里 |
|---------|--------|
| 实现细节 | spec.md 或 design.md |
| Bug 修复过程 | commit message（layer: process） |
| 验收清单 | spec.md §Acceptance |

### tasks.md（layer: fact — 实现清单）

| 禁止写入 | 去哪里 |
|---------|--------|
| 历史任务状态（"v1 做了→v2 回退→v3 重做"） | commit log（layer: log） |
| Bug 修复步骤 | commit message（layer: process） |
| 审查备注 | review 报告（layer: log） |

### contracts/（layer: fact — 接口契约）

| 禁止写入 | 去哪里 |
|---------|--------|
| Bug 修复过程 / diagnose 结论 | docs/bugs/（layer: process） |
| 反模式说明（"不要把 X 切到 Y"） | ≤1 行注释，不展开；详细说明放 docs/bugs/ |
| 验收状态 | review 报告（layer: log） |

---

## 六、项目级文档行数硬限制（V10.8 NEW）

> 根因：AGENTS.md / rules/*.md 无行数限制 → 内联大段代码示例 → 上下文击穿。
> 治理：行数硬限制 + 内联代码块限制 + 每周修剪。

| 文件 | 上限 | 原因 |
|------|:---:|------|
| `AGENTS.md` | 200 行 | 地图必须内联，防止迷路（地图弹性） |
| `rules/*.md` | 150 行 | 规范指针，防止击穿 |
| 内联代码块 | ≤10 行 | 示例放 references/ |
| 单源码文件 | 800 行 | 拆分为多文件 |

**每周修剪**：检查 rules/ 过时规则 → 删除已废弃（标注原因）→ 合并重复 → 保持行数限制内。

---

## 七、三层文档分离（V10.8 NEW）

> 根因：AGENTS.md 内联 50 行代码示例 → 上下文击穿；rules/ 内联完整 API 文档 → 规则文件膨胀。
> 治理：三层分离 + 双向链接 + 禁止内联 >10 行代码块。

### 三层结构

| 层 | 职责 | 内容 |
|----|------|------|
| `AGENTS.md` | 内联地图 | 技术栈 + 目录结构 + 架构拓扑 + 入口文件 + 启动命令 + 核心设计决策（Why，≤3 条） |
| `rules/` | 铁律 | P0/P1/P2 分层规则（指针，不展开示例） |
| `references/` | 示例 | 完整代码示例 + 反例 + 详细展开 |

### 协同铁律

AGENTS.md 指向 rules/，rules/ 指向 references/；禁止在 AGENTS.md / rules/ 内联 >10 行代码块。

**反例**：
- 现象：AGENTS.md 内联 50 行代码示例 → agent 上下文击穿，中间遗忘关键地图信息
- 根因：未规定内联代码块上限，地图与示例混在一起
- 教训：AGENTS.md 只放地图 + 指向 rules/，示例放 references/

---

## 八、项目级文档内容边界（V10.8 NEW）

> 根因：项目级文档（ARCHITECTURE.md 等）混入 Review 评分/测试数/commit hash → 文件膨胀，85% 内容对 agent 无意义。
> 治理：项目级文档只描述"系统是什么"，不描述"系统怎么变成这样的"。

### 内容判定

| 内容类型 | 留/删 | 判定问题 |
|---------|:-----:|---------|
| 架构设计 / 模块职责 / 契约定义 / 设计模式 | ✅ 留 | "系统是什么" |
| Review 评分 / 测试数 / commit hash | ❌ 删 | "系统怎么变成的" |
| DOC SYNC 时间戳 / 实施状态标记 | ❌ 删 | 用 §0 摘要代替 |

**反例**：
- 现象：ARCHITECTURE.md §1.1 包含每个 change 的 Review 评分/测试数/commit hash → 文件膨胀到 1304 行，85% 内容对 agent 无意义
- 根因：未区分"系统是什么"（架构内容） vs "系统怎么变成这样的"（实施过程）
- 教训：项目级文档 = 地图（静态），施工记录 = git log + change artifacts（动态）
