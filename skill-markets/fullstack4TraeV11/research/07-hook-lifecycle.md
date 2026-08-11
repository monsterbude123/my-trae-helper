# Hook 生命周期

> 每个 stage 的关键动作有前后验证。Hook 失败 = 阻断，不得跳过。

---

## Hook 总览

```mermaid
mindmap
  root((Hook生命周期))
    通用Hook
      Stage切换前门禁
      Stage启动依赖检查
      Stage结束状态卡更新
    完成Hook
      13个stage各不同
      必阻塞
      产出验证
    反应模式
      PASS继续
      FAIL阻断
      N/A标注理由
```

---

## 通用 Hook

```mermaid
sequenceDiagram
    participant Stage as 当前Stage
    participant Gate as 门禁
    participant Card as 状态卡
    participant Next as 下一Stage
    
    Stage->>Gate: Stage切换前
    Gate->>Gate: 当前stage门禁
    Gate->>Gate: 产出门禁报告
    
    alt 门禁FAIL
        Gate->>Stage: 🛑 阻断
    end
    
    Stage->>Stage: Stage启动
    Stage->>Stage: 加载stage skill
    Stage->>Stage: 解析depends_on
    Stage->>Stage: 检查前置
    
    alt 前置未满足
        Stage->>Stage: 🛑 阻断
    end
    
    Stage->>Stage: 执行任务
    
    Stage->>Card: Stage结束
    Card->>Card: 更新状态卡
    Card->>Card: 交接物4件套
    
    Stage->>Next: 非阻塞
```

---

## 各 Stage 完成 Hook

```mermaid
graph TB
    subgraph Stage_-1_to_1.5
        A1[Stage -1 Intake] --> A2[状态卡初始化 + 路由决策]
        B1[Stage 0 Plan] --> B2[3路探索 + GitNexus impact]
        C1[Stage 0.5 Test Plan] --> C2[验收维度 → 测试映射]
        D1[Stage 1 Spec] --> D2[Enhanced Acceptance + clarify]
        E1[Stage 1.5 Prototype] --> E2[双源兼容校验]
    end
    
    subgraph Stage_2_to_3.5
        F1[Stage 2 Contract] --> F2[contract-gate.py]
        G1[Stage 3 Implement] --> G2[TDD GREEN + DRIFT CHECK]
        H1[Stage 3.5 Real Verify] --> H2[5项必跑 + 启动验证]
    end
    
    subgraph Stage_4_to_5
        I1[Stage 4 Review] --> I2[4维评分 + 证据链]
        J1[Stage 4.5 Rot Scan] --> J2[proactive-scan 8项]
        K1[Stage 5 Accept] --> K2[归档前检查 + 知识沉淀]
    end
    
    subgraph Stage_6_to_7
        L1[Stage 6 Bug Fix] --> L2[e2e先行 + 6层排查]
        M1[Stage 7 Project Health] --> M2[4维度 + 优先级分级<br/>非阻塞异步]
    end
    
    style A2 fill:#f66
    style B2 fill:#f66
    style C2 fill:#f66
    style D2 fill:#f66
    style E2 fill:#f66
    style F2 fill:#f66
    style G2 fill:#f66
    style H2 fill:#f66
    style I2 fill:#f66
    style J2 fill:#f66
    style K2 fill:#f66
    style L2 fill:#f66
    style M2 fill:#9cf
```

---

## Hook 反应模式

```mermaid
flowchart TB
    A[Hook执行] --> B{结果}
    
    B -->|PASS| C[继续下一动作]
    B -->|FAIL| D[🛑 阻断]
    B -->|N/A| E[标注理由 + 继续]
    
    D --> F[输出5字段阻塞报告]
    F --> G[回退路径]
    G --> H[等待用户决策]
    
    E --> E1[状态卡标注N/A原因]
    E --> E2[继续下一动作]
    
    style D fill:#f66
    style E fill:#ff9
    style C fill:#9f9
```

---

## Stage -1 Intake Hook

```mermaid
flowchart TB
    A[用户意图输入] --> B[意图识别]
    B --> C{意图类型}
    
    C -->|Feature| D[创建Change]
    C -->|Bug| E[Bug录入判断]
    C -->|Consultation| F[直接回答]
    C -->|Refactor| G[评估影响面]
    
    D --> H[状态卡初始化]
    E --> I{是否录入Bug单?}
    I -->|是| J[创建Bug单]
    I -->|否| K[按一般咨询处理]
    
    H --> L[路由决策表]
    J --> L
    G --> L
    
    L --> M{Hook检查}
    M -->|PASS| N[路由到下一Stage]
    M -->|FAIL| O[🛑 阻断]
    
    style M fill:#f9f
    style N fill:#9f9
```

---

## Stage 0 Plan Hook

