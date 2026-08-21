---
name: common-project-coding-conf
version: 1.0.0
description: 通用项目级编码配置中心 — 用户说"加载路由/什么时候用哪个 skill/自检/health check/forge/项目规则"时加载。三件事：(1) 路由表告诉 agent 改代码/修 bug/提交/验收等场景该加载哪些 skills；(2) 自检机制检查关键 skill 描述完整度、MCP 连接性、项目 rules 入口 forge 状态；(3) 锻造协议把 .trae/rules/*.md 转为 .trae/skills/project_rules_skills/ 入口。触发词：路由/加载什么 skill/什么时候用/vibe coding/forge/项目 rules/项目规则。
triggers: [路由, 加载什么 skill, 什么时候用哪个 skill, vibe coding, 找 skill, 自检, health check, forge, 锻造, 项目 rules, 项目规则, 怎么加载, common project coding, 编码配置, 改代码加载什么, 修 bug 加载什么, 提交加载什么]
intent: 通用项目级编码配置中心 — 路由 + 自检 + forge
category: config
audience: [agent]
requires:
---
# Common Project Coding Conf — 通用项目级编码配置中心

> **触发词**：用户说"路由"/"什么时候用哪个 skill"/"vibe coding"/"自检"/"项目 rules"/"forge" 时加载。
>
> **职责**: 三件事合一
> 1. **路由表** — 场景关键词 → 必加载 skills 清单
> 2. **自检机制** — 6 项健康检查，关键 skill 描述完整度、MCP 连接性、项目 rules 入口 forge 状态
> 3. **锻造协议** — 把 `.trae/rules/*.md` 收纳为 `.trae/skills/project_rules_skills/` 入口 skill
>
> **强制级别**: 🔴 P0 — 任何 sub-agent 跳过 = 🛑 REJECT。
> **依赖**: 零。可单独安装使用。

---

## §0 三件套铁律

```
1. MUST 任何 sub-agent 委派头部必含 [PROJECT-RULES-GATE] 块
2. MUST 任何主 agent 任务开始前先调本 skill 拿路由表
3. MUST 任何主 agent 启动后第一步跑 cpcc-self-check.mjs（自检健康度）
4. NEVER 跳过路由表直接 Read 全市场 SKILL.md（撑爆上下文）
5. NEVER Coding agent 误用 subagent_type=search（结构性失败）
6. NEVER 盲信 sub-agent Completion Report "PASS" → 主上下文执行机械验证
```

---

## §1 路由表（场景 → 必加载 skills）

> **使用方式**: 按当前任务场景选 1 行。**不在列表的场景走"全部加载"**（兜底）。
> **触发时机**: 用户开始新任务时主动加载本表。**不要等用户问"该用什么"** — 主动按表加载。

| 场景关键词 | 必加载 skills |
|---|---|
| **改代码 / 重构 / 实现 / 简化 / 审查代码** | `coding-xinfa` + `goal-mode` + `fullstack4TraeV11/skills/07-implement` |
| **修 bug / 排查问题 / 看错误日志** | `fullstack4TraeV11/skills/12-bug-fix` + `acceptance-discipline` |
| **提交代码 / git commit / 准备合并** | `fullstack4TraeV11/scripts/commit-minimum-check.py` + `gitnexus4Trae/skills/gitnexus-impact-analysis` |
| **验收 / 测试 / E2E / 性能压测 / 安全扫描** | `acceptance-discipline` + `e2e-module-audit` + `trae-security-review` |
| **理解代码 / 探索项目 / 找入口** | `gitnexus4Trae/skills/gitnexus-exploring` + `gitnexus4Trae/skills/gitnexus-cli` |
| **修改前影响面 / 重构安全评估** | `gitnexus4Trae/skills/gitnexus-impact-analysis` + `gitnexus4Trae/skills/gitnexus-debugging` |
| **重命名 / 拆分 / 迁移** | `gitnexus4Trae/skills/gitnexus-refactoring` |
| **目标追逐 / 严格验收 / 不准偷懒** | `goal-mode` |
| **加载项目 rules / 看看项目有什么规则** | 本机已 forge: `project-rule-skill`（产物）; 未 forge: 跑 cpcc-self-check Step 4 检查 |
| **新建 / 升级 skill** | `skill-creation-workflow` + `skill-acceptance` |
| **文档治理 / 索引 / 知识图谱** | `doc-map-manager` + `docsify-doc-builder` |
| **UI 设计 / 美化前端** | `trae-remote-official:web-app-development:uicraft` |
| **自动化 / 定时任务** | `Schedule`（TRAE 工具） |
| **不确定 / 全部场景** | 全部加载 |

---

## §2 自检协议（6 项健康检查）

> **触发**: 主 agent 启动后第一步跑（用户说"自检"时也跑）。
> **脚本**: `scripts/cpcc-self-check.mjs`

### §2.1 检查项

| # | 检查项 | 实现方式 | 失败级别 |
|---|---|---|---|
| 1 | **关键 skill 是否安装** | 扫 `~/.trae-cn/skills/` 目录存在性 | FAIL（阻断）|
| 2 | **description 含触发词** | 正则 `/(触发\|触发词\|触发场景\|when to use\|加载时机\|use when)/i` | WARN（不阻断）|
| 3 | **gitnexus MCP 探活** | 调用 `mcp__gitnexus__list_repos` | WARN（不阻断）|
| 4 | **gitnexus 索引新鲜度** | 检查 `.gitnexus/` mtime < 7 天 | WARN（不阻断）|
| 5 | **项目 rules 入口 forge 状态** | 检查 `.trae/skills/project_rules_skills/SKILL.md` 存在性 | WARN（不阻断）|
| 6 | **市场 skill description 健康度扫描** | 扫所有 `skill-markets/*/SKILL.md` | WARN（汇总）|

### §2.2 输出格式

```
[CPCC-SELFCHECK 2026-08-19 14:30:00]
═══════════════════════════════════════════════════════

