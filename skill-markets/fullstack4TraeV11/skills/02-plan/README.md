# Stage 0 Plan — 总览

> **V11.7.0+ 设计入口**: [AC 核销门禁](../skills/09-review/SKILL.md) · [贾维斯门禁守护](../skills/00-boot/SKILL.md) · 评分制废除 → 门禁制 · 详见 [CHANGELOG.md V11.7.0](../CHANGELOG.md)


> 第一性原则：**探索先于规划，禁止凭空设计**。
>
> **本文件 ≤ 80 行**，按 H2 章节拆分到 `README-detail/` 子文件。所有内容保真保留，仅按章节切分。

---

## H2 章节指针

| 章节 | 文件 |
|------|------|
| 第一性原则（3 条） | [01-first-principles.md](./README-detail/01-first-principles.md) |
| 完整骨架流程（6 步） | [02-skeleton-flow.md](./README-detail/02-skeleton-flow.md) |
| 完整铁律（10 条） | [03-iron-rules.md](./README-detail/03-iron-rules.md) |
| 完整反例（4 条） | [04-anti-patterns.md](./README-detail/04-anti-patterns.md) |
| 完整交付协议 + Completion Report + AOP 自检 | [05-handoff-protocol.md](./README-detail/05-handoff-protocol.md) |
| 启动检查清单 | [06-checklist.md](./README-detail/06-checklist.md) |

---

## 必读

- 子代理委派时只 Read 主索引 + 当前需要的章节文件（避免 context 击穿）
- 骨架流程（6 步）在 `02-skeleton-flow.md`，是 Plan 全部决策的执行链路
- 铁律（10 条）在 `03-iron-rules.md`，含 MUST/NEVER 全部红线

---

## 关联引用

- SKILL.md 入口：[SKILL.md](SKILL.md)
- 工作流：[workflows/](workflows/)
- 方法论：[references/](references/)
- 模板：[templates/](templates/)
- 反例：[anti-patterns/](anti-patterns/)
- 公共 references：[../../references/](../../references/)
