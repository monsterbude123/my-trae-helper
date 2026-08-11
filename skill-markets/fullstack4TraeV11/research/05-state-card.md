# 状态卡协议

> 13 个 stage 的状态卡统一协议。状态卡是任务真相源之一，不允许说谎（Article XII）。

---

## 状态卡总览

```mermaid
mindmap
  root((状态卡))
    分类
      项目级
      Change级
      Bug单级
    字段
      身份字段
      状态字段
      产物字段
      门禁字段
      路由字段
    更新时机
      阶段启动
      产物落地
      门禁通过
      阻塞发生
    验证
      存在性
      准确性
      一致性
```

---

## 状态卡分类

```mermaid
graph TB
    subgraph 项目级状态卡
        A[位置: .trae/state-card.md]
        B[作用: 项目整体状态]
        C[生命周期: 项目存在期间]
    end
    
    subgraph Change级状态卡
        D[位置: docs/specs/changes/{id}/.state-card.md]
        E[作用: 单个change状态]
        F[生命周期: change启动→归档]
    end
    
    subgraph Bug单状态卡
        G[位置: docs/bugs/{id}/.state-card.md]
        H[作用: Bug修复进度]
        I[生命周期: 反馈→关闭]
    end
    
    style A fill:#9cf
    style D fill:#9f9
    style G fill:#f9f
```

---

## 必含字段定义

```mermaid
graph TB
    subgraph 身份字段
        A[card_type: project | change | bug]
        B[card_id: 项目名 | change-id | bug-id]
        C[version: 语义版本号]
    end
    
    subgraph 状态字段
        D[current_stage: stage_id]
        E[stage_status: pending | working | completed | blocked | skipped]
        F[stage_started_at: ISO 8601]
        G[stage_ended_at: ISO 8601 | null]
    end
    
    subgraph 元数据字段
        H[updated_at: ISO 8601]
        I[updated_by: 主上下文 | sub-agent]
        J[health: 🟢 | 🟡 | 🔴]
    end
    
    subgraph 产物字段
        K[artifacts: 产物清单]
        L[path: 产物路径]
        M[type: file | dir | report]
        N[exists: true | false]
        O[evidence: 验证方式]
    end
    
    subgraph 门禁字段
        P[gate_result: 门禁结果]
        Q[status: PASS | FAIL | N/A | PENDING]
        R[gate: 门禁脚本名]
        S[output: 脚本输出]
        T[verified_at: ISO 8601]
    end
    
    subgraph 路由字段
        U[next_stage: 下一stage]
        V[id: stage_id]
        W[skill_name: skill名称]
        X[expected_inputs: 输入清单]
        Y[prerequisites: 前置条件]
    end
    
    subgraph 阻塞字段
        Z[blocked_by: 5字段阻塞报告 | null]
    end
```

---

## 状态卡更新时机

```mermaid
sequenceDiagram
    participant Event as 事件
    participant Card as 状态卡
    participant Field as 字段更新
    
    Event->>Card: 阶段启动
    Card->>Field: current_stage, stage_status, stage_started_at
    
    Event->>Card: 产物落地
    Card->>Field: artifacts, updated_at
    
    Event->>Card: 门禁通过
    Card->>Field: gate_result, stage_status
    
    Event->>Card: 门禁失败
    Card->>Field: gate_result, blocked_by
    
    Event->>Card: 阻塞发生
    Card->>Field: health=🔴, blocked_by
    
    Event->>Card: 阻塞解除
    Card->>Field: health=🟢/🟡, blocked_by=null
    
    Event->>Card: 阶段切换
    Card->>Field: current_stage, stage_ended_at, next_stage
```

---

## 交叉验证规则

```mermaid
flowchart TB
    A[状态卡验证] --> B[Rule 1: artifacts文件存在]
    A --> C[Rule 2: gate_result真实跑过]
    A --> D[Rule 3: blocked_by非空时非completed]
    A --> E[Rule 4: completed时stage_ended_at有值]
    A --> F[Rule 5: current_stage在13个名单中]
    
    B --> G{全部通过?}
    C --> G
    D --> G
    E --> G
    F --> G
    
    G -->|是| H[✅ 状态卡有效]
    G -->|否| I[❌ 状态卡说谎]
    
    style H fill:#9f9
    style I fill:#f66
```

---

## 状态卡模板

### 项目级模板

