# 00-product / Spec-Driven Development（SDD 总纲 v5.0）

> **定位**：生产流水线的起点。在让 AI 写代码之前，先把"做什么"用规格（Spec）的形式冻结下来。
>
> **下游消费者**：`01-contract/contract-first.md`（V5 NEW：基于 Spec 产出协议契约）、`10-design/planning.md`（基于 Spec + 契约出方案）、`20-development/doc-sync-protocol.md`（基于 Spec 出模块文档）。

---

## V5.0 核心升级

V5 在传统 SDD 基础上引入**协议先行（Contract-First）**作为新阶段：

```
V4 SDD:  Spec（行为契约） → Design（含接口契约子章节） → Code
V5 SDD:  Spec（行为契约） → Contract（独立接口契约工件） → Design（基于契约） → Code（实现契约）
```

| 维度 | V4 SDD | V5 SDD（CSDD - Contract-first SDD） |
|------|--------|-------------------------------------|
| 工件数 | 4 工件链（proposal/design/tasks/specs） | 5 工件链（+contracts/） |
| 接口契约位置 | design.md §4.3 子章节 | 独立 contracts/ 一等公民工件 |
| 接口契约稳定性 | design 的一部分，易变 | 不可变（Immutable），变更走流程 |
| TDD 起点 | 从零写测试 | contract test 骨架预生成 |
| 设计模式决策时机 | 接口契约之前（接口迁就模式） | 接口契约之后（模式迁就契约） |

详见 `01-contract/contract-first.md`。

---

## 一、SDD 是什么

**SDD（Spec-Driven Development，规格驱动开发）** 是生成式 AI 时代下适配工程化开发的方法论。在让 AI 写代码之前，先由人类定义简洁、可测试、形式化的系统规格说明（Spec），将其作为人、团队与 AI 之间的**动态契约**和开发过程的**唯一事实来源**，再以此驱动 AI 完成代码生成、测试验证等工程实现工作。

**本质转变**：

| 时代 | 文档与代码的关系 |
|------|---------------|
| 传统开发 | 文档是代码的注释 |
| Vibe Coding | 文档缺失，代码即文档（腐烂得最快） |
| **SDD** | **Spec 是"预编译的源代码"，代码只是 Spec 经 AI 编译后的产物** |

---

## 二、为什么需要 SDD

SDD 主要解决 Vibe Coding 的三大痛点：

| 痛点 | 描述 | 不控制的后果 |
|------|------|-----------|
| **非确定性** | 相同的自然语言指令，AI 每次生成的代码结构、实现方式可能完全不同 | 重做时只能从零开始 |
| **上下文遗忘** | 项目规模扩大后，AI 会遗忘前期设计逻辑，修改新功能时极易破坏已有功能 | 改一处坏三处 |
| **隐性技术债** | AI 为快速满足"运行通"的结果，可能引入拙劣的实现方式 | 代码腐烂，无法迭代 |
| **协作性差** | 开发过程的核心逻辑仅存在于 AI 与个别开发者的交互中，形成信息孤岛 | 团队无法接手 |

---

## 三、三种实践强度

SDD 不是非黑即白的流程，根据项目阶段选择档位：

### 1. 轻量级：Spec-First

- 在写代码前，先写一个短 Spec，明确目标、边界和验收标准
- **适合**：小功能开发、原型验证、个人项目
- Spec 不进版本库，写完即用

### 2. 中量级：Spec-Anchored（**本技能包默认档位**）

- Spec 进入版本库，成为长期资产
- **每次行为变更都先修改规范，再修改代码**
- 适合：中长期产品、多人协作项目、需要持续迭代的业务系统
- Spec 文件路径：`docs/specs/{feature-name}/spec.md`

### 3. 高强度：Spec-as-source

- 人类主要维护规范，代码更多被视为由 AI 生成的派生产物
- 适合：高度标准化、规则明确、变化频繁但边界清晰的系统
- 极少使用，仅在规则极清晰的中后台系统考虑

