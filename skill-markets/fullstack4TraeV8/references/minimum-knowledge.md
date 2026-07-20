# 最小必要知识协议（Minimum Necessary Knowledge）

> 原名 minimum-knowledge-principle.md 已合并到此文件。
> 原则：先读父文件（永远小）→ 理清全景 → 需要细节再读子文件。
> 文件系统的拆分边界 = 上下文的自然保护层。详见 [progressive-disclosure.md](progressive-disclosure.md)。

---

## §1 读取模式

```
优先级: 本表 > agent 自身步骤 0 的读取范围指示。

每条 MUST READ 指向「父文件或摘要段」—— 读完就能理清全景。
每条 ON DEMAND 指向「子文件或细节段」—— 用到时按需获取。

  ├── MUST READ — 先读这些，理解全景（父文件 ≥ 单文件的摘要段）
  ├── ON DEMAND — 需要细节时 Grep/Read 子文件
  └── DON'T READ — 属于其他 agent 的工作范围；若当作决策主依据 → 🛑 REJECT
```

---

## §2 Agent → 最小上下文对照表

> 格式: `工件(父文件) → 需要时读 工件(子文件)`

### implementer（编码）

| 优先级 | 读什么 | 为什么 |
|--------|--------|--------|
| MUST | proposal.md（父文件） | 知道做什么、为什么 |
| MUST | tasks.md | 任务 ID + 标题列表 |
| MUST | contracts/ 各父文件（索引段） | 知道接口签名一览 |
| ON DEMAND | proposal/capabilities.md | 拆分后的详细能力 |
| ON DEMAND | specs/{cap}.md（Grep 能力名） | 具体 BDD 场景 |
| ON DEMAND | design/{dNN}.md（Grep 决策 ID） | 特定架构决策 |
| ON DEMAND | contracts/api/{endpoint}.md | 具体 API 签名 |
| ON DEMAND | contracts/models/{entity}.md | 具体实体定义 |
| DON'T | closure-checklist.md | reviewer 的活 |
| DON'T | acceptance-scorecard* | 审查期产物 |
| DON'T | .state-card.md 全文 | 只看前 30 行 state & blocker |

### doc-updater（文档同步）

| 优先级 | 读什么 | 为什么 |
|--------|--------|--------|
| MUST | proposal.md（父文件，Capabilities 段） | 模块描述来源 |
| MUST | design.md（父文件，§文档影响清单） | 知道更新哪些文档 |
| MUST | .state-card.md 前 30 行 | 阶段和阻塞 |
| ON DEMAND | proposal/capabilities.md | 详细的模块能力 |
| ON DEMAND | contracts/ 各父文件（API 索引段） | 模块文档 API 段 |
| ON DEMAND | specs/{cap}.md | 模块文档功能描述 |
| DON'T | tasks.md | 不在 DOC SYNC #1 范围 |
| DON'T | closure-checklist.md | 不在 DOC SYNC #1 范围 |
| DON'T | acceptance-* | 审查期产物 |

### spec-writer（写规格）

