# Acceptance Checklist Template — Spec 完整性验证

<!--
  借鉴 spec-kit 理念：checklist 验证 spec 写得好不好，不是验证代码。
  用途：在 Stage 1 Spec 阶段产物完成后、Stage 2 Contract 阶段开始前，由 spec-writer 或 reviewer 逐项打勾。
  任何 ❌ 项 = 退回 spec-writer 修正。
  来源：V10 templates/checklist-template.md（4 维 × 多条 CHK-C 验证）。
-->

**功能**: {spec.md 链接 / 路径}
**审查人**: {reviewer/agent 名}
**审查时间**: {ISO_8601}
**V11 规则**: 4 维全部 ✅ = PASS；任一 ❌ = REJECT 整个 change

---

## 维度 1: 完整性 (Completeness) — 满分 5.0

<!-- 验证 spec 是否覆盖了必要结构 -->

- [ ] CHK-C01 每个 User Story 有 **Why this priority** 段
- [ ] CHK-C02 每个 User Story 有 **Independent Test** 段
- [ ] CHK-C03 每个 Acceptance Scenario 用 **Given/When/Then BDD 格式**
- [ ] CHK-C04 **Edge Cases ≥ 3 条**（边界/异常/并发/空值/超限）
- [ ] CHK-C05 **Success Criteria 可量化**（含具体数字/比例/时间）
- [ ] CHK-C06 Functional Requirements 全部用 FR-NNN 编号
- [ ] CHK-C07 涉及数据时填了 Key Entities 段
- [ ] CHK-C08 Why / What Changes 段都已填写（V11 Article V + V10 核心）
- [ ] CHK-C09 涉及 UI 时 **prototypes/** 目录已存在并与本 spec 引用
- [ ] CHK-C10 至少包含一个 **Happy Path + Error Case + Boundary** Scenario

**满分判定**: 10/10 勾选 = 5.0；每缺 1 项扣 0.5

---

## 维度 2: 可测试性 (Testability) — 满分 5.0

<!-- 验证 spec 是否可测试 -->

- [ ] CHK-T01 每个 FR-NNN 都有对应测试映射（test-plan.md §2 覆盖映射）
- [ ] CHK-T02 Edge Case 都有对应测试用例
- [ ] CHK-T03 Success Criteria 可测量（如"100ms 内返回" / "错误率 < 0.1%"）
- [ ] CHK-T04 P0 场景 100% 覆盖（test-plan.md §3 必填）
- [ ] CHK-T05 P1 场景 ≥ 80% 覆盖
- [ ] CHK-T06 契约测试骨架已生成（Stage 2 产物在 test-plan.md 中引用）

**满分判定**: 6/6 勾选 = 5.0；每缺 1 项扣 0.83

---

## 维度 3: 明确性 (Clarity) — 满分 5.0

<!-- 验证 spec 是否无歧义 -->

- [ ] CHK-X01 无 SHALL NOT 之外的模糊词（不能含 should/maybe/大概/可能/尽量）
- [ ] CHK-X02 所有 INV-XXX 在 spec.md 中实际定义（不是 state-card / INDEX.md 吹嘘）
- [ ] CHK-X03 涉及多模块时 contracts/api-contracts.md 已就位
- [ ] CHK-X04 BREAKING 变更已标 🔴 并附 BREAKING 流程说明
- [ ] CHK-X05 涉及安全/资金/数据完整性已标 CRITICAL 风险等级

**满分判定**: 5/5 勾选 = 5.0；每缺 1 项扣 1.0

---

## 维度 4: GitNexus 闭环 (GitNexus Loop) — 满分 5.0

<!-- 验证 GitNexus First 是否已走（V11 Article V） -->

- [ ] CHK-G01 已跑 GitNexus impact() 评估受影响 symbol 数量
- [ ] CHK-G02 risk_level 已标注（LOW / MEDIUM / HIGH / CRITICAL）
- [ ] CHK-G03 公共 API 必跑下游评估（≥10 调用者）
- [ ] CHK-G04 GitNexus 失败时已走 3 次重试协议（如失败）
- [ ] CHK-G05 plan.md Impact 段含 gitnexus_calls 数组（4 工具全用）

**满分判定**: 5/5 勾选 = 5.0；每缺 1 项扣 1.0

---

## 总分计算

```
总分 = Σ(各维度得分 × 权重)
- 完整性: 30%
- 可测试性: 30%
- 明确性: 20%
- GitNexus 闭环: 20%
```

| 维度 | 权重 | 得分 (0-5) |
|------|:---:|:---:|
| 完整性 | 30% | __ |
| 可测试性 | 30% | __ |
| 明确性 | 20% | __ |
| GitNexus 闭环 | 20% | __ |
| **总分** | **100%** | **__** |

---

## 判定标准

```
总分 ≥ 4.0 + 4 维全部 ≥ 3.0 = ✅ PASS
任一维度 < 3.0 = 🛑 REJECT
总分 < 4.0 = ⚠️ WARN（需用户决策）
```

---

## 反模式

### 反例 A：凑分

```
完整性 3.0 / 可测试性 2.0 / 明确性 4.0 / GitNexus 3.0 → 总分 3.0  # ❌ 可测试性 < 3.0
正确: 退回 spec-writer 补可测试性
```

### 反例 B：CHC-T01 测试映射造假

```
spec-writer: "FR-001 测在 tests/foo.test.ts:999"  # ❌ 实际不存在
正确: reviewer 必 glob 验证 ≥3 个 TS-{N}，行号不存在计入 REJECT
```

---

## 关联引用

- [references/constitution.md](../references/constitution.md) — V11 17 Articles
- [skills/04-spec/SKILL.md](../skills/04-spec/SKILL.md) — Stage 1 Spec
- [skills/03-test-plan/SKILL.md](../skills/03-test-plan/SKILL.md) — Stage 0.5 Test Plan
- V10 来源（开发期，已蒸馏）：见 V11 references 与 anti-patterns