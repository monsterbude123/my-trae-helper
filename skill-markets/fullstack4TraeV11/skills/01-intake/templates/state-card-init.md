# 状态卡初始化模板 — 总览

> **V11.7.0+ 设计入口**: [AC 核销门禁](../skills/09-review/SKILL.md) · [贾维斯门禁守护](../skills/00-boot/SKILL.md) · 评分制废除 → 门禁制 · 详见 [CHANGELOG.md V11.7.0](../CHANGELOG.md)


> Stage -1 Intake 初始化状态卡的标准模板。3 类（project / change / bug）共用一份骨架，按需替换字段。
>
> **本文件为索引**，按章节拆分到 `state-card-init-detail/` 子文件。所有内容保真保留。

---

## H2 章节指针

| 章节 | 文件 |
|------|------|
| 项目级模板（project-init / project-health） | [01-project.md](./state-card-init-detail/01-project.md) |
| Change 级模板（feature / refactor / doc-sync） | [02-change.md](./state-card-init-detail/02-change.md) |
| Bug 级模板（bug-fix） | [03-bug.md](./state-card-init-detail/03-bug.md) |
| 字段规则 + 渲染示例 + 校验脚本 | [04-fields-and-scripts.md](./state-card-init-detail/04-fields-and-scripts.md) |

---

## 必读

- 初始化时只 Read 当前类型对应的子文件，避免 context 击穿
- 字段规则 + 校验脚本 集中在 `04-fields-and-scripts.md`

---

## 关联引用

- [SKILL.md](../SKILL.md) — Stage -1 入口
- [state-card-protocol.md](../../../references/state-card-protocol.md) — 状态卡协议（完整字段定义 + 更新时机 + 交叉验证）
- [intent-routing.md](../workflows/intent-routing.md) — 意图路由工作流
- [bug-state-machine.md](../references/bug-state-machine.md) — Bug 单状态机
- [bug-template.md](bug-template.md) — Bug 单文档模板