| 优先级 | 读什么 | 为什么 |
|--------|--------|--------|
| MUST | proposal.md 全文 | 用户意图的唯一载体 |
| MUST | intake 影响面清单 | 范围边界 |
| ON DEMAND | proposal/*.md | 拆分后的详细子文件 |
| ON DEMAND | ARCHITECTURE.md | 系统上下文 |
| ON DEMAND | modules/{module}.md | 去重检测 |
| ON DEMAND | progressive-disclosure.md §2 | 输出结构判定（单文件 vs 父+子） |
| DON'T | contracts/ | 还没创建 |
| DON'T | design/ | 还没创建 |

### contract-writer（写契约）

| 优先级 | 读什么 | 为什么 |
|--------|--------|--------|
| MUST | proposal.md（父文件，What+Capabilities） | 知道哪些接口 |
| MUST | spec.md（父文件，BDD 场景索引） | 接口行为来源 |
| ON DEMAND | proposal/capabilities.md | 详细能力 |
| ON DEMAND | specs/{cap}.md（Grep capability ID） | 具体场景细节 |
| ON DEMAND | modules/{module}.md | 已有模型复用 |
| DON'T | tasks.md | 还没创建 |
| DON'T | closure-checklist.md | 还没创建 |

### planner（技术设计 + 任务拆解）

| 优先级 | 读什么 | 为什么 |
|--------|--------|--------|
| MUST | contracts/ 所有文件（全量） | 设计必须基于完整契约 |
| MUST | proposal.md（父文件，Impact + Non-Goals） | 边界条件 |
| MUST | spec.md（父文件，BDD 场景 ID 列表） | 任务映射 |
| ON DEMAND | proposal/*.md | 拆分后的详细子文件 |
| ON DEMAND | specs/{cap}.md（Grep ID） | 具体场景细节 |
| ON DEMAND | modules/{module}.md | 已有设计参考 |
| DON'T | acceptance-* | 还没创建 |

### reviewer（审查）

| 优先级 | 读什么 | 为什么 |
|--------|--------|--------|
| MUST | proposal.md（父文件，Capabilities） | 验收标准 |
| MUST | closure-checklist.md | 审查清单 |
| MUST | git diff --stat + detect_changes() | 变更范围 |
| ON DEMAND | contracts/ 父文件（spot-check 关键接口） | 契约一致性 |
| ON DEMAND | specs/{cap}.md（spot-check 关键场景） | 行为一致性 |
| ON DEMAND | visual-acceptance.md §6(prototype比对)、prototype.md | UI 变更的视觉验收 |
| DON'T | design/ 子文件全文 | 只看父文件的决策索引表 |
| DON'T | tasks.md 全文 | git diff 就够了 |

### proposal-writer（写提案）

| 优先级 | 读什么 | 为什么 |
|--------|--------|--------|
| MUST | intake 输出（影响面清单 + 流程定位卡） | 范围输入 |
| MUST | ARCHITECTURE.md + modules/INDEX.md | 系统全景 |
| MUST | .state-card.md | 当前状态 |
| ON DEMAND | modules/{module}.md | 能力去重 |
| DON'T | contracts/ | 还没创建 |
| DON'T | specs/ | 还没创建 |

---

## §3 自检问句

```
开工前:
  1. 我读了哪个父文件？（能说出文件名才算读了）
  2. 父文件里有没有链接到子文件？
     → 有 → 需要细节时按链接读子文件，不预加载全部
     → 没有 → 单文件模式，读完摘要段就行
  3. 我的 DON'T READ 列表里有东西吗？→ 有 → 坚决不碰

完成后:
  4. 我实际读了多少个文件？
     → 父文件 + 子文件 > 5 个 → 检查是否有滥读的
     → 合理范围: 1 个父文件 + 0-3 个子文件
```

---

## §4 模块文档读取原则（原 minimum-knowledge-principle.md）

> Agent 不应全量加载所有模块文档。先读摘要索引，再按需深入。

### §4.1 问题

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

### §4.2 原则

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

### §4.3 INDEX.md 结构

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

### §4.4 模块文档强制摘要段

每个 `docs/modules/{module}.md` 的**第一段**必须是：

```markdown
## 摘要
- 定位: {一句话 — 这个模块做什么}
- 对外接口: {关键 API / 组件 / 函数}
- 依赖: {模块列表}
- 被依赖: {模块列表}
- 框架标准: {路径 或 "—"}
- 状态: 🟢/🟡/🔴
```

Agent 读到摘要段即可判定：**这个模块和我本次变更有关吗？** 有关 → 继续深入。无关 → 跳过。

### §4.5 框架模块的接入手册

当一个模块被标记为 🔷 Foundational，doc-updater 生成接入手册后：

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

### §4.6 对 doc-updater 的要求（INDEX.md 规范）

每次 DOC SYNC 之后，doc-updater 必须：

1. **更新模块摘要段** — 如果接口/依赖/状态变化
2. **更新 INDEX.md** — 摘要列、状态列、被依赖列
3. **更新被依赖模块的摘要段** — 如果此模块新增为其他模块的依赖方

**INDEX.md 不单独存在**——是 modules/ 下各文档摘要段的自动汇总。

### §4.7 各 Agent 读模块协议对比

| | V7（旧） | V8（新） |
|---|---------|---------|
| **第一步** | `Read modules/*.md`（全量） | `Read modules/INDEX.md`（~50行） |
| **定位** | 无 — 依赖 Agent 自己判断 | INDEX 表一目了然 |
| **深入** | 每次读完整文档 | 先读摘要段（5-10行）→ 判定 → 有必要才深入 |
| **框架模块** | 不知道有接入手册 | INDEX 标记 → 知道有接入手册 |
| **上下文消耗** | 550-2200 行 | ~50（INDEX）+ 2-3 × 5-10（摘要）+ 2-3 × 50（深入）= ~200-300 行 |

### §4.8 禁止行为

| 禁止 | 替代 |
|------|------|
| `Read modules/*.md` 全量加载 | `Read modules/INDEX.md` → 定位 → 按需 |
| 跳过 INDEX 直接读模块 | 先过 INDEX，再读摘要 |
| 读模块时略过摘要段 | 摘要段是快速判定工具 |
| doc-updater 不更新 INDEX | DOC SYNC 必须同步更新 INDEX |