```yaml
---
card_type: project
card_id: my-project
version: "1.0.0"
current_stage: 0/plan
stage_status: working
stage_started_at: 2026-08-11T13:00:00
stage_ended_at: null
updated_at: 2026-08-11T13:30:00
updated_by: 主上下文
health: 🟢 on-track
artifacts:
  - path: docs/specs/changes/2026-08-11-add-user-auth/
    type: dir
    exists: true
    evidence: "ls 验证"
gate_result:
  status: PENDING
  gate: stage-gate.py
  output: null
  verified_at: null
next_stage:
  id: 0.5/test-plan
  skill_name: skills/02-test-plan/SKILL.md
  expected_inputs: [plan.md]
  prerequisites: [plan.md 存在]
blocked_by: null
actor: 主上下文
duration_minutes: 30
---
```

### Change 级模板

```yaml
---
card_type: change
card_id: 2026-08-11-add-user-auth
version: "1.0.0"
current_stage: 3/implement
stage_status: working
stage_started_at: 2026-08-11T14:00:00
stage_ended_at: null
updated_at: 2026-08-11T15:30:00
updated_by: implementer
health: 🟢 on-track
artifacts:
  - path: docs/specs/changes/2026-08-11-add-user-auth/plan.md
    type: file
    exists: true
    evidence: "docs/specs/changes/2026-08-11-add-user-auth/plan.md:1-120"
  - path: docs/specs/changes/2026-08-11-add-user-auth/spec.md
    type: file
    exists: true
    evidence: "docs/specs/changes/2026-08-11-add-user-auth/spec.md:1-200"
gate_result:
  status: PASS
  gate: contract-gate.py
  output: "contract-gate.py: 4件套齐全 + 测试骨架 PASS"
  verified_at: 2026-08-11T14:55:00
next_stage:
  id: 3.5/real-verify
  skill_name: skills/04-real-verify/SKILL.md
  expected_inputs: [代码 + tests/ + docs/modules/]
  prerequisites: [TDD GREEN, DRIFT CHECK ✅]
blocked_by: null
parent_change: null
related_changes: []
risk_level: MEDIUM
priority: P1
notes: 后端API + 前端 + DB schema协同改动
---
```

---

## 状态卡反例

```mermaid
graph TB
    subgraph 反例1_状态卡说谎
        A1[现象: stage_status=completed]
        A2[实际: artifacts路径不存在]
        A3[根因: 未验证产物]
        A4[教训: state-card-validator.py校验]
    end
    
    subgraph 反例2_永远绿灯
        B1[现象: 任何阶段都是🟢]
        B2[实际: 从不降级]
        B3[根因: 不知道blocked_by字段]
        B4[教训: 🟢/🟡/🔴是可视化机制]
    end
    
    subgraph 反例3_无next_stage
        C1[现象: stage=completed]
        C2[实际: 无next_stage路由]
        C3[根因: 未路由到下一stage]
        C4[教训: 阶段切换必须含next_stage]
    end
    
    subgraph 反例4_无时间戳
        D1[现象: 状态卡停留初始版]
        D2[实际: 没有updated_at]
        D3[根因: 忘记加时间戳]
        D4[教训: state-card-staleness是腐烂点16]
    end
    
    style A2 fill:#f66
    style B1 fill:#f66
    style C2 fill:#f66
    style D1 fill:#f66
```

---

## 验证脚本

```mermaid
flowchart TB
    A[state-card-validator.py] --> B[加载状态卡]
    B --> C[验证Rule 1-5]
    
    C --> D[Rule 1: artifacts存在]
    C --> E[Rule 2: gate真实跑过]
    C --> F[Rule 3: blocked逻辑正确]
    C --> G[Rule 4: 时间戳完整]
    C --> H[Rule 5: stage合法]
    
    D --> I{全部通过?}
    E --> I
    F --> I
    G --> I
    H --> I
    
    I -->|是| J[输出: PASS]
    I -->|否| K[输出: FAIL + 不一致清单]
    
    style J fill:#9f9
    style K fill:#f66
```

---

## 不一致处理

```mermaid
graph TB
    A[检测到不一致] --> B{类型}
    
    B -->|file_missing| C[主上下文LS验证]
    C --> D[标记缺失]
    D --> E[触发子代理修复]
    
    B -->|gate_lie| F[检查脚本是否真跑]
    F --> G[重跑]
    G --> H[修正gate_result]
    
    B -->|status_lie| I[主上下文分析]
    I --> J[修正stage_status]
    
    B -->|wrong_stage| K[检测路由]
    K --> L[重置current_stage]
    
    style D fill:#f9f
    style H fill:#f9f
    style J fill:#f9f
    style L fill:#f9f
```

---

## 关联文档

- [状态卡协议详细版](../references/state-card-protocol.md)
- [阶段交互协议](../references/stage-interaction-protocol.md)
- [宪法 Article XII](../references/constitution.md)