# my-trae-helper

> **元项目**：开发 Trae IDE 技能包 + 维护跨 Agent 技能市场 CLI（`@my-trae-helper/cli`）。
>
> **2026-08-16 蒸馏**：fullstack4TraeV11 V11.8.5 协议层承诺 → 脚本落地（13/14 done + 1 留置），参考 [skill-markets/fullstack4TraeV11/references/todos/README.md §2](skill-markets/fullstack4TraeV11/references/todos/README.md)。
>
> **2026-08-16 蒸馏**：fullstack4TraeV11 V11.8.5.P1 — §3.7 #10 commit 准入最小集程序化（`scripts/commit-minimum-check.py` 4 项校验），收尾 P3-6 留置（14/14 done）。参考 [skill-markets/fullstack4TraeV11/CHANGELOG.md V11.8.5.P1](skill-markets/fullstack4TraeV11/CHANGELOG.md)。
>
> **2026-08-16 蒸馏**：fullstack4TraeV11 V11.8.6 — V12 物理隔离思想在 V11 主版本内渐进落地（6 步，不升主版本）：`init-from-zero.py --layout v12-preview` + `process-layer-guard.sh` + `stage-gate.py --reset-to` + 4 个 agent 产物落位规则。P0-v12-physical-rollout 落地（status: done）。参考 [skill-markets/fullstack4TraeV11/CHANGELOG.md V11.8.6](skill-markets/fullstack4TraeV11/CHANGELOG.md) + [skill-markets/fullstack4TraeV11/references/todos/P0-v12-physical-rollout.md](skill-markets/fullstack4TraeV11/references/todos/P0-v12-physical-rollout.md)。
>
> **2026-08-16 蒸馏**：fullstack4TraeV11 audit-fix-2026-08-16 — guard-smith audit B 方案 3 件系统化缺口修补：`AGENTS.md §1.11 增补条款`（主代理直接 Edit）+ `guard-gate-smith SKILL §1.1.1`（guard-smith sub-agent 委派）+ `skill-registration-guard.mjs` 顶部 docstring（guard-smith sub-agent 委派）。三方一致明文化"非 schema 字段注释行豁免 + 硬约束 3 条 + 治理边界算法"。status: done。参考 [skill-markets/fullstack4TraeV11/references/todos/audit-fix-2026-08-16.md](skill-markets/fullstack4TraeV11/references/todos/audit-fix-2026-08-16.md) + [AGENTS.md §1.11 增补条款](AGENTS.md)。
>
> **2026-08-15 蒸馏**：fullstack4TraeV11 V11.8.4 commit 准入最小集与全量验收分层（Stage 3.5/4.5 异步化），参考 [references/common-anti-patterns.md §7](skill-markets/fullstack4TraeV11/references/common-anti-patterns.md)。

---
## .agents 和 .trae
---
- agent配置：本地环境级别的规则和skill放在.trae这里不提交，项目级的云端可以复用的agent配置放置.agents
- 开发脚本要考虑跨平台（win、max、linux）

---

## §0 项目定位

```
my-trae-helper/
├── bin/cli.mjs               # @my-trae-helper/cli 入口
├── src/                      # CLI 实现
│   ├── add.mjs list.mjs remove.mjs update.mjs init.mjs
│   ├── scanner.mjs installer.mjs agents.mjs utils.mjs
│   ├── create.mjs verify.mjs # 带三层控制的扩展命令
│   ├── execution/            # Execution Layer（CP1~CP6 风险/备份/回滚/审计）
│   │   ├── skill-change-control.mjs
│   │   └── skill-install-control.mjs
│   └── guards/               # Guard Layer
│       └── skill-dependency-guard.mjs
├── scripts/                  # 守卫脚本 + 发布预处理
│   ├── prepare-publish.mjs
│   ├── skill-security-guard.py    # 安全守卫
│   ├── skill-structure-guard.py   # 结构守卫
│   └── skill-capability-guard.py  # 能力守卫
├── .husky/                   # Git Hooks (pre-commit + pre-push)
├── .github/workflows/        # GitHub Actions
│   └── skill-market-gate.yml # L3 合并 + L4 发布门禁
├── package.json
├── skill-markets/            # 43 个技能包（每个含 SKILL.md + 可选 agents/references/scripts/）
├── skill-markets/CAPABILITY-MAP.md   # 技能索引 + 共享能力注册表
└── SECURITY-MAP.md           # 每个 skill 的安全评分
```

---

## §1 铁律（强约束）

