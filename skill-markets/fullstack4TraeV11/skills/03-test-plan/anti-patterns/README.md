# Anti-patterns — Stage 0.5 Test Plan 反例库

> **V11.7.0+ 设计入口**: [AC 核销门禁](../skills/09-review/SKILL.md) · [贾维斯门禁守护](../skills/00-boot/SKILL.md) · 评分制废除 → 门禁制 · 详见 [CHANGELOG.md V11.7.0](../CHANGELOG.md)


> 4 条核心反例 + 1 份 V10 实战蒸馏(2 条战役反例) + 主上下文自检清单。

## 反例索引

| # | 反例 | 文件 | 来源 |
|:---:|------|------|------|
| 1 | 无验收维度直接测试 | [01-no-acceptance-dimension.md](01-no-acceptance-dimension.md) | 理论分类 |
| 2 | 测试不可追溯 | [02-test-not-traceable.md](02-test-not-traceable.md) | 理论分类 |
| 3 | 覆盖率门槛宽松 | [03-coverage-too-low.md](03-coverage-too-low.md) | 理论分类 |
| 4 | 跳过 E2E / INV | [04-skip-e2e.md](04-skip-e2e.md) | 理论分类 |
| 5 | 假装 100% 覆盖 | [V10-battle-tested.md](V10-battle-tested.md) §反例 5 | V10 战役蒸馏 |
| 6 | 编造测试文件路径 | [V10-battle-tested.md](V10-battle-tested.md) §反例 6 | V10 战役蒸馏 |

## 自检清单

```yaml
test_plan_checklist:
  - [ ] 每个 Capability 拆为 ≥ 3 验收维度？
  - [ ] 每个验收维度映射到 ≥ 1 测试？
  - [ ] E2E ≥ 2 / INV ≥ 1 / UNIT ≥ 5？
  - [ ] 行覆盖率 ≥ 90% 门槛？
  - [ ] test_to_capability 映射表齐全？
  - [ ] 关键路径 100% E2E 覆盖？
```
