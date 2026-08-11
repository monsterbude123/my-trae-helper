# Anti-patterns — Stage 0.5 Test Plan 反例库

> 4 条核心反例 + 主上下文自检清单。

## 反例索引

| # | 反例 | 文件 |
|:---:|------|------|
| 1 | 无验收维度直接测试 | [01-no-acceptance-dimension.md](01-no-acceptance-dimension.md) |
| 2 | 测试不可追溯 | [02-test-not-traceable.md](02-test-not-traceable.md) |
| 3 | 覆盖率门槛宽松 | [03-coverage-too-low.md](03-coverage-too-low.md) |
| 4 | 跳过 E2E / INV | [04-skip-e2e.md](04-skip-e2e.md) |

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