📋 Skill 安装检查
  ✅ coding-xinfa                  installed
  ✅ goal-mode                     installed
  ⚠️  fullstack4traev11             description 字段缺失
  ✅ gitnexus4Trae                 installed
  ✅ acceptance-discipline         installed
  ✅ trae-security-review          installed

📝 Description 触发词检查
  ✅ coding-xinfa                  含触发场景
  ✅ goal-mode                     含触发词
  ⚠️  fullstack4traev11            description 字段缺失
  ✅ gitnexus4Trae                 含触发场景
  ✅ acceptance-discipline         含触发场景

🔌 GitNexus MCP 探活
  ✅ gitnexus                      MCP alive (3 repos indexed)

🗂️  GitNexus 索引新鲜度
  ⚠️  .gitnexus/                   last analyze: 12 days ago（建议重跑）

🏠 项目 Rules Forge 状态
  ⚠️  project_rule_skill           未 forge，请跑 §3 Step 1

📊 市场 Description 健康度扫描
  ⚠️  7/43 skills description 无触发词或缺失

═══════════════════════════════════════════════════════
Summary: 2 FAIL, 6 WARN, 35 PASS
```

### §2.3 用法

```bash
# 完整检查
node skill-markets/common-project-coding-conf/scripts/cpcc-self-check.mjs

# 只跑关键3 项（1/3/5）
node skill-markets/common-project-coding-conf/scripts/cpcc-self-check.mjs --quick

