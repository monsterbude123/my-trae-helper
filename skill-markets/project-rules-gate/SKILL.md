---
name: project-rules-gate
description: 项目级 Rules 强制加载与子代理门禁 — 把项目 .trae/rules/ 锻造为 project_rules_skills 入口 skill，并强制任何 sub-agent 行动前必走该入口 + Completion Report 声明 rules_loaded/skipped。完全独立于 fullstack4TraeV11，可单独安装使用。命中：想给子代理强制装一个项目级规则加载门禁 / 想把散落的 rules 文件收纳成一个可按需加载的 skill / 不想让 sub-agent 绕开 rules 直接 read 文件。
---

# Project Rules Gate — 项目级 Rules 强制加载与子代理门禁

> **职责**: 两件事
> 1. **锻造**: 把项目 `.trae/rules/*.md` 收纳为 `.trae/skills/project_rules_skills/` 入口 skill(避免主上下文全量注入撑爆)
> 2. **门禁**: 强制任何 agent(主 / sub)行动前先调 `Skill(name="project-rules")`,在 Completion Report 声明 `rules_loaded` / `rules_skipped`
>
> **强制级别**: 🔴 P0 — 任何 sub-agent 跳过 = 🛑 REJECT
> **依赖**: 零。完全独立于 fullstack4TraeV11,也不依赖 GitNexus / 任何编排器。

---

## §0 铁律(10 条)

```
1. MUST 锻造入口前先验证 .trae/rules/ 存在且有 ≥1 个 .md 文件,否则拒绝执行
2. MUST 单一事实来源: 锻造产物 .trae/skills/project_rules_skills/references/{rule}.md 的内容
   = .trae/rules/{rule}.md 的 copy(脚本同步,不写软链接,Windows 兼容)
3. MUST 任何修改必须改 .trae/rules/{rule}.md(默认模式)或 .trae/rules/_archived/{rule}.md(--move 模式)
   + 重新跑 forge 同步到 references/(避免双写漂移)
4. MUST 主 agent 委派 sub-agent 时,prompt 头部必含 [PROJECT-RULES-GATE] 块
5. MUST sub-agent Completion Report 必含 rules_loaded / rules_skipped YAML 字段
6. MUST 路由表 §3 缺场景时 = 全加载(避免漏加载)
7. NEVER 禁止 sub-agent 直接 Read .trae/rules/*.md 或 _archived/*.md(绕过 skill = 上下文撑爆)
8. NEVER 禁止全量 Read 全部 rules(按 §3 路由表按需加载)
9. NEVER 禁止用 grep / Glob 搜 rules 内容(必须走 skill 入口)
10. SHOULD 主 agent 首次进入项目时主动跑一次 forge(默认或 --move 模式按安全等级选)
```

---

## §1 调用入口

```python
Skill(name="project-rules-gate")
```

入口加载后看到本文件,主 agent 决定:
- 项目无 `.trae/rules/` → 跳 §2 Step 0
- 已有 `.trae/rules/` 但无 `.trae/skills/project_rules_skills/` → 跳 §2 Step 1
- 两者齐全 → 跳 §4(主 agent 委派时注入 GATE 头)

---

## §2 锻造流程(主 agent 一次性执行)

> 详见 [references/forge-protocol.md](references/forge-protocol.md)

**Step 0 — 前置检查**

```bash
# 检查项目是否有 .trae/rules/
ls .trae/rules/*.md 2>/dev/null | head
# 0 个 → 提示用户先在 .trae/rules/ 放项目级 rule
# ≥1 个 → Step 1
```

**Step 1 — 跑锻造脚本(本 skill 自带)**

```bash
# 默认模式: 复制 + 自动注入 frontmatter(源不动)
python ~/.trae-cn/skills/project-rules-gate/scripts/forge_project_rules_skill.py --project-root .

# --move 模式: 物理移走源 rules 到 .trae/rules/_archived/(防 sub-agent 绕过)
python ~/.trae-cn/skills/project-rules-gate/scripts/forge_project_rules_skill.py --project-root . --move

# Windows:
python "$env:USERPROFILE\.trae-cn\skills\project-rules-gate\scripts\forge_project_rules_skill.py" --project-root .
```

