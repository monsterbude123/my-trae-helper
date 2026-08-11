# Stage 3 Implement — TDD RED→GREEN

> 契约驱动 + 深度业务理解 + TDD 三步循环 + 漂移检测。

---

## 阶段总览

```mermaid
mindmap
  root((Stage 3 Implement))
    核心职责
      TDD三步循环
      漂移检测
      代码卫生
      模块文档
    TDD循环
      RED写失败测试
      GREEN写实现
      REFACTOR重构
    关键产物
      代码
      测试
      模块文档
      量化报告
```

---

## 第一性原则

```mermaid
graph TB
    A[第一性原则] --> B[TDD RED→GREEN]
    A --> C[最简实现优先]
    A --> D[契约为唯一入口]
    
    B --> E[无失败测试不写实现]
    C --> F[Ponytail: 单文件 ≤ 800行]
    D --> G[深度理解业务后再编码]
    
    style B fill:#f66
```

---

## TDD 三步循环

```mermaid
flowchart TB
    A[🔴 RED<br/>写失败测试] --> B{测试FAIL?}
    B -->|否| C[重写测试]
    C --> A
    B -->|是| D[🟢 GREEN<br/>写实现]
    
    D --> E{测试GREEN?}
    E -->|否| D
    E -->|是| F[♻️ REFACTOR<br/>重构]
    
    F --> G{代码质量?}
    G -->|需改进| F
    G -->|达标| H[🔍 DRIFT CHECK]
    
    H --> I{漂移?}
    I -->|是| J[回流spec]
    I -->|否| K[✅ 完成]
    
    J --> A
    
    style A fill:#f66
    style D fill:#9f9
    style F fill:#9cf
```

---

## 深度理解再编码

```mermaid
sequenceDiagram
    participant Agent as 主上下文
    participant GitNexus as GitNexus MCP
    participant Spec as spec.md
    participant Contract as contracts/
    
    Agent->>Spec: 读规格
    Agent->>Contract: 读契约
    Agent->>GitNexus: context(符号)
    GitNexus->>Agent: 完整定义 + callers
    
    Agent->>Agent: 输出"理解确认"
    Agent->>Agent: 开始TDD循环
    
    Note over Agent: 铁律1: 深度理解再编码
```

---

## 漂移检测（DRIFT CHECK）

```mermaid
flowchart TB
    A[实现完成] --> B[DRIFT CHECK]
    
    B --> C{代码与Spec一致?}
    B --> D{代码与Contract一致?}
    
    C --> E{发现漂移?}
    D --> E
    
    E -->|是| F[立即报告回流]
    E -->|否| G[✅ 继续验收]
    
    F --> H[先改spec]
    H --> I[再改代码]
    I --> B
    
    style F fill:#f9f
```

---

## 骨架流程（4 步）

```mermaid
flowchart TB
    A[Step 1: 门禁检查] --> B[Step 2: 深度理解]
    B --> C[Step 3: TDD循环]
    C --> D[Step 4: 模块文档<br/>+ 量化汇报]
    
    A --> A1[spec.md + contracts/<br/>+ state-card存在]
    B --> B1[GitNexus context<br/>→ 输出"理解确认"]
    C --> C1[tasks.md逐项<br/>RED→GREEN→REFACTOR]
    D --> D1[test/contract_tests/coverage]
    
    style A fill:#9cf
    style C fill:#f9f
```

---

## 量化汇报格式

```mermaid
graph TB
    A[Completion Report] --> B[artifacts: 代码+测试+文档]
    A --> C[test: {pass}/{total}]
    A --> D[contract_tests: {pass}/{total}]
    A --> E[coverage: {X}%]
    A --> F[status: ✓ | ⚠️ | ✗]
    
    style C fill:#f9f
    style D fill:#f9f
    style E fill:#f9f
```

**示例**:
```yaml
## Completion Report - Implementer
- artifacts: [src/services.rs, __tests__/services.test.rs]
- test: 50/50
- contract_tests: 8/8
- coverage: 92%
- status: ✓
```

---

## 10 条铁律

```mermaid
graph TB
    subgraph 理解铁律
        A1[1. 深度理解再编码<br/>读spec+contracts → 输出理解确认]
    end
    
    subgraph TDD铁律
        B1[2. TDD即时 + 红绿重构<br/>改实现同步改测试 + RED→GREEN→REFACTOR]
        B2[8. 禁止虚假绿灯<br/>不可修改测试让用例通过]
    end
    
    subgraph 漂移铁律
        C1[3. 漂移必报告<br/>发现不一致立即回流]
    end
    
    subgraph 代码卫生铁律
        D1[6. 代码卫生<br/>单文件 ≤ 800行；函数 ≤ 50行]
    end
    
    subgraph 量化铁律
        E1[7. 量化必汇报<br/>缺一不验收]
        E2[10. 禁止编造测试证据]
    end
    
    style A1 fill:#f66
    style B1 fill:#f66
    style B2 fill:#f66
```

---

## Bundle Staleness 检测

```mermaid
flowchart TB
    A[改TS后] --> B[dist-hash-check.py]
    B --> C{Bundle stale?}
    
    C -->|是| D[🛑 REJECT<br/>需重新构建]
    C -->|否| E[✅ 继续]
    
    D --> F[重新构建]
    F --> B
    
    style D fill:#f66
```

---

## 模块接入文档（条件触发）

```mermaid
flowchart TB
    A[模块完成] --> B{可作为增值功能基底?}
    
    B -->|是| C[产出接入文档<br/>docs/modules/{module}/README.md]
    B -->|否| D[不产出文档]
    
    C --> E[包含: 快速接入 + API示例<br/>+ 常见问题]
    
    style C fill:#9f9
```

---

## 交接物 4 件套

```yaml
hand_over:
  stage_id: "3/implement"
  stage_skill: skills/07-implement/SKILL.md
  status: completed
  health: "🟢 on-track"
  artifacts:
    - path: src/{module}/{feature}.{ts,py,rs}
      type: file
      evidence: "代码实现"
    - path: __tests__/{unit,integration}/{feature}.test.*
      type: file
      evidence: "测试文件"
  gate_result:
    status: PASS
    gate: stage-gate.py
    output: "TDD GREEN + DRIFT CHECK PASS + code-hygiene PASS"
  next_stage:
    id: "3.5/real-verify"
    skill_name: skills/08-real-verify/SKILL.md
    expected_inputs: [代码 + 测试]
    prerequisites: [TDD GREEN, DRIFT CHECK ✅]
```

---

## 4 条反模式

```mermaid
graph TB
    subgraph 反模式
        A[1. 跳过RED直接GREEN]
        B[2. 编造测试证据]
        C[3. 改实现不改测试]
        D[4. 漂移静默不报告]
    end
    
    A --> A1[❌ 不知TDD三步循环]
    B --> B1[❌ tests/foo.test.ts:999不存在]
    C --> C1[❌ 测试腐烂]
    D --> D1[❌ 真相源被破坏]
    
    style A fill:#f66
    style B fill:#f66
    style C fill:#f66
    style D fill:#f66
```

---

## 关联文档

- [TDD工作流](../skills/07-implement/references/tdd-workflow.md)
- [代码卫生](../skills/07-implement/references/code-hygiene.md)
- [漂移检测](../skills/07-implement/references/drift-detect.md)
- [V10实战蒸馏](../skills/07-implement/anti-patterns/V10-battle-tested.md)