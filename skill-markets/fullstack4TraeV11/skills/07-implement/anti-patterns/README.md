# Anti-patterns — Stage 3 Implement 反例库

## 反例索引

| # | 反例 | V10 来源 |
|:---:|------|---------|
| 1 | 跳过 RED 直接 GREEN | implementer 铁律 8 |
| 2 | 编造测试证据 | V10.12 ANTI-反模式 1+2 |
| 3 | 改实现不改测试（rot #12）| implementer 铁律 2 |
| 4 | 漂移静默（不报告回流）| implementer 铁律 3 |
| 5 | V10 实战蒸馏（rot #13 Bundle Staleness 独有）| implementer 铁律 5 |

## 自检清单

```yaml
implement_checklist:
  - [ ] 深度理解（context + modules）已输出？
  - [ ] 每个 TDD 任务都走过 RED → GREEN → REFACTOR？
  - [ ] DRIFT CHECK 通过？
  - [ ] 测试 pass/total + contract_tests + coverage 三个数字已填？
  - [ ] 代码卫生（≤800/≤50/无魔法数字）通过？
  - [ ] 改实现同步改测试？
  - [ ] 基础模块留文档（铁律 4）？
  - [ ] dist-hash-check.py PASS（铁律 5 / rot #13 Bundle Staleness）？
  - [ ] 不可修改测试让用例通过（铁律 8 / 反例 01）？
  - [ ] 实现方案走质疑性校验（铁律 9）？
  - [ ] 不可编造 tests/foo.test.ts:999（铁律 10 / 反例 02）？
```