### 档位切换原则

| 当前档位 | 触发切换的信号 | 切换到 |
|---------|-------------|--------|
| Spec-First | 功能开始影响多个模块 | Spec-Anchored |
| Spec-First | 多人协作开始介入 | Spec-Anchored |
| Spec-Anchored | 团队规则极清晰、AI 生成代码稳定 | Spec-as-source（谨慎） |

---

## 四、SDD 标准流水线（五步）

```
需求输入 → ① 规格定义 → ② 计划生成 → ③ 任务拆解 → ④ 编码实现 → ⑤ 验证归档
            (00-product)  (10-design)              (20-dev)     (40-acceptance)
```

> 与本技能包目录编号一一对应：00 → 10 → 20 → 30 → 40。出 Bug 时反向触发 50-debugging。

### Step 1：定义规格（Spec）

- 以 Markdown 格式编写规格文档
- 核心内容：项目目标、核心业务逻辑、API 接口定义、数据结构、系统整合规则、测试标准
- 详见 `00-product/spec-templates.md` 的 13 章结构

### Step 2：生成计划（Plan）

- AI 基于 Spec 输出技术方案
- 明确开发的先后顺序
- 输出文档影响清单（DOC FIRST 铁律）
- 详见 `10-design/planning.md`

### Step 3：拆解任务（Tasks）

- 将计划拆分为原子化、独立的可执行任务
- 每个任务仅聚焦一个小功能 / 模块
- 粒度：2-5 分钟可完成

### Step 4：执行与验证（Implementation）

- AI 逐任务完成代码编写
- 强制 TDD：🔴RED → 🟢GREEN → ♻️REFACTOR
- 详见 `20-development/tdd-workflow.md`

### Step 5：迭代与维护

- 需求迭代时**先更新规格文档**，再驱动 AI 修改代码
- 保证规格文档与实际代码始终同步（DOC SYNC GATE）
- 详见 `20-development/doc-sync-protocol.md`

---

## 五、Spec 的三条不变量

无论哪种档位，Spec 都必须满足：

1. **可测试**：每条业务规则都能转化为测试用例
2. **无歧义**：AI 读完 Spec 不需要追问就能开始
3. **可演进**：变更走 Spec 变更记录，不直接改代码

---

## 六、SDD 与其他方法论的关系

| 对比 | 关注点 | 关系 |
|------|--------|------|
| SDD vs TDD | SDD 关注"需求和系统行为是否定义清楚"；TDD 关注"代码是否满足预期" | **SDD 在 TDD 之前**，先用 SDD 明确规格 → 再用 TDD 验证规格 |
| SDD vs BDD | BDD 关注"系统行为是否符合业务场景"；SDD 关注"在 AI 开始实现前，人类意图是否被清楚表达" | SDD 偏前置契约，BDD 偏行为验证 |
| SDD vs DDD | DDD 关注"领域建模"；SDD 不强制领域驱动，但可与 DDD 共用语言 | 可叠加：DDD 提供领域词汇 → SDD 写入 Spec |
| SDD vs Agile | Agile 关注"迭代响应变化"；SDD 是 Agile 在 AI 时代的具体落地形式 | 不冲突，SDD 让迭代有锚 |

**理想组合**：先用 SDD 明确规格 → 再用 TDD/BDD 验证规格。

---

## 七、Spec 文件约定

### 文件位置（唯一合法路径）

```
docs/specs/                       ← 所有 Spec 的唯一根目录
├── INDEX.md                      ← Spec 索引（编号、状态、版本、最后更新）
├── 001-auth/                     ← L0 基础设施层
│   ├── spec.md
│   ├── tasks.md
│   └── checklist.md
├── 002-database/                  ← L0 基础设施层
├── 050-user/                      ← L1 业务核心层
├── 100-dashboard/                 ← L2 业务应用层
└── 150-payment-gateway/           ← L3 集成与网关层
```

