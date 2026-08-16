---
name: github-kownledge-helper
version: 1.0.0
description: 本地 GitHub 仓库管家技能 — 沉淀 ADD / UPDATE / UPDATE-ALL / QUERY / SYNC-TO 五大工作流的可复用经验、命令模式与踩坑记录，TS CLI 化（pnpm ghh add/update/sync-to/sync-docs/verify-docs）。本项目专属技能，零外部目录依赖。
audience: [agent, user]
requires:
  skills: [doc-map-manager]
---

# github-kownledge-helper — 本地 GitHub 仓库管家技能

> 本项目专属技能，沉淀「本地第三方仓库追踪器」的运营经验。
> 遵循零外部目录依赖：仅引用本 skill 相对路径或其他已安装 Skill 名。

## Description

本地 GitHub 仓库管家技能。当用户在本工作空间内进行仓库收录、批量更新、跨仓库知识答疑、manifest 维护、git 状态查询时加载。沉淀 ADD / UPDATE / UPDATE-ALL / QUERY 四大工作流的可复用经验、命令模式与踩坑记录。

## Triggers

- 用户说「加个仓库」「收录」「追踪 facebook/react」→ ADD 工作流（基线见 [workflows-baseline.md §1](./references/workflows-baseline.md#1-add--收录新仓库)）
- 用户说「全部更新」「批量 pull」「同步最新」→ UPDATE-ALL 工作流（基线见 [workflows-baseline.md §3](./references/workflows-baseline.md#3-update-all--一键全更新)）
- 用户问「react 最新发了什么」「v19 在哪个 commit」「这 PR 改了哪些文件」→ QUERY 工作流（基线见 [workflows-baseline.md §4](./references/workflows-baseline.md#4-query--答疑核心场景)）
- 用户说「把 X 同步/镜像/复制到 D:\xxx」「同步 QwenLM/Qwen-MM-Plugins 到 ...」→ SYNC-TO 工作流（镜像到任意绝对路径，含 .git，不写 manifest，详见 [workflows-sync-to.md](./references/workflows-sync-to.md)）
- 用户说「升级 skill」「记录这次经验」→ 触发 [skill-evolution.md](./references/skill-evolution.md) 5 步协议
- 用户说「你看看 X」「处理一下」「这些仓库你看看」（未知初始状态）→ 先走 [task-start-probe.md](./references/task-start-probe.md) 探测协议，4 步（探测 → 列决策点 ≤ 4 → 等用户 → 计划公示）
- 新会话首次启动 / 长时间未活动后 → 走 [first-run-checklist.md](./references/first-run-checklist.md) 4 步自检
- 涉及 manifest.json 读写 / repos/ 路径 / docs/ 索引 → 加载本 skill（路径约束见 [project-paths.md](./references/project-paths.md)，Schema 见 [manifest-schema.md](./references/manifest-schema.md)）
- 用户说「验证 doc manager 索引」「跑下 verify-docs」→ 加载 [doc-verify.md](./references/doc-verify.md)
- 用户说「写个脚本」「加个 CLI 命令」→ 加载 [tdd.md](./references/tdd.md) + [cli-development.md](./references/cli-development.md)
- 用户给的任务现有 CLI 覆盖不了 → 触发 [cli-development.md §协议](./references/cli-development.md#协议5-步强制)
- 业务代码涉及 `process.env` / `os.homedir()` → 必须走 [env-loadenv.md](./references/env-loadenv.md) 收口（禁止直读）
- 答疑类问题（涉及数字/commit/tag/版本号）→ 走 [answer-rules.md](./references/answer-rules.md) 4 条铁律（实测 + 来源标注 + 不盲信 + 不臆造）
- 涉及 git clone / pull / ff-only / 网络降级 → 加载 [git-workflow-rules.md](./references/git-workflow-rules.md) 5 条铁律
- 涉及索引构建 / 新鲜度协议 → 加载 [doc-index-rules.md](./references/doc-index-rules.md) 6 条铁律 + [doc-map-manager-usage.md](./references/doc-map-manager-usage.md) 使用规范
- agent 回复格式（简表 / 来源标注 / 失败直报错）→ 加载 [reply-conventions.md](./references/reply-conventions.md)
- 涉及 token / 密钥 / 临时清理 / `repos/` 入 git → 加载 [safety-cleanup.md](./references/safety-cleanup.md) 4 条铁律

## 依赖的外部 Skill

- `doc-map-manager`：知识索引构建与查询（脚本入口 `scripts/build-index.py` / `query-index.py`）

## 项目结构

```
github-kownledge-helper/
├── AGENT.md
├── manifest.json
├── package.json                          # pnpm 工作区根
├── pnpm-workspace.yaml                   # allowBuilds / verifyDepsBeforeRun
├── .trae/rules/project-rules.md
├── .trae/skills/github-kownledge-helper/  # 本 skill
├── repos/<group?>/<owner>__<repo>/         # 仓库本体（gitignored）
├── docs/<group?>/<owner>__<repo>/          # 文档镜像（doc-map-manager 索引目标）
└── src-cli/                                # TS CLI 源码
    ├── bin/cli.ts                          # 入口
    ├── src/commands/                       # 子命令实现
    └── src/lib/                            # 基础库（git/manifest/paths/time）
```

> ⚠️ `package.json` / `pnpm-workspace.yaml` / `node_modules/` **必须在项目根**，CLI 才能在任意 cwd 跑通。
> 之前放在 `scripts/` 子目录时，用户在项目根执行 `pnpm sync:docs` 会 `[ERR_PNPM_NO_PKG_MANIFEST]`。

## CLI 命令

> 所有命令**必须在项目根**执行（package.json 在项目根）。
> 任何用户给的任务，先查 [commands.md](./references/commands.md) 命令清单。**缺失的命令不要手动拼凑** — 走 [cli-development.md](./references/cli-development.md) §协议 5 步开发。

```bash
pnpm install

# 收录新仓库（完整 clone + 同步 docs + 触发 doc manager 索引）
pnpm ghh add <owner/repo 或 https URL> [--group <聚合目录>]

# 验证 doc manager 索引状态
pnpm ghh verify-docs

# 同步 manifest / 文档
pnpm ghh sync-manifest
pnpm ghh sync-docs

# 更新单仓 / 全量
pnpm ghh update <full_name>
pnpm ghh update-all

# 镜像到任意绝对路径（含 .git，跨平台 fs.cpSync，不写 manifest，不触发索引）
pnpm ghh sync-to <owner/repo> <绝对路径>
# 例：pnpm ghh sync-to QwenLM/Qwen-MM-Plugins D:\ref\qwen-mm-plugins

# 通用入口
pnpm ghh <command>

# 开发期
pnpm test           # vitest run
pnpm test:watch     # vitest
pnpm typecheck      # tsc --noEmit
```

## 升级信号约定

> 区分「任务推进」与「技能升级」信号。避免误升级打断任务流。

### 显式触发（用户明确要求升级）

| 信号 | 动作 |
|------|------|
| 「升级 skill」/「更新 skill」 | 立即按 §9.3 五步流程执行 |
| 「记录这次经验」/「沉淀下来」 | 同上 |
| 「把 X 写进 skill」/「加到 references」 | 写入对应文件 + 双重记录 |
| 「FIXTURE 完毕」/「大型任务完」 | 反思整段会话识别可复用资产再升级 |

### 隐式触发（任务本身够大，agent 主动升级）

| 场景 | 动作 |
|------|------|
| 完成一个明显大型任务（10+ 分钟 / 跨多个阶段 / 包含新决策） | 主动按 §9.3 升级 |
| 修了一个疑难 bug（根因可复述） | 追加 pitfalls §00x |
| 新工作流 / 新命令模式 / 新脚本类型 | 追加 workflows/commands |
| 跑通一个跨阶段任务流（如蒸馏） | 整段反思 + 补遗漏 |

### 不触发（避免误升级）

- 单纯 `git pull` / 简单答疑 / `pnpm install`
- 文件改名 / 路径调整等纯重构
- 用户在提问「X 该放哪」但没真做任务
- 用户说「继续」（纯推进信号）

### 升级回执格式

`已升级 · 沉淀到 references/<file> §NN · CHANGELOG+1 · 演进日志+1`

## 结构

```
github-kownledge-helper/
├── SKILL.md              # 本文件（描述 + 触发 + 升级信号约定 + CHANGELOG）
├── agents/               # 子代理定义（按需）
└── references/           # 经验沉淀
    ├── commands.md       # 可复用命令模式 + CLI 清单
    ├── workflows.md      # 工作流模式（ADD/UPDATE/QUERY + 探测/迁移）
    ├── cli-development.md  # 缺失-CLI 走开发的工作流（5 步协议）
    ├── tdd.md            # TDD 模板（vitest + 红绿循环）
    ├── doc-verify.md     # doc manager 验证流程
    └── pitfalls.md       # 踩坑记录
```

## 使用方式

本 skill 是**经验沉淀库**，不是可执行程序。Agent 在执行任务时：

1. **任务前**：读 `references/` 中对应主题，复用已验证的命令模式与工作流，避免重复踩坑。
2. **任务后（大型任务）**：按 AGENT.md §9 协议，把新经验写入 `references/`，更新本文件 CHANGELOG。

## CHANGELOG

> 格式：`YYYY-MM-DD | 摘要 | 沉淀位置`
> 倒序排列（最新在上）。

| 日期 | 摘要 | 沉淀位置 |
|------|------|---------|
| 2026-08-16 | 接入 my-trae-helper skill 市场 6 维度合规（YAML frontmatter + registry/skills.yaml 注册 + scripts/github-kownledge-helper-guard.py + CAPABILITY-MAP / SECURITY-MAP / README / CHANGELOG / AGENTS §7 同步） | SKILL.md frontmatter + registry + scripts/<name>-guard.py + 多文档 |
| 2026-08-16 | **AGENT.md + project-rules.md 全量沉淀**：13 个 references 文件（基线 4 大工作流 + manifest Schema + doc-map-manager 使用 + load_env 收口 + 回复规范 + 首次启动自检 + 技能演进 + 任务启动探测 + 路径硬约束 + git 工作流硬约束 + 知识索引硬约束 + 答疑红线 + 安全与清理） + workflows.md 基线引用改向 workflows-baseline.md + SKILL.md Triggers 完整扩展。判定原则：通用约定沉淀，具体项目配置仅作示例段 | references/workflows-baseline.md(新增基线) + manifest-schema.md + doc-map-manager-usage.md + env-loadenv.md + reply-conventions.md + first-run-checklist.md + skill-evolution.md + task-start-probe.md + project-paths.md + git-workflow-rules.md + doc-index-rules.md + answer-rules.md + safety-cleanup.md + workflows.md(基线引用重定向) + SKILL.md Triggers 段 |
| 2026-08-13 | 缺失-CLI 走开发的工作流 + TDD 模板 + doc manager 验证步骤写入 skill；TDD 实现 `add` + `verify-docs` 两 CLI（5 套件 25 例全绿） | references/cli-development.md（新增）+ tdd.md（新增）+ doc-verify.md（新增）+ commands.md（CLI 清单扩展）+ SKILL.md Triggers / 结构 / CLI 段 |
| 2026-08-13 | 首次批量收录 38 仓库 + 聚合目录支持（group 字段）+ TS/pnpm CLI 化 | references/workflows.md (聚合变体+TS CLI) + references/commands.md (TS CLI 入口) + references/pitfalls.md (pnpm v11 esbuild / 隐藏 .git / PS 字符串插值) |
| 2026-08-13 | update / update-all 实现 + 跑通 38 仓库更新（24 changed / 13 up-to-date / 1 ff-only 失败 reset 修复） | references/workflows.md (UPDATE 实战) + references/commands.md (update CLI) + references/pitfalls.md (§004 ff-only 失败 + §005 mtime 索引不更新) |
| 2026-08-13 | 包结构修正：package.json / pnpm-workspace.yaml / node_modules 移到项目根，scripts/ 改名为 src-cli/ | references/pitfalls.md §006（未在用户视角测试的盲点） |
| 2026-08-13 | 蒸馏会话：补全 4 个 pitfalls（§007-§010）+ 2 个 workflows（§7 探测 / §8 迁移）+ 升级信号约定 | references/pitfalls.md §007-§010 + references/workflows.md §7-§8 + SKILL.md 升级信号约定 |
| 2026-08-13 | SYNC-TO 工作流 + 跨平台 CLI 实现：TDD 6 例 + fs.cpSync recursive（替换 robocopy 方案），已注册 `pnpm ghh sync-to <owner/repo> <绝对路径>`；目标已存在停手 / 不写 manifest / 不触发 doc 索引 | src-cli/src/commands/sync-to.ts（新增）+ src-cli/test/syncTo.test.ts（新增 6 例）+ references/workflows-sync-to.md + references/commands.md + SKILL.md CLI 段 |
| 2026-08-13 | skill 全局化 + load_env 收口：env `GITHUB_KNOWLEDGE_HELPER_SPACE`（setx 已写入 HKCU\Environment）收口项目根；新增 `load_env.ts` + 11 测；paths.ts / add.ts / query.ts 走 `getEnv()` 替代 process.env 直读；全局入口 `~\.trae-cn\skills\github-kownledge-helper\SKILL.md` §0 协议自动 cd | src-cli/src/lib/load_env.ts（新增）+ src-cli/test/load_env.test.ts（新增 11 测）+ paths.ts + commands/add.ts + commands/query.ts + SKILL.md 环境变量段 |
| 2026-08-13 | 初始化 skill 骨架与演进协议 | SKILL.md + references/ 骨架 |
