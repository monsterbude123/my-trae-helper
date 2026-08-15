# Anti-patterns — Stage 6 Bug Fix 反例库

| # | 反例 | 文件 |
|:---:|------|------|
| 1 | 跳过 e2e 先行直接修 | [01-skip-e2e-first.md](01-skip-e2e-first.md) |
| 2 | 跨层过度修复 | [02-cross-layer-overkill.md](02-cross-layer-overkill.md) |
| 3 | 修复未回写 bug 单 | [03-not-update-bug.md](03-not-update-bug.md) |
| 4 | 大小写不敏感比较违规 | [04-case-insensitive-bug.md](04-case-insensitive-bug.md) |

## 反例自检清单(Stage 6 专属)

```
stage_6_bug_fix_checklist:
  - [ ] 不跳 e2e 先行?(铁律 2 / 反例 1)
  - [ ] 跨层修复最小化?(铁律 6 / 反例 2 — 优先改当前层 + 1 处防御)
  - [ ] 修复回写 bug 单?(铁律 7 / 反例 3 — OPEN → CLOSED + root_cause + fix_commit)
  - [ ] hash/ID/token 比较大小写不敏感?(铁律 5 TDD 间接 / 反例 4 / V10 sub-agent-rules §11)
```

> **与公共 checklist 关系**:Stage 6 专属只覆盖本 stage 4 项反例;完整 23 项 P0/P1/P2/P3 checklist 见 [references/common-anti-patterns.md](../../../references/common-anti-patterns.md)。