```mermaid
flowchart TB
    A[需求输入] --> B[三路并行探索]
    
    B --> C[路1: 快速方案]
    B --> D[路2: 标准方案]
    B --> E[路3: 彻底方案]
    
    C --> F{GitNexus impact}
    D --> F
    E --> F
    
    F --> G[评估影响面]
    G --> H[追问点列表]
    H --> I[plan.md输出]
    
    I --> J{Hook检查}
    J -->|PASS| K[进入Stage 0.5]
    J -->|FAIL| L[🛑 退回Stage 0重做]
    
    style F fill:#f9f
    style J fill:#f9f
    style K fill:#9f9
```

---

## Stage 3 Implement Hook

```mermaid
flowchart TB
    A[contracts/] --> B[TDD RED]
    B --> C[写失败测试]
    C --> D{TDD GREEN}
    D --> E[写实现]
    E --> F{测试通过?}
    F -->|否| E
    F -->|是| G[TDD REFACTOR]
    
    G --> H{Hook检查}
    H --> H1[TDD GREEN验证]
    H --> H2[DRIFT CHECK]
    H --> H3[code-hygiene.py]
    
    H1 --> I{全部通过?}
    H2 --> I
    H3 --> I
    
    I -->|是| J[进入Stage 3.5]
    I -->|否| K[🛑 阻断]
    
    style D fill:#f66
    style H fill:#f9f
    style J fill:#9f9
```

---

## Stage 3.5 Real Verify Hook

```mermaid
flowchart TB
    A[Implement完成] --> B[启动服务]
    B --> C{服务启动成功?}
    C -->|否| D[🛑 阻塞报告]
    
    C -->|是| E[5项必跑Hook]
    
    E --> E1[1. 编译检查]
    E --> E2[2. 测试运行]
    E --> E3[3. 启动验证]
    E --> E4[4. 截图采集]
    E --> E5[5. 交互测试]
    
    E1 --> F{全部通过?}
    E2 --> F
    E3 --> F
    E4 --> F
    E5 --> F
    
    F -->|是| G[进入Stage 4]
    F -->|否| D
    
    style D fill:#f66
    style E fill:#f9f
    style G fill:#9f9
```

---

## Stage 4 Review Hook

```mermaid
flowchart TB
    A[Real Verify通过] --> B[四维评分]
    
    B --> B1[维度1: 代码层]
    B --> B2[维度2: API层]
    B --> B3[维度3: UI/UX层]
    B --> B4[维度4: 模块边际]
    
    B1 --> C{Hook检查}
    B2 --> C
    B3 --> C
    B4 --> C
    
    C --> C1[满分验证]
    C --> C2[证据链3层]
    C --> C3[DOC SYNC]
    
    C1 --> D{全部通过?}
    C2 --> D
    C3 --> D
    
    D -->|是| E[进入Stage 4.5]
    D -->|否| F[🛑 退回Stage 3]
    
    style C fill:#f9f
    style E fill:#9f9
```

---

## Stage 4.5 Rot Scan Hook

```mermaid
flowchart TB
    A[Review通过] --> B[8项扫描Hook]
    
    B --> B1[1. 视觉验证]
    B --> B2[2. 归档修改]
    B --> B3[3. 自评自签]
    B --> B4[4. 孤儿测试]
    B --> B5[5. 构建残留]
    B --> B6[6. 自我吹嘘]
    B --> B7[7. 状态卡陈旧]
    B --> B8[8. 骨架堆积]
    
    B1 --> C{任一FAIL?}
    B2 --> C
    B3 --> C
    B4 --> C
    B5 --> C
    B6 --> C
    B7 --> C
    B8 --> C
    
    C -->|是| D[🛑 修复列表]
    C -->|否| E[进入Stage 5]
    
    D --> F[回到Stage 4]
    
    style B fill:#f9f
    style E fill:#9f9
```

---

## Stage 6 Bug Fix Hook

```mermaid
flowchart TB
    A[Bug单输入] --> B[e2e先行Hook]
    B --> C{初始FAIL?}
    
    C -->|否| D[🛕 重做e2e]
    D --> B
    
    C -->|是| E[6层排查Hook]
    
    E --> E1[1. 表象层]
    E --> E2[2. 日志层]
    E --> E3[3. 数据层]
    E --> E4[4. 配置层]
    E --> E5[5. 依赖层]
    E --> E6[6. 设计层]
    
    E1 --> F{根因定位?}
    E2 --> F
    E3 --> F
    E4 --> F
    E5 --> F
    E6 --> F
    
    F -->|否| G{超5轮?}
    G -->|是| H[用户决策]
    G -->|否| E
    
    F -->|是| I[修复]
    I --> J[全量回归]
    J --> K[Bug单CLOSED]
    
    style B fill:#f66
    style E fill:#f9f
    style K fill:#9f9
```

---

## 关联文档

- [阶段交互协议](../references/stage-interaction-protocol.md)
- [状态卡协议](../references/state-card-protocol.md)
- [脚本使用时机](08-scripts.md)