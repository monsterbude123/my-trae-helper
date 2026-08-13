# Project Iron Laws — 项目级方法论（my-trae-helper）

> 本文件收纳 my-trae-helper 项目**项目级独有**的方法论。
> 与 V11 references/ 区别：V11 是通用全栈开发方法论；本文是 my-trae-helper 元项目的治理 + 反例 + 分支 + 路径权限。
> 适用对象：主 Agent + 委派到本项目的子 Agent。
> AGENTS.md §"项目级方法论" 引用本文，不内联。

---

## §A 反例库（Anti-Patterns，来自 2026-08-13 蒸馏）

> 每条反例含：触发输入 / 错误操作 / 正确操作 / 证据 / 验证方法。

### R-1 意图误读 → 误建技能包

- **触发输入**："放到 cli" / "改 cli" / "用 cli 控制" / "走命令行" / "加个 cli 命令" + 上下文涉及现有能力
- **错误操作**：在 `skill-markets/<new-skill>/` 下新建技能包
- **正确操作**：
  1. 必先 Read `src/*.mjs` + `bin/cli.mjs` + AGENTS.md §1 铁律 1
  2. 现有 CLI 已支持 → 改 `src/` 加新 flag / 子命令
  3. 现有 CLI 未支持 → 评估是否真要新建（不默认）
- **证据**：2026-08-13 会话中，用户说"放到 cli"被误读为"新建 cli 工具包"
- **关键词路由**（用于 `list-needed-rules.mjs`）：
  - "改 cli" / "放到 cli" / "cli 命令" → §1 铁律 + §4 CLI 铁律 + §5 技能库铁律
- **验证**：新建 `skill-markets/<new>/` 前必须 Read `src/` 确认无对应实现，否则 REJECT
- **一句话铁律**："放到 cli"在本项目 = 改 `src/`，**不是**新建技能包

### R-2 路径拼接用 `Path.resolve` 误删源

- **触发输入**：uninstall / clean / replace / move / remove 等破坏性操作
- **错误操作**：`Path.resolve(root / name)` 后 `shutil.rmtree(dst)` 或 `rm -rf`
- **正确操作**：
  1. 用 `os.path.abspath(root / name)`（不解 symlink）或 `Path.resolve(strict=False)`
  2. 必走 `--dry-run` 预演，先打印目标路径
  3. 校验"目标 ≠ 源"（字符串不等）
- **证据**：2026-08-13 会话中，uninstall deep-research 误删 `skill-markets/deep-research/` 整个目录（无 git 跟踪，内容丢失）
- **关键词路由**：
  - "uninstall" / "dry-run" / "remove" / "rm" / "rmtree" → §1 铁律 + §A R-2
- **验证**：rm 操作前必跑 dry-run；dry-run 必打印目标 + 校验"非源"
- **适用语言**：Python（`shutil.rmtree` 跟随后会删源）/ Node（`rmSync` 已安全）/ Bash（`rm -rf`）
- **一句话铁律**：任何 rm 树操作前，先 dry-run + 校验目标不是 symlink 到源

### R-3 用户表态信号未结构化

- **触发输入**：用户发言包含以下任一信号 ≥ 1 次
  - 表态类："懂了吗" / "能懂了吗" / "你到底做啥" / "我在干啥" / "我是没有说明白吗" / "我说得够清楚吗"
  - 纠正类：连续 2 轮 Agent 回答与用户预期不一致
  - 确认类：用户已给出方案选择，Agent 重新提问
- **错误操作**：继续调 `AskUserQuestion` 问方案 A vs B
- **正确操作**：立即 stop 提问 → 选保守方案直接做 → 报告"我做了 X, Y 不做（原因）"
- **证据**：2026-08-13 会话中，用户说"能懂了吗"后 Agent 仍调 `AskUserQuestion`，触发用户回滚
- **关键词路由**：
  - "被质问" / "用户不耐烦" / "回滚" → §3 行为规约 + §A R-3
- **验证**：每次响应结尾自查结尾是否含"要不要 / 可选 / 下一轮 / 我没做"
- **一句话铁律**：表态信号 ≥ 1 次 = 终止提问，做或不做任选，但不重复询问

### R-1~R-3 共同判定

```
任意 R 触发 → 主 Agent 必须：
  Step 1：自查本次响应是否违反该 R
  Step 2：违反 → 立即重做，不解释，不道歉
  Step 3：通过 → 在响应开头声明"本响应已通过 R-N 自查"
```

### 反例登记流程（新增 R 时）

```
1. 收集证据：触发输入 + 错误操作 + 后果（具体到 file:line）
2. 提炼关键词：用于 list-needed-rules.mjs 路由
3. 补强：Edit 本文件 §A，新增 R-N 段落
4. 验证：写一个最小复现 case，确认下次能命中
5. 通知：在 PR / 变更日志中提及"新增 R-N：<一句话>"
```

---

## §B 决策层级 L0~L9（V11.2 蒸馏）

> 改动级别语义标准化。判定原则：改动级别 ≥ L5 → 必须含 state-card 更新；≥ L3 → 必须含 `impact()` 评估；≥ L1 → 必须含 `decisions/ADR` 文档。

