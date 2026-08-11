# V11 哲学体系

> 10 条核心哲学指导全栈文档驱动开发。

---

## 哲学总览

```mermaid
mindmap
  root((V11 哲学))
    质量优先
      复用而非自研
      质量而非流程
      验证而非信任
      干净而非兼容
    主动执行
      主动而非被动
      诚实而非吹嘘
    简洁清晰
      骨感而非堆积
      分层而非混置
    V11 新增
      高内聚低耦合
      插拔式专家
```

---

## 哲学层次结构

```mermaid
graph TB
    subgraph 质量底线
        P1[复用而非自研]
        P2[质量而非流程]
        P3[验证而非信任]
        P4[干净而非兼容]
    end
    
    subgraph 执行态度
        P5[主动而非被动]
        P6[诚实而非吹嘘]
    end
    
    subgraph 文档风格
        P7[骨感而非堆积]
        P8[分层而非混置]
    end
    
    subgraph V11架构哲学
        P9[高内聚低耦合]
        P10[插拔式专家]
    end
    
    P1 --> P9
    P2 --> P5
    P3 --> P6
    P7 --> P8
    P8 --> P9
    P9 --> P10
```

---

## 各哲学详解

### 1. 复用而非自研

```mermaid
flowchart LR
    A[需求] --> B{已存在?}
    B -->|是| C[复用现有组件]
    B -->|否| D{社区有?}
    D -->|是| E[引入成熟方案]
    D -->|否| F[最小化自研]
    C --> G[快速交付]
    E --> G
    F --> H[沉淀为可复用]
    H --> G
```

**核心原则**:
- 标准库优先
- 成熟库优先
- 必要时最小化自研
- 自研后沉淀为可复用

---

### 2. 质量而非流程

```mermaid
graph LR
    A[流程] --> B{质量门禁}
    B -->|PASS| C[继续]
    B -->|FAIL| D[阻断]
    D --> E[修复]
    E --> B
    C --> F[交付]
    
    style B fill:#f9f,stroke:#333,stroke-width:4px
    style D fill:#f66,stroke:#333,stroke-width:2px
```

**核心原则**:
- 门禁 PASS 是唯一通行证
- 流程服务于质量
- 跳过门禁 = 流程失效

---

### 3. 验证而非信任

```mermaid
flowchart TB
    A[子代理返回] --> B{3层独立验证}
    B --> C[存在性: LS]
    B --> D[准确性: Run]
    B --> E[产物存在: Glob]
    C --> F{全部通过?}
    D --> F
    E --> F
    F -->|是| G[接受]
    F -->|否| H[质疑+退回]
```

**核心原则**:
- 不盲信自评
- 主上下文亲自验证
- 证据链必须真实

---

### 4. 干净而非兼容

```mermaid
graph TB
    A[迁移/重构] --> B{旧代码}
    B --> C[彻底清理]
    B --> D[保留兼容层]
    C --> E[干净代码库]
    D --> F[技术债累积]
    
    style C fill:#9f9,stroke:#333
    style D fill:#f66,stroke:#333
```

**核心原则**:
- Git 有历史，不留 `.bak`
- 兼容层是临时技术债
- 彻底迁移优于缝补

---

### 5. 主动而非被动

```mermaid
sequenceDiagram
    participant User
    participant Agent
    
    Note over Agent: 主动模式
    Agent->>Agent: 预判用户意图
    Agent->>Agent: 提前准备
    Agent->>Agent: 主动汇报状态
    Agent->>User: 按需交付
    
    Note over Agent: 被动模式 ❌
    User->>Agent: 问一句做一句
    User->>Agent: 反复追问
    User->>Agent: 等待指令
```

**核心原则**:
- 预判用户需求
- 主动状态汇报
- 减少用户追问

---

### 6. 诚实而非吹嘘

