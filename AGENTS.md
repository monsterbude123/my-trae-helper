# my-trae-helper — Trae IDE 技能市场 + CLI 元项目

> **这是元项目**：开发和管理 Trae IDE 技能包 + 维护跨 Agent 技能市场 CLI（`@my-trae-helper/cli`）。两条腿走路：
> - **CLI 建设**：`bin/cli.mjs` + `src/*.mjs` — `npx @my-trae-helper/cli add <skill>` 一键装到 22+ Agent
> - **技能库建设**：`skill-markets/<name>/SKILL.md` — 23+ 个精选技能，按 AgentSkills.io 开放标准

---

## §0 实战项目位置

`D:\workspace\my-trae-helper\example\` 子目录都是软连接目录。

---

## §1 项目定位（双主调）

```
my-trae-helper/
├── bin/cli.mjs               # @my-trae-helper/cli 入口（npx trae-skills）
├── src/                      # CLI 实现（scanner / installer / agents / add|list|remove|update|init）
├── scripts/prepare-publish.mjs  # 发布预处理（剥 .pyc / __pycache__ / .zip）
├── package.json              # bin: trae-skills → ./bin/cli.mjs
├── skill-markets/            # 23+ 个技能（每个含 SKILL.md + 可选 agents/ references/ scripts/）
├── skill-markets/CAPABILITY-MAP.md   # 技能索引 + 共享能力注册表
└── SECURITY-MAP.md           # 每个 skill 的安全评分
```

- **`~\.trae-cn\skills`** ← Trae CN 装载位置（CLI `add` 时建 symlink/junction）
- **`skill-markets/`** —— 禁止在此目录外创建/修改技能
- **`docs/references/`** —— 参考材料，禁止修改

---

## §1.5 会话启动加载协议（强制）

> **每次 Agent 唤起会话时，第一步必须加载 project rule skill**。

```
1. 主 Agent → Skill(name="project-rule-skill")
2. 输出 needed_rules 清单
3. 只 Read needed_rules 列出的文件
4. 委派 sub-agent → 头部注入 [PROJECT-RULE-GATE]
```

详见 [.trae/skills/project-rule-skill/SKILL.md](.trae/skills/project-rule-skill/SKILL.md) 和 [skill-markets/fullstack4TraeV11/references/sub-agent-rules.md](skill-markets/fullstack4TraeV11/references/sub-agent-rules.md)。

---

## §2 铁律（强约束，做不到立刻停）

1. **YAML frontmatter**：SKILL.md 必带 `name` + `description`；推荐 `version` / `requires`
2. **技能位置硬约束**：技能只能在 `skill-markets/<name>/` 下，不发明路径
3. **Agent 文件 ≤150 行 + 铁律 ≤10 条**：超过立即精简（防上下文击穿）
4. **安全审查必走**：新建/引入/变更 skill 必跑 `scan_skills_dir.py` + 更新 SECURITY-MAP.md
5. **能力去重**：新增脚本/技能必先 Read `CAPABILITY-MAP.md`「共享能力注册表」
6. **不在项目路径之外写脚本**：所有临时产物必须落 `logs/` 或 `.publish/`
7. **写代码保持 ponytail 思路**：最简实现、标准库优先
8. **任务明确时才用 fullstack 流程**：不加不必要的阶段
9. **禁止自主部署**：不主动执行安装命令，除非用户明确要求"部署"、"安装技能"
10. **SKILL.md/agents 引用优先**：核心铁律 + 骨架流程内联，详细内容 references/ 引用，禁止内联全文

**§2.1 路径位置**：`scripts/` 放 Node/Python 脚本；`logs/` 放临时输出；不在根目录散落脚本。

**§2.2 CLI 多文件拆分**：≥ 3 个职责的脚本必拆 `src/<module>.mjs`；只允许 bin/cli.mjs 做路由。

---

## §3 Agent 回复行为规约（V10.12.5 NEW — 防"问下一步"模式）

```
1. 不问"要不要做 X" —— 做或不做，不问（方向性决策例外：方案 A vs B 用 AskUserQuestion）
2. 不挂 P0/P1/P2/P3 backlog —— 做完或不做
3. 不写"我没做但应诚实声明的 N 项" —— 做了标 ✅，没做的直接"不做" + 原因
4. 不写"下一轮升级前 backlog" —— 这是拖延仪式
5. 结尾报告只用三类结尾句之一：
   - 完成："完成报告 + 修改清单"（无问句）
   - 部分："X 已完成，Y 不做（原因）"（无问句）
   - 失败："🛑 阻塞：X（具体缺什么）"（无问句）
