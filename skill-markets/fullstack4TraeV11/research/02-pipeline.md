# V11 十三阶段流水线

> 从 Intake 到 Project Health 的完整流水线。

---

## 流水线总览

```mermaid
flowchart TB
    subgraph 主链路_必走
        S1[-1 Intake<br/>意图识别]
        S2[0 Plan<br/>三路探索]
        S3[0.5 Test Plan<br/>测试映射]
        S4[1 Spec<br/>规格编写]
        S5[1.5 Prototype<br/>双源验证]
        S6[2 Contract<br/>契约定义]
        S7[3 Implement<br/>TDD实现]
        S8[3.5 Real Verify<br/>启动验证]
        S9[4 Review<br/>四维验收]
        S10[4.5 Rot Scan<br/>腐化扫描]
        S11[5 Accept<br/>归档沉淀]
    end
    
    subgraph 支线_独立
        S12[6 Bug Fix<br/>Bug修复]
        S13[7 Project Health<br/>健康检查]
    end
    
    S1 --> S2
    S2 --> S3
    S3 --> S4
    S4 --> S5
    S5 --> S6
    S6 --> S7
    S7 --> S8
    S8 --> S9
    S9 --> S10
    S10 --> S11
    
    S1 -.-> S12
    S12 -.-> S7
    
    S1 -.-> S13
    S7 -.-> S13
```

---

## 阶段门禁链

```mermaid
graph LR
    subgraph Stage_-1_to_1.5
        A[-1 Intake] -->|意图识别| B[0 Plan]
        B -->|3路探索| C[0.5 Test Plan]
        C -->|测试映射| D[1 Spec]
        D -->|规格确认| E[1.5 Prototype]
    end
    
    subgraph Stage_2_to_3.5
        E -->|契约验证| F[2 Contract]
        F -->|TDD GREEN| G[3 Implement]
        G -->|启动验证| H[3.5 Real Verify]
    end
    
    subgraph Stage_4_to_5
        H -->|四维验收| I[4 Review]
        I -->|腐化扫描| J[4.5 Rot Scan]
        J -->|归档| K[5 Accept]
    end
```

---

## 各阶段详解

### Stage -1: Intake（意图识别）

```mermaid
flowchart TB
    A[用户输入] --> B{意图类型}
    B -->|新需求| C[Feature]
    B -->|Bug反馈| D[Bug录入]
    B -->|咨询| E[Consultation]
    B -->|重构| F[Refactor]
    
    C --> G[创建Change]
    D --> H[创建Bug单]
    E --> I[直接回答]
    F --> J[评估影响面]
    
    G --> K[路由到Stage 0]
    H --> L[路由到Stage 6]
    J --> K
    
    style D fill:#f66
    style H fill:#f66
```

**门禁**:
- 意图识别完成
- 路由决策表输出
- Bug录入判断完成

**产物**:
- 状态卡初始化
- 路由决策表

---

### Stage 0: Plan（规划）

```mermaid
flowchart TB
    A[需求输入] --> B[三路并行探索]
    
    B --> C[路1: 快速方案]
    B --> D[路2: 标准方案]
    B --> E[路3: 彻底方案]
    
    C --> F{对比评估}
    D --> F
    E --> F
    
    F --> G[推荐方案]
    G --> H[GitNexus Impact]
    H --> I[追问点列表]
    I --> J[plan.md输出]
    
    style B fill:#9cf
    style H fill:#f9f
```

**门禁**:
- 3 路并行探索完成
- GitNexus impact 执行
- 追问点明确

**产物**:
- plan.md
- 影响面评估报告

---

### Stage 0.5: Test Plan（测试规划）

```mermaid
flowchart LR
    A[plan.md] --> B[验收维度提取]
    B --> C[测试用例映射]
    C --> D[覆盖率计算]
    D --> E{覆盖率 ≥ 阈值?}
    E -->|是| F[test-plan.md]
    E -->|否| G[补充用例]
    G --> C
    
    style D fill:#9f9
```

**门禁**:
- 验收维度完整
- 测试用例映射完成
- 覆盖率达标

**产物**:
- test-plan.md

---

### Stage 1: Spec（规格）

