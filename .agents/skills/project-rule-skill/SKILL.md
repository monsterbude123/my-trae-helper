---
name: project-rule-skill
description: 项目级规则加载网关 — 任何任务开始前调用本 skill 获取本会话所需 rules，再按需 Read。Use when any task requires loading project rules — paths / governance / code-style / stack / git / 反例库 / 决策层级 / 路径权限 / 分支规则.
version: 2.0.0
updatedAt: 2026-08-15
requires:
  - skill-creation-workflow
  - skills-development-rules
  - protocol-coverage-protocol
---

# project-rule-skill — 项目级规则加载网关

> **强制**:本 skill 是项目内 `Skill` 工具的入口。任何主 agent / sub-agent 在本项目执行任务前,**必须**先调用本 skill 获取本会话需要的 rules,再按需 Read。
>
> **禁止**:直接 Read `references/*.md`(本目录之外)或 `skill-markets/fullstack4TraeV11/references/*.md` 而不走本 skill — 会污染上下文 + 绕过强制协议。
>
> **V11.8.0.1 升级说明(2026-08-15 NEW)**:
> - **本目录新增 `references/` 子目录**,与 SKILL.md 同包统一管理协议规范文件
> - 三个 V11.8.0 协议(`skill-creation-workflow.md` / `skills-development-rules.md` / `protocol-coverage-protocol.md`)已从 `.agents/rules/` 迁移到本目录
> - 原 `.agents/rules/` 路径保留 redirect stub(防死链)
> - frontmatter 新增 `version: 2.0.0` + `requires` 字段声明本 skill 依赖的协议

---

## §1 加载协议(4 步)

### Step 1 — 调用本 skill

```
Skill(name="project-rule-skill")
```

### Step 1.5 — 加载经验沉淀 skill (路径 A,2026-08-14 落地)

> **强制**: 调用本 skill 后必须**立刻**调用 `self-improving-agent`,把跨会话经验注入当前会话上下文。

```
Skill(name="self-improving-agent")
```

**行为**:
- ✅ 成功:把全局 LEARNING/ERROR/FEATURE_REQUESTS 加载进会话上下文(只读)
- ⚠️ 失败(用户未全局安装):不阻断会话,在响应开头标注 `[learning-skip]`
- ❌ 禁止:跳过本步直接进入 Step 2

**理由**:见 [.agents/rules/learning.md §5](../../rules/learning.md) — 路径 A 网关注入。

### Step 2 — 输出:本会话所需 rules 清单

格式:

```yaml
needed_rules:
  - <relative path>
reason: "<本任务场景关键词>"
```

### Step 3 — 主 agent / sub-agent 只 Read needed_rules

- ✅ 用 `Read` 工具加载 needed_rules 列出的文件
- ❌ **禁止** 直接 Read 未声明的 rules
- ❌ **禁止** Read 全部 rules(按需加载,避免撑爆上下文)

### Step 4 — 在响应中声明

主 agent / sub-agent 必须在响应开头声明:

```
本会话已加载 rules: <loaded list>
未加载: <skipped list>
```

### Step 5 — 按场景关键词自动加载相关 skill (V2.1 新增)

任务启动后,根据场景关键词自动 Skill() 调用相关 skill,**禁止凭记忆调用**:

