# my-trae-helper — Trae IDE 技能包开发项目

> **这是元项目**：开发和管理 Trae IDE 技能包的工程。编辑代码时优先用 ponytail 的懒人思路，开发新技能时参考已有技能包结构。

---

## 项目定位

这个项目存储和开发 Trae IDE 的**技能包**（skills），每个技能包是给 AI 代理加载的指令集。

---

```

`~\.trae-cn\skills` ← trae技能目录

## 参考资料

参考资料见docs/references/,禁止修改参考材料；

## 技能市场

技能市场见skill-markets/,禁止在技能市场之外创建或修改技能；
```

## 关键教训（来自开发历史）

### 技能安装路径

```
✅ 正确: C:\Users\septe\.trae-cn\builtin_skills\
❌ 幻觉: C:\Users\septe\.trae-cn\builtin\global\skills\   ← AI 之前造的错误路径
```

**装到 `builtin_skills/`**，不要发明路径。安装命令：

```powershell
Copy-Item -Recurse "${PWD}\{package}\skills\{skill-name}" "$env:USERPROFILE\.trae-cn\builtin_skills\{skill-name}"
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
4. 安装到 builtin_skills/，不要造路径
5. 安装后提醒用户重启 IDE
6. 写代码时保持 ponytail 思路（最简实现、标准库优先）
7. 任务明确时才用 fullstack 流程（不加不必要的阶段）
8. 不主动创建 md 文档文件（除非用户要求）
9. 禁止自主部署：不主动执行 Copy-Item 安装命令，除非用户明确要求"部署"、"安装技能"
10. 新建/引入/变更 skill 后必须走安全审查流程（见下方 §安全审查流程），审查后必须更新 SECURITY-MAP.md 的量化评分和点评
11. SKILL.md只能放置核心铁律和骨架流程，不能啰嗦，需要详细内容就是要引用的方式引出，让ai可以选择性的参考；
12. Agent 文件同样受 §11 约束：agents/*.md 只能放核心铁律（≤10条）+ 骨架工作流（每步一句话引用 references/）+ 输入/输出骨架 + 异常速查表 + 参考链接区。禁止把 references/ 和 templates/ 已有内容内联到 agent 文件。控制单文件 ≤150 行。原因：Agent 文件通过 Task 工具注入子代理 prompt，过大直接击穿上下文。
```

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
Step 6 — 安装到 builtin_skills/ 后重启 IDE
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

## 快速命令

```powershell
# 安装技能到全局（从仓库根运行）
Copy-Item -Recurse "${PWD}\{pkg}\skills\{name}" "$env:USERPROFILE\.trae-cn\builtin_skills\{name}"

# 清理单个技能
Remove-Item -Recurse -Force "$env:USERPROFILE\.trae-cn\builtin_skills\{name}"

# 查看已安装技能
Get-ChildItem -Directory "$env:USERPROFILE\.trae-cn\builtin_skills\" | Select-Object Name
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