6. 保留 AskUserQuestion 用于：方案选择 / 参数确认 / 多分支决策
7. 子代理返回后主上下文自查结尾是否含"要不要 / 可选 / backlog / 下一轮 / 我没做"
```

### §3.1 用户表态信号触发条件（V10.12.6 NEW — 防回滚）

```
MUST 终止提问，当用户输入包含以下任一信号：
  - 表态类："懂了吗" / "能懂了吗" / "你到底做啥" / "我是没有说明白吗" / "我说得够清楚吗"
  - 纠正类：连续 2 轮 Agent 回答与用户预期不一致
  - 确认类：用户已给出方案选择，Agent 重新提问

MUST 选保守方案：
  - 改 < 不改（最小变更）
  - 改 src/ < 改 skill-markets/（项目代码优先于新建技能）
  - 显式 < 隐式（可读优于可推）

输出格式："我做了 X，Y 不做（原因）" —— 不用问句结尾
```

**详见反例库 R-3**：[references/project-iron-laws.md §A R-3](skill-markets/fullstack4TraeV11/references/project-iron-laws.md)

---

## §4 Skill 与 Agent 严格区分

| 概念 | 目录 | 加载方式 | 何时用 |
|------|------|---------|--------|
| Skill（技能） | `skill-markets/<name>/` | `Skill` 工具加载 | 改变主 Agent 行为/知识 |
| Agent（子代理） | `skill-markets/<name>/agents/*.md` | `Task` 工具委派 | 流水线中的专业化工人 |

- `skill-markets/` 放技能，`agents/` 放 Agent 定义，**严禁交叉**
- Agent 文件名 kebab-case，**不带 `-agent` 后缀**（已在 `agents/` 目录内）
- 新包优先做纯 Skill，多角色流水线才引入 Agent

### YAML frontmatter 规范

```yaml
---
name: skill-name               # 全小写 kebab-case
description: 一句话 + 触发条件
requires:                      # 有依赖时必须声明
  skills: [dependency-name]    # 硬依赖：必须先加载
  optional: [optional-name]    # 软引用：建议但不强制
---
```

---

## §5 安全审查流程（强制门禁）

> 新建/引入/变更 skill 必须走流程一/二/三。审查后更新 [SECURITY-MAP.md](SECURITY-MAP.md) §量化评分。

```
决策矩阵：
    HIGH 真实风险    MEDIUM 真实风险    准入
    0                ≤ 3                🟢 PASS
    0                > 3                🟡 WARNING（人工审查）
    ≥ 1              任意                🛑 BLOCKED（拒绝/修复）
```

执行：

```bash
python skill-markets/trae-security-review/scripts/scan_skills_dir.py skill-markets/<pkg>
```

---

## §6 能力地图（新建/修改前必读）

| 文件 | 何时读 |
|------|------|
| [skill-markets/CAPABILITY-MAP.md](skill-markets/CAPABILITY-MAP.md) | 加新技能 / 新脚本前 |
| [SECURITY-MAP.md](SECURITY-MAP.md) | 加新 skill / 引入第三方 / 改脚本后 |
| [README.md](README.md) | 改 CLI 行为 / 加新 agent 支持 |
| [skill-markets/fullstack4TraeV11/references/skill-optimization-method.md](skill-markets/fullstack4TraeV11/references/skill-optimization-method.md) | 觉得流程太重 / 升级技能时 |
| [skill-markets/fullstack4TraeV11/references/skeptical-validation-protocol.md](skill-markets/fullstack4TraeV11/references/skeptical-validation-protocol.md) | P0/P1 决策 / 改既有规则前 |
| [skill-markets/fullstack4TraeV11/references/project-iron-laws.md](skill-markets/fullstack4TraeV11/references/project-iron-laws.md) | 反例库 / 决策层级 / 路径权限 / 分支规则 |

---

## §7 项目级方法论（指针化引用，不内联）

> 这些方法是项目级方法论。**核心摘要** + **真实路径**——详细内容按需 Read 引用文件。

### §7.1 反例库（Anti-Patterns）

- **R-1** 意图误读 → 误建技能包
- **R-2** 路径拼接用 `Path.resolve` 误删源
- **R-3** 用户表态信号未结构化

**真实路径**：[skill-markets/fullstack4TraeV11/references/project-iron-laws.md §A](skill-markets/fullstack4TraeV11/references/project-iron-laws.md)

### §7.2 决策层级 L0~L9（V11.2 蒸馏）

| 层级 | 语义 |
|:---:|------|
| L0 | 元规则（改 AGENTS.md 顶层结构） |
| L1 | 架构决策 → ADR |
| L2 | 模块边界 |
| L3 | API 契约 |
| L4 | 内部实现 |
| L5 | 测试规范 |
| L6 | 命名规范 |
| L7 | 注释 / 文档 |
| L8 | 兼容保留（必含"保留原因 / L9 计划"注释） |
| L9 | 兼容清理 |

**判定原则**：≥ L5 → state-card 更新；≥ L3 → `impact()` 评估；≥ L1 → `decisions/ADR` 文档。

**真实路径**：[skill-markets/fullstack4TraeV11/references/project-iron-laws.md §B](skill-markets/fullstack4TraeV11/references/project-iron-laws.md)

### §7.3 路径读写权限分离（V11.2 蒸馏）

- 同一路径多张表 → **写权限取最严**
- `docs/specs/` 可写可读可走 archive；`docs/archive/` 只可读不可写不可删；`dist/` / `build/` 不可读不可写，走 `_trash_<ts>/`
- 本项目映射：`skill-markets/` 可写但删要走 `_archived_<ts>/`；`docs/references/` 禁改

**真实路径**：[skill-markets/fullstack4TraeV11/references/project-iron-laws.md §C](skill-markets/fullstack4TraeV11/references/project-iron-laws.md)

### §7.4 Change ↔ Feature 分支 1:1（V11.2 蒸馏）

```
1 change = 1 feature 分支 = N commit
change-id 命名 = {YYYY-MM-DD}-{kebab-name}
feature 从 release/v{MAJOR}.x 拉取
commit 含 stage 标签（prep/design/impl/verify/bug/health）
```

**真实路径**：[skill-markets/fullstack4TraeV11/references/project-iron-laws.md §D](skill-markets/fullstack4TraeV11/references/project-iron-laws.md)

### §7.5 CLI 建设铁律（@my-trae-helper/cli）

- `bin/cli.mjs` 唯一入口，`src/*.mjs` 各司其职
- Windows symlink 用 junction；YAML 解析用 yaml 包；交互用 `@inquirer/prompts` v7+ `checkbox`
- 发布前 `scripts/prepare-publish.mjs` 预处理（剥 `.pyc/.zip/cache`），用户未授权不发布

**真实路径**：[skill-markets/fullstack4TraeV11/references/project-iron-laws.md §E](skill-markets/fullstack4TraeV11/references/project-iron-laws.md)

### §7.6 技能库建设铁律

- 目录结构 `SKILL.md` + 可选 `agents/ references/ scripts/ assets/`；`SKILL.md ≤ 500 行`
- `name` = 目录名 kebab-case；`description` 第三人称 + "做什么 + 何时用 + 触发词"
- 装完提示"重启 IDE"

**真实路径**：[skill-markets/fullstack4TraeV11/references/project-iron-laws.md §F](skill-markets/fullstack4TraeV11/references/project-iron-laws.md)

### §7.7 skill-optimization-method — 技能包优化升级方法论

**何时加载**："技能包太重" / "想精简" / "升级 X 技能" / "进入 V{N} 升级流程" / "我有点担心矫枉过正"

**真实路径**：[skill-markets/fullstack4TraeV11/references/skill-optimization-method.md](skill-markets/fullstack4TraeV11/references/skill-optimization-method.md)

**核心要点**：11 铁律（体积诊断 / 根因分层 / 外部对标 / 方案分级 / 决策前置 / 核心保底 / 缺口对照 / 三级分级 / 最小修复 / 门禁显式 / **质疑性校验必走**）

### §7.8 knowledge-system-upgrade — 知识库系统升级方法论

**何时加载**："评估这个知识库" / "文档召回质量差" / "Agent 盲信过期文档" / "对标 GitNexus"

**真实路径**：[skill-markets/fullstack4TraeV11/references/knowledge-system-upgrade.md](skill-markets/fullstack4TraeV11/references/knowledge-system-upgrade.md)

### §7.9 skeptical-validation-protocol — 质疑性校验协议

**何时加载**：任何升级/P0/P1 决策前必走。

**真实路径**：[skill-markets/fullstack4TraeV11/references/skeptical-validation-protocol.md](skill-markets/fullstack4TraeV11/references/skeptical-validation-protocol.md)

**核心方法**：§1 P0/P1 必要性质疑（根因验证 / 责任主体 / 重叠校验 / 成本校验 4 维度）；§2 通用质疑三层（问题 / 方案 / 实施）；§3 强制声明格式

---

## §8 已开发的技能包

| 技能包 | 路径 | 说明 |
|--------|------|------|
| fullstack4TraeV11 | `skill-markets/fullstack4TraeV11/` | 全栈文档驱动开发 V10 — 满分硬门禁 + 五阶段流水线 + spec-purge 物理归档 |

---

## §9 安装技能（本地开发用）

**推荐（用刚开发的 CLI）**：

```bash
node bin/cli.mjs add <skill-name> -a trae-cn -y
node bin/cli.mjs list -a trae-cn
node bin/cli.mjs remove <skill-name> -a trae-cn -y
```

**备用（软链方式）**：

```powershell
$skillPath = "$env:USERPROFILE\.trae-cn\skills\{name}"
if (Test-Path $skillPath) {
    Write-Host "⚠️ 已安装：$skillPath"
} else {
    New-Item -ItemType SymbolicLink -Path $skillPath -Target "${PWD}\skill-markets\{name}" -Force
    Write-Host "✅ 安装完成，请重启 IDE"
}
```

---

<!-- gitnexus:start -->
# GitNexus — Code Intelligence

This project is indexed by GitNexus as **my-trae-helper** (17139 symbols, 19679 relationships, 212 execution flows). Use the GitNexus MCP tools to understand code, assess impact, and navigate safely.

> Index stale? Run `node .gitnexus/run.cjs analyze` from the project root — it auto-selects an available runner. No `.gitnexus/run.cjs` yet? `npx gitnexus analyze` (npm 11 crash → `npm i -g gitnexus`; #1939).

## Always Do

- **MUST run impact analysis before editing any symbol.** Before modifying a function, class, or method, run `impact({target: "symbolName", direction: "upstream"})` and report the blast radius (direct callers, affected processes, risk level) to the user.
- **MUST run `detect_changes()` before committing** to verify your changes only affect expected symbols and execution flows. For regression review, compare against the default branch: `detect_changes({scope: "compare", base_ref: "main"})`.
- **MUST warn the user** if impact analysis returns HIGH or CRITICAL risk before proceeding with edits.
- When exploring unfamiliar code, use `query({query: "concept"})` to find execution flows instead of grepping. It returns process-grouped results ranked by relevance.
- When you need full context on a specific symbol — callers, callees, which execution flows it participates in — use `context({name: "symbolName"})`.

## Never Do

- NEVER edit a function, class, or method without first running `impact` on it.
- NEVER ignore HIGH or CRITICAL risk warnings from impact analysis.
- NEVER rename symbols with find-and-replace — use `rename` which understands the call graph.
- NEVER commit changes without running `detect_changes()` to check affected scope.

## Resources

| Resource | Use for |
|----------|---------|
| `gitnexus://repo/my-trae-helper/context` | Codebase overview, check index freshness |
| `gitnexus://repo/my-trae-helper/clusters` | All functional areas |
| `gitnexus://repo/my-trae-helper/processes` | All execution flows |
| `gitnexus://repo/my-trae-helper/process/{name}` | Step-by-step execution trace |

## CLI

| Task | Read this skill file |
|------|---------------------|
| Understand architecture / "How does X work?" | `.claude/skills/gitnexus/gitnexus-exploring/SKILL.md` |
| Blast radius / "What breaks if I change X?" | `.claude/skills/gitnexus/gitnexus-impact-analysis/SKILL.md` |
| Trace bugs / "Why is X failing?" | `.claude/skills/gitnexus/gitnexus-debugging/SKILL.md` |
| Rename / extract / split / refactor | `.claude/skills/gitnexus/gitnexus-refactoring/SKILL.md` |
| Tools, resources, schema reference | `.claude/skills/gitnexus/gitnexus-guide/SKILL.md` |
| Index, status, clean, wiki CLI commands | `.claude/skills/gitnexus/gitnexus-cli/SKILL.md` |

<!-- gitnexus:end -->
