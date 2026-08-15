# V10 实战蒸馏（Battle-Tested Patterns）

> **V11.7.0+ 设计入口**: [AC 核销门禁](../skills/09-review/SKILL.md) · [贾维斯门禁守护](../skills/00-boot/SKILL.md) · 评分制废除 → 门禁制 · 详见 [CHANGELOG.md V11.7.0](../CHANGELOG.md)


> Stage 0 Plan 在 V10 中由 planner role 承担，能力散落在 SKILL.md §5 探索 + §6 委派子代理 + scenarios.md §1 §2 §3。本节蒸馏 V10 实战智慧。

---

## V10 实战反例（4 条：1 部分 + 3 独特蒸馏）

### 蒸馏 1：主上下文直行探索未委派（独特）

**独特差异**: 不同于 01-no-exploration.md 聚焦"跳过探索直接规划"，本条聚焦"主上下文**部分**委派但自己又 Read/Grep 一遍验证"——委派意义消失、上下文击穿、子代理产出被主上下文偏向解读。V11 改进为铁律 2 SUBAGENT ONLY + 铁律 6 DUAL SEARCH（主上下文不直行代码 = 主上下文不直行探索）。

→ 关联 [01-no-exploration.md](01-no-exploration.md)。

### 蒸馏 2：Capability 凭经验列未走 3 路证据（部分重叠）

**独特差异**: 不同于 01-no-exploration.md 聚焦"无 evidence 的 plan.md"，本条聚焦**"有 evidence 但 capability 列表是从经验列出而非 3 路 evidence 抽取"**——Capabilities 与 Impact 段脱钩、Closure 闭环步骤 > 5（违反铁律 9）。V11 改进为铁律 8 PLAN ≤ 80 LINES + Capabilities ≤ 5 + 反例 4 拆分原则。

→ 关联 [04-plan-too-long.md](04-plan-too-long.md)。

### 蒸馏 3：3 路探索产出 summary 格式不统一导致 plan.md 拼接错位（独特）

**独特差异**: 不同于 01-no-exploration.md 聚焦"未走 3 路"，本条聚焦**"3 路探索全走，但子代理 A/B/C 返回 summary 结构不同（json / yaml / md 混用）→ 主上下文拼装 plan.md 时字段错位 → Capabilities 与 Impact 不对齐"**。V11 改进为铁律 2 SUBAGENT ONLY + AOP 移交自检（README-detail/05-handoff-protocol.md L64-72）+ 3 个子代理必返统一 Completion Report 格式。

→ 关联 [README-detail/05-handoff-protocol.md](../README-detail/05-handoff-protocol.md) §Completion Report。

### 蒸馏 4：重构不 purge 致 spec.md 漂移（独特）

**独特差异**: 不同于 03-refactor-without-purge.md 聚焦"未调 spec-purge.py"，本条聚焦**"调了 spec-purge.py 但没看退出码 + 旧产物仍残留 docs/specs/changes/{old-id}/（未隔离到 _invalidated/）"**。V11 改进为反例 3 §spec-purge.py 用法 §dry-run 验证 + §失败回滚审计。

→ 关联 [03-refactor-without-purge.md](03-refactor-without-purge.md)。

---

## V10 实战蒸馏经验（4 条）

| 经验 | V10 来源 | V11 落地位置 |
|------|---------|------------|
| 探索必委派 | SKILL.md §5 + scenarios.md §1 §2 | 铁律 2 SUBAGENT ONLY + 铁律 6 DUAL SEARCH + 反例 1 |
| Capability 必 ≤ 5 | scenarios.md §3 plan.md 模板 | 铁律 8 PLAN ≤ 80 LINES + 反例 4 |
| 3 路 evidence 必对齐 | scenarios.md §1 §2 §3 | README-detail/05-handoff-protocol.md §AOP 移交自检 |
| 重构必 purge + 隔离 | SKILL.md §5 重构场景 | 铁律 5 PURGE ON REFACTOR + 反例 3 |

---

## V10 来源溯源（开发期，部署前可删）

> ⚠️ 本节记录 V10 来源，仅供 V11 维护者追溯。**V11 部署时不依赖 V10**——V10 内容已蒸馏进 V11 references/anti-patterns。

| V10 来源 | 蒸馏到 V11 位置 |
|---------|---------------|
| V10 SKILL.md §5 探索三路 | → 本文档蒸馏 1 + `../workflows/three-path-exploration.md` |
| V10 SKILL.md §6 委派子代理 | → 本文档蒸馏 1 + `../workflows/three-path-exploration.md` |
| V10 scenarios.md §1 §2 §3 | → 本文档蒸馏 2+3 |
| V10 process-rot-analysis.md §"重构不 purge" | → 本文档蒸馏 4 + [03-refactor-without-purge.md](03-refactor-without-purge.md) |

---

## 关联引用

- [SKILL.md](../SKILL.md) — Stage 0 入口
- [README.md](../README.md) — 阶段元信息
- [three-path-exploration.md](../workflows/three-path-exploration.md) — 3 路并行探索
- [plan-clarification.md](../workflows/plan-clarification.md) — 计划追问点
- 其他反例: [01-no-exploration.md](01-no-exploration.md) / [02-grep-instead-of-gitnexus.md](02-grep-instead-of-gitnexus.md) / [03-refactor-without-purge.md](03-refactor-without-purge.md) / [04-plan-too-long.md](04-plan-too-long.md)