# JSON 格式（供 agent 解析）
node skill-markets/common-project-coding-conf/scripts/cpcc-self-check.mjs --json
```

---

## §3 锻造协议（forge）

> **目的**: 把项目级 rules 从"永久注入主上下文"改为"按需加载的入口 skill"。
> **脚本**: `scripts/forge_project_rules_skill.py`

### §3.1 调用入口

```python
Skill(name="common-project-coding-conf")
```

### §3.2 锻造步骤

**Step 0 — 前置检查**

```bash
# 检查项目是否有 .trae/rules/
ls .trae/rules/*.md 2>/dev/null | head
# 0 个 → 提示用户先在 .trae/rules/ 放项目级 rule
# ≥1 个 → Step 1
```

**Step 1 — 跑锻造脚本（cpcc 自带）**

```bash
# 默认模式：复制 + 自动注入 frontmatter（源不动）
python ~/.trae-cn/skills/common-project-coding-conf/scripts/forge_project_rules_skill.py --project-root .

# --move 模式：物理移走源 rules 到 .trae/rules/_archived/（防 sub-agent 绕过）
python ~/.trae-cn/skills/common-project-coding-conf/scripts/forge_project_rules_skill.py --project-root . --move

# Windows：
python "$env:USERPROFILE\.trae-cn\skills\common-project-coding-conf\scripts\forge_project_rules_skill.py" --project-root .
```

**Step 2 — 验证产物**

```
.trae/
├── rules/                    # 单一事实来源
│   ├── README.md             # 自动改为强制入口（指向 skill）
│   ├── stack.md              # 自动注入 frontmatter
│   ├── paths.md              # 自动注入 frontmatter
│   ├── git.md                # 自动注入 frontmatter
│   └── coding-standards.md   # 自动注入 frontmatter
└── skills/
    └── project_rules_skills/ # 入口 skill（自动生成）
        ├── SKILL.md
        ├── README.md
        ├── workflows/
        │   └── sub-agent-delegate-load.md
        └── references/       # 复制 .trae/rules/*.md 内容（同步源）
            ├── stack.md
            ├── paths.md
            ├── git.md
            └── coding-standards.md
```

**Step 3 — 全 agent 改走入口**

```
任何主 agent 委派 sub-agent 时 → 头部注入 [PROJECT-RULES-GATE]（见 §4）
任何 sub-agent 启动后 → 先调 Skill(name="common-project-coding-conf") 拿本任务所需 skills 路由 + 项目 rules
```

---

## §4 sub-agent 委派头部模板

```python
Task(
    subagent_type="{agent-type}",
    description="<task-summary>",
    prompt="""
[PROJECT-RULES-GATE]
  必须先调用 Skill(name="common-project-coding-conf") 获取本任务所需 skills 路由 + 项目 rules。
  在 Completion Report 中必须声明 rules_loaded / rules_skipped / skills_loaded 清单。
[/PROJECT-RULES-GATE]

[TASK]
  {task-description, ≤200 chars}
[/TASK]

[OUTPUT]
  必填 4 字段 + rules_loaded / rules_skipped / skills_loaded 清单:
  - artifacts
  - status (PASS | FAIL | PARTIAL)
  - evidence (command + output + file:line)
  - next_hook (任一阶段后钩子,本 skill 无关)
  - rules_loaded: [list of loaded rule files with reason]
  - rules_skipped: [list of skipped rule files]
  - skills_loaded: [list of skills loaded from routing table with reason]
[/OUTPUT]

{task-specific-content}
"""
)
```

完整模板: [workflows/sub-agent-delegate-load.md](workflows/sub-agent-delegate-load.md)

---

## §5 与 fullstack4TraeV11 关系

```
本 skill (common-project-coding-conf)
  ├── §1 路由表       → V11 用户 / 非 V11 用户通用
  ├── §2 自检协议    → V11 兼容（检查 V11 description / 索引）
  ├── §3 锻造协议    → V11 init-from-zero.py Step 5 调用
  └── §4 委派头部    → V11 Task 委派协议兼容（[PROJECT-RULES-GATE] 同名）

V11 (fullstack4TraeV11)
  ├── 13 stage 流水线
  ├── [PIPELINE] 块       (本 skill 不涉及)
  ├── [DOC_WHITELIST] 块   (本 skill 不涉及)
  ├── [FORBIDDEN] 块       (本 skill 不涉及)
  └── [PROJECT-RULES-GATE] 块 (本 skill §4 同名同协议，V11 委派时复用)
```

**关键差异**: 本 skill **不引入** PIPELINE / DOC_WHITELIST / FORBIDDEN 块。V11 子代理的额外约束（如禁读 archive / 阶段门禁）继续由 V11 自身注入。

V11 用户 + 本 skill = 完整流水线；非 V11 用户 + 本 skill = 仅 rules 门禁。

---

## §6 与历史 skill 关系

| 历史 skill | 关系 | 处理 |
|---|---|---|
| `vibe-coding-routes`（未落地） | 概念被本 skill §1 路由表接管 | 不再单独建 |
| `project-rules-gate`（v0.2 已存在） | 全部职责被本 skill 接管 | 删除（forge 脚本 / templates / workflows / references 全迁移到本 skill）|
| `project-rule-skill`（TRAE 本机产物名） | 由本 skill §3 锻造流程产出 | 保留产物名 |
| `fullstack4TraeV11` | 聘用本 skill 协议 | 不动（仅补 description） |

---

## §7 反模式（违反任一即 🛑 REJECT）

```
❌ 跳过 cpcc-self-check 直接开始任务
❌ 跳过 forge 直接 Read .trae/rules/*.md（绕过入口）
❌ Coding agent 误用 subagent_type=search（结构性失败）
❌ 盲信 Completion Report "PASS" → 主上下文执行机械验证
❌ 双写 .trae/rules/ 和 .trae/skills/project_rules_skills/（必须只改源，再 forge 同步）
❌ forge 不加 --move 在高安全等级场景（sub-agent 可绕过 skill 直接 Read 源 rules）
❌ 全量 Read 全部 SKILL.md 撑爆上下文（必须按 §1 路由表按需加载）
❌ 项目已有 .trae/skills/project_rules_skills/ 但内容过期未重 forge
```

---

## §8 关联引用

- [references/forge-protocol.md](references/forge-protocol.md) — 锻造协议完整版
- [references/agent-delegate-protocol.md](references/agent-delegate-protocol.md) — 委派 GATE 头 + Completion Report 校验
- [workflows/sub-agent-delegate-load.md](workflows/sub-agent-delegate-load.md) — 委派头部模板
- [scripts/cpcc-self-check.mjs](scripts/cpcc-self-check.mjs) — 自检脚本
- [scripts/forge_project_rules_skill.py](scripts/forge_project_rules_skill.py) — 锻造脚本
- [templates/SKILL.md.template](templates/SKILL.md.template) — 锻造产物 SKILL.md 模板

---

*本 skill 由 common-project-coding-conf v1.0 接管了 project-rules-gate v0.2 + vibe-coding-routes（未落地）的合并职责。V11 用户可同时安装两个，行为一致；非 V11 用户装本 skill 即可获得完整 PROJECT-RULES-GATE + 路由 + 自检能力。*