```mermaid
graph LR
    A[完成报告] --> B{内容检查}
    B --> C[状态 + 证据]
    B --> D[自我评价]
    C --> E[诚实报告 ✓]
    D --> F[吹嘘 ❌]
    
    style E fill:#9f9
    style F fill:#f66
```

**禁止项**:
- ❌ "我成功完成"
- ❌ "完美实现"
- ❌ "快速交付"

**正确模式**:
- ✅ 状态变化 + 证据
- ✅ 阻塞明确汇报
- ✅ 未完成项诚实声明

---

### 7. 骨感而非堆积

```mermaid
graph TB
    A[文档] --> B{内容检查}
    B --> C[核心铁律]
    B --> D[引用外置]
    C --> E[精简骨架 ✓]
    D --> E
    
    F[反例] --> G[内联大段内容]
    G --> H[上下文击穿 ❌]
```

**核心原则**:
- SKILL.md 只放骨架
- 详细内容放 references/
- Agent 文件 ≤150 行

---

### 8. 分层而非混置

```mermaid
graph TB
    subgraph fact层
        F1[宪法]
        F2[架构]
        F3[契约]
        F4[规格]
    end
    
    subgraph process层
        P1[诊断手记]
        P2[修复记录]
        P3[调试草稿]
    end
    
    subgraph log层
        L1[历史报告]
        L2[变更日志]
        L3[归档版本]
    end
    
    F1 --> F4
    P1 --> P3
    L1 --> L3
    
    style F1 fill:#9f9
    style P1 fill:#ff9
    style L1 fill:#9cf
```

**子代理可读性**:
- fact: ✅ 必读
- process: ❌ 禁读
- log: ⚠️ 可读但不作验收依据

---

### 9. 高内聚低耦合

```mermaid
graph LR
    subgraph Stage Skill
        A[SKILL.md]
        B[铁律]
        C[反例]
        D[模板]
        E[脚本]
        F[工作流]
    end
    
    A --> B
    A --> C
    A --> D
    A --> E
    A --> F
    
    G[编排器] --> H[路由]
    G --> I[门禁]
    G --> J[状态卡同步]
    
    H --> A
```

**核心原则**:
- 每个 stage 自包含
- stage skill 可独立升级
- 编排器只做路由+门禁

---

### 10. 插拔式专家

```mermaid
flowchart TB
    A[13个Stage Skills] --> B[01-intake]
    A --> C[02-plan]
    A --> D[03-test-plan]
    A --> E[...]
    A --> F[13-project-health]
    
    B --> G[独立升级]
    C --> G
    D --> G
    E --> G
    F --> G
    
    G --> H[不影响其他stage]
    
    style G fill:#9f9,stroke:#333
```

**核心原则**:
- stage skill 像组件一样插拔
- 升级一个不影响其他
- 依赖声明在 frontmatter

---

## 哲学冲突判定

```mermaid
graph TB
    A[冲突发生] --> B{判定顺序}
    B --> C[1. Constitution]
    B --> D[2. Spec]
    B --> E[3. Contract]
    B --> F[4. Code]
    B --> G[5. 个人判断]
    
    C --> H[宪法优先]
    D --> I[规格优先]
    E --> J[契约优先]
    F --> K[代码次之]
    G --> L[最后考虑]
```

**冲突判定顺序**: Constitution > Spec > Contract > Code > 个人判断

---

## 哲学与宪法映射

```mermaid
graph LR
    P1[复用而非自研] --> A6[Ponytail First]
    P2[质量而非流程] --> A2[满分硬门禁]
    P3[验证而非信任] --> A10[异会话验证]
    P4[干净而非兼容] --> A3[零残留迁移]
    P6[诚实而非吹嘘] --> A12[文档诚实]
    P8[分层而非混置] --> A7[文档优先]
```

---

## 关联文档

- [宪法详细版](../references/constitution.md)
- [公共铁律](../references/common-iron-rules.md)
- [公共反例](../references/common-anti-patterns.md)