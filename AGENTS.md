# my-trae-helper

> **元项目**：开发 Trae IDE 技能包 + 维护跨 Agent 技能市场 CLI（`@my-trae-helper/cli`）。

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

**§1.4 经验沉淀路由(覆盖 §1.4 可能引入)**:仓库内不建 `.learnings/` 目录。ERR / LEARN / FEATURE_REQUESTS 用全局 `self-improving-agent` 统一管理。本仓库内反例 → `skill-markets/<pkg>/references/trap-instructions.yaml`。详见 [.trae/rules/learning.md](.trae/rules/learning.md)。

**§1.1 路径位置**：`scripts/` 放 Node/Python 脚本；`logs/` 放临时输出。

**§1.2 CLI 多文件拆分**：≥ 3 个职责的脚本必拆 `src/<module>.mjs`；只允许 `bin/cli.mjs` 做路由。

**§1.3 会话启动加载协议（强制）**：

```
1. Skill(name="project-rule-skill")  → 输出 needed_rules
1.5. Skill(name="self-improving-agent")  → 加载全局经验上下文(详见 .trae/rules/learning.md §5 路径 A)
2. 按场景关键词自动加载相关 skill：
   ├─ 测试/验收 → acceptance-discipline + test-experience
   ├─ 安全扫描 → trae-security-review
   ├─ 新建/验收技能 → skill-acceptance §7
   ├─ Gate/CI 配置 → skill-acceptance §7 + agent-dev-control-kit §11
   └─ 重构/升级 → fullstack-skill-architect
3. 只 Read needed_rules + 加载的 skill 列出的文件
4. 委派 sub-agent → 头部注入 [PROJECT-RULE-GATE]
```

详见 [project-rule-skill/SKILL.md](.trae/skills/project-rule-skill/SKILL.md) §1 Step 5。

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
  反例(PowerShell 中文换行符截断):
    git commit -m "line 1 中文" -m "line 2 中文"   # 输出空、exit 1
  正例:
    Write .commit_msg.txt "<完整多行>"
    git commit -F .commit_msg.txt
    rm .commit_msg.txt                              # 立即删,不污染

MUST §4.1.3: Git Bash hook 必须探测 miniconda Python,不能信 /usr/bin/python3
  反例: Git Bash 的 /usr/bin/python3 没 pip/pytest → subprocess 报 No module
  正例:
    PY=""
    for cand in /mnt/c/ProgramData/miniconda3/python.exe \
                 /c/ProgramData/miniconda3/python.exe \
                 python3 py python; do
      [ -x "$cand" ] && PY="$cand" && break
    done
    [ -n "$PY" ] && ! "$PY" -c "import pytest, yaml" 2>/dev/null && PY=""
    export MY_TRAE_HELPER_PY="$PY"
    "$PY" scripts/verify.py ...   # 子脚本用 $PY
  详见 trap-instructions.yaml AP-9 + §11.1.4
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
|------|------|
| `skill-markets/CAPABILITY-MAP.md` | 加新技能 / 新脚本前 |
| `SECURITY-MAP.md` | 加新 skill / 引入第三方 / 改脚本后 |
| `README.md` | 改 CLI 行为 / 加新 agent 支持 |
| `package.json` | 改依赖 / 版本号 |
| `.trae/rules/*.md` | 加新规则 / 改 §1 铁律 / 路由经验沉淀前 |

完整索引见 [skill-markets/CAPABILITY-MAP.md](skill-markets/CAPABILITY-MAP.md)。

---

## §8 实战项目位置

`D:\workspace\my-trae-helper\example\` 子目录都是软连接目录（指向真实项目）。

---

<!-- gitnexus:start -->
# GitNexus — Code Intelligence

This project is indexed by GitNexus as **my-trae-helper**. Use the GitNexus MCP tools to understand code, assess impact, and navigate safely.

> Index stale? Run `node .gitnexus/run.cjs analyze` from the project root — it auto-selects an available runner.

## Always Do

- **MUST run impact analysis before editing any symbol.** Before modifying a function, class, or method, run `impact({target: "symbolName", direction: "upstream"})` and report the blast radius.
- **MUST run `detect_changes()` before committing** to verify your changes only affect expected symbols.
- When exploring unfamiliar code, use `query({query: "concept"})` to find execution flows.
- When you need full context on a specific symbol, use `context({name: "symbolName"})`.

## Never Do

- NEVER edit a function without first running `impact` on it.
- NEVER ignore HIGH or CRITICAL risk warnings from impact analysis.
- NEVER rename symbols with find-and-replace — use `rename` which understands the call graph.

<!-- gitnexus:end -->