# 使用场景：Bug 修复流程

> Stage 6 独立支线 — 根因不明不修复 + e2e 先行。

---

## 场景总览

```mermaid
mindmap
  root((Bug修复流程))
    触发
      用户反馈问题
      Intake识别触发词
      询问是否录入
    流程
      理解期望
      e2e先行
      6层排查
      TDD修复
      验收关闭
    关键产物
      Bug单
      e2e测试
      修复代码
```

---

## Bug 修复流程

```mermaid
flowchart TB
    A[用户反馈问题] --> B[Intake识别触发词]
    B --> C[询问是否录入Bug单]
    
    C --> D{用户同意?}
    D -->|否| E[按一般咨询处理]
    D -->|是| F[创建Bug单]
    
    F --> G[路由到Stage 6]
    G --> H[5步精简流程]
    H --> I[Bug单CLOSED]
    
    style B fill:#f9f
    style F fill:#9f9
```

---

## 触发词识别

```mermaid
graph TB
    A[用户输入] --> B{触发词匹配}
    
    B --> C[报错/错误/异常]
    B --> D[不工作/失败/崩溃]
    B --> E[应该X但出现Y]
    B --> F[期望X但实际Y]
    
    C --> G[问题类触发词]
    D --> G
    E --> G
    F --> G
    
    G --> H[询问Bug录入]
    
    style G fill:#f9f
```

---

## 5 步精简流程

```mermaid
sequenceDiagram
    participant Dev as 开发者
    participant Bug as Bug单
    participant Test as e2e测试
    participant Code as 代码
    
    Dev->>Bug: Step 1: 理解期望
    Bug->>Dev: spec.md + INV
    
    Dev->>Test: Step 2: e2e先行
    Test->>Dev: 初始FAIL ✅
    
    Dev->>Dev: Step 3: 6层排查
    Dev->>Dev: GitNexus impact
    
    Dev->>Code: Step 4: TDD修复
    Code->>Test: GREEN
    
    Dev->>Bug: Step 5: Bug单CLOSED
    
    Note over Test: 必初始FAIL
```

---

## e2e 先行验证

```mermaid
flowchart TB
    A[编写e2e测试] --> B{初始结果}
    
    B -->|FAIL| C[✅ 证明bug真实存在]
    B -->|PASS| D[❌ 不是bug / 测试写错]
    
    C --> E[继续修复]
    D --> F[回退OPEN]
    
    E --> G[TDD修复]
    G --> H[e2e GREEN]
    
    H --> I[全量回归]
    I --> J{回归通过?}
    
    J -->|是| K[Bug单CLOSED]
    J -->|否| G
    
    style C fill:#9f9
    style D fill:#f66
```

---

## 6 层排查详解

```mermaid
graph TB
    A[根因排查] --> B[Layer 1: 网络层]
    A --> C[Layer 2: 接入层]
    A --> D[Layer 3: 应用层]
    A --> E[Layer 4: 数据层]
    A --> F[Layer 5: 集成层]
    A --> G[Layer 6: 客户端层]
    
    B --> H[检查curl / DNS / TLS]
    C --> I[检查gateway / 路由]
    D --> J[检查业务逻辑 / 中间件]
    E --> K[检查DB schema / 索引]
    F --> L[检查第三方服务]
    G --> M[检查UI / 缓存]
    
    H --> N{根因定位?}
    I --> N
    J --> N
    K --> N
    L --> N
    M --> N
    
    N -->|否| O[继续排查]
    O --> A
    N -->|是| P[开始修复]
    
    style P fill:#9f9
```

---

## Bug 单生命周期

```mermaid
stateDiagram-v2
    [*] --> OPEN: Intake创建
    OPEN --> IN_PROGRESS: 开始修复
    IN_PROGRESS --> BLOCKED: 遇到阻塞
    BLOCKED --> IN_PROGRESS: 阻塞解除
    IN_PROGRESS --> FIXED: 修复完成
    FIXED --> VERIFIED: 验收通过
    VERIFIED --> CLOSED: 用户确认关闭
    
    FIXED --> IN_PROGRESS: 验收失败
    VERIFIED --> IN_PROGRESS: 回归失败
    
    note right of OPEN: 6字段必填
    note right of CLOSED: 用户确认关闭
```

---

## Bug 单 6 字段

```mermaid
graph TB
    A[Bug单] --> B[1. Bug ID]
    A --> C[2. 标题]
    A --> D[3. 复现步骤]
    A --> E[4. 期望行为]
    A --> F[5. 实际行为]
    A --> G[6. 优先级]
    
    B --> B1[格式: {module}-{seq}]
    C --> C1[一句话描述]
    D --> D1[详细步骤]
    E --> E1[用户期望]
    F --> F1[实际发生]
    G --> G1[P0/P1/P2/P3]
    
    style A fill:#f9f
```

---

## 跨层修复决策

```mermaid
flowchart TB
    A[发现bug] --> B{根因在哪层?}
    
    B -->|客户端层| C[仅修客户端层]
    B -->|应用层| D[仅修应用层]
    B -->|数据层| E[评估下游影响后修数据层]
    
    C --> F[最小化修复]
    D --> F
    E --> F
    
    F --> G[全量回归]
    
    style F fill:#9f9
```

---

## 异常处理

```mermaid
flowchart TB
    A[修复阻塞] --> B{阻塞类型}
    
    B -->|根因不明| C[继续6层排查]
    B -->|测试失败| D[退回TDD修复]
    B -->|回归失败| E[分析影响面]
    
    C --> F{超5轮?}
    D --> G[Retry]
    E --> H[扩大修复范围]
    
    F -->|是| I[上报用户决策]
    F -->|否| C
    
    G --> J{超3次?}
    J -->|是| K[阻塞报告]
    J -->|否| D
    
    style I fill:#f66
    style K fill:#f66
```

---

## 关联文档

- [Stage 6 Bug Fix](22-stage-bug-fix.md)
- [Stage -1 Intake](11-stage-intake.md)
- [6层排查](../skills/12-bug-fix/references/six-layer-diagnosis.md)
- [Bug状态机](../skills/12-bug-fix/references/bug-state-machine.md)