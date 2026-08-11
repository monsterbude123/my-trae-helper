# 反例 2：测试不可追溯

> 测试与 Capability 必须可追溯。缺映射 = Stage 4 Review 无法定位失败维度。

## 现象 / 根因 / 教训 / 正确替代

**现象**: test-plan.md 只有测试列表，无 test_to_capability 映射。

**根因**: 觉得"测试只管 pass"。

**教训**: 测试失败时无法定位哪个 Capability 受影响 → 返工定位耗时。

**正确替代**: test-plan.md 必含 `test_to_capability` 映射表（每个测试标注 capability + 验收维度）。

## 关联引用

- [SKILL.md §铁律 4](../SKILL.md) — 测试可追溯
- [coverage-mapping.md §Step 3](../workflows/coverage-mapping.md)
