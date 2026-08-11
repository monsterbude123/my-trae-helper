# 文档分层（fact / process / log）

> 三层文档标注协议。解决"子代理误读过程文档作为任务输入"的问题。

---

## 分层总览

```mermaid
mindmap
  root((文档分层))
    fact层
      真相源
      契约规格
      子代理必读
    process层
      过程产物
      诊断手记
      子代理禁读
    log层
      历史快照
      操作日志
      可读但不验收
```

---

## 三层定义

```mermaid
graph TB
    subgraph fact层_真相源
        A1[宪法]
        A2[架构]
        A3[契约]
        A4[规格]
        A5[模块文档]
    end
    
    subgraph process层_过程产物
        B1[诊断手记]
        B2[修复记录]
        B3[调试草稿]
        B4[Bug草稿]
    end
    
    subgraph log层_历史快照
        C1[历史报告]
        C2[变更日志]
        C3[归档版本]
        C4[Commit log]
    end
    
    A1 --> D[✅ 子代理必读]
    B1 --> E[❌ 子代理禁读]
    C1 --> F[⚠️ 可读但不验收]
    
    style A1 fill:#9f9
    style B1 fill:#f66
    style C1 fill:#ff9
```

---

## 子代理可读性

```mermaid
graph LR
    A[fact层] --> B[✅ 必读]
    B --> B1[任务输入]
    B --> B2[验收依据]
    
    C[process层] --> D[❌ 禁读]
    D --> D1[不作验收依据]
    D --> D2[不回流到spec]
    
    E[log层] --> F[⚠️ 可读]
    F --> F1[历史参考]
    F --> F2[不作验收依据]
    
    style B fill:#9f9
    style D fill:#f66
    style F fill:#ff9
```

---

## 目录 layer 映射表

### fact 目录

```mermaid
graph TB
    subgraph fact目录
        A[docs/constitution.md]
        B[docs/ARCHITECTURE.md]
        C[docs/INDEX.md]
        D[docs/api-endpoints/]
        E[docs/domain-models/]
        F[docs/events/]
        G[docs/contracts/]
        H[docs/modules/]
        I[AGENTS.md]
        J[docs/specs/changes/{id}/spec.md]
        K[docs/specs/changes/{id}/contracts/*.md]
        L[docs/bugs/{id}.md]
        M[.trae/rules/]
    end
    
    style A fill:#9f9
    style B fill:#9f9
    style C fill:#9f9
```

### process 目录

```mermaid
graph TB
    subgraph process目录
        A[docs/bugs/{id}-draft.md]
        B[docs/bugs/{id}/reproduction.md]
        C[docs/bugs/{id}/root-cause.md]
        D[.trae/tmp/]
        E[.trae/logs/agent-detail/]
        F[diagnose.md]
        G[fix_result.md]
        H[analysis.md]
        I[_invalidated/]
    end
    
    style A fill:#f66
    style B fill:#f66
    style C fill:#f66
```

### log 目录

```mermaid
graph TB
    subgraph log目录
        A[docs/changelog.md]
        B[docs/history/]
        C[docs/reports/]
        D[docs/specs/archive/]
        E[docs/archive/]
        F[docs/reports/review-latest.md]
        G[docs/reports/doc-sync-latest.md]
    end
    
    style A fill:#ff9
    style B fill:#ff9
    style C fill:#ff9
```

---

## 判定规则

```mermaid
flowchart TB
    A[文档判定] --> B{是真相源?}
    B -->|是| C[fact层]
    B -->|否| D{是过程产物?}
    
    D -->|是| E[process层]
    D -->|否| F{是历史快照?}
    
    F -->|是| G[log层]
    F -->|否| H[默认process]
    
    C --> C1[标注: layer: fact]
    E --> E1[标注: layer: process]
    G --> G1[标注: layer: log]
    H --> H1[无标注 = process]
    
    style C fill:#9f9
    style E fill:#f66
    style G fill:#ff9
```

---

## 子代理 DOC_WHITELIST 协议

### 委派头部模板