### 编号机制

#### 层次段位分配（从底层到应用层）

> **编号反映层次依赖关系，不是创建顺序。底层被依赖的模块拿小号，上层依赖别人的模块拿大号。**

| 段位 | 编号范围 | 层次 | 典型内容 |
|------|---------|------|---------|
| L0 | 001-049 | 基础设施层 | auth、db、storage、queue、cache、config |
| L1 | 050-099 | 业务核心层 | user、order、product、payment、inventory |
| L2 | 100-149 | 业务应用层 | dashboard、report、notification、search |
| L3 | 150-199 | 集成与网关层 | third-party-api、webhook、export、import |
| L4 | 200-249 | 前端页面层 | page-layout、component-library、routing |
| 自定义 | 250-999 | 扩展预留 | 按需分配 |

**分配规则**：
1. 先在 INDEX.md 中确定当前段位内的最大编号
2. 段位内递增 +1（不是全局递增）
3. 跨段位时跳到目标段位的起始编号
4. 例如：已存在 003-auth(L0)、051-user(L1)，新建 dashboard(L2) → 取 100

#### 常规属性

| 元素 | 说明 |
|------|------|
| 编号格式 | 3 位数字前缀：`001-`、`002-`、... |
| 编号不变 | 一旦分配，永不变更（即使 Spec 废弃，编号保留） |
| INDEX.md | 每次新建/状态变更/废弃时更新，是**文档运维的真相来源** |

### 文件命名

- 目录全小写、连字符分隔：`001-user-auth`、`002-batch-download`
- 编号前缀必须 >= 3 位（自动补零）
- 不用日期前缀（日期记在 Spec 内的"变更记录"章节和 INDEX.md 内）

### 路径硬约束

```
✅ docs/specs/{编号}-{feature}/spec.md       ← 唯一合法
✅ docs/specs/INDEX.md                        ← 唯一合法索引

❌ specs/{feature}/spec.md                     ← 禁止
❌ frontend/specs/{feature}/spec.md            ← 禁止
❌ frontend/docs/specs/{feature}/spec.md      ← 禁止
❌ docs/specs/{feature}/spec.md                ← 禁止
❌ src/specs/{feature}/spec.md                ← 禁止
❌ {any}/{any}/spec.md                        ← 禁止
```

### INDEX.md 结构

```markdown
# Spec Index

> 最后更新: YYYY-MM-DD

| 编号 | 功能 | 状态 | 版本 | 创建 | 最后更新 |
|------|------|------|------|------|----------|
| 001 | auth | implemented | 1.2.0 | 2026-01-15 | 2026-03-20 |
| 002 | database | implemented | 1.0.0 | 2026-01-15 | 2026-02-10 |
| 050 | user | approved | 0.1.0 | 2026-03-21 | 2026-03-21 |
| 100 | dashboard | draft | 0.1.0 | 2026-06-01 | 2026-06-01 |
| 150 | payment-gateway | deprecated | 1.0.0 | 2026-02-10 | 2026-05-15 |
```

### 与 docs/modules/ 的关系

| 文档 | 用途 | 写入时机 |
|------|------|---------|
| `docs/specs/{编号}-{feature}/spec.md` | 需求规格（人类意图） | 编码前 |
| `docs/modules/{module}.md` | 模块文档（实现状态） | 编码前 P0 同步 + 编码后更新 |
| `docs/CODEMAPS/` | 架构地图 | 大迭代后由 fullstack-doc-updater 生成 |

**关键区分**：Spec 是"要做什么"，模块文档是"已经做了什么"。Spec 是 input，模块文档是 output 之一。

### Spec 状态流转（生命周期）

