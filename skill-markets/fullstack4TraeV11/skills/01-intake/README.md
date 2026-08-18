# Stage -1 Intake — 总览

> **V11.7.0+ 设计入口**: [AC 核销门禁](../skills/09-review/SKILL.md) · [贾维斯门禁守护](../skills/00-boot/SKILL.md) · 评分制废除 → 门禁制 · 详见 [CHANGELOG.md V12.0.0](../CHANGELOG.md)


> 第一性原则：**意图不明不路由，未勘察项目惯例不初始化**。
>
> **本文件 ≤ 80 行**，按 H2 章节拆分到 `README-detail/` 子文件。所有内容保真保留，仅按章节切分。

---

## H2 章节指针

| 章节 | 文件 |
|------|------|
| 第一性原则（3 条） | [01-first-principles.md](./README-detail/01-first-principles.md) |
| 完整骨架流程 | [02-skeleton-flow.md](./README-detail/02-skeleton-flow.md) |
| 完整铁律（10 条） | [03-iron-rules.md](./README-detail/03-iron-rules.md) |
| 完整反例（4 条） | [04-anti-patterns.md](./README-detail/04-anti-patterns.md) |
| 完整交接协议 | [05-handoff-protocol.md](./README-detail/05-handoff-protocol.md) |
| 启动检查清单 | [06-checklist.md](./README-detail/06-checklist.md) |

---

## 必读

- 子代理委派时只 Read 主索引 + 当前需要的章节文件（避免 context 击穿）
- 第一性原则（3 条）放在 `01-first-principles.md`，是 Intake 全部决策的根依据
- 铁律（10 条）放在 `03-iron-rules.md`，包含 MUST/NEVER 全部红线

---

## 关联引用

- SKILL.md 入口：[SKILL.md](SKILL.md)
- 工作流：[workflows/](workflows/)
- 方法论：[references/](references/)
- 模板：[templates/](templates/)
- 反例：[anti-patterns/](anti-patterns/)
- 公共 references：[../../references/](../../references/)
