# ai-prompt-guide.md — 怎么跟 AI 说

> 按 V3 工作流，你需要说的关键提示词。AI 听到这些就会自动走对应 Agent。

---

## 一条命令启动全流程

```
帮我在项目里初始化 spec-driven 开发环境，创建 docs/specs/config.yaml 和 docs/specs/ 目录结构。
```

> 这会让 AI 自动创建 `docs/specs/changes/`、`docs/specs/archive/` 目录和项目配置。

---

## 新功能开发：逐阶段说

### Step 1: 提需求 → 出 proposal

```
我想做一个 {功能}。帮我写个 proposal。
```

或者：

```
我要加一个 {功能}，先分析一下为什么要做、做什么、不做什么。
```

AI 产出：`docs/specs/changes/{变更名}/proposal.md`

### Step 2: proposal 确认后 → 写 Spec

```
proposal 没问题，开始写 spec。
```

AI 产出：`docs/specs/changes/{变更名}/specs/{能力}/spec.md`（BDD 场景格式）

### Step 3: Spec 确认后 → 规划

```
spec 没问题，帮我规划一下怎么实现。
```

AI 产出：`design.md`（架构决策）+ `tasks.md`（勾选清单）

### Step 4: 规划确认后 → 写代码

```
方案就用推荐的 B 方案，开始写代码。
```

AI 产出：代码 + 测试 + `tasks.md` 逐个 `[x]`

### Step 5: 代码完成后 → 审查

```
代码写完了，帮我审查一下。
```

---

## 一句话端到端（AI 自动串流程）

如果不想逐阶段交互，直接说：

```
我要做一个 {功能}，按 fullstack 流程来：先出 proposal，再规划，再实现。
```

AI 会自动按 fullstack-proposal-writer → fullstack-spec-writer → fullstack-planner → fullstack-implementer 顺序推进，每个阶段结束后问你是否继续。

---

## 常见场景的提示词

| 场景 | 说什么 |
|------|--------|
| 修 Bug | "报了一个错：{描述}，帮我 debug" |
| 改已有功能 | "改一下 {功能} 的 {行为}，先出 proposal" |
| 重构 | "重构 {模块}，帮我分析架构方案" |
| 紧急修复 | "紧急修复，跳过 proposal，直接 debug + TDD" |
| 只规划不写码 | "帮我规划 {需求} 的方案，先不写代码" |
| 只写 Spec | "帮我把 {需求} 写成 spec，不规划不写码" |
| 查已有的 Spec | "看一下 docs/specs/changes/ 下有哪些进行中的变更" |
| 归档已完成变更 | "把 docs/specs/changes/{变更} 归档到 docs/specs/archive/" |
| 初始化项目 | "帮我在项目里初始化 spec-driven 开发环境" |
| 写模块文档 | "帮我把 {模块} 的实现状态写入 docs/modules/{模块}.md" |

---

## 关键词速查（AI 听到就触发对应 Agent）

| 你说的词 | AI 走哪个 Agent | 产出 |
|---------|---------------|------|
| 提案、proposal、新功能、为什么要做 | fullstack-proposal-writer | `proposal.md` |
| 写规格、写spec、需求文档、PRD | fullstack-spec-writer | `spec.md`（BDD场景） |
| 规划、设计、架构、技术选型、重构 | fullstack-planner | `design.md` + `tasks.md` |
| 实现、开发、写代码、TDD、开始写 | fullstack-implementer | 代码 + 测试 |
| 审查、验证、检查、review | fullstack-reviewer | 审查报告 |
| 调试、debug、bug、报错、失败 | fullstack-debugger | 根因 + 修复 |
| codemap、架构图、生成文档 | fullstack-doc-updater | 架构地图 |

---

## 重要提示

### 说"规划"之前确保 proposal 已确认

如果 proposal 还没确认就说"规划"，AI 会退回去先出 proposal。正确顺序是：

```
1. "帮我写个 proposal" → 确认
2. "proposal 没问题，开始写 spec" → 确认
3. "spec approved，帮我规划"
```

### 跳过 proposal 直接 spec（小变更）

```
这是个很小的改动，跳过 proposal，直接写轻量 spec。
```

### 不用 `/` 命令，直接说人话

不需要 `/fullstack-proposal-writer` 或 `/fullstack-spec-writer`。说"帮我写个提案"或"分析一下这个需求"就会自动触发。
