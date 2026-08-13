---
name: fullstack-03-test-plan
description: "Stage 0.5 测试覆盖映射 — 验收维度 → 测试用例，spec.md 测试覆盖映射。触发词：test plan / 测试计划 / 覆盖率 / 验收维度。"
stage: 0.5
parent: fullstack4traev11
depends_on:
  skills: [gitnexus4Trae]
  stages: [0/plan]
  references:
    - ../../references/state-card-protocol.md
    - ../../references/stage-interaction-protocol.md
    - ../../references/common-iron-rules.md
    - ../../references/common-anti-patterns.md
  scripts:
    - ../../scripts/stage-gate.py
---

# Stage 0.5 Test Plan — 测试覆盖映射

> 第一性原则：**验收维度决定测试覆盖，测试覆盖决定交付质量**。Test Plan 把 plan.md 的 Capabilities 拆解为可执行的测试用例。

## 边界

| Test Plan 处理 | Test Plan 不处理 |
|---------------|-----------------|
| 验收维度拆解 | 规格编写 → Stage 1 Spec |
| 覆盖率门槛设定 | 实施编码 → Stage 3 Implement |
| test-plan.md 产出 | 验收 → Stage 4 Review |

## 铁律（8 条）

```
1. 验收维度先于测试用例 — 没有验收维度就没有测试
2. 覆盖率门槛 ≥ 90% — 测试覆盖率硬门槛
3. E2E ≥ 2 / INV ≥ 1 / UNIT ≥ 5 — 最低测试组合
4. 测试用例可追溯 — 每条测试映射到 plan.md Capability
5. 测试在 spec 前 — test-plan.md 必在 spec.md 之前
6. 测试命名规范 — test_{module}_{scenario}_{expected}
7. NEVER 空测试 — 每个测试必有断言
8. NEVER 跳覆盖率门槛 — 覆盖率不达标不进入 Stage 1
```

## 委派触发词

**主上下文识别后加载**:
```
"test plan" / "测试计划" / "覆盖率" / "验收维度" / "测试用例"
```

## 骨架流程（5 步）

```
Step 1: 加载 plan.md → 识别 Capabilities（≤ 5 项）
Step 2: 验收维度拆解（每个 Capability 拆为 ≥ 3 验收维度）
Step 3: 测试用例映射（每个验收维度 → 至少 1 个测试用例）
Step 4: 覆盖率门槛校验（E2E/INV/UNIT 最低组合）
Step 5: 产出 test-plan.md + 状态卡更新
```

## 关键产物

| 产物 | 路径 | 模板 |
|------|------|------|
| test-plan.md | `docs/specs/changes/{id}/test-plan.md` | [templates/test-plan.md](templates/test-plan.md) |
| 状态卡 | `docs/specs/changes/{id}/.state-card.md` | — |

## 测试层级最低组合

| 层级 | 数量 | 说明 |
|------|:---:|------|
| **E2E** | ≥ 2 | 端到端流程测试 |
| **INV** | ≥ 1 | 不变量测试（数据一致性 / 安全约束） |
| **UNIT** | ≥ 5 | 单元测试（覆盖核心函数） |
| **总计** | ≥ 8 | 最低测试数量 |

## 覆盖率门槛

| 层级 | 门槛 | 不足处置 |
|------|:---:|---------|
| 行覆盖率 | ≥ 90% | Stage 1 Spec 标注"覆盖率不足"+ Stage 3 必补 |
| 分支覆盖率 | ≥ 85% | 同上 |
| 函数覆盖率 | ≥ 95% | 同上 |
| 关键路径 | 100% | 必须 E2E 覆盖 |

## 反模式（4 条）

| 反例 | 简述 | 详细 |
|------|------|------|
| 无验收维度直接测试 | 直接写测试 | [anti-patterns/01-no-acceptance-dimension.md](anti-patterns/01-no-acceptance-dimension.md) |
| 测试不可追溯 | 测试与 Capability 无映射 | [anti-patterns/02-test-not-traceable.md](anti-patterns/02-test-not-traceable.md) |
| 覆盖率门槛宽松 | < 90% 行覆盖率 | [anti-patterns/03-coverage-too-low.md](anti-patterns/03-coverage-too-low.md) |
| 跳过 E2E / INV | 只有 UNIT | [anti-patterns/04-skip-e2e.md](anti-patterns/04-skip-e2e.md) |

## 参考索引

| 资源 | 路径 |
|------|------|
| Stage 元信息 | [README.md](README.md) |
| 验收维度 → 测试用例工作流 | [workflows/coverage-mapping.md](workflows/coverage-mapping.md) |
| 覆盖率门槛规则 | [references/coverage-rules.md](references/coverage-rules.md) |
| test-plan.md 模板 | [templates/test-plan.md](templates/test-plan.md) |
