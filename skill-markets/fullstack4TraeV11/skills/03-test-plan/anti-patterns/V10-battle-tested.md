# V10 实战蒸馏（Battle-Tested Patterns）

> Stage 0.5 Test Plan 从 V10 acceptance-gates-v10.md + scenarios.md §3 蒸馏。

---

## V10 实战反例（3 条）

### 蒸馏 1：验收维度无 INV（V10 acceptance-gates-v10.md 实战）

**实战场景**（V10 蒸馏）:
- planner 出 plan.md：3 个 Capability
- 测试人员直接写 UNIT 测试，无 INV（数据一致性 / 安全约束）
- Stage 4 Review 时 reviewer 发现"事务回滚无测试" → 返工

**根因**: Test Plan 未明确 INV 测试层级（与 UNIT/E2E 平级的独立维度）。

**V11 改进**: 铁律 3（INV ≥ 1）+ 测试层级最低组合（E2E ≥ 2 / INV ≥ 1 / UNIT ≥ 5）+ coverage-mapping.md 验收维度类型表。

**V10 源**: acceptance-gates-v10.md §验收维度 + INV。

---

### 蒸馏 2：测试覆盖率被"放宽"（V10 实战）

**实战场景**（V10 蒸馏）:
- Stage 0.5 test-plan.md 标注"行覆盖率 ≥ 70%"
- Stage 4 Review 时 reviewer 不质疑（"70% 也行"）
- Stage 3 Implement 后实际覆盖率 65% → 上线后 bug

**根因**: V10 早期测试覆盖率门槛"可商量"。

**V11 改进**: 铁律 2（覆盖率门槛 ≥ 90% 硬门槛）+ 反例 3（覆盖率门槛宽松）+ coverage-rules.md 硬门槛表（不可豁免）。

**V10 源**: acceptance-gates-v10.md Article II 满分硬门禁。

---

### 蒸馏 3：测试与 Capability 脱节（V10 实战）

**实战场景**（V10 蒸馏）:
- 测试人员写 50 个 UNIT 测试，但未标注对应 Capability
- 测试失败时 reviewer 无法定位"哪个能力未实现"

**根因**: 无 test_to_capability 映射表。

**V11 改进**: 铁律 4（测试用例可追溯）+ 反例 2（测试不可追溯）+ coverage-mapping.md Step 3 模板。

**V10 源**: acceptance-gates-v10.md §通过依据 3 类分层 + sub-agent-rules.md。

---

## V10 实战蒸馏经验（3 条）

| 经验 | V10 来源 | V11 落地位置 |
|------|---------|------------|
| INV ≥ 1（与 UNIT/E2E 平级） | acceptance-gates-v10.md | 铁律 3 + 测试层级最低组合 |
| 覆盖率硬门槛 ≥ 90% | Article II 满分硬门禁 | 铁律 2 + 反例 3 |
| test_to_capability 映射 | sub-agent-rules.md | 铁律 4 + coverage-mapping.md Step 3 |

---

## V10 来源溯源（开发期，部署前可删）

> ⚠️ 本节记录 V10 来源，仅供 V11 维护者追溯。**V11 部署时不依赖 V10**——V10 内容已蒸馏进 V11 references/anti-patterns。

| V10 来源 | 蒸馏到 V11 位置 |
|---------|---------------|
| V10 acceptance-gates-v10.md（4 维评分 + 证据链） | → `../../03-test-plan/references/coverage-rules.md` + `../../09-review/references/four-dimension-scoring.md` + `evidence-3-layer.md` |
| V10 scenarios.md §3 | → 本文档蒸馏 1+2+3 |
| V10 sub-agent-rules.md | → 主上下文委派纪律 + test_to_capability 映射 |

---

## 关联引用

- [SKILL.md](../SKILL.md) | [README.md](../README.md) | [coverage-mapping.md](../workflows/coverage-mapping.md) | [coverage-rules.md](../references/coverage-rules.md)
- 其他反例: [01-no-acceptance-dimension.md](01-no-acceptance-dimension.md) / [02-test-not-traceable.md](02-test-not-traceable.md) / [03-coverage-too-low.md](03-coverage-too-low.md) / [04-skip-e2e.md](04-skip-e2e.md)
