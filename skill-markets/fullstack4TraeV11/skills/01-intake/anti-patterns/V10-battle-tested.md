# V10 实战蒸馏（Battle-Tested Patterns）

> Stage -1 Intake 在 V10 中无独立 agent 封装，能力散落在 SKILL.md §1.6 委派注入 + §3.4 项目类型专属 + §7.5 AskUserQuestion 反模式 + bug-workflow.md。本节蒸馏 V10 实战智慧。

---

## V10 实战反例（4 条：2 部分 + 2 完全重叠）

### 蒸馏 1：Bug 单"先斩后奏"（完全重叠）

→ 见 [03-force-create-bug.md](03-force-create-bug.md)（V10.11 真实失误，铁律 4 Bug 录入必询问 + 询问模板）。

### 蒸馏 2：项目初始化"假装勘察"（完全重叠）

→ 见 [04-no-convention-survey.md](04-no-convention-survey.md)（V10.9 §0.5 失误，铁律 2 未勘察不初始化 + 4 类文件 Glob 必走）。

### 蒸馏 3：状态卡说谎导致跨会话迷路（部分重叠）

**独特差异**: 不同于 02-skip-state-card.md 聚焦"跳过状态卡初始化"，本条聚焦状态卡存在但与 stage 完成不同步 → current_stage 仍显示旧值 → 下次会话误判起点 → 重复实施。V11 改进为 state-card-protocol.md + state-card-validator.py（Task 17）同步校验。

→ 关联 [02-skip-state-card.md](02-skip-state-card.md)。

### 蒸馏 4：AskUserQuestion 反模式（部分重叠）

**独特差异**: 不同于 01-no-intent-recognition.md 聚焦"未识别意图类型"，本条聚焦"用户没选 AskUserQuestion 选项 = 可能在质疑流程本身，不是要换选项"——主上下文误读为"换选项"继续给编号，应先读 references/project-structure.md 看项目惯例。

→ 关联 [01-no-intent-recognition.md](01-no-intent-recognition.md)（ask-question-anti-patterns.md 公共 references + 反例 1 经验主义臆断）。

---

## V10 实战蒸馏经验（4 条）

| 经验 | V10 来源 | V11 落地位置 |
|------|---------|------------|
| Bug 录入必询问 | SKILL.md §1.6 + bug-workflow.md | 铁律 4 + 反例 3 + bug-intake-flow.md Step 2 |
| 项目惯例勘察不可跳 | SKILL.md §0.5 + §0.5.1 | 铁律 2 + 反例 4 + project-convention-survey.md |
| 状态卡是真相源 | SKILL.md §6.1 | 铁律 3 + state-card-protocol.md + state-card-init.md |
| AskUserQuestion 反模式 | SKILL.md §7.5 | ask-question-anti-patterns.md + 反例 1 |

---

## V10 来源溯源（开发期，部署前可删）

> ⚠️ 本节记录 V10 来源，仅供 V11 维护者追溯。**V11 部署时不依赖 V10**——V10 内容已蒸馏进 V11 references/anti-patterns。

| V10 来源 | 蒸馏到 V11 位置 |
|---------|---------------|
| V10 SKILL.md §1.6 Bug 录入触发 | → 本文档蒸馏 1 + `../../01-intake/workflows/bug-intake-flow.md` |
| V10 SKILL.md §0.5 加载协议 | → 本文档蒸馏 2 + `../../01-intake/workflows/project-convention-survey.md` |
| V10 SKILL.md §7.5 AskUserQuestion 反模式 | → 本文档蒸馏 4 + `../../../references/ask-question-anti-patterns.md` |
| V10 bug-workflow.md | → 本文档蒸馏 1 + `../../01-intake/workflows/bug-intake-flow.md` |
| V10 scenarios.md §1 §2 §5 | → 本文档蒸馏 1+2+3 |

---

## 关联引用

- [SKILL.md](../SKILL.md) — Stage -1 入口
- [README.md](../README.md) — 阶段元信息
- [intent-routing.md](../workflows/intent-routing.md) — 意图路由工作流
- [bug-intake-flow.md](../workflows/bug-intake-flow.md) — Bug 录入工作流
- 其他反例: [01-no-intent-recognition.md](01-no-intent-recognition.md) / [02-skip-state-card.md](02-skip-state-card.md) / [03-force-create-bug.md](03-force-create-bug.md) / [04-no-convention-survey.md](04-no-convention-survey.md)
