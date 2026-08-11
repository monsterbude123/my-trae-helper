# 反例 4：跳过 E2E / INV

> E2E ≥ 2 + INV ≥ 1 + UNIT ≥ 5 是最低组合。只写 UNIT = 端到端流程无保障。

## 现象 / 根因 / 教训 / 正确替代

**现象**: test-plan.md 只有 UNIT 测试，无 E2E 无 INV。

**根因**: 觉得"E2E 太慢" / "INV 不知道测什么"。

**教训**: 单元测试全 pass 但端到端流程失败 = Stage 3.5 Real Verify 启动验证发现 → 返工。

**正确替代**: E2E ≥ 2（关键流程）+ INV ≥ 1（数据一致性 / 安全约束）+ UNIT ≥ 5。

## 关联引用

- [SKILL.md §铁律 3](../SKILL.md) — E2E ≥ 2 / INV ≥ 1 / UNIT ≥ 5
- [coverage-mapping.md §最低组合](../workflows/coverage-mapping.md)
