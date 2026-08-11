# 阶段交互协议

> Stage 间交接的标准化协议。每个 stage 完成后必须输出统一格式的交接物。

---

## 交互总览

```mermaid
mindmap
  root((阶段交互))
    交接物
      标准4件套
      产物清单
      门禁结果
      阻塞报告
    消息协议
      状态卡更新
      启动前检查
      异常状态定义
    回退路径
      单次1-2个stage
      连续3次升级
      禁止跨级跳跃
    并发控制
      可并行场景
      不可并行场景
```

---

## 标准 4 件套

```mermaid
graph TB
    subgraph 交接物[Stage交接物 4件套]
        A[1. 状态卡更新]
        B[2. 产物清单]
        C[3. 门禁结果]
        D[4. 阻塞报告]
    end
    
    A --> A1[stage_id]
    A --> A2[stage_status]
    A --> A3[health]
    
    B --> B1[artifacts]
    B --> B2[evidence]
    
    C --> C1[gate: PASS/FAIL]
    C --> C2[脚本输出]
    
    D --> D1[type]
    D --> D2[description]
    D --> D3[solution]
    D --> D4[duration]
    D --> D5[attempts]
```

---

## 阶段门禁链

```mermaid
flowchart TB
    A[Stage N 完成] --> B{门禁检查}
    B --> C[产物完整度]
    B --> D[门禁PASS度]
    B --> E[阻塞报告]
    B --> F[状态卡同步]
    
    C --> G{健全度 ≥ 90%?}
    D --> G
    E --> G
    F --> G
    
    G -->|是| H[允许进入Stage N+1]
    G -->|否| I[修复当前Stage]
    
    style H fill:#9f9
    style I fill:#f66
```

---

## 启动前检查清单

```mermaid
flowchart TB
    A[启动下一Stage前] --> B[检查清单]
    
    B --> C[✅ 上一stage状态 = completed]
    B --> D[✅ 上一stage门禁 = PASS]
    B --> E[✅ 上一stage状态卡已更新]
    B --> F[✅ 上一stage阻塞已解除]
    B --> G[✅ 下一stage依赖的inputs存在]
    B --> H[✅ 下一stage skill依赖检查]
    
    C --> I{全部通过?}
    D --> I
    E --> I
    F --> I
    G --> I
    H --> I
    
    I -->|是| J[启动下一Stage]
    I -->|否| K[🛑 阻断]
    
    style J fill:#9f9
    style K fill:#f66
```

---

## 阶段回退路径

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
    
    I[Stage 6 Bug Fix] -->|e2e初始PASS| I
    I -->|排查超5轮| J[用户决策]
    
    style A fill:#9cf
    style B fill:#f9f
```

---

## 异常状态定义

```mermaid
graph TB
    subgraph 状态类型
        A[🟢 on-track<br/>按计划推进]
        B[🟡 degraded<br/>有阻塞但可并行]
        C[🔴 blocked<br/>完全阻塞]
    end
    
    A --> D[继续下一stage]
    B --> E[记录但不阻塞]
    C --> F[5字段阻塞报告<br/>等待用户决策]
    
    style A fill:#9f9
    style B fill:#ff9
    style C fill:#f66
```

---

## 阶段产物层级

```mermaid
graph TB
    subgraph Stage_-1_to_1.5
        A1[Stage -1] --> A2[状态卡 + 路由决策表]
        B1[Stage 0] --> B2[plan.md]
        C1[Stage 0.5] --> C2[test-plan.md]
        D1[Stage 1] --> D2[spec.md]
        E1[Stage 1.5] --> E2[prototypes/]
    end
    
    subgraph Stage_2_to_3.5
        F1[Stage 2] --> F2[contracts/ 四件套]
        G1[Stage 3] --> G2[代码 + tests/unit]
        H1[Stage 3.5] --> H2[verify-report.md]
    end
    
    subgraph Stage_4_to_5
        I1[Stage 4] --> I2[review-report.md]
        J1[Stage 4.5] --> J2[rot-scan-{date}.md]
        K1[Stage 5] --> K2[archive/done/]
    end
    
    subgraph Stage_6_to_7
        L1[Stage 6] --> L2[Bug单CLOSED]
        M1[Stage 7] --> M2[project-health-{date}.md]
    end
```

---

## 阶段并发控制

### 可并行场景

```mermaid
graph LR
    A[Stage 0 Plan] --> B[3路并行探索]
    
    C[Stage 1 完成后] --> D[Stage 0.5 Test Plan]
    C --> E[Stage 1.5 Prototype]
    
    F[任一Stage] --> G[Stage 7 Project Health]
    
    style B fill:#9f9
    style D fill:#9f9
    style E fill:#9f9
    style G fill:#9f9
```

### 不可并行场景

```mermaid
graph TB
    A[同一Stage] --> B[❌ 多子代理同时改同一产物]
    C[下一Stage] --> D[❌ 必须等上一Stage产物落地]
    E[Stage 5 Accept] --> F[❌ 归档阶段必须独占]
    
    style B fill:#f66
    style D fill:#f66
    style F fill:#f66
```

---

## 状态卡更新协议

```mermaid
sequenceDiagram
    participant Stage as 当前Stage
    participant Card as 状态卡
    participant Next as 下一Stage
    
    Stage->>Card: 更新current_stage
    Stage->>Card: 更新stage_status
    Stage->>Card: 更新artifacts
    Stage->>Card: 更新gate_result
    Stage->>Card: 更新next_stage
    
    Stage->>Next: 交接物4件套
    Next->>Card: 验证上一Stage状态
    Next->>Next: 启动前检查清单
    Next->>Next: 开始执行
```

---

## 交接物 YAML 模板

```yaml
hand_over:
  stage_id: {stage编号}
  stage_skill: {stage skill name}
  status: {completed | blocked | skipped}
  health: {🟢 on-track | 🟡 degraded | 🔴 blocked}
  duration: {开始时间 → 结束时间}
  artifacts:
    - path: {产物路径}
      type: {file | dir | report | state-update}
      evidence: {验证方式}
  gate_result:
    status: {PASS | FAIL | N/A}
    gate: {门禁脚本名}
    output: {门禁脚本输出}
  blocker: {无 | 5字段阻塞报告}
  next_stage:
    stage_id: {下一stage编号}
    skill_name: {下一stage skill name}
    expected_inputs: {下一stage需要的输入物清单}
    prerequisites: {启动前必含条件}
```

---

## 阶段健全度指标

```mermaid
graph TB
    A[健全度计算] --> B[产物完整度]
    A --> C[门禁PASS度]
    A --> D[阻塞报告]
    A --> E[状态卡同步]
    
    B --> B1[LS验证产物存在]
    C --> C1[脚本输出PASS]
    D --> D1[状态卡扫描]
    E --> E1[交叉验证]
    
    B1 --> F{健全度 ≥ 90%?}
    C1 --> F
    D1 --> F
    E1 --> F
    
    F -->|是| G[✅ 允许进入下一Stage]
    F -->|否| H[❌ 修复当前Stage]
    
    style G fill:#9f9
    style H fill:#f66
```

---

## 关联文档

- [阶段交互协议详细版](../references/stage-interaction-protocol.md)
- [状态卡协议](../references/state-card-protocol.md)
- [公共铁律](../references/common-iron-rules.md)