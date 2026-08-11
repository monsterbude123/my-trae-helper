# 使用场景：小任务流线化

> ≤6 Task + LOW + 无新 API → 无 Contract，跳过部分阶段。

---

## 场景总览

```mermaid
mindmap
  root((小任务流线化))
    判定条件
      ≤6个Task
      LOW风险
      无新API
      无新契约
    流线化流程
      Intake → Plan → Spec
      → Implement → Review → Accept
    跳过阶段
      Test Plan
      Prototype
      Contract
```

---

## 判定条件

```mermaid
flowchart TB
    A[小任务判定] --> B{Task数 ≤ 6?}
    A --> C{风险等级 LOW?}
    A --> D{无新API?}
    A --> E{无新契约?}
    
    B --> F{全部满足?}
    C --> F
    D --> F
    E --> F
    
    F -->|是| G[✅ 流线化流程]
    F -->|否| H[❌ 完整13阶段]
    
    style G fill:#9f9
    style H fill:#f9f
```

---

## 流线化流程

```mermaid
flowchart TB
    A[Stage -1 Intake] --> B[Stage 0 Plan]
    B --> C[Stage 1 Spec]
    C --> D[Stage 3 Implement]
    D --> E[Stage 4 Review]
    E --> F[Stage 5 Accept]
    
    style A fill:#9cf
    style B fill:#9cf
    style C fill:#9cf
    style D fill:#9cf
    style F fill:#9f9
    
    G[跳过] --> H[Stage 0.5 Test Plan]
    G --> I[Stage 1.5 Prototype]
    G --> J[Stage 2 Contract]
    
    style H fill:#ccc
    style I fill:#ccc
    style J fill:#ccc
```

---

## vs 完整流程

```mermaid
graph TB
    subgraph 完整13阶段
        A1[-1 Intake]
        A2[0 Plan]
        A3[0.5 Test Plan]
        A4[1 Spec]
        A5[1.5 Prototype]
        A6[2 Contract]
        A7[3 Implement]
        A8[3.5 Real Verify]
        A9[4 Review]
        A10[4.5 Rot Scan]
        A11[5 Accept]
    end
    
    subgraph 小任务流线化
        B1[-1 Intake]
        B2[0 Plan]
        B3[1 Spec]
        B4[3 Implement]
        B5[4 Review]
        B6[5 Accept]
    end
    
    A1 --> B1
    A2 --> B2
    A3 --> |跳过| X1[×]
    A4 --> B3
    A5 --> |跳过| X2[×]
    A6 --> |跳过| X3[×]
    A7 --> B4
    A8 --> |简化| X4[×]
    A9 --> B5
    A10 --> |简化| X5[×]
    A11 --> B6
    
    style X1 fill:#ccc
    style X2 fill:#ccc
    style X3 fill:#ccc
    style X4 fill:#ccc
    style X5 fill:#ccc
```

---

## 风险等级判定

```mermaid
graph TB
    A[风险等级] --> B[LOW]
    A --> C[MEDIUM]
    A --> D[HIGH]
    A --> E[CRITICAL]
    
    B --> B1[单模块修改<br/>无外部依赖<br/>无破坏性变更]
    C --> C1[多模块修改<br/>有外部依赖<br/>有破坏性变更]
    D --> D1[核心模块修改<br/>多外部依赖]
    E --> E1[架构级修改<br/>数据迁移]
    
    B1 --> F[✅ 流线化]
    C1 --> G[❌ 完整流程]
    D1 --> G
    E1 --> G
    
    style F fill:#9f9
```

---

## Task 数统计

```mermaid
flowchart TB
    A[Task统计] --> B[UI修改]
    A --> C[业务逻辑]
    A --> D[数据层]
    A --> E[测试]
    A --> F[文档]
    
    B --> B1[每个页面 = 1 Task]
    C --> C1[每个函数 = 1 Task]
    D --> D1[每个表 = 1 Task]
    E --> E1[每个测试文件 = 1 Task]
    F --> F1[每个文档 = 1 Task]
    
    B1 --> G{总Task ≤ 6?}
    C1 --> G
    D1 --> G
    E1 --> G
    F1 --> G
    
    G -->|是| H[✅ 流线化]
    G -->|否| I[❌ 完整流程]
```

---

## 简化的 Spec

```mermaid
graph TB
    A[spec.md] --> B[背景与目标]
    A --> C[变更范围]
    A --> D[验收标准]
    
    B --> B1[≤ 20行]
    C --> C1[≤ 5 Capabilities]
    D --> D1[≤ 10 Acceptance Criteria]
    
    style A fill:#9cf
```

---

## 简化的 Review

```mermaid
flowchart TB
    A[简化Review] --> B[代码层]
    A --> C[API层]
    
    B --> B1[单元测试 + 覆盖率]
    C --> C1[现有接口调用正常]
    
    B1 --> D{通过?}
    C1 --> D
    
    D -->|是| E[✅ PASS]
    D -->|否| F[❌ FAIL]
    
    style E fill:#9f9
```

---

## 用户确认

```mermaid
sequenceDiagram
    participant User as 用户
    participant Agent as 主上下文
    
    Agent->>Agent: 判定流线化条件
    Agent->>User: 提示流线化流程
    
    alt 用户同意
        User->>Agent: 同意
        Agent->>Agent: 执行流线化
    else 用户拒绝
        User->>Agent: 要求完整流程
        Agent->>Agent: 执行完整13阶段
    end
```

---

## 反例

```mermaid
graph TB
    subgraph 反模式
        A[强行流线化]
        B[忽略风险等级]
        C[隐瞒Task数]
    end
    
    A --> A1[❌ 7+ Task仍流线化]
    B --> B1[❌ HIGH风险仍流线化]
    C --> C1[❌ 隐瞒外部依赖]
    
    style A fill:#f66
    style B fill:#f66
    style C fill:#f66
```

---

## 关联文档

- [13阶段流水线](02-pipeline.md)
- [Stage 0 Plan](12-stage-plan.md)
- [Stage 1 Spec](../skills/04-spec/SKILL.md)
- [Stage 3 Implement](17-stage-implement.md)
- [Stage 4 Review](19-stage-review.md)