```mermaid
sequenceDiagram
    participant User
    participant Agent
    participant Clarify
    
    Agent->>Agent: 读取plan.md + test-plan.md
    Agent->>Agent: 生成spec骨架
    Agent->>User: 提交初稿
    User->>Agent: 反馈澄清需求
    Agent->>Clarify: 第一轮澄清
    Clarify->>Agent: 明确点
    Agent->>User: 更新spec
    User->>Agent: 再次反馈
    Agent->>Clarify: 第二轮澄清
    Clarify->>Agent: 最终明确
    Agent->>Agent: Enhanced Acceptance
    Agent->>User: spec.md最终版
```

**门禁**:
- Enhanced Acceptance 完成
- INV ≥ 1
- Clarify ≥ 2 轮

**产物**:
- spec.md
- 澄清记录

---

### Stage 1.5: Prototype（原型）

```mermaid
graph TB
    A[spec.md] --> B[设计稿]
    A --> C[代码原型]
    
    B --> D{双源兼容}
    C --> D
    
    D -->|一致| E[通过]
    D -->|不一致| F[回流修正]
    F --> B
    F --> C
    
    style D fill:#9cf
    style E fill:#9f9
```

**门禁**:
- 双源兼容校验通过

**产物**:
- 设计稿
- 代码原型

---

### Stage 2: Contract（契约）

```mermaid
graph TB
    A[spec.md] --> B[contracts/]
    
    B --> C[api-contracts.md]
    B --> D[domain-models.md]
    B --> E[events.md]
    B --> F[validation-rules.md]
    
    C --> G[contract-gate.py]
    D --> G
    E --> G
    F --> G
    
    G --> H{四件套齐全?}
    H -->|是| I[测试骨架]
    H -->|否| J[退回Stage 1]
    
    I --> K[Contract PASS]
    
    style G fill:#f9f
    style K fill:#9f9
```

**门禁**:
- contract-gate.py 通过
- 四件套齐全
- 测试骨架存在

**产物**:
- contracts/ 四件套
- tests/contracts/

---

### Stage 3: Implement（实现）

```mermaid
flowchart TB
    A[contracts/] --> B[TDD RED]
    B --> C[写失败测试]
    C --> D[TDD GREEN]
    D --> E[写实现]
    E --> F{测试通过?}
    F -->|是| G[TDD REFACTOR]
    F -->|否| E
    
    G --> H[DRIFT CHECK]
    H --> I{漂移?}
    I -->|是| J[回流spec]
    I -->|否| K[code-hygiene.py]
    J --> B
    
    K --> L[Implement PASS]
    
    style B fill:#f66
    style D fill:#9f9
    style G fill:#9cf
```

**门禁**:
- TDD GREEN
- DRIFT CHECK
- code-hygiene.py

**产物**:
- 代码
- tests/unit
- docs/modules

---

### Stage 3.5: Real Verify（真实验证）

```mermaid
flowchart TB
    A[Implement完成] --> B[启动服务]
    B --> C{服务启动成功?}
    C -->|否| D[阻塞报告]
    C -->|是| E[5项必跑]
    
    E --> F[1. 编译]
    E --> G[2. 测试]
    E --> H[3. 启动]
    E --> I[4. 截图]
    E --> J[5. 交互]
    
    F --> K{全部通过?}
    G --> K
    H --> K
    I --> K
    J --> K
    
    K -->|是| L[verify-report.md]
    K -->|否| D
    
    style D fill:#f66
    style L fill:#9f9
```

**门禁**:
- 5 项必跑
- 启动可见产物

**产物**:
- verify-report.md
- 截图证据

---

### Stage 4: Review（评审）

```mermaid
graph TB
    A[Real Verify通过] --> B[四维评分]
    
    B --> C[维度1: 代码层]
    B --> D[维度2: API层]
    B --> E[维度3: UI/UX层]
    B --> F[维度4: 模块边际]
    
    C --> G{满分?}
    D --> G
    E --> G
    F --> G
    
    G -->|是| H[证据链3层]
    G -->|否| I[退回Stage 3]
    
    H --> J[DOC SYNC]
    J --> K[Review PASS]
    
    style G fill:#f9f
    style K fill:#9f9
```

**门禁**:
- 四维满分
- 证据链3层
- DOC SYNC

**产物**:
- review-report.md

---

### Stage 4.5: Rot Scan（腐化扫描）