| 层级 | 语义 | 触发条件 | 产物 |
|:---:|------|---------|------|
| **L0** | 元规则 | 修改 §2 铁律本身 / AGENTS.md 顶层结构 | 走 §2 铁律变更流程 + 用户确认 |
| **L1** | 架构决策 | 选框架 / 选语言 / 选存储 | `docs/decisions/ADR-NNN-<title>.md` |
| **L2** | 模块边界 | 拆包 / 拆模块 / 拆目录 | 状态卡 stage 1 Spec |
| **L3** | API 契约 | 新 API / 修改 API | `skills/06-contract` 四件套 |
| **L4** | 内部实现 | 函数级 / 类级重构 | commit message |
| **L5** | 测试规范 | 新增测试模式 | `skills/03-test-plan` |
| **L6** | 命名规范 | 单文件 / 单函数命名 | commit message |
| **L7** | 注释 / 文档 | 改动不影响行为 | commit message |
| **L8** | 兼容保留 | 为兼容旧行为保留过渡层 | 含"保留原因 / L9 计划"注释 + `coding-standards.md §1.3` 豁免条款 |
| **L9** | 兼容清理 | 删除 L8 保留的过渡层 | 走完整流程（不可直接删） |

**兼容保留（L8）注释必含**："保留原因" + "L9 计划"任一关键字，否则视为违规死代码。

---

## §C 路径读写权限分离（V11.2 蒸馏）

> 三类路径权限矩阵。同一路径出现在多张表 → **写权限取最严**（"不可写"覆盖"可写"）。

| 路径 | 读 | 写 | 删 | 来源 |
|------|:--:|:--:|:--:|------|
| `docs/specs/` | ✅ | ✅ | ⚠️ 走 archive | fact 层 |
| `docs/archive/` | ⚠️ 显式允许 | ❌ | ❌ | Article VIII |
| `docs/reports/` | ⚠️ 仅引用 | ✅ 仅追加 | ❌ | log 层 |
| `docs/decisions/`（新） | ✅ | ✅ | ⚠️ 仅 ADR 编号保留 | L1+ 决策 |
| `dist/` / `build/` | ❌ | ❌ | ⚠️ 走 `_trash_<ts>/` | 构建产物 |
| `src-tauri/target/debug/` | ❌ | ❌ | ⚠️ 走 `_trash_<ts>/` | 构建产物 |
| `src-tauri/target/`（根目录） | ✅（清单） | ❌ | ⚠️ 走 `_trash_<ts>/` | 构建产物（仅清单可读） |
| `node_modules/` | ❌ | ❌ | ❌ | 第三方依赖 |
| `.trae/tmp/` | ❌ | ✅（过程层） | ✅ | 过程层 |
| `.trae/logs/` | ⚠️ 仅 sub-agent 产物 | ✅（append-only） | ❌ | 过程层 |
| `pnpm-lock.yaml` | ✅ | ❌ | ❌ | 锁文件 |
| `Cargo.lock` | ✅ | ❌ | ❌ | 锁文件 |

**本项目（my-trae-helper）实际映射**：

| 路径 | 读 | 写 | 删 | 说明 |
|------|:--:|:--:|:--:|------|
| `skill-markets/` | ✅ | ✅ | �️ 走 `_archived_<ts>/` | 技能市场 |
| `bin/` / `src/` | ✅ | ✅ | ❌ | CLI 源码 |
| `docs/references/` | ✅ | ❌ | ❌ | 参考材料（禁改） |
| `.trae/rules/` | ✅ | ⚠️ 仅 sub-agent | ❌ | 项目规则 |
| `examples/` | �️ 仅清单 | ❌ | ❌ | 软链接目录（实际在 example 项目） |

---

## §D Change ↔ Feature 分支 1:1 规则（V11.2 蒸馏）

```
MUST：1 change = 1 feature 分支 = N commit
MUST：change-id 命名格式 = {YYYY-MM-DD}-{kebab-name}（如 2026-08-13-add-feature）
MUST：feature 分支从 release/v{MAJOR}.x 拉取
MUST：commit 信息含 stage 标签（prep/design/impl/verify/bug/health 五选一）

例外：
  - bug 单修复 = 1 bug = 1 bugfix 分支（来自 docs/bugs/{bug-id}.md）
  - 跨 change 整合 = 1 feature 分支可含 N change，仅限主分支 merge 前的最后整合阶段
```

---

## §E CLI 建设铁律（@my-trae-helper/cli）

```
- 命令路由：bin/cli.mjs 唯一入口，src/*.mjs 各司其职
- 多文件拆分：禁止把 scanner + installer + agents 揉在一个文件
- Windows 兼容：symlink 用 junction；目录判断用 statSync（跟随链接）
- YAML 解析：必走 yaml 包，不手写正则
- 交互：@inquirer/prompts v7+ 用 `checkbox`（不是 multiselect，已弃用）
- 输出：NO_COLOR / !isTTY 时禁用 ANSI；错误走 console.error
- 发布：npm pack 前必须跑 scripts/prepare-publish.mjs（剥 .pyc/.zip/cache）
```

**发布流程**（用户未授权时**不动手**）：

```bash
node scripts/prepare-publish.mjs   # 准备 .publish/
cd .publish && npm pack            # 本地验证
# 用户明确说"可以发布"再执行 npm publish
```

---

## §F 技能库建设铁律

```
- 目录结构：skill-markets/<name>/SKILL.md + 可选 agents/ references/ scripts/ assets/
- SKILL.md 大小：≤ 500 行（超了就拆 references/）
- name 字段：kebab-case，必须等于目录名
- description 字段：第三人称 + "做什么 + 何时用 + 触发词"
- requires.skills：硬依赖（装本 skill 前必须装）
- requires.optional：软引用（提示用户）
- 版本：vMAJOR.MINOR.PATCH，放 frontmatter `version: "x.y.z"`
- 禁止在 SKILL.md 写 README.md —— 那是给人类看的，不进 agent context
- 装完提示"重启 IDE"（Trae CN skills 目录变更需 IDE 重新扫描）
```

**`init` 子命令**（CLI 自带）一键创建合规 SKILL.md 模板：

```bash
npx @my-trae-helper/cli init my-cool-skill "做 X 用"
```
