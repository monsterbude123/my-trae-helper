# Stage 6 Bug Fix — 独立专精流程

> 根因不明不修复 + e2e 先行 + 6 层排查 + TDD 修复。

---

## 阶段总览

```mermaid
mindmap
  root((Stage 6 Bug Fix))
    核心原则
      根因不明不修复
      e2e先行证明bug存在
      6层排查
    流程步骤
      理解期望
      e2e先行
      数据分析
      TDD修复
      验收
    关键产物
      Bug单
      e2e测试
      修复代码
```

---

## 第一性原则

```mermaid
graph TB
    A[第一性原则] --> B[根因不明不修复]
    A --> C[e2e先行证明bug真实存在]
    
    B --> D[必6层排查 + GitNexus impact]
    C --> E[必初始FAIL → GREEN]
    
    style B fill:#f66
    style C fill:#f66
```

---

## 5 步精简流程

```mermaid
flowchart TB
    A[Step 1: 理解期望] --> B[Step 2: e2e先行]
    B --> C[Step 3: 数据分析]
    C --> D[Step 4: TDD修复]
    D --> E[Step 5: 验收]
    
    A --> A1[读bug单 + spec.md + INV]
    B --> B1[必初始FAIL → 证明bug真实存在]
    C --> C1[GitNexus impact + 6层排查]
    D --> D1[RED → GREEN → REFACTOR]
    E --> E1[回归测试 + bug单CLOSED]
    
    style B fill:#f66
```

---

## e2e 先行

```mermaid
sequenceDiagram
    participant Dev as 开发者
    participant Test as e2e测试
    participant Bug as Bug系统
    
    Dev->>Test: 编写e2e测试（重现bug）
    Test->>Test: 运行测试
    
    alt 初始FAIL
        Test->>Dev: ✅ 证明bug真实存在
        Dev->>Dev: 继续修复
    else 初始PASS
        Test->>Dev: ❌ 不是bug / 测试写错
        Dev->>Bug: 回退OPEN状态
    end
    
    Note over Test: 必初始FAIL
```

---

## 6 层排查

```mermaid
graph TB
    A[6层排查] --> B[Layer 1: 网络层]
    A --> C[Layer 2: 接入层]
    A --> D[Layer 3: 应用层]
    A --> E[Layer 4: 数据层]
    A --> F[Layer 5: 集成层]
    A --> G[Layer 6: 客户端层]
    
    B --> B1[curl / DNS / TLS / proxy]
    C --> C1[API gateway / 路由 / 限流]
    D --> D1[业务逻辑 / 中间件 / 状态]
    E --> E1[DB schema / 索引 / 事务]
    F --> F1[第三方服务 / SDK]
    G --> G1[UI / 缓存 / localStorage]
    
    style A fill:#f9f
```

---

## Bug 单状态机

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
```

---

## TDD 修复流程

```mermaid
flowchart TB
    A[根因定位] --> B[🔴 RED<br/>写失败e2e]
    B --> C{测试FAIL?}
    
    C -->|否| D[重写测试]
    D --> B
    
    C -->|是| E[🟢 GREEN<br/>写修复]
    E --> F{测试GREEN?}
    
    F -->|否| E
    F -->|是| G[♻️ REFACTOR]
    
    G --> H[全量回归]
    H --> I{回归通过?}
    
    I -->|是| J[Bug单CLOSED]
    I -->|否| K[继续修复]
    K --> E
    
    style B fill:#f66
```

---

## 8 条铁律

```mermaid
graph TB
    subgraph 根因铁律
        A1[1. 根因不明不修复<br/>必6层排查 + GitNexus impact]
    end
    
    subgraph e2e铁律
        B1[2. e2e先行<br/>必初始FAIL]
        B2[3. INITIAL PASS = 不是bug<br/>e2e初始PASS → 回退OPEN]
    end
    
    subgraph 流程铁律
        C1[4. 5步精简流程<br/>理解期望→e2e→数据→TDD→验收]
        C2[5. TDD即时<br/>改实现同步改测试]
    end
    
    subgraph 跨层铁律
        D1[6. 跨层修复最小化<br/>Ponytail决策阶梯]
    end
    
    subgraph 回写铁律
        E1[7. 修复回写bug单<br/>Bug单状态 OPEN → CLOSED]
    end
    
    style A1 fill:#f66
    style B1 fill:#f66
    style B2 fill:#f66
```

---

## 跨层修复最小化（Ponytail 决策阶梯）

```mermaid
flowchart TB
    A[发现bug] --> B{根因在哪层?}
    
    B --> C[客户端层]
    B --> D[应用层]
    B --> E[数据层]
    
    C --> C1[仅修客户端层<br/>不扩散]
    D --> D1[仅修应用层<br/>不扩散到数据层]
    E --> E1[仅修数据层<br/>评估下游影响]
    
    C1 --> F[最小化修复]
    D1 --> F
    E1 --> F
    
    style F fill:#9f9
```

---

## 障碍诚实汇报（5 字段阻塞报告）

```mermaid
graph TB
    A[遇到障碍] --> B[5字段阻塞报告]
    
    B --> C[type: 类型]
    B --> D[description: 描述]
    B --> E[solution: 方案]
    B --> F[duration_minutes: 耗时]
    B --> G[attempts: 尝试次数]
    
    style B fill:#f66
```

---

## 关键产物

```mermaid
graph TB
    A[Bug Fix产物] --> B[Bug单<br/>docs/bugs/{bug-id}.md]
    A --> C[e2e测试<br/>tests/e2e/test_{bug-id}.py]
    A --> D[修复代码<br/>src/{module}/{file}.ts]
    A --> E[根因报告（可选）<br/>docs/bugs/{bug-id}-root-cause.md]
    
    B --> B1[Intake创建]
    C --> C1[初始FAIL → GREEN]
    D --> D1[TDD修复]
```

---

## 交接物 4 件套

```yaml
hand_over:
  stage_id: "6/bug-fix"
  stage_skill: skills/12-bug-fix/SKILL.md
  status: completed
  health: "🟢 on-track"
  artifacts:
    - path: docs/bugs/{bug-id}.md
      type: file
      evidence: "Bug单状态 CLOSED"
    - path: tests/e2e/test_{bug-id}.py
      type: file
      evidence: "e2e测试 GREEN"
  gate_result:
    status: PASS
    gate: stage-gate.py
    output: "e2e GREEN + 全量回归PASS + bug单CLOSED"
  next_stage:
    id: null  # Bug Fix是独立支线，完成后归档
    skill_name: null
    expected_inputs: []
    prerequisites: []
```

---

## 4 条反模式

```mermaid
graph TB
    subgraph 反模式
        A[1. 跳过e2e先行直接修]
        B[2. 跨层过度修复]
        C[3. 修复未回写bug单]
        D[4. 大小写不敏感比较违规]
    end
    
    A --> A1[❌ 不知bug是否真实存在]
    B --> B1[❌ 违反Ponytail最小化]
    C --> C1[❌ Bug单状态未同步]
    D --> D1[❌ V10实战：config key大小写不一致]
    
    style A fill:#f66
    style B fill:#f66
    style C fill:#f66
```

---

## 关联文档

- [5步精简流程](../skills/12-bug-fix/references/five-step-flow.md)
- [6层排查](../skills/12-bug-fix/references/six-layer-diagnosis.md)
- [跨层修复](../skills/12-bug-fix/references/cross-layer-fix.md)
- [Bug状态机](../skills/12-bug-fix/references/bug-state-machine.md)
- [V10实战蒸馏](../skills/12-bug-fix/anti-patterns/V10-battle-tested.md)