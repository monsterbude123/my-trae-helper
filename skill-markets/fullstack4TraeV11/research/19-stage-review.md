# Stage 4 Review — 质疑式验收

> FAIL IS FAIL + 4 维评分 + 主动证伪 + DOC SYNC。

---

## 阶段总览

```mermaid
mindmap
  root((Stage 4 Review))
    核心立场
      质疑式验收
      有罪推定
      证伪思维
    四维评分
      代码层25%
      API层30%
      UI/UX层25%
      模块边际20%
    关键产物
      4维评分报告
      证据链3层
      DOC SYNC
```

---

## 立场转变

```mermaid
graph TB
    subgraph 旧视角_盖章者
        A1[默认已完成]
        A2[找证据确认]
        A3[找不到就放过]
    end
    
    subgraph 新视角_质疑式验收官
        B1[默认未完成/有隐瞒]
        B2[索要事实证据]
        B3[证据不全就拦截]
    end
    
    A1 --> |转变| B1
    A2 --> |转变| B2
    A3 --> |转变| B3
    
    style A3 fill:#f66
    style B3 fill:#9f9
```

---

## 质疑式验收 SUITE

```mermaid
graph TB
    A[质疑式验收] --> B[ZERO TRUST<br/>零信任]
    A --> C[EVIDENCE MANDATORY<br/>证据必呈]
    A --> D[ACTIVE FALSIFICATION<br/>主动证伪]
    A --> E[REQUIREMENT TRACING<br/>需求溯源]
    
    B --> B1[不盲信子代理自评]
    C --> C1[必须file:line/命令/截图]
    D --> D1[主动找反例]
    E --> E1[功能 → spec段号]
    
    style B fill:#f66
    style C fill:#f66
    style D fill:#f66
```

---

## 4 维评分

```mermaid
graph TB
    A[4维评分] --> B[维度1: 代码层 25%]
    A --> C[维度2: API层 30%]
    A --> D[维度3: UI/UX层 25%]
    A --> E[维度4: 模块边际 20%]
    
    B --> B1[单元测试 + Contract测试<br/>+ Lint 0 error + 覆盖率 ≥ 90%]
    C --> C1[真实端点 + 接口签名<br/>+ 数据模型 + 错误码]
    D --> D1[视觉一致性 + 交互逻辑<br/>+ UI细态]
    E --> E1[GitNexus impact + 下游无副作用<br/>+ 文档同步 + 扩展点]
    
    style A fill:#f9f
```

---

## 评分公式

```mermaid
flowchart TB
    A[评分计算] --> B[总分 = 通过维度 / 适用维度 × 5.0]
    
    B --> C{任一维度0分?}
    C -->|是| D[🛑 REJECT]
    C -->|否| E{总分 ≥ 4.0?}
    
    E -->|是| F[✅ PASS]
    E -->|否| G[🛑 REJECT]
    
    style D fill:#f66
    style G fill:#f66
```

---

## 骨架流程（V10 reviewer 8 步）

```mermaid
flowchart TB
    A[Step -2: 拆解验收基准] --> B[Step -1: 跨4工件一致性]
    B --> C[Step 0: 硬门禁]
    C --> D[Step 0.5: 索要事实证据]
    D --> E[Step 1: 4维验收]
    E --> F[Step 1.5: 主动证伪]
    F --> G[Step 2: 功能效果验证]
    G --> H[Step 3: 评分]
    H --> I[Step 4: DOC SYNC]
    I --> J[Step 5: 知识提取]
    
    style C fill:#f66
    style E fill:#f9f
```

---

## 硬门禁（Step 0）

```mermaid
flowchart TB
    A[硬门禁检查] --> B[测试 100% GREEN]
    A --> C[理解确认存在]
    A --> D[code-hygiene PASS]
    A --> E[contracts 稳定]
    
    B --> F{全部通过?}
    C --> F
    D --> F
    E --> F
    
    F -->|是| G[继续验收]
    F -->|否| H[🛕 退回Implement]
    
    style H fill:#f66
```

---

## 证据链 3 层

```mermaid
graph TB
    A[证据链] --> B[Layer 1: file:line]
    A --> C[Layer 2: 命令 + 退出码]
    A --> D[Layer 3: 截图/产物]
    
    B --> B1[源码定位]
    C --> C1[真实运行结果]
    D --> D1[视觉验证]
    
    style A fill:#f9f
```

