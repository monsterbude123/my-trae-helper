# 体量自适应工件架构（Progressive Disclosure）

> 核心思想：工件不设行数上限。当内容自然长大到可以独立阅读时，拆成子文件。
> Agent 读父文件（永远小）就能理解全景，需要细节时再读子文件。
> 文件系统是天然的分界线和上下文保护层。

---

## §1 拆分原则

```
一个工件何时从单文件变成多文件？

  判断标准: 删除已有子文件后，父文件是否仍可在 2 分钟内读完后理解全景？
    └── 能 → 单文件即可，不拆
    └── 不能 → 拆。拆分边界 = 最大的语义块（section/能力/决策/实体）

拆分铁律:
  ✅ 拆分后每个子文件可独立阅读（有自己的标题和摘要）
  ✅ 父文件保留每段的 1-2 句摘要 + 链接到子文件
  ✅ 拆分边界 = 语义边界（一个能力、一个决策、一个实体），不按行数切
  ❌ 禁止机械切割（如"超过 200 行就拆一个 detail-2.md"）
  ❌ 禁止拆到单文件小于 30 行（那是碎片，不是模块）
```

执行归属: 拆分动作在产出阶段执行（如 proposal-writer 写完发现超标 → 自拆）。下一个 agent 只读父文件，不负责拆分上游工件。

---

## §2 四种工件的拆分模式

### proposal.md

```
小变更（Why+What+Capabilities+Non-Goals 未超过 thresholds.md 拆分触发值）:
  proposal.md  ← 单文件，够用

大变更（超过 thresholds.md 拆分触发值）:
  proposal.md           ← 决策概要（What 摘要 + Capabilities 一览 + 结论，参考 thresholds.md proposal.md 父文件默认值）
  proposal/
    why.md              ← 业务动机详细论证
    capabilities.md     ← 7 capability 详细描述
    non-goals.md        ← 边界说明
    impact.md           ← 影响面分析
```

**拆分标准**：why.md 超过 30 行独立成段 → 拆。capabilities 列表超过 5 个且每个 ≥ 5 行 → 拆。non-goals 超过 10 条 → 拆。

> 阈值 → [thresholds.md](thresholds.md)
> 执行者: proposal-writer

### spec.md

```
单文件模式（总体量可控）:
  所有 capability BDD 场景 + Invariants 加起来，读完不超过 2 分钟
  → 一个 spec.md，不拆

多文件模式（需要导航）:
  任何维度超标（场景数量多 / capability 独立复杂度高 / 多人协作冲突）:
    spec.md             ← 父文件：能力索引 + BDD 编号表 + Invariants
    specs/
      c1-data-layer/spec.md
      c2-scanner/spec.md
      ...              ← 每个 capability 独立 BDD 场景

父文件体量参考: ~80 行（上下 20% 浮动，即 64~96 行），以"2 分钟读完能讲清全景"为准，不设硬上限
```

> 执行者: spec-writer

### design.md

```
小设计（决策 ≤ 3 个，无文档影响表需求）:
  design.md  ← 单文件

大设计（决策 3+ 或涉及多模块）:
  design.md             ← 决策索引表 + 文档影响清单 + 全局约束，参考 thresholds.md design.md 父文件默认值
  design/
    d01-phase1-strategy.md
    d02-routing-design.md
    d03-auth-model.md
    ...                 ← 每个决策独立文件，格式: 问题 → 方案对比 → 选定 → 影响
```

**拆分标准**：任何单个决策描述超过 25 行 → 独立成文件。

> 阈值 → [thresholds.md](thresholds.md)
> 执行者: planner

### contracts/

> contracts/ 已经多文件。问题是个别文件过大（如 api-contracts.md 1105 行）。

```
单域（每文件未超过 thresholds.md 拆分触发值）:
  contracts/
    api-contracts.md
    domain-models.md
    events.md
    validation-rules.md  ← 现有结构，不改

跨域（超过 thresholds.md 拆分触发值）:
  contracts/
    api-contracts.md          ← API 索引（端点列表 + 通用规则），参考 thresholds.md contracts/api 父文件默认值
    api/
      models-api.md
      download-api.md
      import-api.md
    domain-models.md          ← 实体索引，参考 thresholds.md contracts/domain 父文件默认值
    models/
      model.md
      model-version.md
      model-tag.md
    events.md
    validation-rules.md
```

**拆分标准**：API 端点超过 5 个 OR domain entity 超过 5 个 → 拆。

> 阈值 → [thresholds.md](thresholds.md)
> 执行者: contract-writer

---

## §3 Agent 如何读

```
读完父文件（参考 thresholds.md 内容型工件父文件默认值）→ 2 分钟内理解全景
  └── 需要某个能力的详细 BDD → Read specs/003-model-import.md
  └── 需要某个 API 的签名 → Read contracts/api/search-api.md
  └── 需要某个决策的完整论证 → Read design/d03-auth-model.md
  └── 不需要细节 → 不读。父文件摘要够用了。

父文件的摘要格式:
  ## 2. Contract List
  - POST /api/models          → [api/models-api.md](api/models-api.md)  ← 3 words
  - GET /api/models/:id       → [api/models-api.md](api/models-api.md)
  - POST /api/models/import   → [api/import-api.md](api/import-api.md)

  ## 3. Decisions
  - D01: Phase 1 Strategy     → [d01-phase1.md](d01-phase1.md)          ← 1 sentence
    → B 级 MVP，先做模型注册和搜索，后做下载和渲染
```

### §3.1 父文件摘要的标准格式

父文件的每个可拆分段统一用此格式：

```markdown
## Sub-files
| 内容 | 文件 | 状态 | 行数（估） |
|------|------|:---:|:---------:|
| 业务动机详细论证 | [why.md](proposal/why.md) | 🟢 | ~60 |
| 7 capability 详细描述 | [capabilities.md](proposal/capabilities.md) | 🟡 | ~150 |
| 边界说明 | [non-goals.md](proposal/non-goals.md) | 🟢 | ~20 |
| 影响面分析 | [impact.md](proposal/impact.md) | 🟢 | ~40 |

Agent 判断: 需要业务动机 → Read proposal/why.md; 不需要边界 → 跳过 non-goals.md
```

---

## §4 拆分时机（不是数字，是触觉）

| 触觉信号 | 行动 |
|---------|------|
| 滚动这个文件超过 3 屏还没看到结构全貌 | 需要父文件摘要 |
| 想引用某个段落但没法一句话定位 | 需要拆成独立文件 |
| 不同的人需要看这个文件的不同部分 | 该拆了 |
| 同一个文件里有两类不同的读者 | 该拆了 |
| 一个 section 写了 20 行以上还没有结束 | 考虑拆 |
