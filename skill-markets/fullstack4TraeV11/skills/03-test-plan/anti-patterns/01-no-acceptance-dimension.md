# 反例 1：无验收维度直接测试

> Stage 0.5 Test Plan 必走验收维度拆解。跳过 = 测试覆盖不全。

## 现象 / 根因 / 教训 / 正确替代

**现象**: plan.md Capabilities 直接对应 1 个测试，跳过验收维度拆解。

**根因**: 觉得"测试 = 写 case"，不区分 Capability → Acceptance Dimension → Test Case。

**教训**: 1 个测试覆盖多个维度 = 维度遗漏 + 边界 case 漏测 + Stage 4 Review 无法定位失败维度。

**正确替代**: Step 2 必走验收维度拆解（每个 Capability ≥ 3 维度）。

## 关联引用

- [SKILL.md §铁律 1](../SKILL.md) — 验收维度先于测试用例
- [coverage-mapping.md §Step 2](../workflows/coverage-mapping.md)