| 状态 | 含义 | 触发条件 |
|------|------|---------|
| `draft` | 撰写中 | Spec 创建 |
| `review` | 待审批 | 撰写完成，等待用户确认 |
| `approved` | 已批准 | 用户确认，可进入规划 |
| `implemented` | 已实现 | 开发完成并通过审查 |
| `deprecated` | 已退役 | 长期未更新、被新 Spec 替换、或功能已移除 |
| `superseded by {编号}` | 被替换 | 指明替代的新 Spec 编号 |

**状态变更必须同步更新 INDEX.md。**

---

## 八、Spec 退役与替换机制

> Spec 不是永远的。它会过期、会被纠正、会被更好的 Spec 取代。

### 退役触发条件

满足以下任一条件，Spec 应标记为 `deprecated`：

- [ ] Spec 与模块文档/实际代码偏离超过 3 个月未同步
- [ ] Spec 描述的功能已被移除
- [ ] Spec 被另一个新 Spec 覆盖（标记 `superseded by {编号}`）
- [ ] Spec 的 Out of Scope 范围已不再适用
- [ ] 实现中发现了根本性的架构错误，Spec 从根上就是错的

### 退役流程

```
发现 Spec 应退役（fullstack-planner / fullstack-implementer / fullstack-reviewer 任一环节）
    ↓
在 INDEX.md 中将状态改为 deprecated（或 superseded by {编号}）
    ↓
在 Spec 文件头部添加退役标记：
    > ⚠️ **DEPRECATED** — 退役日期: YYYY-MM-DD
    > 退役原因: {简述}
    > 替代: {新 Spec 编号或"无替代"}
    ↓
回流 fullstack-spec-writer（如需要写替代 Spec）
```

### 替换流程

```
新 Spec 覆盖旧 Spec 时
    ↓
旧 Spec: 状态 → superseded by {新编号}
    ↓
新 Spec: §1 目标中声明"替代 {旧编号}"
    ↓
INDEX.md: 两条都更新
    ├── 旧 Spec: deprecated, superseded by {新编号}
    └── 新 Spec: draft/review/approved（按正常流程）
```

### INDEX.md 退役示例

```markdown
| 编号 | 功能 | 状态 | 版本 | 创建 | 最后更新 |
|------|------|------|------|------|----------|
| 150 | payment-gateway-v1 | deprecated | 1.0.0 | 2026-02-10 | 2026-05-15 |
| 151 | payment-gateway-v2 | approved | 0.1.0 | 2026-05-15 | 2026-05-15 |
```

---

## 九、Spec-First 何时升级为 Spec-Anchored

满足以下任一条件，建议从 Spec-First 升级：

- [ ] 该功能已经被 2 个以上模块依赖
- [ ] 已经迭代过 3 次以上
- [ ] 多人协作开发
- [ ] 出现过"AI 改 A 坏 B"的事故
- [ ] 测试用例数 > 20

---

## 十、什么时候可以跳过 Spec

以下场景可以不走完整 SDD，但仍建议写一句话规格：

| 场景 | 走法 |
|------|------|
| 改一个文案、调一个颜色 | 直接改代码，不需要 Spec |
| 修一个明显的 Bug | 走 `50-debugging/`，但要在 Spec 中补充"Bug 描述"作为根因记录 |
| 加一个字段、改一个返回值 | 走 `20-development/change-workflow.md` 的小变更流程 |
| 重构（不改行为） | 不需要新 Spec，但要更新现有 Spec 的"实现方式"章节 |

> **原则**：抓大放小。核心功能、复杂业务模块严格走 SDD；小修小补直接动手。

---

## 十一、检查清单

写完 Spec 后自检：

- [ ] 目标章节里有可验证的结果描述（不是"用户体验更好"这种模糊话）
- [ ] 范围章节明确写出 Out of Scope
- [ ] 每个用户故事都能对应到至少一个验收标准
- [ ] 数据模型有字段、类型、必填、说明
- [ ] API 契约有请求/响应/错误码
- [ ] 边界情况列了至少 3 个
- [ ] 待确认问题（Open Questions）有记录
- [ ] 变更记录有版本号
