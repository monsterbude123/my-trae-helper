---
name: project-rules
description: 项目级 Rules 强制加载入口 — 所有 agent(主 agent / sub-agent)进入项目执行任务前必走本 skill 获取本会话所需 rules,禁止直接 Read .trae/rules/*.md。
---

# Project Rules Skill — 项目级 Rules 强制加载入口

> **触发**: 任何 agent 进入本项目执行任务前。
> **强制级别**: 🔴 P0 — 任何跳过本入口的行为 = 🛑 REJECT。
> **职责**: 把项目 `.trae/rules/` 下的多个 rule 文件收纳到本 skill,按"场景关键词 → 必加载 rules"路由表按需加载,**避免 context 撑爆**。

---

## §0 强制协议(主 agent + sub-agent 通用)

```
🚨 必读 · .trae/rules/ 目录的唯一入口

任何 agent(主 agent / sub-agent / 主上下文开启子 agent 时)进入本项目执行任务前,
必须走本 skill 获取本会话需要的 rules。

❌ 禁止绕过本入口直接 Read .trae/rules/*.md 中除 README.md 外的其他文件
❌ 禁止 Read 全部 rules(按需加载,避免撑爆上下文)
❌ 禁止用 grep / Glob 搜 rules(必须走 Skill 入口)
```

## §1 调用本 Skill

```python
Skill(name="project-rules")
```

skill 入口:本文件(自动加载)

## §2 路由表:场景关键词 → 必加载 rules

> **使用方式**: 按当前任务场景选 1 个或多个 rules。**不在列表的场景走"全部加载"**。
> **路由表由 init-from-zero.py 自动生成**,根据项目现有 rules 列表填充。

| 场景关键词 | 必加载 rules |
|-----------|-------------|
| 改 API / 改契约 | governance.md + code-style.md |
| 改前端 / 改样式 | code-style.md + style.md |
| 改依赖 / 改 build | stack.md + governance.md |
| 提 PR / 合分支 | git.md + governance.md |
| 修 bug | anti-patterns.md + code-style.md |
| 任何场景(未列出) | 全加载 |

> **项目专属路由映射**: agent 可在加载本 skill 后,根据项目实际情况扩展本表(不破坏骨架)。

## §3 Read 选中的 rules

✅ Read `.trae/skills/project_rules_skills/references/{rule-name}.md`

references 目录下是**软链接或符号引用**,指向 `.trae/rules/` 下的实际文件(避免内容重复)。

❌ 禁止直接 Read `.trae/rules/*.md` 中除本 README.md 外的其他文件

❌ 禁止 Read 全部 9+ 个 rules(按需加载)

## §4 sub-agent 必走 — Completion Report 声明

sub-agent 必须在 Completion Report 显式声明已加载/跳过的 rules:

```yaml
rules_loaded:
  - governance.md (reason: 改 API)
  - code-style.md (reason: 改 API)
rules_skipped:
  - anti-patterns.md
  - asset-hygiene.md
  - git.md
  - ...
```

## §5 主 agent 委派 sub-agent 头部必加

```
[PROJECT-RULES-GATE]
  必须先调用 Skill(name="project-rules") 获取本任务所需 rules,再开始工作。
  在 Completion Report 中必须声明 rules_loaded / rules_skipped 清单。
```

完整模板: `workflows/sub-agent-delegate-load.md`

## §6 为什么有这个目录?

`.trae/rules/` 历史上散落 N 个文件(stack / paths / governance / code-style / anti-patterns / asset-hygiene / style / git / kill-rules 等),每个会话通过 workspace_rules 永久注入主上下文,总量 ~800+ 行,**直接撑爆 context**。

现在的设计:

| 关注点 | 在哪里 |
|--------|-------|
| 加载规则(怎么找到需要的 rule) | 本 SKILL.md + .trae/skills/project_rules_skills/ |
| 实际 rule 内容(single source of truth) | 通过 references/ 软链接指向 .trae/rules/ 原文件 |
| AGENTS.md 业务约束 | 仓库根 AGENTS.md |
| V11 通用铁律 | ~/.trae-cn/skills/fullstack4TraeV11/references/ |

## §7 反模式(违反任一即 🛑 REJECT)

```
❌ 跳过 Skill(name="project-rules") 而用 grep / Glob 搜 rules
❌ Sub-agent 不声明 rules_loaded / rules_skipped
❌ 主 agent 委派 sub-agent 时不注入 [PROJECT-RULES-GATE] 头部
❌ Read 全部 rules 撑爆上下文
❌ 直接 Read .trae/rules/*.md 中除 README.md 外的其他文件
```

## §8 关联引用

- `.trae/rules/README.md` — 强制入口说明(本项目唯一指向本 skill 的入口)
- `references/*.md` — 软链接到 `.trae/rules/` 实际 rule 文件
- `~/.trae-cn/skills/fullstack4TraeV11/references/` — V11 通用铁律(本项目通用规范)

---

*本文件由 fullstack4TraeV11 init-from-zero.py --rules-as-skill 自动生成。路由表 §2 由 init 根据项目现有 rules 列表动态填充。*