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
