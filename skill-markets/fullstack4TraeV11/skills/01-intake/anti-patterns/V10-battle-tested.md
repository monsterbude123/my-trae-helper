# V10 实战蒸馏（Battle-Tested Patterns）

> Stage -1 Intake 在 V10 中无独立 agent 封装，能力散落在 SKILL.md §1.6 委派注入 + §3.4 项目类型专属 + §7.5 AskUserQuestion 反模式 + bug-workflow.md。本节蒸馏 V10 实战智慧。

---

## V10 实战反例（4 条）

### 蒸馏 1：Bug 单"先斩后奏"（V10.11 真实失误）

**实战场景**（V10.11 蒸馏，2026-08-08）:
- 用户："报错 token 失效"
- 主上下文未询问 → 直接创建 bug 单 → 路由到 debugger
- debugger e2e 先行 → **FAIL → NOT FOUND** → 用户反馈："我只是想问下，不是要修"

**根因**: V10 早期 Bug 录入触发词识别后默认创建，未走 AskUserQuestion 询问确认。

**V11 改进**: 铁律 4（Bug 录入必询问）+ 反例 3（强制创建 bug 单）+ 询问模板（"看起来像 Bug（命中触发词 XXX），是否作为 bug 单录入？...如果只是想咨询或讨论，请告诉我"）。

**V10 源**: SKILL.md §1.6 Bug 录入触发条件（V10.11 NEW）+ 反模式 1。

---

### 蒸馏 2：项目初始化"假装勘察"（V10.9 §0.5 失误）

**实战场景**（V10.9 蒸馏，2026-08-07）:
- 主上下文加载 V10 SKILL.md → 直接进入 Plan，未 Glob 项目 docs/ + AGENTS.md
- 首次产物命名/编号/结构与项目惯例冲突 → 用户 4+ 轮返工

**根因**: V10 §0.5 Skill 加载协议要求"Glob 1 次项目惯例"，但当时未严格遵循。

**V11 改进**: Intake Step 2 项目惯例勘察（workflows/project-convention-survey.md）+ 铁律 2（未勘察不初始化）+ 反例 4（未勘察项目惯例）+ 4 类文件 Glob 必走。

**V10 源**: SKILL.md §0.5 Skill 加载协议（V10.9 NEW）+ §0.5.1 同类约定强制清单。

---

### 蒸馏 3：状态卡说谎导致跨会话迷路（V10 §6.1 实战）

**实战场景**（V10 蒸馏）:
- Stage 4 Review 完成后状态卡未更新 → current_stage 还显示 3/Implement
- 下次会话激活时读状态卡 → 误判起点 → 重复实施

**根因**: V10 状态卡更新与 stage 完成不同步。

**V11 改进**: state-card-protocol.md（公共 references）+ state-card-init.md 模板 + state-card-validator.py（Task 17）+ Intake 状态卡初始化必走。

**V10 源**: SKILL.md §6.1 状态卡 / references/state-card-protocol.md（如有）。

---

### 蒸馏 4：AskUserQuestion 反模式（V10.9 §7.5 实战）

**实战场景**（V10.9 蒸馏，2026-08-07）:
- 第 3 轮用户："为啥没有编号了，这个是全栈流程没有指导你这么做吗"
- 主上下文："加编号 L1-01"
- 应答（反事实）："我应先读 references/project-structure.md 看项目惯例 + 写蒸馏报告给技能开发者"

**根因**: 用户没选 AskUserQuestion 选项 = 可能在质疑流程本身，不是要换选项。

**V11 改进**: ask-question-anti-patterns.md（公共 references）+ Intake 反模式链路（反例 1 经验主义臆断）。

**V10 源**: SKILL.md §7.5 AskUserQuestion 反模式（V10.9 NEW）。

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
