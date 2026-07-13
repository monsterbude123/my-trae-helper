# 最小知道原则（Minimum Knowledge Principle）

> V8 治理核心：Agent 不应全量加载所有模块文档。先读摘要索引，再按需深入。

---

## §1 问题

```
V7 现状:
  spec-writer:   "读 docs/modules/*.md — 所有已有模块文档，理解全局"
  contract-writer: "读 docs/modules/*.md — 所有已有模块文档"
  proposal-writer: "读 docs/modules/*.md — 所有已有模块文档"
  planner:       "读 docs/modules/*.md — 所有已有模块文档，理解全局依赖"

  后果（AIGCMediaDesktop 实测）:
    11 个模块 × 50-200 行 = 550-2200 行一次性灌入上下文
    → 10 个不相关的模块也全部加载
    → Agent 实际关注的可能只有 2-3 个相关模块
    → 上下文击穿 + Agent 迷失在无关信息中
```

## §2 原则

```
每个 Agent 在"召回知识库"步骤:

Step 1: 读 docs/modules/INDEX.md          (~50行 — 所有模块的摘要表)
Step 2: 从 INDEX 定位相关模块             (哪些模块与本次变更相关?)
Step 3: 读相关模块的"§摘要"段             (每个 5-10 行)
Step 4: 摘要说"需要深入" → 读该模块 §2 接口 / §5 依赖
        摘要说"不相关"     → 跳过该模块（不读完整内容）
        摘要说"框架模块"   → 读接入手册（模块如何被接入）
```

**铁律：禁止直接 `Read modules/*.md` 全量加载。必须先过 INDEX。**

## §3 INDEX.md 结构

```markdown
# 模块索引

| 模块 | 摘要 | 对外接口 | 依赖 | 被依赖 | 框架标准 | 状态 |
|------|------|---------|------|--------|---------|:---:|
| 01-asset-management | 资产管理核心 | GET/POST /assets | db, error | 02, 09 | §Integration | 🟢 |
| 10-app-shell | Workbench框架 | TabBar, DnD | 01, 05 | 全部前端模块 | module-integration.md | 🟢 |
| 04-ai-services | AI服务端点管理 | GET/POST /ai-services | db, error | 05, 06 | — | 🟡 |
```

- 摘要 ≤ 15 字 — Agent 一眼判断相关性
- 框架标准列 — 空或 `module-integration.md` / `integration.md` 路径
- 被依赖列 — 让新 Agent 知道"动了这个模块谁受影响"

## §4 模块文档强制摘要段

每个 `docs/modules/{module}.md` 的**第一段**必须是：

```markdown
## 摘要
- 定位: {一句话 — 这个模块做什么}
- 对外接口: {关键 API / 组件 / 函数}
- 依赖: {模块列表}
- 被依赖: {模块列表}
- 框架标准: {路径 或 "—"}  ← 其他模块接入此模块必须遵循的规范
- 状态: 🟢/🟡/🔴
```

Agent 读到摘要段即可判定：**这个模块和我本次变更有关吗？** 有关 → 继续深入。无关 → 跳过。

## §5 框架模块的接入手册

当一个模块被标记为 🔷 Foundational（场景 03 的 spec-writer AOP P-07），doc-updater 生成接入手册后：

1. `docs/modules/{module}/integration.md` 写入具体接入规范
2. INDEX.md 的"框架标准"列指向接入手册路径
3. 该模块的 §摘要 → 框架标准指向接入手册

**后续 Agent 的流程**：

```
读 INDEX.md → 发现 10-app-shell 的框架标准 = module-integration.md
    ↓
Agent 判定: 我的新模块需要嵌入 Workbench
    ↓
读 docs/modules/10-app-shell.md §摘要 (5行) → 确认相关
    ↓
读 docs/standards/module-integration.md → 知道接入标准
    ↓
写 spec/contract 时遵循接入标准（不重新发明框架交互方式）
```

## §6 对 doc-updater 的要求

每次 DOC SYNC 之后，doc-updater 必须：

1. **更新模块摘要段** — 如果接口/依赖/状态变化
2. **更新 INDEX.md** — 摘要列、状态列、被依赖列
3. **更新被依赖模块的摘要段** — 如果此模块新增为其他模块的依赖方

**INDEX.md 不单独存在**——是 modules/ 下各文档摘要段的自动汇总。

## §7 各 Agent 读模块协议对比

| | V7（旧） | V8（新） |
|---|---------|---------|
| **第一步** | `Read modules/*.md`（全量） | `Read modules/INDEX.md`（~50行） |
| **定位** | 无 — 依赖 Agent 自己判断 | INDEX 表一目了然 |
| **深入** | 每次读完整文档 | 先读摘要段（5-10行）→ 判定 → 有必要才深入 |
| **框架模块** | 不知道有接入手册 | INDEX 标记 → 知道有接入手册 |
| **上下文消耗** | 550-2200 行 | ~50（INDEX）+ 2-3 × 5-10（摘要）+ 2-3 × 50（深入）= ~200-300 行 |

## §8 禁止行为

| 禁止 | 替代 |
|------|------|
| `Read modules/*.md` 全量加载 | `Read modules/INDEX.md` → 定位 → 按需 |
| 跳过 INDEX 直接读模块 | 先过 INDEX，再读摘要 |
| 读模块时略过摘要段 | 摘要段是快速判定工具 |
| doc-updater 不更新 INDEX | DOC SYNC 必须同步更新 INDEX |
