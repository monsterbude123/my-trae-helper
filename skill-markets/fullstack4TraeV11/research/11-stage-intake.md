# Stage -1 Intake — 意图受理 + 路由起点

> 全栈流程的唯一入口，所有用户请求必须先经过意图识别 + 路由决策。

---

## 阶段总览

```mermaid
mindmap
  root((Stage -1 Intake))
    核心职责
      意图识别
      路由决策
      状态卡初始化
      Bug录入触发
    意图类型
      project-init
      change-start
      bug-fix
      project-health
      consultation
    关键产物
      状态卡
      路由决策表
      Bug单（可选）
```

---

## 第一性原则

```mermaid
graph TB
    A[第一性原则] --> B[意图不明不路由]
    A --> C[未勘察不初始化]
    
    B --> D[必须识别意图才能路由]
    C --> E[项目级AGENTS.md/docs/.trae/rules/必先Glob]
    
    style B fill:#f66
    style C fill:#f66
```

---

## 5 种意图类型

```mermaid
graph TB
    A[用户意图] --> B{意图识别}
    
    B --> C[project-init<br/>项目初始化]
    B --> D[change-start<br/>新功能/重构]
    B --> E[bug-fix<br/>Bug修复]
    B --> F[project-health<br/>健康检查]
    B --> G[consultation<br/>咨询]
    
    C --> H[路由: Stage 0 Plan<br/>→ ... → Stage 5 Accept]
    D --> I[路由: Stage 0 Plan]
    E --> J[路由: Stage 6 Bug Fix<br/>独立支线]
    F --> K[路由: Stage 7 Project Health<br/>异步自检]
    G --> L[直接回答]
```

---

## 触发词识别

```mermaid
flowchart TB
    A[用户输入] --> B{触发词匹配}
    
    B --> C[意图类触发词]
    B --> D[问题类触发词]
    B --> E[模糊意图]
    
    C --> C1["初始化/新项目" → project-init]
    C --> C2["新需求/新增功能" → change-start]
    C --> C3["重构/改造" → change-start<br/>refactor子类]
    C --> C4["文档同步" → change-start<br/>doc-sync子类]
    
    D --> D1["报错/错误/异常" → 询问Bug录入]
    D --> D2["不工作/失败/崩溃" → 询问Bug录入]
    D --> D3["应该X但出现Y" → 询问Bug录入]
    
    E --> E1[AskUserQuestion<br/>5种意图选项]
    
    style D1 fill:#f9f
    style D2 fill:#f9f
    style D3 fill:#f9f
```

---

## Bug 录入流程

```mermaid
sequenceDiagram
    participant User as 用户
    participant Agent as 主上下文
    participant Bug as Bug系统
    
    User->>Agent: 问题反馈（触发词）
    Agent->>Agent: 识别问题类触发词
    Agent->>User: 是否作为Bug单录入？
    
    alt 用户同意
        User->>Agent: 同意
        Agent->>Bug: 创建Bug单（6字段）
        Bug->>Agent: Bug ID
        Agent->>Agent: 路由到Stage 6
    else 用户拒绝
        User->>Agent: 拒绝
        Agent->>Agent: 按一般咨询处理
    end
    
    Note over Agent: NEVER 默认创建Bug单
```

---

## 骨架流程（7 步）

```mermaid
flowchart TB
    A[Step 1: 加载skill] --> B[Step 2: Glob项目惯例]
    B --> C[Step 3: 识别意图]
    C --> D[Step 4: Bug录入判断]
    D --> E[Step 5: 路由决策]
    E --> F[Step 6: 初始化状态卡]
    F --> G[Step 7: 交接给下一Stage]
    
    style C fill:#f9f
    style E fill:#f9f
```

---

## 10 条铁律

```mermaid
graph TB
    subgraph 意图识别铁律
        A1[1. 意图不明不路由]
        A2[5. 路由决策不臆断]
    end
    
    subgraph 状态卡铁律
        B1[3. 状态卡不立不启动]
        B2[9. NEVER跳过状态卡]
    end
    
    subgraph Bug录入铁律
        C1[4. Bug录入必询问]
        C2[8. NEVER默认创建Bug单]
    end
    
    subgraph 项目勘察铁律
        D1[2. 未勘察不初始化]
    end
    
    subgraph 路由记录铁律
        E1[6. 路由必记录]
        E2[10. NEVER静默路由]
    end
    
    style A1 fill:#f66
    style C1 fill:#f9f
```

---

## 状态卡初始化

```mermaid
graph TB
    A[状态卡初始化] --> B{意图类型}
    
    B --> C[project-init]
    B --> D[change-start]
    B --> E[bug-fix]
    
    C --> F[项目级状态卡<br/>.trae/state-card.md]
    D --> G[Change级状态卡<br/>docs/specs/changes/{id}/.state-card.md]
    E --> H[Bug单状态卡<br/>docs/bugs/{id}/.state-card.md]
    
    F --> I[card_type: project]
    G --> J[card_type: change]
    H --> K[card_type: bug]
    
    style F fill:#9f9
    style G fill:#9cf
    style H fill:#f9f
```

---

## 交接物 4 件套

```yaml
hand_over:
  stage_id: "-1/intake"
  stage_skill: skills/01-intake/SKILL.md
  status: completed
  health: "🟢 on-track"
  artifacts:
    - path: .trae/state-card.md
      type: file
      evidence: "状态卡初始化 + next_stage 路由"
  gate_result:
    status: PASS
    gate: state-card-validator.py
    output: "状态卡字段完整 + 文件存在性 OK"
  next_stage:
    id: "0/plan" | "6/bug-fix" | "7/project-health"
    skill_name: skills/02-plan/SKILL.md
    expected_inputs: [状态卡 + 路由决策表]
    prerequisites: [意图识别 PASS + 状态卡初始化 PASS]
```

---

## 4 条反模式

```mermaid
graph TB
    subgraph 反模式
        A[1. 无意图识别直接动手]
        B[2. 跳过状态卡初始化]
        C[3. 强制创建Bug单]
        D[4. 未勘察项目惯例]
    end
    
    A --> A1[❌ 收到需求立即写spec]
    B --> B1[❌ 不立状态卡直接进stage]
    C --> C1[❌ 用户拒绝时仍创建]
    D --> D1[❌ 不Glob就初始化]
    
    style A fill:#f66
    style B fill:#f66
    style C fill:#f66
    style D fill:#f66
```

---

## 关联文档

- [意图路由工作流](../skills/01-intake/workflows/intent-routing.md)
- [Bug录入工作流](../skills/01-intake/workflows/bug-intake-flow.md)
- [项目惯例勘察](../skills/01-intake/workflows/project-convention-survey.md)
- [5种意图类型](../skills/01-intake/references/intent-types.md)
- [路由决策树](../skills/01-intake/references/routing-decision-tree.md)