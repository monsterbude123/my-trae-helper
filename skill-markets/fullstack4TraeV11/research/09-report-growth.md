# 异常分级（Report Growth）

> L1-L4 异常分级 + 累积升级规则 + 异常处理协议。

---

## 异常分级总览

```mermaid
mindmap
  root((异常分级))
    L1文件系统
      文件缺失
      权限不足
      路径错误
    L2_Agent执行
      工具调用失败
      解析错误
      契约不符
    L3状态不一致
      状态卡与实际不一致
      漂移
      契约破坏
    L4外部依赖
      GitNexus不可用
      API不可达
      端口占用
```

---

## L1-L4 分级定义

```mermaid
graph TB
    subgraph L1_文件系统
        A1[文件缺失]
        A2[权限不足]
        A3[路径错误]
        A4[Retry 1次 → 继续]
    end
    
    subgraph L2_Agent执行
        B1[工具调用失败]
        B2[解析错误]
        B3[契约不符]
        B4[换参数/策略 → 最多3次]
    end
    
    subgraph L3_状态不一致
        C1[state-card与实际不一致]
        C2[漂移]
        C3[契约破坏]
        C4[汇报用户 → 等待决策]
    end
    
    subgraph L4_外部依赖
        D1[GitNexus不可用]
        D2[API不可达]
        D3[端口占用]
        D4[降级运行 + 标注风险]
    end
    
    A4 --> E[重试上限: 1次]
    B4 --> F[重试上限: 3次]
    C4 --> G[不可自动]
    D4 --> H[不可自动]
    
    style A4 fill:#9f9
    style B4 fill:#ff9
    style C4 fill:#f66
    style D4 fill:#f66
```

---

## 异常处理流程

```mermaid
flowchart TB
    A[异常发生] --> B[评估异常等级]
    B --> C{等级判定}
    
    C -->|L1| D[Retry 1次]
    C -->|L2| E[Retry 最多3次]
    C -->|L3| F[立即阻塞报告]
    C -->|L4| G[降级运行 + 阻塞报告]
    
    D --> H{仍失败?}
    E --> I{仍失败?}
    
    H -->|是| J[升级L2]
    I -->|是| K[阻塞报告]
    
    J --> E
    
    F --> L[写入report-growth.jsonl]
    G --> L
    K --> L
    
    L --> M[更新状态卡]
    M --> N[5字段阻塞报告]
    
    style F fill:#f66
    style G fill:#f66
    style K fill:#f66
```

---

## 累积升级规则

```mermaid
graph TB
    A[异常累积] --> B{升级触发}
    
    B --> C[同一agent同一phase<br/>L2+异常 ≥ 3次]
    B --> D[同一stage<br/>跨agent异常 ≥ 5次]
    
    C --> E[升级到L3]
    D --> E
    
    E --> F[汇报用户]
    E --> G[标记高风险]
    E --> H[触发process review]
    
    style E fill:#f66
```

---

## 升级矩阵

```mermaid
graph TB
    A[异常数] --> B{判定}
    
    B -->|1次| C[L1/L2正常<br/>retry 1次]
    B -->|2次| D[L2升级<br/>换参数/策略]
    B -->|3次相同| E[L3<br/>升级用户 + process review]
    B -->|≥5次任意| F[L3<br/>强制升级 + 整体回退]
    B -->|任意L4| G[L3<br/>升级用户]
    
    style E fill:#f66
    style F fill:#f66
    style G fill:#f66
```

---

## 阻塞报告 5 字段

```mermaid
graph TB
    A[阻塞报告] --> B[5字段必含]
    
    B --> C[type: 类型]
    B --> D[description: 描述]
    B --> E[solution: 方案]
    B --> F[duration_minutes: 耗时]
    B --> G[attempts: 尝试次数]
    
    C --> C1[依赖未启动 | 迁移失败<br/>测试失败 | 编译错误<br/>资源缺失 | 环境问题<br/>外部依赖L4]
    
    D --> D1[具体阻塞描述<br/>附命令输出]
    
    E --> E1[建议解决方案<br/>风险评估]
    
    F --> F1[已耗时分钟数]
    
    G --> G1[已尝试次数<br/>每次的action]
    
    style B fill:#f66
```

---

## JSONL 写入格式

```mermaid
graph TB
    A[report-growth.jsonl] --> B[单条JSONL格式]
    
    B --> C[timestamp: ISO 8601]
    B --> D[agent: agent名称]
    B --> E[phase: 子阶段]
    B --> F[level: L1/L2/L3/L4]
    B --> G[error: 错误描述]
    B --> H[root_cause: 根因分析]
    B --> I[action: 已采取动作]
    B --> J[ticket_id: change-id]
    B --> K[stage_id: stage编号]
    
    style A fill:#9cf
```

### 示例

```jsonl
{"timestamp": "2026-08-11T14:30:00", "agent": "implementer", "phase": "TDD-GREEN", "level": "L2", "error": "test_foo(): assertion error", "root_cause": "domain model field type mismatch", "action": "revert to contract definition, fix test expectation", "ticket_id": "2026-08-11-add-user-auth", "stage_id": "3/implement"}
```

---

## 4 禁止项

```mermaid
graph TB
    A[禁止项] --> B[❌ 不要静默失败]
    A --> C[❌ 不要猜测修复]
    A --> D[❌ 不要隐藏异常]
    A --> E[❌ 不要无限重试]
    
    B --> B1[必须写入report-growth.jsonl]
    C --> C1[根因不明确时停止]
    D --> D1[在Completion Report中标注]
    E --> E1[同一操作最多3次]
    
    style B fill:#f66
    style C fill:#f66
    style D fill:#f66
    style E fill:#f66
```

---

## Process Review 协议

```mermaid
flowchart TB
    A[触发条件] --> B{升级触发 ≥ 3次?}
    B -->|是| C[收集report-growth.jsonl]
    B -->|否| D[继续监控]
    
    C --> E[提炼共同根因]
    E --> F[输出process-review-{date}.md]
    F --> G[提交到技能升级循环]
    
    G --> H[反馈给技能开发者]
    G --> I[更新公共铁律]
    G --> J[反馈到项目级rules]
    
    style F fill:#9cf
```

---

## 关键指标

```mermaid
graph TB
    A[健康度指标] --> B[L1异常率]
    A --> C[L2异常率]
    A --> D[L3异常率]
    A --> E[L4异常率]
    A --> F[升级触发次数]
    
    B --> B1[健康: < 5%]
    B --> B2[警告: 5-10%]
    B --> B3[阻塞: > 10%]
    
    C --> C1[健康: < 2%]
    C --> C2[警告: 2-5%]
    C --> C3[阻塞: > 5%]
    
    D --> D1[健康: < 0.5%]
    D --> D2[警告: 0.5-1%]
    D --> D3[阻塞: > 1%]
    
    F --> F1[健康: = 0]
    F --> F2[警告: 1-2]
    F --> F3[阻塞: ≥ 3]
    
    style B1 fill:#9f9
    style C1 fill:#9f9
    style D1 fill:#9f9
    style F1 fill:#9f9
    
    style B3 fill:#f66
    style C3 fill:#f66
    style D3 fill:#f66
    style F3 fill:#f66
```

---

## 关联文档

- [异常分级详细版](../references/report-growth.md)
- [宪法 Article XV](../references/constitution.md)
- [阻塞报告协议](../references/report-growth.md)