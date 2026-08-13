# Anti-patterns — Stage 3 Implement 反例库

## 反例索引

| # | 反例 | V10 来源 |
|:---:|------|---------|
| 1 | 跳过 RED 直接 GREEN | implementer 铁律 8 |
| 2 | 编造测试证据 | V10.12 ANTI-反模式 1+2 |
| 3 | 改实现不改测试（rot #12）| implementer 铁律 2 |
| 4 | 漂移静默（不报告回流）| implementer 铁律 3 |

## 自检清单

```yaml
implement_checklist:
  - [ ] 深度理解（context + modules）已输出？
  - [ ] 每个 TDD 任务都走过 RED → GREEN → REFACTOR？
  - [ ] DRIFT CHECK 通过？
  - [ ] 测试 pass/total + contract_tests + coverage 三个数字已填？
  - [ ] 代码卫生（≤800/≤50/无魔法数字）通过？
  - [ ] 改实现同步改测试？
```
