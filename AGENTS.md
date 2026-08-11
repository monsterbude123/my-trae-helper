# my-trae-helper — Trae IDE 技能包开发项目

> **这是元项目**：开发和管理 Trae IDE 技能包的工程。编辑代码时优先用 ponytail 的懒人思路，开发新技能时参考已有技能包结构。

---


## 实战项目的位置

D:\workspace\my-trae-helper\example\ 子目录都是软连接目录

## 项目定位

这个项目存储和开发 Trae IDE 的**技能包**（skills），每个技能包是给 AI 代理加载的指令集。


```

`~\.trae-cn\skills` ← trae技能目录

## 参考资料

参考资料见docs/references/,禁止修改参考材料；

## 技能市场

技能市场见skill-markets/,禁止在技能市场之外创建或修改技能；
```

## 关键教训（来自开发历史）


**装到 `skills/`**，不要发明路径。安装命令（符号链接方式）：

## 安装技能
```powershell
# 检查并安装（从仓库根运行）
$skillPath = "$env:USERPROFILE\.trae-cn\skills\{skill-name}"
if (Test-Path $skillPath) {
    Write-Host "⚠️ 已安装: $skillPath"
} else {
    New-Item -ItemType SymbolicLink -Path $skillPath -Target "${PWD}\skill-markets\{skill-name}" -Force
    Write-Host "✅ 安装完成，请重启 IDE"
}
```

### 技能格式

每个技能必须有 `SKILL.md`，头部 YAML frontmatter：