1. **YAML frontmatter**：SKILL.md 必带 `name` + `description`；推荐 `version` / `requires`
2. **技能位置硬约束**：技能只能在 `skill-markets/<name>/` 下，不发明路径
3. **行数与铁律数不设硬上限**——参考 [`vibe-coding-standards` SKILL](skill-markets/vibe-coding-standards/SKILL.md)（v2.5 弹性 100~350 行）决定是否提取 references/；行数超阈时按"指针引用"原则瘦身，而非裁剪内容。
4. **安全审查必走**：新建/引入/变更 skill 必跑 `scan_skills_dir.py` + 更新 SECURITY-MAP.md
5. **能力去重**：新增脚本/技能必先查 `CAPABILITY-MAP.md`「共享能力注册表」
6. **临时产物落 `logs/` 或 `.publish/`**：不在项目路径之外写脚本
7. **写代码保持 ponytail 思路**：最简实现、标准库优先
8. **任务明确时才用 fullstack 流程**：不加不必要的阶段
9. **禁止自主部署**：不主动执行安装命令，除非用户明确要求
10. **SKILL.md/agents 引用优先**：核心铁律 + 骨架流程内联，详细内容 references/ 引用
11. **guard/gate 注册表强制（2026-08-14 §3 收紧方案 A）**：
    - 每个 skill 必须在 `registry/skills.yaml` 按同名条目注册 guard + gate 路由（src/guards/skill-registration-guard.mjs 自动校验）
    - 每个 skill 必带 `scripts/<name>-guard.<ext>`（**项目侧**，禁止放 `skill-markets/<name>/scripts/`）
    - 每个 skill 的 gate 必须挂到正确的 `.husky/<name>-gate` 或 `.github/workflows/<name>-gate`
    - **仅 `guard-smith` sub-agent** 可改 `registry/skills.yaml` / `scripts/<name>-guard.*` / `scripts/guard-router.mjs` / `.husky/<name>-gate` / `src/guards/skill-registration-guard.mjs` / `.github/workflows/skill-market-gate.yml`
    - 其他 agent 试图 Edit 这些路径 → guard-approver Tier 3 拦截 + 注册表守卫自举
    - 详见 `skill-markets/guard-gate-smith/SKILL.md`

    **§1.11 增补条款（2026-08-16 蒸馏补 — guard-smith audit 落地）**：
    - **豁免范围**（明确不属于 §1.11 写权范畴，主代理可直接 Edit 无需 guard-smith 委派）：
      - `registry/skills.yaml` 顶部 YAML 注释行（以 `#` 开头的非 schema 字段），如 `# 版本(last_updated)`、文档说明、字段说明
      - 元数据注释（`last_updated` / `total_skills` / 协议说明等）
      - 理由：`yaml.safe_load()` parse 后注释行被丢弃，不影响 schema 完整性
    - **改注释行的硬约束**（不留隐性风险）：
      1. commit msg 显式声明「非 schema 注释行变更」
      2. 跑 `node src/guards/skill-registration-guard.mjs` → 期望 PASS
      3. 跑 `node scripts/guard-router.mjs --all` → 期望 PASS（47 条目仍可执行）
    - **仍属 §1.11 写权范畴**（必须 guard-smith 委派）：
      - YAML schema 字段（`skill/status/guards/gates/maintainer/notes/version`）
      - 注册表条目（添加/删除/重命名 skill）
      - 守卫/门禁路由（`guards[].script` / `gates[].hooks` 等）
    - 治理边界算法：`schema_required_fields ∩ yaml_keys` ⊆ guard-smith 域，否则 ⊆ 主代理直接改域
    - 详见：[skill-markets/guard-gate-smith/SKILL.md §1.1.1](skill-markets/guard-gate-smith/SKILL.md) + [audit 报告 §4.3-4.5](skill-markets/fullstack4TraeV11/references/todos/audit-history/2026-08-16-guard-smith-registry-annotation-audit.md)