**默认行为**:

1. 检测每个 rule 是否含 YAML frontmatter,缺则自动注入(description 字段从文件名推断)
2. 复制到 `.trae/skills/project_rules_skills/references/`
3. 改写 `.trae/rules/README.md` 为强制入口

**--move 模式额外行为**:

4. 把 `.trae/rules/{rule}.md` 物理移走到 `.trae/rules/_archived/{rule}.md`(保留 git 历史 + 可回溯)

**Step 2 — 验证产物**

默认模式产物:
```
.trae/
├── rules/                    # 单一事实来源
│   ├── README.md             # 自动改为强制入口(指向 skill)
│   ├── stack.md              # 自动注入 frontmatter
│   ├── paths.md              # 自动注入 frontmatter
│   ├── git.md                # 自动注入 frontmatter
│   └── coding-standards.md   # 自动注入 frontmatter
└── skills/
    └── project_rules_skills/ # 入口 skill(自动生成)
        ├── SKILL.md
        ├── README.md
        ├── workflows/
        │   └── sub-agent-delegate-load.md
        └── references/       # 复制 .trae/rules/*.md 内容(同步源)
            ├── stack.md
            ├── paths.md
            ├── git.md
            └── coding-standards.md
```

`--move` 模式产物:
```
.trae/
├── rules/
│   ├── README.md             # 强制入口
│   └── _archived/            # 移走的原 rules(归档,前缀 _ 防二次扫描)
│       ├── stack.md
│       ├── paths.md
│       ├── git.md
│       └── coding-standards.md
└── skills/
    └── project_rules_skills/
        └── references/       # 唯一访问入口(sub-agent 只能通过这里 Read)
            ├── stack.md
            ├── paths.md
            ├── git.md
            └── coding-standards.md
```

**Step 3 — 全 agent 改走入口**

```
任何主 agent 委派 sub-agent 时 → 头部注入 [PROJECT-RULES-GATE](见 §5)
任何 sub-agent 启动后 → 先调 Skill(name="project-rules") 拿本任务所需 rules
```

---

## §3 路由表:场景关键词 → 必加载 rules

> **使用方式**: 选 1 个或多个。**未列出场景 = 全加载**。
> **本表是默认骨架**,项目首次跑 forge 后,主 agent 可按 `.trae/rules/` 实际文件扩展本表(不破坏骨架)。

| 场景关键词 | 必加载 rules |
|-----------|-------------|
| 改 API / 改契约 | coding-standards.md + paths.md |
| 改前端 / 改样式 | coding-standards.md + paths.md |
| 改依赖 / 改 build | stack.md + paths.md |
| 提 PR / 合分支 | git.md + paths.md |
| 修 bug | coding-standards.md + paths.md |
| 任何场景(未列出) | 全加载 |

**项目自定义路由**: 跑 forge 后,主 agent 可在 `.trae/skills/project_rules_skills/SKILL.md` §3 扩展本表(改一处即可,本 skill 模板不再要求)。

---

## §4 sub-agent 必走 — Completion Report 声明

sub-agent 必须在 Completion Report 显式声明已加载/跳过的 rules:

```yaml
rules_loaded:
  - coding-standards.md (reason: 改 API)
  - paths.md (reason: 改 API)
rules_skipped:
  - stack.md
  - git.md
```

缺字段 = 🛑 REJECT。

---

## §5 主 agent 委派 sub-agent 头部必加

```python
Task(
    subagent_type="{agent-type}",
    description="<task-summary>",
    prompt="""
[PROJECT-RULES-GATE]
  必须先调用 Skill(name="project-rules") 获取本任务所需 rules,再开始工作。
  在 Completion Report 中必须声明 rules_loaded / rules_skipped 清单。
[/PROJECT-RULES-GATE]

[TASK]
  {task-description, ≤200 chars}
[/TASK]

[OUTPUT]
  必填 4 字段 + rules_loaded / rules_skipped 清单:
  - artifacts
  - status (PASS | FAIL | PARTIAL)
  - evidence (command + output + file:line)
  - next_hook (任一阶段后钩子,本 skill 无关)
  - rules_loaded: [list of loaded rule files with reason]
  - rules_skipped: [list of skipped rule files]
[/OUTPUT]

{task-specific-content}
"""
)
```

