# Stage 2 Contract — 契约四件套

> 契约是不可变的接口真相，先于实现。

---

## 阶段总览

```mermaid
mindmap
  root((Stage 2 Contract))
    核心职责
      领域模型定义
      API契约编写
      事件定义
      校验规则
    四件套
      domain-models.md
      api-contracts.md
      events.md
      validation-rules.md
    变更类型
      ADDITIVE新增
      BREAKING破坏
```

---

## 第一性原则

```mermaid
graph TB
    A[第一性原则] --> B[契约是不可变的接口真相]
    A --> C[先于实现]
    
    B --> D[approved后不可单方面改]
    C --> E[无契约不写代码]
    
    style B fill:#f66
```

---

## 契约四件套

```mermaid
graph TB
    A[contracts/] --> B[domain-models.md<br/>领域模型]
    A --> C[api-contracts.md<br/>API契约]
    A --> D[events.md<br/>事件定义]
    A --> E[validation-rules.md<br/>校验规则]
    
    B --> B1[先于接口]
    C --> C1[接口签名]
    D --> D1[事件契约]
    E --> E1[校验规则]
    
    style B fill:#f9f
    style B1 fill:#f9f
```

---

## 骨架流程（5 步）

```mermaid
flowchart TB
    A[Step 1: 读上游] --> B[Step 2: domain-models.md]
    B --> C[Step 3: api-contracts.md<br/>+ events.md<br/>+ validation-rules.md]
    C --> D[Step 4: orphan-detector.py]
    D --> E[Step 5: contract-gate.py]
    
    B --> B1[先于接口]
    D --> D1[清理孤儿契约测试]
    E --> E1[验证四件套齐全]
    
    style B fill:#f9f
```

---

## DOMAIN FIRST 原则

```mermaid
sequenceDiagram
    participant Spec as spec.md
    participant Domain as domain-models.md
    participant API as api-contracts.md
    participant Code as 代码
    
    Spec->>Domain: 需求 → 领域模型
    Domain->>API: 模型 → 接口签名
    API->>Code: 契约 → 实现
    
    Note over Domain: 先定领域模型
    Note over API: 再定接口
    Note over Code: 无契约不写代码
```

---

## ADDITIVE / BREAKING 变更流程

```mermaid
flowchart TB
    A[契约变更] --> B{变更类型}
    
    B --> C[ADDITIVE<br/>新增可选字段/接口]
    B --> D[BREAKING<br/>删字段/改类型/改路径]
    
    C --> E[直接添加 + 通知]
    E --> F[版本: minor]
    
    D --> G[必用户确认]
    G --> H[版本: major]
    
    style D fill:#f66
    style G fill:#f9f
```

---

## 孤儿契约测试清理

```mermaid
flowchart TB
    A[写新契约前] --> B[orphan-detector.py]
    B --> C[扫描契约测试]
    
    C --> D{存在孤儿测试?}
    D -->|是| E[列出孤儿列表]
    D -->|否| F[继续写新契约]
    
    E --> G[删除孤儿测试]
    G --> F
    
    style B fill:#f9f
```

---

## 三方同步（THREE-WAY SYNC）

```mermaid
graph TB
    A[契约修改] --> B[代码层]
    A --> C[契约文档层]
    A --> D[测试层]
    
    B --> B1[services.rs / handlers.rs]
    C --> C1[api-contracts.md<br/>+ validation-rules.md]
    D --> D1[契约测试 + 单元测试]
    
    B1 --> E[必须同步修改]
    C1 --> E
    D1 --> E
    
    style E fill:#f66
```

---

## 10 条铁律

```mermaid
graph TB
    subgraph 契约不变性
        A1[1. CONTRACT IS IMMUTABLE<br/>approved后不可单方面改]
        A2[7. NO CODE NO CONTRACT<br/>无契约不写代码]
    end
    
    subgraph 顺序铁律
        B1[2. DOMAIN FIRST<br/>先定领域模型再定接口]
    end
    
    subgraph 清理铁律
        C1[3. ORPHAN TEST SWEEP<br/>写新契约前清理孤儿]
    end
    
    subgraph 变更铁律
        D1[4. ADDITIVE OVER BREAKING<br/>优先加法变更]
        D2[5. DELTA ONLY<br/>只写增量]
    end
    
    subgraph 同步铁律
        E1[9. THREE-WAY SYNC<br/>契约修改必3处同步]
    end
    
    style A1 fill:#f66
    style B1 fill:#f9f
```

---

## 契约模板

### domain-models.md

```markdown
# 领域模型 — {Change Name}

## 核心实体

### User
- id: string (UUID)
- name: string (≤ 100 chars)
- email: string (email format)
- created_at: datetime (ISO 8601)

## 关系图

```mermaid
graph LR
    User --> Order
    Order --> Product
```
```

### api-contracts.md

```markdown
# API 契约 — {Change Name}

## POST /api/users

### Request
```json
{
  "name": "string",
  "email": "string"
}
```

### Response (201)
```json
{
  "id": "string",
  "name": "string",
  "email": "string",
  "created_at": "string"
}
```

### Errors
- 400: Validation error
- 409: Email already exists
```

---

## 交接物 4 件套

```yaml
hand_over:
  stage_id: "2/contract"
  stage_skill: skills/06-contract/SKILL.md
  status: completed
  health: "🟢 on-track"
  artifacts:
    - path: docs/specs/changes/{id}/contracts/domain-models.md
      type: file
      evidence: "领域模型定义 + INV"
    - path: docs/specs/changes/{id}/contracts/api-contracts.md
      type: file
      evidence: "API契约 + 错误码"
    - path: docs/specs/changes/{id}/contracts/events.md
      type: file
      evidence: "事件定义"
    - path: docs/specs/changes/{id}/contracts/validation-rules.md
      type: file
      evidence: "校验规则 + regex"
  gate_result:
    status: PASS
    gate: contract-gate.py
    output: "四件套齐全 + 测试骨架PASS"
  next_stage:
    id: "3/implement"
    skill_name: skills/07-implement/SKILL.md
    expected_inputs: [contracts/ 四件套]
    prerequisites: [contract-gate PASS]
```

---

## 4 条反模式

```mermaid
graph TB
    subgraph 反模式
        A[1. 跳过DOMAIN FIRST]
        B[2. 跳过孤儿清理]
        C[3. BREAKING不确认]
        D[4. 契约漂移]
    end
    
    A --> A1[❌ 直接写API]
    B --> B1[❌ 孤儿测试残留]
    C --> C1[❌ 破坏变更不用户确认]
    D --> D1[❌ 代码与契约不一致]
    
    style A fill:#f66
    style C fill:#f66
    style D fill:#f66
```

---

## 关联文档

- [契约四件套详细规则](../skills/06-contract/references/contract-four-suite.md)
- [孤儿测试扫描](../skills/06-contract/references/orphan-test-sweep.md)
- [契约模板目录](../skills/06-contract/templates/)
- [V10实战参考](../skills/06-contract/anti-patterns/V10-battle-tested.md)