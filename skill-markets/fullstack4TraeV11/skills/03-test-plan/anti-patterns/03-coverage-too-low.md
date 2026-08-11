# 反例 3：覆盖率门槛宽松

> 行 ≥ 90% 是硬门槛。宽松 = Stage 3 必补风险 + Stage 4 Review 质疑。

## 现象 / 根因 / 教训 / 正确替代

**现象**: test-plan.md 标注"覆盖率 ≥ 70%"或未标注。

**根因**: 觉得"覆盖率不是必须的"或"项目没要求"。

**教训**: V11 公共铁律 Article II 满分硬门禁要求覆盖率不达标 = REJECT。

**正确替代**: 行 ≥ 90% / 分支 ≥ 85% / 函数 ≥ 95% / 关键路径 100%。

## 关联引用

- [SKILL.md §铁律 2](../SKILL.md) — 覆盖率门槛 ≥ 90%
- [coverage-rules.md](../references/coverage-rules.md)
- 公共铁律 Article II: [../../../references/common-iron-rules.md](../../../references/common-iron-rules.md)