---

## 主动证伪（Step 1.5）

```mermaid
flowchart TB
    A[高风险清单] --> B[逐项核查]
    
    B --> C{发现反例?}
    C -->|是| D[标记质疑]
    C -->|否| E[继续验收]
    
    D --> F[退回修复]
    F --> G[下一轮Review]
    
    style C fill:#f9f
```

---

## 自动循环（Round 机制）

```mermaid
flowchart TB
    A[Round 1 Review] --> B{结果}
    
    B -->|FAIL| C[退回Implement]
    B -->|PASS| D[完成]
    
    C --> E[Round 2 Review]
    E --> F{结果}
    
    F -->|FAIL| G[上报用户]
    F -->|PASS| D
    
    G --> H[Round 3+ Rescue Hatch]
    H --> I{用户决策}
    
    I -->|继续| E
    I -->|终止| J[放弃变更]
    
    style G fill:#f66
```

---

## 10 条铁律

```mermaid
graph TB
    subgraph 核心铁律
        A1[1. FAIL IS FAIL<br/>不存在非阻塞FAIL]
        A2[4. NO DOWNGRADE<br/>不可验证标N/A]
    end
    
    subgraph 评分铁律
        B1[2. SCORING IS DERIVED<br/>总分=通过/适用×5.0]
        B2[3. FOUR DIMENSIONS<br/>4维缺一不可]
    end
    
    subgraph 验证铁律
        C1[5. VERIFY UNDERSTANDING<br/>机械验证理解确认]
        C2[6. REVIEWER DOES NOT FIX<br/>审查者不修代码]
    end
    
    subgraph 验收铁律
        D1[8. CROSS-SESSION VERIFY<br/>主上下文必二次抽检]
        D2[9. 质疑式验收SUITE<br/>零信任+证据必呈+主动证伪]
    end
    
    style A1 fill:#f66
    style A2 fill:#f66
```

---

## DOC SYNC

```mermaid
flowchart TB
    A[Review通过] --> B[DOC SYNC检查]
    
    B --> C[docs/api-endpoints/ 更新?]
    B --> D[docs/domain-models/ 更新?]
    B --> E[docs/INDEX.md 更新?]
    
    C --> F{全部同步?}
    D --> F
    E --> F
    
    F -->|是| G[✅ 进入Stage 4.5]
    F -->|否| H[补全文档同步]
    H --> G
    
    style B fill:#f9f
```

---

## 交接物 4 件套

```yaml
hand_over:
  stage_id: "4/review"
  stage_skill: skills/09-review/SKILL.md
  status: completed
  health: "🟢 on-track"
  artifacts:
    - path: docs/specs/changes/{id}/review-report.md
      type: file
      evidence: "4维评分 + 证据链"
  gate_result:
    status: PASS
    gate: acceptance-audit.py
    output: "4维满分 + 证据链3层 + DOC SYNC ✅"
  next_stage:
    id: "4.5/rot-scan"
    skill_name: skills/10-rot-scan/SKILL.md
    expected_inputs: [review-report.md]
    prerequisites: [4维 ≥ 4.0, 任一维度 > 0]
```

---

## 4 条反模式

```mermaid
graph TB
    subgraph 反模式
        A[1. 非阻塞FAIL放水]
        B[2. reviewer帮忙修代码]
        C[3. 编造测试覆盖]
        D[4. 自动循环Round 3+继续绕]
    end
    
    A --> A1[❌ FAIL IS FAIL]
    B --> B1[❌ 退回实现者修复]
    C --> C1[❌ 证据必须真实]
    D --> D1[❌ Round 3+上报用户]
    
    style A fill:#f66
    style B fill:#f66
    style C fill:#f66
    style D fill:#f66
```

---

## 关联文档

- [四维评分详细](../skills/09-review/references/four-dimension-scoring.md)
- [证据链3层](../skills/09-review/references/evidence-3-layer.md)
- [质疑式验收](../skills/09-review/references/skeptical-acceptance.md)
- [多轮修订](../skills/09-review/references/multi-round-revision.md)
- [Review报告模板](../skills/09-review/templates/review-report-template.md)