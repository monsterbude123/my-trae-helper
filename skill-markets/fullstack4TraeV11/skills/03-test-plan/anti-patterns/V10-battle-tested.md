# V10 实战蒸馏（Battle-Tested Patterns）

> Stage 0.5 Test Plan 从 V10 acceptance-gates-v10.md + scenarios.md §3 蒸馏。

---

## V10 实战反例（3 条，均完全重叠于独立反例文件）

| # | 蒸馏主题 | 反例文件指针 |
|---|---------|------------|
| 蒸馏 1 | 验收维度无 INV（INV 测试层级缺失，与 UNIT/E2E 平级） | → 见 [01-no-acceptance-dimension.md](01-no-acceptance-dimension.md) |
| 蒸馏 2 | 测试覆盖率被"放宽"（70% 门槛可商量） | → 见 [03-coverage-too-low.md](03-coverage-too-low.md) |
| 蒸馏 3 | 测试与 Capability 脱节（无 test_to_capability 映射） | → 见 [02-test-not-traceable.md](02-test-not-traceable.md) |

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