| 场景关键词 | 自动加载的 skill |
|------------|----------------|
| `测试` / `test` / `E2E` / `验收` / `verify` | `acceptance-discipline` / `test-experience` |
| `安全` / `secret` / `扫描` / `audit` | `trae-security-review` |
| `新建技能` / `skill` / `create` / `verify` | `skill-acceptance` + **V11.8.0.1** [`references/skill-creation-workflow.md`](references/skill-creation-workflow.md)(协议先行 + 多维度一致) + [`references/skills-development-rules.md`](references/skills-development-rules.md)(短细则) |
| `protocol` / `协议先行` / `*-protocol.md` | **V11.8.0.1** [`references/protocol-coverage-protocol.md`](references/protocol-coverage-protocol.md)+ `python scripts/_check_protocol_coverage.py --protocol <path> --check` |
| `catalog` / `Skill catalog` / `skill-catalog.yaml` | **V11.8.0.1** [`tests/catalogs/catalog-protocol.md`](../../../tests/catalogs/catalog-protocol.md)+ `python tests/catalogs/_check_skill_catalog.py` |
| `Gate` / `pre-commit` / `pre-push` / `CI` | `skill-acceptance §7` + `agent-dev-control-kit §11` |
| `GH Actions` / `workflow` / `push` / `force-push` / `workflow_dispatch` | `skill-acceptance §7` + `.github/workflows/*.yml` 必读 + 必走 guard-smith 委派(白名单) |
| `重构` / `升级` / `V{N}` | `fullstack-skill-architect` |
| `AGENTS.md` / `README` / `文档` | 不自动加载,改 docs/ 即可 |

---

## §2 路由表（场景 → 必加载 rules）

| 场景关键词 | 必加载 references/ |
|------------|-------------------|
| `cli` / `bin/` / `src/` / `打包` / `发布` / `npm` | [project-iron-laws.md §E](../../skill-markets/fullstack4TraeV11/references/project-iron-laws.md) |
| 新建 / 修改 / 删除 skill | [project-iron-laws.md §F](../../skill-markets/fullstack4TraeV11/references/project-iron-laws.md) + [.agents/rules/README.md](../../rules/README.md) + **[references/skill-creation-workflow.md](references/skill-creation-workflow.md)**(V11.8.0.1 路径迁移 + 多维度一致) + [references/skills-development-rules.md](references/skills-development-rules.md)(V11.8.0.1 短细则) |
| 反例 / 回滚 / 被质问 / 不耐慎 | [project-iron-laws.md §A R-1~R-3](../../skill-markets/fullstack4TraeV11/references/project-iron-laws.md) |
| 升级 / P0 / P1 / 决策 / ADR | [project-iron-laws.md §B L0~L9](../../skill-markets/fullstack4TraeV11/references/project-iron-laws.md) + [skeptical-validation-protocol.md](../../skill-markets/fullstack4TraeV11/references/skeptical-validation-protocol.md) |
| 分支 / commit / release | [project-iron-laws.md §D](../../skill-markets/fullstack4TraeV11/references/project-iron-laws.md) |
| 路径 / 读写权限 / archive / trash | [project-iron-laws.md §C](../../skill-markets/fullstack4TraeV11/references/project-iron-laws.md) |
| 流程太重 / 升级技能 / 矫枉过正 | [skill-optimization-method.md](../../skill-markets/fullstack4TraeV11/references/skill-optimization-method.md) |
| 不确定 / 全部场景 | 全部 rules |

> 真实路径以本仓库 `skill-markets/fullstack4TraeV11/references/` 为准（V11.2 蒸馏）。

---

## §3 与 AGENTS.md 的关系

| 内容 | 在哪里 |
|------|--------|
| AGENTS.md §1.5 会话启动协议 | 主 agent 启动时调用本 skill 的引用源 |
| AGENTS.md §2 铁律(10 条) | 主 agent 必读 → 本 skill 负责路由 |
| AGENTS.md §3 行为规约 + §3.1 表态信号 | 反例库 R-3 联动 → 本 skill 反例路由命中 |
| AGENTS.md §7 项目级方法论 | 9 个 references/ 引用,本 skill §2 路由表覆盖 |
| **本 skill — 项目 rules 加载网关** | `.agents/skills/project-rule-skill/SKILL.md` |
| **实际 rule 内容(single source of truth,V11.8.0.1 NEW)** | **本目录 `references/` 子目录**(`skill-creation-workflow.md` / `skills-development-rules.md` / `protocol-coverage-protocol.md`)+ `skill-markets/fullstack4TraeV11/references/*.md` |
| ~~V11.8.0 旧路径(已迁移)~~ | ~~`.agents/rules/skill-creation-workflow.md` 等~~ — 现 redirect stub |

---