```yaml
[DOC_WHITELIST]
  # 必读路径（fact层）
  - docs/constitution.md
  - docs/ARCHITECTURE.md
  - docs/INDEX.md
  - docs/specs/changes/{change-id}/spec.md
  - docs/specs/changes/{change-id}/contracts/api-contracts.md

[FORBIDDEN]
  # 禁读路径（process / log层）
  - docs/bugs/{bug-id}-draft.md
  - .trae/tmp/*.md
  - docs/reports/archive/**
  - docs/archive/**
```

### 委派前检查

```mermaid
flowchart TB
    A[委派前自检] --> B[DOC_WHITELIST全是fact层?]
    A --> C[FORBIDDEN覆盖所有process/log?]
    A --> D[是否漏列docs/bugs/?]
    A --> E[是否漏列docs/archive/?]
    A --> F[是否漏列.trae/tmp/?]
    
    B --> G{全部通过?}
    C --> G
    D --> G
    E --> G
    F --> G
    
    G -->|是| H[✅ 允许委派]
    G -->|否| I[❌ 补充FORBIDDEN]
    
    style H fill:#9f9
    style I fill:#f66
```

---

## 归档路径防护

```mermaid
graph TB
    subgraph 归档黑名单
        A[docs/archive/out/stub-pileup/**]
        B[docs/archive/out/spec-purge/**]
        C[docs/archive/bak_v8doc/**]
        D[docs/reports/review-latest.md]
        E[docs/reports/doc-sync-latest.md]
        F[docs/bugs/{id}-draft.md]
        G[.trae/tmp/*.md]
        H[.trae/logs/agent-detail/**]
    end
    
    A --> I[❌ 默认FORBIDDEN]
    B --> I
    C --> I
    D --> I
    E --> I
    F --> I
    G --> I
    H --> I
    
    style I fill:#f66
```

---

## archaeology-mode 例外

```mermaid
flowchart TB
    A[任务动词] --> B{∈ 调研/考古/查历史/research/archaeology?}
    B -->|是| C[允许读归档路径]
    B -->|否| D[❌ 禁止读归档]
    
    C --> E[返回产物必须标注]
    E --> F[来源: archive路径]
    E --> G[性质: HISTORICAL-REFERENCE-ONLY]
    E --> H[限制: NOT-ACCEPTANCE-EVIDENCE]
    
    style C fill:#9f9
    style D fill:#f66
```

---

## 文档分层反例

```mermaid
graph TB
    subgraph 反例1_漂移未回流
        A1[现象: spec写A代码做B]
        A2[根因: 不知道文档优先]
        A3[教训: 漂移→先改spec再改代码]
    end
    
    subgraph 反例2_子代理读process
        B1[现象: 读Bug草稿作输入]
        B2[根因: 不区分文档分层]
        B3[教训: 委派头部含DOC_WHITELIST]
    end
    
    subgraph 反例3_状态卡无layer
        C1[现象: 状态卡无layer标签]
        C2[根因: 不知道状态卡也需分层]
        C3[教训: 状态卡是fact层]
    end
    
    subgraph 反例4_归档被修改
        D1[现象: 尝试修改归档代码]
        D2[根因: 不知道归档不可变]
        D3[教训: 归档是冻结快照]
    end
    
    subgraph 反例5_草稿被读
        E1[现象: 读诊断草稿作结论]
        E2[根因: 不知道draft是process层]
        E3[教训: 草稿不可作验收依据]
    end
    
    style A1 fill:#f66
    style B1 fill:#f66
    style C1 fill:#f66
    style D1 fill:#f66
    style E1 fill:#f66
```

---

## Layer 标签覆盖率

```mermaid
graph TB
    A[覆盖率计算] --> B[含layer字段md文件数]
    A --> C[总md文件数]
    
    B --> D[覆盖率 = B / C]
    
    D --> E{覆盖率阈值}
    E -->|≥ 80%| F[✅ 健康]
    E -->|60-80%| G[⚠️ 警告]
    E -->|< 60%| H[❌ REJECT]
    
    style F fill:#9f9
    style G fill:#ff9
    style H fill:#f66
```

---

## 关联文档

- [文档分层详细版](../references/document-layer.md)
- [宪法 Article VII](../references/constitution.md)
- [公共铁律](../references/common-iron-rules.md)