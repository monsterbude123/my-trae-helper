# Document Layer — 4 层文档架构

> V11 文档分层规范。Stage 1 Spec / Stage 5 Accept 必读。

---

## 4 层文档

```
Layer 1: SPEC（什么是 / 为什么）
  └─ docs/specs/changes/{id}/spec.md
  └─ 描述 AC / INV / Edge Cases

Layer 2: PLAN（怎么实现）
  └─ docs/specs/changes/{id}/plan.md
  └─ 描述 Capabilities / Non-Goals / 决策记录

Layer 3: CONTRACT（接口真相）
  └─ docs/specs/changes/{id}/contracts/{domain-models,api-contracts,events,validation-rules}.md
  └─ 不可变接口定义

Layer 4: IMPLEMENT（已写代码）
  └─ src/{module}/{file}.{ts,py,rs}
  └─ 实际代码
```

---

## 流转关系

```
SPEC ──→ PLAN ──→ CONTRACT ──→ IMPLEMENT
  │        │         │             │
  │        │         │             ↓
  │        │         └──→ Contract Test
  │        │               (sync with contract)
  │        │
  │        └──→ Test Plan (Stage 0.5)
  │
  └──→ Prototype (Stage 1.5)
```

---

## 一致性要求

| Layer | 与上层一致 |
|-------|----------|
| PLAN ↔ SPEC | Capabilities 全部满足 SPEC INV |
| CONTRACT ↔ PLAN | 接口覆盖所有 PLAN capabilities |
| IMPLEMENT ↔ CONTRACT | 实现严格匹配 CONTRACT 接口 |
| TEST ↔ CONTRACT | 测试覆盖 CONTRACT 接口（V11 §5 全场景）|

**违反一致性 = rot #1 spec drift** → V11 §4.5 腐化扫描

---

## 归档层级（Stage 5 Accept）

```
docs/archive/done/{change-id}/
├── spec.md            (Layer 1)
├── plan.md            (Layer 2)
├── contracts/         (Layer 3)
│   ├── domain-models.md
│   ├── api-contracts.md
│   ├── events.md
│   └── validation-rules.md
├── review-report.md   (Stage 4)
├── rot-scan-{date}.md (Stage 4.5)
└── verify-report.md   (Stage 3.5)
```

---

## 反例

### 反例 1：跳 PLAN 直接 SPEC

```
实施: SPEC → CONTRACT → CODE  # ❌ 跳 PLAN
正确: SPEC → PLAN → CONTRACT → CODE
```

### 反例 2：CONTRACT 包含未来接口

```
CONTRACT:
  - /api/v1/auth/login  # 当前实现
  - /api/v1/auth/sso    # 未来接口，未实现
```

后果: 验证覆盖率低 + rot #12 孤儿测试。

正确: DELTA ONLY（仅写当前 change 必需的接口）。

### 反例 3：IMPLEMENT 与 CONTRACT 漂移

```
CONTRACT: create_user(name, email)
CODE:     create_user(name, email, role)  # ❌ 加了未在契约的字段
```

正确: 走 BREAKING 流程（V11 §6.3 Article III）。

---

## 关联引用

- [stage-card-protocol.md](state-card-protocol.md) — 4 层流转
- [common-iron-rules.md](common-iron-rules.md) — Article VIII archive immutable
- V10 来源（开发期，已蒸馏）：见 V11 references 与 anti-patterns