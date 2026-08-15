# Anti-patterns — Stage 0 Plan 反例库

> **V11.7.0+ 设计入口**: [AC 核销门禁](../skills/09-review/SKILL.md) · [贾维斯门禁守护](../skills/00-boot/SKILL.md) · 评分制废除 → 门禁制 · 详见 [CHANGELOG.md V11.7.0](../CHANGELOG.md)


> 4 条核心反例 + 1 个 V10 实战蒸馏集。每条核心反例含：现象 + 根因 + 教训 + 正确替代。

---

## 反例索引

| # | 反例 | 文件 |
|:---:|------|------|
| 1 | 无探索直接规划 | [01-no-exploration.md](01-no-exploration.md) |
| 2 | GitNexus 可用却 grep | [02-grep-instead-of-gitnexus.md](02-grep-instead-of-gitnexus.md) |
| 3 | 重构不 purge | [03-refactor-without-purge.md](03-refactor-without-purge.md) |
| 4 | plan.md 超长 | [04-plan-too-long.md](04-plan-too-long.md) |
| 5 | V10 实战蒸馏（4 条独特） | [V10-battle-tested.md](V10-battle-tested.md) |

---

## 4 行结构（每条反例必含）

每条反例文档严格遵循：

```
## 现象    [具体场景 + 识别信号]
## 根因    [根因 + 占比]
## 教训    [为什么错 + 真实案例 + 量化后果]
## 正确替代 [MUST + NEVER + 完整步骤]
```

---

## 主上下文自检清单

每收到"规划"/"设计"/"重构"类需求时必查：

```yaml
plan_checklist:
  探索:
    - [ ] 3 路并行子代理已委派？
    - [ ] 3 个 exploration summary 已产出？
    - [ ] GitNexus MCP 已使用（非 grep）？
  去重:
    - [ ] docs/specs/changes/ 活跃目录已扫描？
    - [ ] docs/archive/done/ 已扫描？
  重构:
    - [ ] 意图 = 重构？→ spec-purge.py 已执行？
  plan.md:
    - [ ] 行数 ≤ 80？
    - [ ] Capabilities ≤ 5？
    - [ ] Tasks ≤ 20？
    - [ ] Closure ≤ 5？
```

---

## 关联引用

- [SKILL.md](../SKILL.md) — Stage 0 入口
- [README.md](../README.md) — 阶段元信息
- [公共反例](../../../references/common-anti-patterns.md) — 18 条跨阶段公共反例
- [公共铁律](../../../references/common-iron-rules.md) — 17 跨阶段铁律（Article XVII Secret Redaction）
