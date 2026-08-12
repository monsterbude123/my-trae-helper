---
name: spec
description: "Stage 1 规格增强 + 验收维度 — Spec 是真相源，验收维度决定交付质量。Enhanced Acceptance + INV ≥1 + E2E ≥2 + clarify ≥2 轮。触发词：spec / 规格 / 验收维度 / invariants。"
stage: 1
parent: fullstack4traev11
depends_on:
  skills: []
  stages: [0.5/test-plan]
  references:
    - ../../references/state-card-protocol.md
    - ../../references/stage-interaction-protocol.md
    - ../../references/constitution.md
  scripts:
    - ../../scripts/stage-gate.py
---

# Stage 1 Spec — 规格增强 + 验收维度

> 第一性原则：**Spec 是真相源，验收维度决定交付质量**。Spec 必含 Enhanced Acceptance + Invariants + 澄清历史。

## 边界

| Spec 处理 | Spec 不处理 |
|----------|-----------|
| 验收维度增强 | 项目探索 → Stage 0 Plan |
| 不变量（INV）定义 | 实施编码 → Stage 3 Implement |
| 澄清清单 + 历史 | 验收 → Stage 4 Review |
| spec.md 产出 | 测试覆盖 → Stage 0.5 Test Plan |

## 铁律（10 条）

```
1. SPEC IS TRUTH     — Spec 是真相源，代码为规格服务
2. E2E ≥ 2            — 至少 2 个端到端验收维度
3. INV ≥ 1            — 至少 1 个不变量（数据一致性 / 安全 / 业务规则）
4. ACCEPTANCE ≥ 3     — 至少 3 个验收维度（每个 Capability）
5. CLARIFY ≥ 2 ROUNDS  — 至少 2 轮澄清（防止单向理解）
6. NEVER 凭空 INV     — INV 必基于业务规则，不臆造
7. NEVER 写实施       — spec.md 不写代码细节
8. DRIFT → SPEC FIRST — 代码与 spec 漂移时先改 spec
9. DOC HONEST         — spec.md INV 必在 Stage 4 落地
10. SKEPTICAL          — P0/P1 spec 按 [skeptical-validation-protocol.md](../references/skeptical-validation-protocol.md) 质疑性校验
```

## 委派触发词

**主上下文识别后加载**:
```
"spec" / "规格" / "验收维度" / "invariants" / "acceptance criteria"
```

## 骨架流程（6 步）

```
Step 1: 加载 plan.md + test-plan.md → 识别 Capabilities + 测试覆盖
Step 2: Enhanced Acceptance — 每个 Capability 拆 ≥ 3 验收维度（E2E ≥ 2）
Step 3: INV 定义 — ≥ 1 不变量（数据 / 安全 / 业务）
Step 4: Clarify ≥ 2 轮 — AskUserQuestion 澄清模糊点
Step 5: spec.md 产出 — Why / Acceptance / INV / Non-Goals / Clarify History
Step 6: 状态卡更新 + validator PASS + **updated_at 必刷新**(腐烂点 16 阈值 24h,详见 [references/state-card-stage1-fields.md](references/state-card-stage1-fields.md))
```

## 关键产物

| 产物 | 路径 | 模板 |
|------|------|------|
| spec.md | `docs/specs/changes/{id}/spec.md` | [templates/spec-template.md](templates/spec-template.md) |
| ac_list.md | `docs/specs/changes/{id}/ac_list.md` | 从 spec.md §Capabilities §Acceptance Criteria 提取(纯 AC 列表,结构化移交下游) |
| edge_cases.md | `docs/specs/changes/{id}/edge_cases.md` | 从 spec.md §INV 边界提取(供 Stage 1.5 Prototype + Stage 2 Contract 引用) |
| 状态卡 | `docs/specs/changes/{id}/.state-card.md` | [references/state-card-stage1-fields.md](references/state-card-stage1-fields.md) |

## Enhanced Acceptance 规则

每个 Capability 必含：
- **≥ 3 Acceptance Criteria**（功能 / 边界 / 异常）
- **≥ 1 E2E 场景**（端到端流程）
- **可测试**（每个 AC 必可被一条测试覆盖）

## INV 定义规则

不变量（Invariants）= 任何时候都成立的规则：
- 数据一致性（事务原子性）
- 安全约束（认证必在授权前）
- 业务规则（订单总额 = 单价 × 数量）

**MUST**: INV 必基于业务规则，不臆造。

## Clarify ≥ 2 轮协议

```
Round 1: AskUserQuestion 列出 ≥ 3 模糊点 → 用户答
Round 2: 基于 Round 1 回答追问更深层 → 用户答
（每轮 < 4 题，避免疲劳）
```

**反模式**: 单轮猜意图 = 违反 V10.16 禁止编造抽象理由。

## 反模式（3 条索引到 anti-patterns/）

| 反例 | 简述 |
|------|------|
| INV 凭空臆造 | 不基于业务规则 |
| Clarify 跳过 | 单轮就写 spec |
| Spec 写实施 | 写代码细节而非规格 |

## 参考索引

| 资源 | 路径 |
|------|------|
| Stage 元信息 | [README.md](README.md) |
| Enhanced Acceptance 规则 | [references/acceptance-enhancement.md](references/acceptance-enhancement.md) |
| Clarify 检查清单 | [references/clarify-checklist.md](references/clarify-checklist.md) |
| spec.md 模板 | [templates/spec-template.md](templates/spec-template.md) |
| 公共铁律 Article VII | [../../references/common-iron-rules.md](../../references/common-iron-rules.md) |