12. **调整 guard/gate 必走 7 步 SOP（2026-08-14 §2.4 新增，调用方强制）**：
    任何 agent（含主 agent / 其他 sub-agent）要调整 guard / gate，按以下 7 步：
    1. **识别需求** —— 锁定"要改什么 + 为什么"，现象源：pre-commit 报错 / 用户需求 / 新建 skill / 注册表守卫 BLOCK
    2. **自我判定** —— 查 guard-gate-smith §2.1 表：
       - 目标 ∈ 白名单路径（registry / scripts/<name>-guard.* / .husky/<name>-gate / scripts/guard-router.mjs / src/guards/* / gate workflow）→ 委派 guard-smith
       - 目标 ∉ 白名单但触发 guard/gate 联动 → 仍委派 guard-smith
       - 目标 = Tier 4（.husky/_* / .trae/identity/* / scripts/change-guard-approver.mjs）→ 🛑 终止，提 Tier 4 清单修订 PR
    3. **准备委派上下文** —— 按 guard-gate-smith §2.2 填 `[GUARD-SMITH-DELEGATION]` 头部：任务 + 上下文 + 约束（**不省略影响范围**）
    4. **委派 Task** —— `subagent_type="general-purpose"`（隔离上下文 + 审计清晰）
    5. **等 sub-agent 报告 + 验收** —— 检查越界 + 输出合理性
    6. **主 agent 自己兜底验证**（关键 —— §2.4 防假通过）—— 亲自跑：
       - `node src/guards/skill-registration-guard.mjs`
       - `node scripts/guard-router.mjs <changed-skill>`
       - `node tests/unit/test_guard_router.mjs`
       - `python tests/unit/test_registration_guard.py`
       - `npm run lint`
    7. **commit + 文档同步** —— `git commit -F .commit_msg.txt`（多行中文用 -F 文件，见 §4.1.2）+ 同步 SECURITY-MAP.md / CAPABILITY-MAP.md

    反模式（必避免）：❌ 绕过 guard-smith 直接 Edit 白名单路径 / ❌ 跳过 Step 6 自检 / ❌ 不填 §2.2 头部 / ❌ 让 sub-agent 越界改非白名单路径 / ❌ 跳过文档同步
    完整流程 + 场景对照表详见 `skill-markets/guard-gate-smith/SKILL.md` §2.4

**§1.4 经验沉淀路由(覆盖 §1.4 可能引入)**:仓库内不建 `.learnings/` 目录。ERR / LEARN / FEATURE_REQUESTS 用全局 `self-improving-agent` 统一管理。本仓库内反例 → `skill-markets/<pkg>/references/trap-instructions.yaml`。详见 [.agents/rules/learning.md](.agents/rules/learning.md)。

**§1.1 路径位置**：`scripts/` 放 Node/Python 脚本；`logs/` 放临时输出。

**§1.2 CLI 多文件拆分**：≥ 3 个职责的脚本必拆 `src/<module>.mjs`；只允许 `bin/cli.mjs` 做路由。

**§1.3 会话启动加载协议（强制）**：

```
1. Skill(name="project-rule-skill")  → 输出 needed_rules
1.5. Skill(name="self-improving-agent")  → 加载全局经验上下文(详见 .agents/rules/learning.md §5 路径 A)
2. 按场景关键词自动加载相关 skill：
   ├─ 测试/验收 → acceptance-discipline + test-experience
   ├─ 安全扫描 → trae-security-review
   ├─ **新建/升级 skill → [`.agents/skills/project-rule-skill/references/skill-creation-workflow.md`](.agents/skills/project-rule-skill/references/skill-creation-workflow.md) 必读(V11.8.0.1 路径迁移到 project-rule-skill 网关,协议先行 + 多维度一致)** + skill-acceptance §7
   ├─ Gate/CI 配置 → skill-acceptance §7 + agent-dev-control-kit §11
   └─ 重构/升级 → fullstack-skill-architect
3. 只 Read needed_rules + 加载的 skill 列出的文件
4. 委派 sub-agent → 头部注入 [PROJECT-RULE-GATE]
```

详见 [project-rule-skill/SKILL.md](.agents/skills/project-rule-skill/SKILL.md) §1 Step 5。

---

## §2 三层控制体系（技能市场管理）

| 层 | 职责 | 实现 |
|---|------|------|
| **Execution** | 标准化执行 + 风险分级 + 备份回滚 + 审计 | `src/execution/*.mjs`（CP1~CP6）|
| **Guard** | 自动化检查 + 阻断违规 | `scripts/skill-*-guard.py` + `src/guards/*.mjs` |
| **Gate** | 提交/推送/合并/发布门禁 | `.husky/` + `.github/workflows/` |

### 2.1 Execution 控制点

- **CP1 风险判定**：HIGH/MEDIUM/LOW
- **CP2 前置检查**：依赖 + 冲突 + 命名
- **CP3 备份**：HIGH/MEDIUM 强制备份到 `_archived_<ts>/`
- **CP4 执行变更**：symlink/copy
- **CP5 后置验证**：完整性 + 结构守卫
- **CP6 回滚/审计**：失败回滚 + JSONL 审计日志

### 2.2 Guard 清单

| 守卫 | 检查维度 | 触发 |
|------|---------|------|
| Skill Security | HIGH/MEDIUM/LOW 风险 + 真实密钥检测 | pre-commit / verify |
| Skill Structure | 命名 + 行数 + YAML frontmatter + 铁律数量 | pre-commit (新建) / verify |
| Skill Dependency | 硬依赖完整性 + 软依赖降级影响 | pre-push / verify |
| Skill Capability | 脚本去重 + CAPABILITY-MAP.md 同步 | verify |

### 2.3 Gate 层级

- **L1 Commit** (`git commit`)：lint + typecheck + unit + security/structure
- **L2 Push** (`git push`)：integration + coverage + dependency + build
- **L3 Merge** (PR merge)：L2 + CAPABILITY-MAP 同步 + SECURITY-MAP 同步
- **L4 Publish** (Release)：L3 + 全量扫描 + 灰度发布 + 自动升级 tag

### 2.4 Gate 自验收强制（防止"假通过"）

```
MUST: 写完任何 Gate / Guard 脚本后必须用真反例跑自验收
触发:
  - .husky/pre-commit / pre-push
  - *.guard.{py,mjs}
  - package.json scripts.* (lint/test:unit/build 等)
  - GitHub Actions workflow
验证:
  - tmp 目录造违规样本 → 跑 Gate → 期望 exit ≠ 0
  - PASS 态 / BLOCK 态 / 边界态 三态必跑
固化:
  - 反例样本必须写进 tests/unit/test_*.py
  - 不能跑一次就丢
辅助工具:
  - python skill-markets/agent-dev-control-kit/scripts/validate-gate-integrity.py --target .
    → 自动检测 package.json scripts / pre-commit/pre-push 是否"假通过"
```

详见 [skill-acceptance §7](skill-markets/skill-acceptance/SKILL.md) + [agent-dev-control-kit §11](skill-markets/agent-dev-control-kit/SKILL.md) + [references/traps.md](skill-markets/agent-dev-control-kit/references/traps.md)（含 7 个反例）。

---

## §3 CLI 命令

| 命令 | 功能 | 三层控制 |
|------|------|---------|
| `add <name>` | 安装技能 | Execution: install-control + Dependency Guard |
| `list` / `ls` | 列出已装技能 | - |
| `remove` / `rm` | 卸载技能 | Execution: install-control |
| `update` / `up` | 更新技能 | - |
| `init` | 创建 SKILL.md 模板 | - |
| `create <name>` | 新建技能包 | Execution: change-control + Structure Guard |
| `verify <name>` | 验证技能（执行所有守卫）| All Guards |

```bash
node bin/cli.mjs add <skill-name> -a trae-cn -y
node bin/cli.mjs create <name> "描述"
node bin/cli.mjs verify <name>
```

---

## §4 Agent 回复行为规约

```
1. 不问"要不要做 X" —— 做或不做，不问
2. 不挂 P0/P1/P2/P3 backlog —— 做完或不做
3. 不写"我没做但应诚实声明的 N 项" —— 做了标 ✅，没做的直接"不做" + 原因
4. 结尾报告三类之一：
   - 完成："完成报告 + 修改清单"（无问句）
   - 部分："X 已完成，Y 不做（原因）"（无问句）
   - 失败："🛑 阻塞：X（具体缺什么）"（无问句）
5. 保留 AskUserQuestion 用于：方案选择 / 参数确认 / 多分支决策
6. 不给 P0/P1/P2 配硬性条数(2026-08-14 蒸馏补充) ——
   禁"几条落地 / 几条留空 / 每档 ≥N"这类分组配额。
   仓库内无此规则出处,只在 AGENTS.md §4.2 与本条明文,
   其余位置出现 = 反例,见 trap-instructions.yaml AP-14。
```

**用户表态信号**（"懂了吗"/"能懂了吗"/"你到底做啥"）出现时必须终止提问，选保守方案：
- 改 < 不改（最小变更）
- 改 src/ < 改 skill-markets/
- 显式 < 隐式

### §4.1 通用跨会话铁律(2026-08-14 第二轮蒸馏补充)

```
MUST §4.1.1: 任何数字声明必须第一轮带证据
  反例: user 说 "43 个 skill" → agent 不核对 → 默默按 39 做 → user 反复纠正
  正例: 任何 "N 个" 必须 ls/glob/Read 精确计数 + 第一轮列清单
  详见 trap-instructions.yaml AP-12

MUST §4.1.2: 多行 commit message 用 -F 文件,不用 -m 多参数
  使用git bash进行操作

MUST §4.1.3: Git Hook 必须跨平台探测 Python + 自愈依赖,不硬编码任何具体路径
  反例 1: 写死 /mnt/c/ProgramData/miniconda3/python.exe → macOS/Linux 跑不动,违反跨平台铁律
  反例 2: 探测失败就 BLOCK → 装了 pip 但忘装 pytest 时连跑一次机会都没有,矫枉过正
  正例(共享 scripts/detect-python.sh,hook 内 source):
    # 跨平台探测 — PATH + 平台典型位置(由 uname 动态生成),带能力校验
    # 缺 pytest/yaml → 自动 python -m pip install --user(自愈,不阻断)
    . scripts/detect-python.sh
    # detect-python.sh 自动导出 MY_TRAE_HELPER_PY=$PY
    "$MY_TRAE_HELPER_PY" scripts/verify.py ...
  详见 trap-instructions.yaml AP-9 + §11.1.4 + scripts/detect-python.sh
```

## §5 Skill 与 Agent 严格区分

| 概念 | 目录 | 加载方式 | 何时用 |
|------|------|---------|--------|
| Skill | `skill-markets/<name>/` | `Skill` 工具 | 改变主 Agent 行为/知识 |
| Agent | `skill-markets/<name>/agents/*.md` | `Task` 工具 | 流水线中的专业化工人 |

- `skill-markets/` 放技能，`agents/` 放 Agent 定义，**严禁交叉**
- Agent 文件名 kebab-case，**不带 `-agent` 后缀**（已在 `agents/` 目录内）
- 新包优先做纯 Skill，多角色流水线才引入 Agent

---

## §6 安全审查（强制门禁）

```
决策矩阵：
    HIGH 真实风险    MEDIUM 真实风险    准入
    0                ≤ 3                🟢 PASS
    0                > 3                🟡 WARNING（人工审查）
    ≥ 1              任意                🛑 BLOCKED（拒绝/修复）
```

```bash
python skill-markets/trae-security-review/scripts/scan_skills_dir.py skill-markets/<pkg>
```

审查后更新 `SECURITY-MAP.md` §量化评分。

---

## §7 能力地图（新建/修改前必读）

| 文件 | 何时读 |
|------|--------|
| `skill-markets/CAPABILITY-MAP.md` | 加新技能 / 新脚本前 |
| `SECURITY-MAP.md` | 加新 skill / 引入第三方 / 改脚本后 |
| `README.md` | 改 CLI 行为 / 加新 agent 支持 |
| `package.json` | 改依赖 / 版本号 |
| `.trae/rules/*.md` | 加新规则 / 改 §1 铁律 / 路由经验沉淀前 |
| **`.agents/skills/project-rule-skill/references/skill-creation-workflow.md`** (V11.8.0.1 路径迁移) | **任何 skill 创建 / 升级 / 合并 / 废弃操作前必读**(协议先行 + 多维度一致) |
| **`.agents/skills/project-rule-skill/references/protocol-coverage-protocol.md`** (V11.8.0.1 路径迁移) | **任何协议规范 (`*-protocol.md`) 创建后必跑 `python scripts/_check_protocol_coverage.py --protocol <path> --check`**;CI gate L3/L4 已自动检 |
| **`tests/catalogs/catalog-protocol.md`** (2026-08-15 NEW) | **任何 SKILL 创建/修改必跑 `python tests/catalogs/_check_skill_catalog.py`**(V1 report-only);CI gate L3/L4 §5.8 自动检 |
| **`skill-markets/github-kownledge-helper/SKILL.md`** (V1.0 NEW 2026-08-16) | 本项目专属:本地 GitHub 仓库管家 — ADD/UPDATE/UPDATE-ALL/QUERY/SYNC-TO 五大工作流 + 命令模式 + 踩坑记录;TS CLI 化(`pnpm ghh ...`);仅软依赖 doc-map-manager;**2026-08-16 全量沉淀**:AGENT.md + project-rules.md → 13 个 references(workflows-baseline/manifest-schema/doc-map-manager-usage/env-loadenv/reply-conventions/first-run-checklist/skill-evolution/task-start-probe/project-paths/git-workflow-rules/doc-index-rules/answer-rules/safety-cleanup) |

完整索引见 [skill-markets/CAPABILITY-MAP.md](skill-markets/CAPABILITY-MAP.md)。

---

## §8 实战项目位置

`D:\workspace\my-trae-helper\example\` 子目录都是软连接目录（指向真实项目）。

---

<!-- gitnexus:start -->
# GitNexus — Code Intelligence

This project is indexed by GitNexus as **my-trae-helper** (32516 symbols, 39969 relationships, 300 execution flows). Use the GitNexus MCP tools to understand code, assess impact, and navigate safely.

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
