# 使用场景：新功能开发

> 完整的 13 阶段流水线 — 从 Intake 到 Accept。

---

## 场景总览

```mermaid
mindmap
  root((新功能开发))
    流水线
      Intake → Plan → Test Plan
      → Spec → Prototype → Contract
      → Implement → Verify → Review
      → Rot Scan → Accept
    用户确认点
      Plan确认
      Spec确认
      Implement确认
    关键产物
      plan.md
      test-plan.md
      spec.md
      contracts/
      代码 + 测试
```

---

## 完整流水线

```mermaid
flowchart TB
    A[Stage -1 Intake] --> B[Stage 0 Plan]
    B --> C[Stage 0.5 Test Plan]
    C --> D[Stage 1 Spec]
    D --> E[Stage 1.5 Prototype]
    E --> F[Stage 2 Contract]
    F --> G[Stage 3 Implement]
    G --> H[Stage 3.5 Real Verify]
    H --> I[Stage 4 Review]
    I --> J[Stage 4.5 Rot Scan]
    J --> K[Stage 5 Accept]
    
    style A fill:#9cf
    style B fill:#9cf
    style D fill:#9cf
    style G fill:#9cf
    style K fill:#9f9
```

---

## 用户确认点

```mermaid
sequenceDiagram
    participant User as 用户
    participant Agent as 主上下文
    participant Stage as Stage
    
    Agent->>Stage: Stage -1 Intake
    Stage->>Agent: 状态卡 + 路由
    
    Agent->>Stage: Stage 0 Plan
    Stage->>Agent: plan.md
    Agent->>User: 提交Plan确认
    User->>Agent: 确认/拒绝
    
    Agent->>Stage: Stage 1 Spec
    Stage->>Agent: spec.md
    Agent->>User: 提交Spec确认
    User->>Agent: 确认/拒绝
    
    Agent->>Stage: Stage 3 Implement
    Stage->>Agent: 代码 + 测试
    Agent->>User: 提交Implement确认
    User->>Agent: 确认/拒绝
    
    Note over Agent,User: Plan/Spec/Implement必确认
```

---

## 各阶段关键产物

```mermaid
graph TB
    subgraph 规划阶段
        A1[plan.md]
        A2[test-plan.md]
        A3[spec.md]
    end
    
    subgraph 契约阶段
        B1[domain-models.md]
        B2[api-contracts.md]
        B3[events.md]
        B4[validation-rules.md]
    end
    
    subgraph 实现阶段
        C1[代码]
        C2[测试]
        C3[模块文档]
    end
    
    subgraph 验收阶段
        D1[verify-report.md]
        D2[review-report.md]
        D3[rot-scan]
    end
    
    A1 --> A2 --> A3
    A3 --> B1 --> B2 --> B3 --> B4
    B4 --> C1 --> C2 --> C3
    C3 --> D1 --> D2 --> D3
```

---

## 门禁链

```mermaid
graph TB
    A[Intake门禁] --> A1[意图识别 + 路由]
    B[Plan门禁] --> B1[3路探索 + GitNexus impact]
    C[Test Plan门禁] --> C1[验收维度 → 测试映射]
    D[Spec门禁] --> D1[Enhanced Acceptance + clarify ≥ 2轮]
    E[Prototype门禁] --> E1[双源兼容]
    F[Contract门禁] --> F1[contract-gate.py]
    G[Implement门禁] --> G1[TDD GREEN + DRIFT CHECK]
    H[Verify门禁] --> H1[5项必跑 + 启动验证]
    I[Review门禁] --> I1[4维满分 + 证据链]
    J[Rot Scan门禁] --> J1[8项扫描]
    K[Accept门禁] --> K1[归档不可变 + INDEX更新]
    
    style A1 fill:#f9f
    style B1 fill:#f9f
    style G1 fill:#f9f
    style I1 fill:#f9f
```

---

## 时间线估算

```mermaid
gantt
    title 新功能开发时间线
    dateFormat X
    axisFormat %s
    
    section 规划
    Intake :0, 1
    Plan :1, 2
    Test Plan :2, 3
    Spec :3, 4
    Prototype :4, 5
    
    section 契约
    Contract :5, 6
    
    section 实现
    Implement :6, 7
    Verify :7, 8
    
    section 验收
    Review :8, 9
    Rot Scan :9, 10
    Accept :10, 11
```

---

## 异常处理

```mermaid
flowchart TB
    A[异常发生] --> B{等级}
    
    B -->|L1| C[Retry 1次]
    B -->|L2| D[Retry 3次]
    B -->|L3| E[阻塞报告]
    B -->|L4| F[降级运行]
    
    C --> G{仍失败?}
    D --> H{仍失败?}
    
    G -->|是| D
    H -->|是| E
    
    E --> I[写入report-growth.jsonl]
    F --> I
    
    I --> J[更新状态卡]
    J --> K[等待用户决策]
    
    style E fill:#f66
```

---

## 关联文档

- [13阶段流水线](02-pipeline.md)
- [Intake阶段](11-stage-intake.md)
- [Plan阶段](12-stage-plan.md)
- [Contract阶段](16-stage-contract.md)
- [Implement阶段](17-stage-implement.md)
- [Review阶段](19-stage-review.md)