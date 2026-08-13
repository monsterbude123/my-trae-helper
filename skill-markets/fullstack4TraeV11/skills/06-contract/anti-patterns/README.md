# Anti-patterns — Stage 2 Contract 反例库

## 反例索引

| # | 反例 | 文件 |
|:---:|------|------|
| 1 | 跳过 DOMAIN FIRST 直接写 API | [01-skip-domain.md](01-skip-domain.md) |
| 2 | 跳过孤儿契约测试清理 | [02-skip-orphan-sweep.md](02-skip-orphan-sweep.md) |
| 3 | BREAKING 变更不用户确认 | [03-breaking-without-confirm.md](03-breaking-without-confirm.md) |
| 4 | 契约漂移（代码与契约不一致）| [04-contract-drift.md](04-contract-drift.md) |

## 自检清单

```yaml
contract_checklist:
  - [ ] DOMAIN FIRST 顺序（domain → api → events → validation）？
  - [ ] INV ≥ 1（基于业务规则）？
  - [ ] orphan-detector.py 已跑？
  - [ ] BREAKING 变更已用户确认？
  - [ ] 三方同步（代码 + 契约文档 + 测试）？
  - [ ] contract-gate.py PASS？
```
