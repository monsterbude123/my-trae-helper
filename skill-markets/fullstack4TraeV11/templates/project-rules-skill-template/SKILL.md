---
name: project-rules
description: 项目级 Rules 强制加载入口 — 所有 agent(主 agent / sub-agent)进入项目执行任务前必走本 skill 获取本会话所需 rules,禁止直接 Read .trae/rules/*.md。**强制多选 + 漏选审查 + 用户通知**(V11.8.7 蒸馏补)。
---

# Project Rules Skill — 项目级 Rules 强制加载入口

> **触发**: 任何 agent 进入本项目执行任务前。
> **强制级别**: 🔴 P0 — 任何跳过本入口的行为 = 🛑 REJECT。
> **职责**: 把项目 `.trae/rules/` 下的多个 rule 文件收纳到本 skill,按"场景关键词 → 必加载 rules"路由表按需加载,**避免 context 撑爆**。

---

## §0 强制协议(主 agent + sub-agent 通用 — V11.8.7 三件套强化)

```
🚨 必读 · .trae/rules/ 目录的唯一入口

任何 agent(主 agent / sub-agent / 主上下文开启子 agent 时)进入本项目执行任务前,
必须走本 skill 获取本会话需要的 rules。

❌ 禁止绕过本入口直接 Read .trae/rules/*.md 中除 README.md 外的其他文件
❌ 禁止 Read 全部 rules(按需加载,避免撑爆上下文)
❌ 禁止用 grep / Glob 搜 rules(必须走 Skill 入口)

[V11.8.7 NEW — 三件套]
1. 强制多选       — 一个场景至少命中 §2 路由表 2-3 行,禁止单选 1 条 rule
2. 强制漏选审查   — 列完 needed_rules 后必走 §3.5 自审 7 维 checklist
3. 强制用户通知   — 选了什么/漏了什么/N/A 理由 都要告知,就算一个没选也要告知

❌ 选了但不 Read(占位空转)→ 违反铁律 3
❌ 不通知用户选了哪些 → 违反铁律 4
❌ 单选 1 条 → 违反铁律 1
❌ 跳过 checklist 自审 → 违反铁律 2
```

## §1 调用本 Skill

```python
Skill(name="project-rules")
```

skill 入口:本文件(自动加载)

## §2 路由表:场景关键词 → 必加载 rules(强制多选)

> **使用方式**: 按当前任务场景**选多个 rules**(V11.8.7 NEW — 单选 = 漏选反例)。
> **不在列表的场景或不确定性 → 直接走"全部加载"分支**(原则 5)。
> **路由表由 init-from-zero.py 自动生成**,根据项目现有 rules 列表填充。
> **agent 命中后必经 §3.5 漏选审查 + §5 用户通知**,不得跳过。

| 场景关键词 | 必加载 rules |
|-----------|-------------|
| 改 API / 改契约 | governance.md + code-style.md + paths.md |
| 改前端 / 改样式 | code-style.md + style.md + git.md |
| 改依赖 / 改 build | stack.md + governance.md + git.md |
| 提 PR / 合分支 | git.md + governance.md + code-style.md |
| 修 bug | anti-patterns.md + code-style.md + git.md |
| 任何场景(未列出) | 全加载 |

> **项目专属路由映射**: agent 可在加载本 skill 后,根据项目实际情况扩展本表(不破坏骨架)。
>
> **V11.8.7 NEW**: 实际场景几乎都触发 ≥ 2 行(单行 = 漏选),且必触发 git.md(所有 commit/合分支场景)。

## §3 Read 选中的 rules

✅ Read `.trae/skills/project_rules_skills/references/{rule-name}.md` (列了必读,禁止"占位不读")

references 目录下是**软链接或符号引用**,指向 `.trae/rules/` 下的实际文件(避免内容重复)。

❌ 禁止直接 Read `.trae/rules/*.md` 中除本 README.md 外的其他文件

❌ 禁止 Read 全部 9+ 个 rules(按需加载)

### §3.5 漏选审查 checklist(V11.8.7 NEW — 强制)

```yaml
checklist:
  paths:
    asked: 是否触碰 archive/ / _lib_paths / secrets/?
    loaded: [paths.md, governance.md]
  code_style:
    asked: 是否改 .py/.ts/.md 写法?
    loaded: [code-style.md, style.md]
  build_dep:
    asked: 是否改 package.json / Cargo.toml / pyproject.toml?
    loaded: [stack.md, governance.md]
  git:
    asked: 是否要 commit / push / merge / PR?
    loaded: [git.md, governance.md]
  bug_fix:
    asked: 是否在修已 QA/测试/bug?
    loaded: [anti-patterns.md, code-style.md]
  asset_hygiene:
    asked: 是否触碰大文件/二进制/媒体资产?
    loaded: [asset-hygiene.md, governance.md]
  uncertainty:
    asked: 场景模糊 / 跨多领域?
    loaded: ["全加载"]
任一 checklist 命中但 loaded 为空 → 强制重选,不允许跳过
```

## §4 sub-agent 必走 — Completion Report 声明(含 N/A 理由)

sub-agent 必须在 Completion Report 显式声明已加载/跳过的 rules + **每个 skipped 项附 N/A 理由**:

```yaml
rules_loaded:
  - governance.md (reason: 改 API)
  - code-style.md (reason: 改 API)
rules_skipped:
  - path: anti-patterns.md
    reason: "N/A - 当前非 bug 修复场景"
  - path: asset-hygiene.md
    reason: "N/A - 无大文件/二进制操作"
  - path: git.md
    reason: "N/A - 委派任务不直接 commit"
checklist_summary:
  paths: ☑
  code_style: ☑
  build_dep: □ skipped_with_reason
  git: □ skipped_with_reason
  bug_fix: □ skipped_with_reason
  asset_hygiene: □ skipped_with_reason
  uncertainty: □
```

## §5 主 agent 委派 sub-agent 头部必加(V11.8.7 加强 — 含用户通知)

```
[PROJECT-RULES-GATE]
  必须先调用 Skill(name="project-rules") 获取本任务所需 rules,再开始工作。
  MUST: 多选 ≥ 2 行 §2 路由表,禁止单选
  MUST: 走 §3.5 漏选审查 7 维 checklist,缺一 = 重选
  MUST: 在 Completion Report 中必须声明 rules_loaded / rules_skipped(含 N/A 理由) / checklist_summary
  MUST: 在响应开头输出"📋 Rules 加载通知"(场景关键词 + 命中数 + 漏选数 + checklist 命中)
  就算一个没选也要告知,禁止静默
```

完整模板: `workflows/sub-agent-delegate-load.md`

### 用户通知格式(V11.8.7 主代理必走)

```markdown
📋 Rules 加载通知
- 场景关键词:`<触发词>`
- 命中数:N 条(列出 paths)
- 漏选数:M 条(列出每条 + N/A 理由)
- 7 维 checklist 命中:
  - paths / archive: ☑ 或 □ (□ → 附 N/A)
  - code-style / formatting: ☑ 或 □
  - build / dep: ☑ 或 □
  - git / release: ☑ 或 □
  - bug / 反例: ☑ 或 □
  - asset / 大文件: ☑ 或 □
  - uncertainty: ☑ 或 □
- 任一维度 □ → 已自动加入 needed_rules / 列 N/A 理由
```

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
❌ Sub-agent 不声明 rules_loaded / rules_skipped / checklist_summary
❌ Sub-agent 主代理不通知用户选了哪些(就算一个没选也要告知)
❌ Sub-agent 单选 1 条 rule(违反 V11.8.7 强制多选)
❌ Sub-agent 选了但不 Read(占位空转,违反 V11.8.7 铁律 3)
❌ Sub-agent 跳过 §3.5 漏选审查(违反 V11.8.7 铁律 2)
❌ 主 agent 委派 sub-agent 时不注入 [PROJECT-RULES-GATE] 头部
❌ Read 全部 rules 撑爆上下文
❌ 直接 Read .trae/rules/*.md 中除 README.md 外的其他文件
```

## §8 关联引用

- `.trae/rules/README.md` — 强制入口说明(本项目唯一指向本 skill 的入口)
- `references/*.md` — 软链接到 `.trae/rules/` 实际 rule 文件
- `~/.trae-cn/skills/project-rule-skill/SKILL.md` — 全局级 project-rules 网关协议(V11.8.7 三件套源头)
- `~/.trae-cn/skills/fullstack4TraeV11/references/` — V11 通用铁律(本项目通用规范)
- `~/.trae-cn/skills/fullstack4TraeV11/SKILL.md §14.1-§14.4` — 项目级 rules skill 创建协议(5 步整合)

---

*本文件由 fullstack4TraeV11 init-from-zero.py --rules-as-skill 自动生成。路由表 §2 由 init 根据项目现有 rules 列表动态填充。*
*V11.8.7 NEW*: §0 / §3.5 / §5 / §7 已硬强 三件套协议。