完整模板: [workflows/sub-agent-delegate-load.md](workflows/sub-agent-delegate-load.md)
协议说明: [references/agent-delegate-protocol.md](references/agent-delegate-protocol.md)

---

## §6 为什么有这个 skill?

`.trae/rules/` 历史上散落 N 个文件(stack / paths / git / coding-standards 等),每个会话通过 `workspace_rules` 永久注入主上下文,总量 ~800+ 行,**直接撑爆 context**。

| 关注点 | 在哪里 |
|--------|-------|
| 怎么找到需要的 rule | 本 SKILL.md(主入口) |
| 实际 rule 内容(single source of truth) | `.trae/rules/*.md` |
| 入口 skill 副本(sync) | `.trae/skills/project_rules_skills/references/` |
| 委派头部模板 | `.trae/skills/project_rules_skills/workflows/` |

---

## §7 反模式(违反任一即 🛑 REJECT)

```
❌ 跳过 Skill(name="project-rules") 而用 grep / Glob 搜 rules
❌ Sub-agent 不声明 rules_loaded / rules_skipped
❌ 主 agent 委派 sub-agent 时不注入 [PROJECT-RULES-GATE] 头部
❌ Read 全部 rules 撑爆上下文
❌ 直接 Read .trae/rules/*.md(默认模式下绕过 skill)
❌ 直接 Read .trae/rules/_archived/*.md(--move 模式下绕过 skill)
❌ 双写(同时改源 rules 和 .trae/skills/project_rules_skills/references/)
   → 必须只改源,再跑 forge 同步
❌ 项目已有 .trae/skills/project_rules_skills/ 但内容过时
   → 主 agent 启动时检查 mtime,过期则提醒重跑 forge
❌ 高安全等级项目跑 forge 不加 --move
   → sub-agent 可绕过 skill 直接 Read 源 rules,门禁失效
```

---

## §8 与 fullstack4TraeV11 的关系

```
本 skill    =  fullstack4TraeV11 内部 [PROJECT-RULES-GATE] 机制 的可独立分发版本
V11 init    =  create_rules_skill()  Step 5  ← 本 skill forge_project_rules_skill.py
V11 委派头  =  [PIPELINE] + [DOC_WHITELIST] + [FORBIDDEN] + [PROJECT-RULES-GATE]  ← 本 skill 只取 PROJECT-RULES-GATE
V11 协议    =  PIPELINE 阶段式(13 stage) ← 本 skill 不依赖,纯规则门禁
```

**关键差异**: 本 skill **不引入** PIPELINE / DOC_WHITELIST / FORBIDDEN 块。V11 子代理的额外约束(如禁读 archive / 阶段门禁)继续由 V11 自身注入。

---

## §9 关联引用

- [references/forge-protocol.md](references/forge-protocol.md) — 锻造协议(从 .trae/rules 到入口 skill)
- [references/agent-delegate-protocol.md](references/agent-delegate-protocol.md) — 委派 GATE 头 + Completion Report 校验
- [workflows/sub-agent-delegate-load.md](workflows/sub-agent-delegate-load.md) — 委派头部模板
- [scripts/forge_project_rules_skill.py](scripts/forge_project_rules_skill.py) — 锻造脚本(自包含)
- [templates/SKILL.md.template](templates/SKILL.md.template) — 生成物 SKILL.md 模板
- `~/.trae-cn/skills/fullstack4TraeV11/templates/project-rules-skill-template/` — V11 内部原版(本 skill 剥离版,自包含)

---

*本 skill 是 fullstack4TraeV11 `[PROJECT-RULES-GATE]` 机制的独立分发版。V11 用户可同时安装两个,行为一致;非 V11 用户装本 skill 即可获得相同门禁。*
