# Document Layer — 4 层文档架构

> **V12.0.0+ 设计入口**: [AC 核销门禁](../skills/09-review/SKILL.md) · [贾维斯门禁守护](../skills/00-boot/SKILL.md) · 评分制废除 → 门禁制 · 详见 [CHANGELOG.md V12.0.0](../CHANGELOG.md)


> V12.0.0 文档分层规范。Stage 1 Spec / Stage 5 Accept 必读。

---

## V12 物理映射(V12.0.0 NEW — 主版本升级后强制)

> **来源**:[references/todos/v12-physical-isolation/V12-ADR-DRAFT.md](../todos/v12-physical-isolation/V12-ADR-DRAFT.md) §4.3 + [templates/change-dir-layout-v12-preview.md](../../templates/change-dir-layout-v12-preview.md)
>
> **V12 默认行为**:4 层文档(Layer 1-4)落到 `fact/` 目录物理子目录;13 stage 流程产物落到 `stage/{N}/` 物理子目录。

```
V12 物理布局(V12.0.0 默认)
docs/specs/changes/{change-id}/
├── fact/                                  # 4 层文档物理映射(V12 强制)
│   ├── spec.md                            # Layer 1: AC / INV / Edge Cases
│   ├── plan.md                            # Layer 2: Capabilities / Non-Goals
│   ├── prototype.md                       # Stage 1.5 产物(可选)
│   ├── test-plan.md                        # Stage 0.5 产物
│   └── contracts/                         # Layer 3: 契约 4 件套
│       ├── domain-models.md
│       ├── api-contracts.md
│       ├── events.md
│       └── validation-rules.md
├── stage/                                 # 13 stage 流程产物(可重置,V12 §2)
│   ├── -1/intake/{intake-notes, handoff-out}.md
│   ├── 0/plan/{plan-notes, handoff-out}.md
│   ├── 0.5/test-plan/{test-plan-notes, handoff-out}.md
│   ├── 1/spec/{spec-notes, handoff-out}.md
│   ├── 1.5/prototype/{prototype-notes, handoff-out}.md
│   ├── 2/contract/{contract-notes, handoff-out}.md
│   ├── 3/implement/{impl-notes, handoff-out}.md
│   ├── 3.5/real-verify/{verify-notes, handoff-out}.md
│   ├── 4/review/{review-notes, handoff-out}.md
│   ├── 4.5/rot-scan/{rot-notes, handoff-out}.md
│   └── 5/accept/{accept-notes, handoff-out}.md
└── archive/                               # Stage 5 完成后写入(V12 不可变)
```

**映射规则**:
- `fact/` = 4 层文档物理落位(Layer 1/2/3 + Stage 0.5/1.5 产物)
- `stage/{N}/` = 13 stage 流程产物(N-1 → 0 → 0.5 → ... → 5)
- `archive/` = Stage 5 完成后写入(Article VIII 不可变)
- 主上下文项目级 `.state-card.md` → 副本到 `fact/.state-card.md`(只读)

**V11 兼容(V11.8.7.1 已废弃)**:既有 V11 项目必须用 `--migrate-from-v11` 升级到 V12 layout,`init-from-zero.py --layout` 不再支持 v11-default(仅 v12-preview)。

**强制校验**:[templates/hooks/process-layer-guard.sh](../../templates/hooks/process-layer-guard.sh) 3 规则:
- Rule 1: `docs/specs/changes/{id}/` 根目录禁止任何 .md
- Rule 2: `fact/` 禁止 process 层命名(`*-notes.md` / `*handoff*.md` / `diagnosis-*` / `fix-*` / `v[0-9]*`)
- Rule 3: `stage/{N}/` 禁止 fact 层命名(`spec.md` / `plan.md` / `contracts/`)

---

## 4 层文档（V12 物理布局,V12.0.0 主版本升级后强制）

```
Layer 1: SPEC（什么是 / 为什么）
  └─ docs/specs/changes/{id}/fact/spec.md   (V12 fact/ 物理布局)
  └─ 描述 AC / INV / Edge Cases

Layer 2: PLAN（怎么实现）
  └─ docs/specs/changes/{id}/fact/plan.md   (V12 fact/ 物理布局)
  └─ 描述 Capabilities / Non-Goals / 决策记录

Layer 3: CONTRACT（接口真相）
  └─ docs/specs/changes/{id}/fact/contracts/{domain-models,api-contracts,events,validation-rules}.md
  └─ 不可变接口定义(V12 fact/contracts/ 物理布局)

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
| TEST ↔ CONTRACT | 测试覆盖 CONTRACT 接口（V12 沿用 V11 §5 全场景）|

**违反一致性 = rot #1 spec drift** → V12 §4.5 腐化扫描

---

## 归档层级（Stage 5 Accept,V12 物理布局保留）

V12 spec-purge.py `archive_keep_v12_layout()` 自动 1:1 保留 `fact/` + `stage/{N}/` 物理布局,**不展平**：

```
docs/archive/done/{change-id}/
├── _module.md         (项目级模块真相源,从 docs/specs/changes/_module.md 复制)
├── fact/              (V12 物理布局保留)
│   ├── spec.md        (Layer 1)
│   ├── plan.md        (Layer 2)
│   ├── test-plan.md   (Stage 0.5)
│   ├── prototype.md   (Stage 1.5)
│   ├── module.md      (change 级模块声明)
│   └── contracts/     (Layer 3)
│       ├── domain-models.md
│       ├── api-contracts.md
│       ├── events.md
│       └── validation-rules.md
└── stage/             (V12 物理布局保留)
    ├── -1/intake/{intake-notes,handoff-out}.md + .state-card.md
    ├── 0/plan/{plan-notes,handoff-out}.md + .state-card.md
    ├── 0.5/test-plan/{test-plan-notes,handoff-out}.md + .state-card.md
    ├── 1/spec/{spec-notes,handoff-out}.md + .state-card.md
    ├── 1.5/prototype/{prototype-notes,handoff-out}.md + .state-card.md
    ├── 2/contract/{contract-notes,handoff-out}.md + .state-card.md
    ├── 3/implement/{impl-notes,handoff-out}.md + .state-card.md
    ├── 3.5/real-verify/{verify-notes,handoff-out}.md + .state-card.md
    ├── 4/review/{review-notes,handoff-out}.md + .state-card.md
    ├── 4.5/rot-scan/{rot-scan-{date}.md,handoff-out}.md + .state-card.md
    └── 5/accept/{accept-notes,handoff-out}.md + .state-card.md
```

**V12 强制行为**: `archive_keep_v12_layout()` copytree 1:1 保留物理布局,不得展平(展平函数 `flatten_v12_to_v11_layout` 已废)。

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

正确: 走 BREAKING 流程（V12 沿用 V11 §6.3 Article III）。

---

## 关联引用

- [stage-card-protocol.md](state-card-protocol.md) — 4 层流转
- [common-iron-rules.md](common-iron-rules.md) — Article VIII archive immutable
- V10 来源（开发期，已蒸馏）：见 V11 references 与 anti-patterns
