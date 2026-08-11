# Stage 0 Plan — 探索 + 规划

> 项目现状 3 路并行探索 + GitNexus impact + 追问点 + plan.md 产出。

---

## 阶段总览

```mermaid
mindmap
  root((Stage 0 Plan))
    核心职责
      项目现状探索
      GitNexus impact
      追问点收集
      plan.md产出
    探索路径
      文档探索
      代码探索
      依赖探索
    关键产物
      plan.md
      影响面报告
      追问点列表
```

---

## 第一性原则

```mermaid
graph TB
    A[第一性原则] --> B[探索先于规划]
    A --> C[禁止凭空设计]
    
    B --> D[发现而非创作]
    C --> E[无探索不规划]
    
    style B fill:#f66
```

---

## 3 路并行探索

```mermaid
graph TB
    A[3路并行探索] --> B[子代理A: 文档探索]
    A --> C[子代理B: 代码探索]
    A --> D[子代理C: 依赖探索]
    
    B --> B1[读INDEX → ARCHITECTURE<br/>→ spec → 模块文档]
    C --> C1[GitNexus impact<br/>+ context分析]
    D --> D1[检测公共模块/工具<br/>/可复用组件]
    
    B1 --> B2[输出: 已有能力清单<br/>+ 架构约束]
    C1 --> C2[输出: 受影响符号列表<br/>+ 风险等级]
    D1 --> D2[输出: 可复用资源清单<br/>+ 需新建模块]
    
    style B fill:#9cf
    style C fill:#9f9
    style D fill:#f9f
```

---

## 骨架流程（6 步）

```mermaid
flowchart TB
    A[Step 0: Cockpit读取] --> B[Step 1: 意图识别 + 选链]
    B --> C[Step 2: 去重检查]
    C --> D[Step 3: 3路并行探索]
    D --> E[Step 4: 重构场景 → spec-purge]
    E --> F[Step 5: 产出plan.md]
    F --> G[Step 6: 状态卡更新]
    
    style D fill:#f9f
```

---

## GitNexus Impact 评估

```mermaid
sequenceDiagram
    participant Agent as 主上下文
    participant GitNexus as GitNexus MCP
    
    Agent->>GitNexus: impact(target: "symbolName")
    GitNexus->>Agent: 返回影响面报告
    
    Agent->>Agent: 分析blast radius
    Agent->>Agent: 评估风险等级
    
    Note over Agent: 改函数 → impact() 上游+下游
    Note over GitNexus: 禁止手动grep追踪
```

---

## 去重检查（DEDUP BY ATOM）

```mermaid
flowchart TB
    A[需求输入] --> B[扫描活跃change]
    B --> C[扫描archive/done/]
    
    C --> D{重叠率}
    D -->|≥ 50%| E[合并到现有change]
    D -->|< 50%| F[新建change]
    
    E --> G[更新plan.md]
    F --> H[创建新plan.md]
    
    style D fill:#f9f
```

---

## 重构场景（PURGE ON REFACTOR）

```mermaid
flowchart TB
    A[重构意图] --> B[spec-purge.py]
    B --> C[清除旧产物]
    
    C --> D[隔离旧spec]
    D --> E[隔离旧contracts]
    E --> F[创建新change目录]
    
    F --> G[开始新plan]
    
    style B fill:#f9f
```

---

## 10 条铁律

```mermaid
graph TB
    subgraph 探索铁律
        A1[1. EXPLORE FIRST<br/>探索后再规划]
        A2[2. SUBAGENT ONLY<br/>委派子代理探索]
        A3[3. IMPACT BY TOOL<br/>用GitNexus不用grep]
    end
    
    subgraph 规划铁律
        B1[8. PLAN ≤ 80 LINES<br/>plan.md ≤ 80行]
        B2[9. CLOSURE ≤ 5 STEPS<br/>P0闭环步骤 ≤ 5步]
    end
    
    subgraph 重构铁律
        C1[5. PURGE ON REFACTOR<br/>重构先清除旧产物]
    end
    
    subgraph 禁止项
        D1[10. NEVER ACT ON PLAN<br/>plan是规划不是实施]
    end
    
    style A1 fill:#f66
    style A2 fill:#f66
    style A3 fill:#f66
```

---

## plan.md 模板结构

```mermaid
graph TB
    A[plan.md] --> B[背景与目标]
    A --> C[现状分析]
    A --> D[变更范围]
    A --> E[影响面评估]
    A --> F[追问点]
    A --> G[里程碑]
    
    B --> B1[≤ 10行]
    C --> C1[3路探索结果]
    D --> D1[Capabilities ≤ 5项]
    E --> E1[GitNexus impact报告]
    F --> F1[需用户澄清的问题]
    G --> G1[检查点列表]
    
    style A fill:#9cf
```

---

## 交接物 4 件套

```yaml
hand_over:
  stage_id: "0/plan"
  stage_skill: skills/02-plan/SKILL.md
  status: completed
  health: "🟢 on-track"
  artifacts:
    - path: docs/specs/changes/{id}/plan.md
      type: file
      evidence: "plan.md ≤ 80行 + 3路探索evidence"
  gate_result:
    status: PASS
    gate: stage-gate.py
    output: "plan.md行数 + Capabilities数 PASS"
  next_stage:
    id: "0.5/test-plan"
    skill_name: skills/03-test-plan/SKILL.md
    expected_inputs: [plan.md + 3路探索evidence]
    prerequisites: [意图识别PASS, 去重检查PASS]
```

---

## 4 条反模式

```mermaid
graph TB
    subgraph 反模式
        A[1. 无探索直接规划]
        B[2. GitNexus可用却grep]
        C[3. 重构不purge]
        D[4. plan.md超长]
    end
    
    A --> A1[❌ 凭经验写plan.md]
    B --> B1[❌ 手动grep找影响面]
    C --> C1[❌ 直接覆盖旧产物]
    D --> D1[❌ > 80行 / > 5 Capabilities]
    
    style A fill:#f66
    style B fill:#f66
    style C fill:#f66
    style D fill:#f66
```

---

## 关联文档

- [3路并行探索工作流](../skills/02-plan/workflows/three-path-exploration.md)
- [计划追问点工作流](../skills/02-plan/workflows/plan-clarification.md)
- [原子级去重](../skills/02-plan/references/dedup-by-atom.md)
- [GitNexus影响面评估](../skills/02-plan/references/impact-assessment.md)
- [plan.md模板](../skills/02-plan/templates/plan-template.md)