```mermaid
graph TB
    A[Review通过] --> B[8项扫描]
    
    B --> C[1. 视觉验证]
    B --> D[2. 归档修改]
    B --> E[3. 自评自签]
    B --> F[4. 孤儿测试]
    B --> G[5. 构建残留]
    B --> H[6. 自我吹嘘]
    B --> I[7. 状态卡陈旧]
    B --> J[8. 骨架堆积]
    
    C --> K{全部PASS?}
    D --> K
    E --> K
    F --> K
    G --> K
    H --> K
    I --> K
    J --> K
    
    K -->|是| L[Rot Scan PASS]
    K -->|否| M[修复列表]
    M --> N[回到Stage 4]
    
    style K fill:#f9f
    style L fill:#9f9
```

**门禁**:
- proactive-scan 8 项全部 PASS

**产物**:
- rot-scan-{date}.md
- fix-list.json

---

### Stage 5: Accept（归档）

```mermaid
flowchart TB
    A[Rot Scan PASS] --> B[归档前检查]
    B --> C[spec-purge.py]
    C --> D{清理完成?}
    D -->|否| E[手动清理]
    E --> C
    
    D -->|是| F[知识沉淀]
    F --> G[spec-knowledge-extract.py]
    G --> H[INDEX更新]
    H --> I[archive/done]
    
    style I fill:#9f9
```

**门禁**:
- 归档不可变
- INDEX 更新

**产物**:
- archive/done/{change}/
- 知识沉淀文档

---

### Stage 6: Bug Fix（Bug修复）

```mermaid
flowchart TB
    A[Bug单输入] --> B[e2e先行]
    B --> C{初始FAIL?}
    C -->|否| D[重做e2e]
    D --> B
    C -->|是| E[6层排查]
    
    E --> F[1. 表象层]
    E --> G[2. 日志层]
    E --> H[3. 数据层]
    E --> I[4. 配置层]
    E --> J[5. 依赖层]
    E --> K[6. 设计层]
    
    F --> L{根因定位?}
    G --> L
    H --> L
    I --> L
    J --> L
    K --> L
    
    L -->|是| M[修复]
    M --> N[全量回归]
    N --> O[Bug单CLOSED]
    
    style C fill:#f66
    style O fill:#9f9
```

**门禁**:
- e2e 先行（必须初始 FAIL）
- 6 层排查
- 全量回归

**产物**:
- 修复代码
- Bug单 CLOSED

---

### Stage 7: Project Health（项目健康）

```mermaid
graph TB
    A[任一阶段触发] --> B[4维度检查]
    
    B --> C[维度1: 代码健康]
    B --> D[维度2: 测试健康]
    B --> E[维度3: 文档健康]
    B --> F[维度4: 流程健康]
    
    C --> G{优先级分级}
    D --> G
    E --> G
    F --> G
    
    G --> H[P0: 立即修复]
    G --> I[P1: 本周修复]
    G --> J[P2: 本月修复]
    G --> K[P3: 待办]
    
    style A fill:#9cf
    style H fill:#f66
```

**门禁**:
- 非阻塞，异步

**产物**:
- project-health-{date}.md
- .json

---

## 回退路径

```mermaid
graph TB
    A[Stage 0 Plan] -->|user拒绝| B[Stage -1 Intake]
    A -->|探索不够| A
    
    C[Stage 1 Spec] -->|user拒绝| A
    C -->|验收不完整| C
    
    D[Stage 2 Contract] -->|gate FAIL| C
    
    E[Stage 3 Implement] -->|TDD FAIL| D
    E -->|DRIFT FAIL| C
    
    F[Stage 4 Review] -->|非满分| E
    
    G[Stage 4.5 Rot Scan] -->|rot FAIL| F
    
    H[Stage 5 Accept] -->|归档失败| G
```

---

## 阶段度量指标

```mermaid
graph LR
    A[健全度] --> B[产物完整度]
    A --> C[门禁PASS度]
    A --> D[阻塞报告]
    A --> E[状态卡同步]
    
    B --> F{健全度 ≥ 90%?}
    C --> F
    D --> F
    E --> F
    
    F -->|是| G[允许进入下一Stage]
    F -->|否| H[修复当前Stage]
    
    style G fill:#9f9
```

---

## 关联文档

- [阶段交互协议](../references/stage-interaction-protocol.md)
- [状态卡协议](../references/state-card-protocol.md)
- [宪法](../references/constitution.md)