## §4 Sub-Agent 委派头部（主 agent 强制注入）

```
[PROJECT-RULE-GATE]
  必读 skill: Skill(name="project-rule-skill")
  必读后输出 needed_rules 清单
  只 Read needed_rules,禁止 Read 未声明的 rules
  在响应中必含字段:
    rules_loaded: [...]
    rules_skipped: [...]
```

---

## §5 反模式

- ❌ 跳过本 skill 直接 Read `.agents/rules/*.md`(V11.8.0.1 后只读 redirect stub,真内容在本目录 `references/`)
- ❌ 跳过本 skill 直接 Read `references/*.md`(本目录 `references/` 下的协议)— 仍要走本 skill 路由
- ❌ Read 全部 rules(即使本项目只有 N 个 references)
- ❌ 在用户未确认新场景时复用旧会话的 rules 列表
- ❌ 把 `Skill(name="project-rule-skill")` 当成"可选"——它是强制
- ❌ 把本 skill 退化为可选(vvicat 上游是 fallback,本项目主 agent 启动时优先用本 skill)

---

## §6 一句话铁律

**会话开始 = `Skill(name="project-rule-skill")` 优先 → `Skill(name="self-improving-agent")` 必跟,再做事。**

---

## §7 signal-detect 自动调用契约(A+B+C 组合的关键环节,2026-08-14)

> **强制**: 主 agent 在以下时机必须调 `scripts/agent-signal-detect.mjs "<user_msg>"`,把会话级 hint 落入 `logs/agent-hints.jsonl`,由 post-commit 钩子或显式 `self-improving-agent scan-hints` 转入 `.learnings/ERRORS.md` / `FEATURE_REQUESTS.md`。

### §7.1 触发时机(强制契约)

| 时机 | 调用 | 原因 |
|------|------|------|
| 每个新 turn 第一条响应前 | `signal-detect "$last_user_msg"` | 加载 SIA 后立即捕获信号,阻断"漏信号"路径 |
| 用户消息含 AGENTS.md §3.1 表态信号(不耐慎/纠正/特性请求) | 调一次 | 把"懂了吗/你确定/不对/能 XXX 吗"等显式声明转 hint |
| Commit / lint / test 失败回显前 | 调一次 | 把工具失败归类到 ERRORS.md |
| 用户消息末尾是问号 | 调一次(防止遗漏) | 把"为什么/怎么"问号归类到 FEATURE_REQUESTS |

### §7.2 调用方式

**argv 模式**(推荐):
```bash
node scripts/agent-signal-detect.mjs "你确定这样行吗"
```

**stdin 模式**(长文本):
```bash
echo "$last_user_msg" | node scripts/agent-signal-detect.mjs
```

**提示**:`signal-detect.mjs` 内置 stdin/argv 二选一探测(WSL/Windows 兼容),主 agent 直接调即可。

### §7.3 漏调代价(铁律)

| 漏调场景 | 后果 | 关联反例 |
|---------|------|----------|
| 漏调 signal-detect | 用户纠正/不耐慎/特性请求**永不进 ERRORS.md** | **AP-9**(新增,固化到 `trap-instructions.yaml`) |
| signal-detect 命中但 post-commit 没跑 scan-hints | hint 累积在 jsonl 不被消费 | AP-8 已有 |
| 主 agent 自报"已调过"实际没调 | LLM 幻觉路径,需在响应开头显式声明 `[signal-scanned]` 标记 |

### §7.4 主 agent 响应标记(强制)

每次 signal-detect 调用后,响应开头必须包含:

```
[signal-scanned] hits=<count> files=[agent-hints.jsonl]
```

- `hits=N`: 本轮信号检测命中条数(0/1/N)
- `files=[...]`: 写入的 hint 文件列表

**漏标 = §7.3 漏调代价 = AP-9 反例触发**。

---

## §8 一句话铁律(扩充)

**会话开始 = `Skill("project-rule-skill")` → `Skill("self-improving-agent")` → 每个 turn 调 `signal-detect "$last_msg"`,再做事。**
