# Anti-patterns — Stage 1 Spec 反例库

> 3 条核心反例。

## 反例索引

| # | 反例 | 违反铁律 |
|:---:|------|---------|
| 1 | INV 凭空臆造 | 铁律 6 |
| 2 | Clarify 跳过 | 铁律 5 |
| 3 | Spec 写实施 | 铁律 7 |

## 自检清单

```yaml
spec_checklist:
  - [ ] 每个 Capability ≥ 3 AC？
  - [ ] 整体 E2E ≥ 2？
  - [ ] 整体 INV ≥ 1（基于业务规则）？
  - [ ] Clarify ≥ 2 轮记录？
  - [ ] Spec 未写代码细节？
  - [ ] Non-Goals 明确？
```
