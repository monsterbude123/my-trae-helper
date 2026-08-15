# Anti-patterns — Stage 1 Spec 反例库

> 3 条核心反例 + V10 实战蒸馏(V11.2 NEW)。

## 反例索引

| # | 反例 | 违反铁律 |
|:---:|------|---------|
| 1 | INV 凭空臆造 | 铁律 6 |
| 2 | Clarify 跳过 | 铁律 5 |
| 3 | Spec 写实施 | 铁律 7 |
| V10-battle-tested | 状态卡字段漂移(updated_at / e2e_count / gate_result.gate / expected_inputs / stage_ended_at 5 类实战反例) | 铁律 12 + state-card-stage1-fields.md §2 强约束 |

## 自检清单

```yaml
spec_checklist:
  - [ ] 每个 Capability ≥ 3 AC？
  - [ ] 整体 E2E ≥ 2？
  - [ ] 整体 INV ≥ 1(基于业务规则)？
  - [ ] Clarify ≥ 2 轮记录？
  - [ ] Spec 未写代码细节？
  - [ ] Non-Goals 明确？
  - [ ] updated_at 与 stage_ended_at 一致？(V10 反例 4 + 8)
  - [ ] e2e_count = grep spec.md 实际 E2E 数？(V10 反例 5)
  - [ ] inv_count = grep spec.md 实际 INV 数？(V10 反例 5)
  - [ ] gate_result.gate = "spec-validate-hook"？(V10 反例 6)
  - [ ] next_stage.expected_inputs 含 [spec.md, ac_list.md, edge_cases.md]？(V10 反例 7)
```
