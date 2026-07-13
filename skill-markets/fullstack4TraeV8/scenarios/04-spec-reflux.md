# 场景 4: Spec 回流（DOC SYNC 知识持久化）

> **模拟**: 一个 spec 完成后，知识如何从临时工件（specs/changes/）回流到持久化文档（modules/、ARCHITECTURE.md），供后续所有 Agent 参考。

---

## 用户视角

```
用户看不到 DOC SYNC 的细节——这是系统内部机制。
用户只知道："Agent 在 plan 之后和 review 之后各做了一次文档同步。"

DOC SYNC #1（Phase 5.5，plan 确认后）:
  - 把 contracts/ 中的接口定义写入 modules/payment.md
  - 把 spec 中的能力描述写入 modules/payment.md
  - 把原型提取到 docs/prototypes/
  - 标记 modules/payment.md 实施状态: 🟡 计划中

DOC SYNC #2（Phase 7.5，review 通过后）:
  - 把代码实现后的最终状态写入 modules/payment.md
  - 标记实施状态: 🟢 已实现
  - 更新 ARCHITECTURE.md §实施状态
  - 验证无 specs/changes/ 残留引用
  - 更新 Cockpit 项目级工件状态
```

---

## 系统内部流程

```mermaid
graph TD
    subgraph DOC1["DOC SYNC #1 (Phase 5.5): 计划→文档"]
        D1_IN["输入: contracts/ + spec.md + prototypes/"] --> D1_1["读取 contracts/ 接口定义"]
        D1_1 --> D1_2["写入 modules/{module}.md<br/>📋 能力: 退款处理<br/>📡 接口: POST /refund<br/>📊 模型: RefundOrder"]
        D1_2 --> D1_3["提取原型到 docs/prototypes/"]
        D1_3 --> D1_4["标记实施状态: 🟡 计划中<br/>来源 Change 03-payment-refund"]
        D1_4 --> D1_5["写入 Completion Report<br/>source_change: 03-payment-refund"]
    end

    subgraph GAP["编码阶段"]
        G0["implementer 编码 + 测试"]
    end

    subgraph DOC2["DOC SYNC #2 (Phase 7.5): 实现→文档"]
        D2_IN["输入: 代码 + 测试结果 + Review报告"] --> D2_1["读取代码实际实现"]
        D2_1 --> D2_2["更新 modules/{module}.md<br/>实施状态: 🟢 已实现<br/>覆盖率: 87%"]
        D2_2 --> D2_3["更新 ARCHITECTURE.md<br/>§实施状态 + 模块依赖图"]
        D2_3 --> D2_4["验证无 specs/changes/ 残留引用<br/>grep 'specs/changes/' docs/"]
        D2_4 --> D2_5["更新 Cockpit<br/>modules/ ✅最新<br/>contracts/ ✅最新"]
        D2_5 --> D2_6["更新文档索引<br/>python build-index.py"]
    end

    D1_5 --> G0
    G0 --> D2_IN

    style D1_1 fill:#f9ca24,stroke:#333,color:#000
    style D2_2 fill:#00b894,stroke:#333,color:#000
    style D2_4 fill:#ff6b6b,stroke:#333,color:#fff
```

---

## 知识回流前后对比

| 时间点 | modules/payment.md 状态 | 其他 Agent 读到什么 |
|--------|------------------------|-------------------|
| DOC SYNC #1 前 | 无退款能力描述 | spec-writer 从零开始 |
| DOC SYNC #1 后 | 🟡 计划中 — 退款处理能力 | 其他 change 知道"正在计划退款" |
| DOC SYNC #2 后 | 🟢 已实现 — 覆盖率 87% | 其他 change 可以依赖退款接口 |

---

## 为什么有两次 DOC SYNC

- **#1（Phase 5.5）**: 让其他并行的 change 知道"有计划中的接口"（虽然还没实现）
- **#2（Phase 7.5）**: 让所有后续 change 知道"接口已稳定可用"（代码已完成+Review通过）
- 两次之间: modules/ 中的内容带 traceability（来源 Change XX），Agent 可以判断状态