```yaml
---
name: skill-name
description: 一句话描述 + 触发条件
---
---

## 开发新技能时的规则

```
1. SKILL.md 必须带 YAML frontmatter（name + description）
2. 技能目录放 skill-markets/ 下，每个技能一个子目录
3. 大类技能用: SKILL.md + references/ + workflows/ + agents/ + scripts/
4. 安装到 skills/，不要造路径
5. 安装后提醒用户重启 IDE
6. 写代码时保持 ponytail 思路（最简实现、标准库优先）
7. 任务明确时才用 fullstack 流程（不加不必要的阶段）
8. 不主动创建 md 文档文件（除非用户要求）
9. 禁止自主部署：不主动执行 Copy-Item 安装命令，除非用户明确要求"部署"、"安装技能"
10. 新建/引入/变更 skill 后必须走安全审查流程（见下方 §安全审查流程），审查后必须更新 SECURITY-MAP.md 的量化评分和点评
11. SKILL.md只能放置核心铁律和骨架流程，不能啰嗦，需要详细内容就是要引用的方式引出，让ai可以选择性的参考；
12. Agent 文件同样受 §11 约束：agents/*.md 只能放核心铁律（≤10条）+ 骨架工作流（每步一句话引用 references/）+ 输入/输出骨架 + 异常速查表 + 参考链接区。禁止把 references/ 和 templates/ 已有内容内联到 agent 文件。控制单文件 ≤150 行。原因：Agent 文件通过 Task 工具注入子代理 prompt，过大直接击穿上下文。

**§11 例外条款（V10.12 NEW — 已废弃 V10.12.1）**：

> V10.12.1 reviewer 铁律减肥后已恢复 ≤10 + ≤150 行，**本例外条款不再需要**。
> 保留段作历史记录，提醒未来 reviewer 仍需警惕膨胀问题。

```
[历史背景] V10.12 阶段 reviewer.md 因 4 批升级（§Step 2.4/2.5/2.6 + 4 条 V10.12 铁律）
         铁律数膨胀到 16 条 / 文件 113 行，破 §11 ≤10 + ≤150 双约束
         本例外条款临时放宽到 ≤16 + ≤250
         V10.12.1 用 SUITE 模式合并 6 条 V10.12 铁律 + 4 条 V10.8 铁律 → 2 条
         → 铁律 10 / 文件 108 行，本例外条款废弃
```

## Agent 回复行为规约（V10.12.5 NEW — 防"问下一步"模式）

> 根因：Agent 每次回复结尾习惯性加"要不要继续做 X / 下一轮 backlog / 可选下一步"——
> 这是把决策推给用户 + 仪式性结尾 + 拖延的形式主义。用户已多次（V10.12.1~V10.12.4）明确反对。

### 行为红线（强制）

```
1. 不问"要不要做 X"——做或不做，不问
   例外: 真正的方向性决策（方案 A vs B）才用 AskUserQuestion
2. 不挂 P0/P1/P2/P3 backlog——做完或不做，不留待办
3. 不写"我没做但应诚实声明的 N 项"——做了标 ✅，没做的直接说"不做"+ 原因
4. 不写"下一轮升级前 backlog"——这是拖延仪式
5. 结尾报告只用三类结尾句之一：
   - 完成: "完成报告 + 修改清单"（无问句）
   - 部分: "X 已完成，Y 不做（原因）"（无问句）
   - 失败: "🛑 阻塞: X（具体缺什么）"（无问句）
6. 保留 AskUserQuestion 用于：方案选择 / 参数确认 / 多分支决策（不放报告里当结尾）
   子代理返回后主上下文也检查是否含"要不要 / 可选 / backlog / 下一轮 / 我没做"
```

### 用户已表态拒绝的模式（V10.12.5 确认）

- ❌ "要不要继续做 1/2 ？" → ✅ 做完全部
- ❌ "可选下一步" → ✅ 做或不做
- ❌ "下一轮 backlog" → ✅ 当前轮做完
- ❌ "我没做但应诚实声明的 N 项" → ✅ 做或不做，不挂
- ❌ "做还是停？" → ✅ 做全部
- ❌ 仪式性承诺"我会努力改" → ✅ 直接改行为（用户看效果）

### 边界场景（可问的情况）

- 真正的方向性决策（方案 A vs B 选哪个）
- 模糊参数（端口、命名、范围）
- 用户已问"要不要做 X"（被动回答时可问）
- 安全风险决策（删除/移动/破坏性操作）

### 与 §11 关系

- §11 约束**文档**（SKILL.md / agents/*.md 不能啰嗦）
- 本章节约束**回复行为**（Agent 每次输出不能啰嗦）
- 二者互补：本章节是 §11 在行为层面的延伸

### 检测机制

- 主上下文自查: 每次回复结尾检查是否含"要不要 / 可选 / backlog / 下一轮 / 我没做"
- 命中即重写（不留问句结尾）
- 子代理返回后主上下文也检查

### 能力地图（必读）

**新建或修改技能前**，必须先读 [skill-markets/CAPABILITY-MAP.md](skill-markets/CAPABILITY-MAP.md)：

- **新增技能** → 先查「技能索引」确认不重复，再加一行
- **新增脚本** → 先查「共享能力注册表」确认没有已存在的同类脚本，禁止跨包复制副本
- **存在跨包依赖** → 必须在 SKILL.md 的 YAML frontmatter 中声明 `requires` 字段
- **修改依赖** → 同步更新 CAPABILITY-MAP.md

### Skill 与 Agent 严格区分

| 概念 | 目录 | 加载方式 | 何时用 |
|------|------|---------|--------|
| Skill（技能） | `skills/` | `Skill` 工具加载 | 改变主 Agent 行为/知识 |
| Agent（子代理） | `agents/` | `Task` 工具委派 | 流水线中的专业化工人 |

- `skills/` 放子技能，`agents/` 放 Agent 定义，**严禁交叉**
- Agent 文件名 kebab-case，**不带 `-agent` 后缀**（已在 `agents/` 目录内）
- 新包优先做纯 Skill，Agent 仅在明确多角色流水线时引入

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

## 安全审查流程

> 每次新建 Skill、引入第三方 Skill、变更 Skill 脚本时，必须走对应安全审查流程。
> 审查后更新 [SECURITY-MAP.md](SECURITY-MAP.md) 中的量化评分和点评。

### 流程一：新建 Skill

```
Step 1 — 在 skill-markets/ 下创建包目录 + SKILL.md
Step 2 — 运行安全扫描
    python skill-markets\trae-security-review\scripts\scan_skills_dir.py skill-markets\{包名}
Step 3 — 评估扫描结果
    ├─ 真实 HIGH > 0 → 🛑 修复后再提交
    ├─ 真实 MEDIUM > 3 → 🟡 评估并记录到 SECURITY-MAP.md
    └─ 通过 → 🟢 继续
Step 4 — 注册到 CAPABILITY-MAP.md
Step 5 — 更新 SECURITY-MAP.md（评分 + 点评）
Step 6 — 安装到 skills/ 后重启 IDE
```

### 流程二：引入第三方 Skill

```
Step 1 — 先用 plugable.io 在线扫描器检查 SKILL.md 是否有恶意模式
Step 2 — 尝试安装并扫描
    # 若通过 npx skills 安装
    python skill-markets\trae-security-review\scripts\scan_skills_dir.py .agents\skills\{skill-name}
    
    # 若通过 git clone
    python skill-markets\trae-security-review\scripts\scan_skills_dir.py skill-markets\{source-name}
Step 3 — 按判定决策
    ├─ BLOCKED (HIGH > 0) → 🛑 拒绝引入，记录原因
    ├─ WARNING (MEDIUM > 2) → 🟡 人工审查后决定
    └─ PASS → 🟢 可引入
Step 4 — 在 SECURITY-MAP.md "外部引入" 区记录评分 + 点评
Step 5 — 提醒用户该 Skill 的权限范围和使用风险
```

### 流程三：变更 Skill 脚本

```
Step 1 — 定位变更的脚本文件
Step 2 — 如果是新增脚本 → 查 CAPABILITY-MAP.md "共享能力注册表" 避免重复
Step 3 — 增量扫描：只扫描变更文件所在包
    python skill-markets\trae-security-review\scripts\scan_skills_dir.py skill-markets\{包名}
Step 4 — 对比变更前后风险计分变化
    ├─ 评分下降 ≥ 0.5 → 🛑 要求说明原因
    ├─ 评分下降 < 0.5 → 🟡 记录到 SECURITY-MAP.md
    └─ 评分不变/上升 → 🟢 通过
Step 5 — 如果是跨包共享脚本 → 同步更新 CAPABILITY-MAP.md 注册表
Step 6 — 更新 SECURITY-MAP.md 中的评分和点评
```

### 安全审查决策矩阵

```
扫描判定          HIGH 真实风险    MEDIUM 真实风险    准入决策
──────────────────────────────────────────────────────
PASS             0                ≤ 3                🟢 直接通过
WARNING          0                > 3                🟡 人工审查
BLOCKED          ≥ 1              任意                🛑 拒绝/修复
```

### 量化评分规则（SECURITY-MAP.md）

| 维度 | 权重 | 扣分规则 |
|------|------|---------|
| HIGH 风险 | 40% | 每个真实 HIGH -0.5（文档引用不扣） |
| MEDIUM 风险 | 25% | 每个真实 MEDIUM -0.2 |
| LOW 风险 | 10% | 每个 LOW -0.1 |
| 脚本规模 | 10% | >10 脚本 -0.3，>20 -0.5 |
| 网络/执行面 | 15% | Shell 执行 -0.3，HTTP 外联 -0.3 |
| **5.0 - 总分 = 最终评分** | | < 3.0 🔴 需整改 / 3.0-4.0 🟡 警告 / > 4.0 🟢 通过 |

---

## 项目专属技能（按引用挂入，不内联全文）

> 这些方法是项目级方法论。**不在 `.trae/skills/`**——前者两节曾错误指 `.trae/skills/skill-optimization-method/` 和 `.trae/skills/knowledge-system-upgrade/`，但实际目录不存在。**真实路径在 `skill-markets/fullstack4TraeV10/references/`**，按引用加载。

### skill-optimization-method — 技能包优化升级方法论

**何时加载**（命中任一即加载）：

```
用户说:
  - "技能包太重/臃肿"
  - "想精简/瘦身某个技能"
  - "要优化升级技能"
  - "新建 V 版本替代旧版本"
  - "感觉流程过于繁重"
  - "进入 V{N} 升级流程" / "升级 X 技能"
  - "我有点担心矫枉过正" / "会不会和已有规则重复"（触发质疑性校验）
```

**真实路径**：[skill-markets/fullstack4TraeV10/references/skill-optimization-method.md](skill-markets/fullstack4TraeV10/references/skill-optimization-method.md)（74 行精简方法论，V10.12 加 §0 第 11 条「质疑性校验必走」+ §1 Step 0 + §4 触发词）

**核心要点**（不在 AGENTS.md 展开，按需 Read 上述文件）：
- 11 铁律：体积诊断 / 根因分层 / 外部对标 / 方案分级 / 决策前置 / 核心保底 / 缺口对照 / 三级分级 / 最小修复 / 门禁显式 / **质疑性校验必走**
- 6 步流程：Step 0 质疑性校验 → Step 1 体积诊断 → ... → Step 5 缺口对照 + 修复

---

### knowledge-system-upgrade — 知识库系统升级方法论

**何时加载**：

```
用户说:
  - "评估这个知识库"
  - "文档召回质量差"
  - "Agent 盲信过期文档"
  - "对标 GitNexus"
  - "设计文档索引系统"
  - "升级 doc-map-manager"
```

**真实路径**：[skill-markets/fullstack4TraeV10/references/knowledge-system-upgrade.md](skill-markets/fullstack4TraeV10/references/knowledge-system-upgrade.md)

> ⚠️ **AGENTS.md 漂移警示**: 本节原写"`.trae/skills/knowledge-system-upgrade/SKILL.md`"但路径不存在，已修正为真实路径。**今后引用任何路径前必须 Glob 验证**。

---

### skeptical-validation-protocol — 质疑性校验协议（V10.12 NEW）

**何时加载**（任何升级/P0/P1 决策前必走）：

```
用户说:
  - "进入 V{N} 升级流程"
  - "改 P0/P1 缺陷"
  - "我有点担心矫枉过正"
  - "会不会和已有规则重复"
  - "这值得做吗"

子代理返回"完成"声明前主上下文必查:
  - 已按 §3 强制声明格式回复?
  - 4 维度独立校验（不基于子代理自述）?
```

**真实路径**：[skill-markets/fullstack4TraeV10/references/skeptical-validation-protocol.md](skill-markets/fullstack4TraeV10/references/skeptical-validation-protocol.md)

**核心方法**（不在 AGENTS.md 展开）：
- §1 P0/P1 必要性质疑：根因验证 / 责任主体 / 重叠校验 / 成本校验（4 维度）
- §2 通用质疑三层：问题 / 方案 / 实施
- §3 强制声明格式（升级方案回报前必含）
- §4 反例：盲信 P0 / 责任主体误判 / 已有规则重叠未检出 / AGENTS.md 路径漂移盲信

**触发范围**（V10.12 已挂入）：
- skill-optimization-method §0 第 11 条 + §1 Step 0 + §4 触发词
- fullstack4TraeV10 9 个 agents §铁律 各加 1 条 SKEPTICAL VALIDATION 引用

---

## 已开发的技能包

| 技能包 | 路径 | 说明 |
|--------|------|------|
| fullstack4TraeV10 | `skill-markets/fullstack4TraeV10/` | 全栈文档驱动开发 V10 — 满分硬门禁 + 五阶段流水线 + spec-purge 物理归档 |

---

## 快速命令

```powershell
# 安装技能到全局（符号链接方式，自动检查已安装）
$skillPath = "$env:USERPROFILE\.trae-cn\skills\{name}"
if (Test-Path $skillPath) {
    Write-Host "⚠️ 已安装: $skillPath"
} else {
    New-Item -ItemType SymbolicLink -Path $skillPath -Target "${PWD}\skill-markets\{name}" -Force
    Write-Host "✅ 安装完成，请重启 IDE"
}

# 清理单个技能
Remove-Item -Recurse -Force "$env:USERPROFILE\.trae-cn\skills\{name}"

# 查看已安装技能
Get-ChildItem -Directory "$env:USERPROFILE\.trae-cn\skills\" | Select-Object Name
```

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
