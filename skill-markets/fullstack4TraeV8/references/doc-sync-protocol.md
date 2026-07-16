# 20-development / 文档同步协议（DOC SYNC Protocol）

> **定位**：DOC FIRST 铁律的具体落地。编码前的强制门禁。
>
> **上游**：`10-design/planning.md` 的"文档影响清单"  
> **下游**：`20-development/tdd-workflow.md`（DOC SYNC 通过后才能进入 TDD）

---

## 一、核心原则

**文档同步不是"写文档"，而是"知识一致性对齐"。**

目的是确保：当下次 AI（或人）读取文档时，看到的是最新的知识状态，而不是过时的"僵尸知识"。

**禁止猴子掰包谷**：知识不能只留在 `docs/specs/changes/` 施工图纸里。spec 敲定后、代码实现后，必须回流到持久化文档，否则每次重新拉起开发都要翻旧 spec。

### DOC SYNC 质量判定标准（V8 强化）

> "已同步" 不等于 "改了 header"。真正的同步意味着文档内容反映了最新变更的知识。

| 等级 | 判定 | 说明 |
|------|------|------|
| ✅ 深度同步 | 模块文档的能力列表/数据模型/状态机与 per-change 最新契约一致 | 这是合格的同步 |
| ⚠️ 浅同步 | 只改了 header（来源/版本号），核心内容未更新 | 视同未同步，需回溯 |
| ❌ 虚假同步 | 文件存在但内容与代码/契约不一致 | 状态失真，触发 L3 异常 |

**同步验证检查点：**
- 能力列表：模块文档中的能力数量/名称 = per-change spec 的 capability 数量/名称（去重后）
- 数据模型：模块文档中的字段/枚举值 = contracts/domain-models.md 的最新定义
- 状态机：模块文档中的状态枚举 = 代码中实际使用的枚举值
- 接口契约：模块文档中的接口签名 = contracts/api-contracts.md 的最新签名

### 禁止施工图纸路径引用（V8 NEW）

> 铁律 #6：项目级持久化文档禁止引用 `docs/specs/changes/` 路径。

**为什么：** `docs/specs/changes/{NN}-{name}/` 是施工图纸目录，变更完成后会被归档到 `docs/archive/done/` 或 `docs/archive/out/`。如果持久化文档引用这些路径，归档后会变成死链。

**正确做法：**
- 持久化文档（`docs/modules/`、`docs/design/`、`docs/contracts/`）之间互相引用
- 引用格式：`[模块名](../modules/{module}.md)`、`[契约](../contracts/{contract}.md)`
- 禁止格式：`[spec](../specs/changes/07-xxx/specs/...)` ← 施工图纸路径

**DOC SYNC 时必须检查并清除所有 specs/changes/ 引用。**

### 持久化文档四件套（DOC SYNC 覆盖范围）

| 文档类型 | 路径 | 内容 |
|---------|------|------|
| **模块文档** | `docs/modules/{module}.md` | 接口契约表、数据模型、职责边界、关联模块 |
| **产品文档** | `docs/modules/`（产品级） 或项目根产品 spec | 产品设计结论、功能描述、用户流程 |
| **前端设计文档** | `docs/modules/`（前端架构） 或独立设计文档 | UI/UX 设计决策、组件架构、布局方案 |
| **契约/协议文档** | 从 `contracts/` 回流到模块文档 | 接口协议最终形态、领域模型、事件契约

---

## 二、同步时机决策树

```
变更即将发生
    ↓
变更类型？
    │
    ├── 新增模块/接口/数据模型 ───── 编码前同步（写"将要变成什么"）
    │
    ├── 修改现有接口/数据模型 ───── 编码前同步（写"将要改成什么"）
    │
    ├── 新增页面/组件 ─────────── 编码前同步（写页面设计文档）
    │
    ├── 重构 ─────────────────── 编码前同步（写目标架构）
    │
    ├── Bug 修复 ─────────────── 编码后同步（写"修了什么"）
    │
    └── 纯 UI 样式调整（无逻辑变更） ─ 无需同步文档
```

---

## 三、同步执行五步

### Step 1: 读取现状

DOC SYNC 的主源是 **planner 产出的文档影响清单**（内嵌在 `design.md` 第一章），不是靠搜索发现。影响清单已明确列出了每份需同步的文档及变更内容。

**V8 辅助增强**：在读取影响清单列出的文档之外，用 doc-map-manager 做交叉验证。

```bash
# 1. Git diff 精确检测（推荐）：对比 specs/ vs modules/ 变更缺口
python build-index.py --git-diff
# → 自动按子目录分类输出 ADDED / MODIFIED / DELETED
# → 自动检测 DOC SYNC 缺口：specs 有新增但 modules 未覆盖时提醒 ⚠️

# 2. mtime 回退（不需要 Git 时）
python build-index.py --diff
# → 输出 ADDED / DELETED / MODIFIED 列表
# → 对比文档影响清单 → 清单外的 MODIFIED → 标记 ⚠️ 意外变更
# → 清单上的 DELETED → 🛑 文档丢失，阻塞

# 3. 如果索引不存在，先建立
python build-index.py --incremental
```

然后基于文档影响清单，读取受影响的文档：

```bash
# 只读影响清单里标记的模块文档
cat docs/modules/{affected-module}.md
```

**关键区别**：`--diff` 是安全网（检测计划外的文件变动），不是导航仪（不替代文档影响清单）。同步范围永远由 planner 的影响清单决定。

### Step 2: 生成变更差异

对每份受影响文档，明确：

| 字段 | 说明 |
|------|------|
| 文档路径 | `docs/modules/xxx.md` |
| 当前状态 | 文档中当前描述的是什么 |
| 目标状态 | 本次变更后应该描述什么 |
| 变更动作 | 新增条目 / 修改条目 / 删除条目 / 无变更 |

### Step 3: 按优先级执行同步

#### P0 - 持久化文档核心内容（**必须同步，编码前**）
- 模块文档：接口契约表（新增/修改接口行）、数据模型描述（新增/修改字段）、职责边界
- 产品文档：功能描述、用户流程、产品设计结论
- 前端设计文档：组件架构、布局方案、UI/UX 设计决策
- 契约/协议文档：接口协议最终形态、领域模型、事件契约（从 contracts/ 回流）

#### P1 - 模块文档辅助内容（应该同步，编码前或编码中）
- 关联模块表（如依赖关系变化）
- 状态标记（beta → stable）
- 版本号递增

#### P2 - 全局文档（可以延后，但编码后必须同步）
- `docs/ARCHITECTURE.md`（模块增减、架构调整时）
- `docs/dependency-matrix.yaml`（依赖关系变化时）
- `docs/DECISIONS.md`（架构决策时）

#### P3 - 低优先级（大迭代结束时同步即可）
- CHANGELOG
- index.md

### Step 4: 一致性自检

同步完成后，自检 3 个问题：

1. **接口一致性**：文档中每个接口，代码中都有对应实现（或标注"待实现"）？
2. **模型一致性**：文档中描述的数据模型，与 TypeScript 类型定义一致？
3. **依赖一致性**：文档中记录的模块依赖，与实际 import 关系一致？

### Step 5: 输出同步报告 + 重建索引

同步完成后：

1. 输出同步报告（格式见下方）
2. **V8：重建文档索引**

```bash
# DOC SYNC 完成后必须重建索引，确保下次 --diff / --grab 基于最新状态
python build-index.py --incremental
```

```markdown
## 文档同步报告

### 同步范围
- 受影响文档: X 个
- 同步优先级: P0:X  P1:X  P2:X

### 已同步变更
| 文档 | 类型 | 优先级 | 变更类型 | 变更内容 |
|------|------|--------|---------|---------|
| docs/modules/ai-services.md | 模块文档 | P0 | 新增 | 添加 ProviderAdapter 接口契约 |
| docs/modules/aigc-engine.md | 模块文档 | P0 | 修改 | Task 类型增加 priority 字段 |
| docs/modules/shuxia-product.md | 产品文档 | P0 | 新增 | F-001 世界观浏览功能描述 |
| docs/modules/writing-frontend.md | 前端设计 | P0 | 修改 | DraftEditor 组件交互说明更新 |
| docs/dependency-matrix.yaml | 全局 | P2 | 修改 | 新增 ai-services → aigc-engine 依赖 |

### 一致性自检
- [x] 接口一致性
- [x] 模型一致性
- [x] 依赖一致性

### 待同步（P2/P3，可延后）
| 文档 | 变更内容 | 计划时间 |
|------|---------|---------|
| docs/ARCHITECTURE.md | 新增 ProviderAdapter 层描述 | 本次迭代结束时 |
```

---

## 四、模块文档标准结构

每个模块文档应包含以下核心章节：

```markdown
---
module: {模块名称}
status: beta | stable | deprecated
version: 1.0.0
last_updated: YYYY-MM-DD
---

# {模块名称}

## 一句话描述
{从需求中提取}

## 职责边界
- ✅ {负责什么}
- ❌ 不负责：{不负责什么}

## 数据模型
| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| id | string | 是 | 唯一标识 |

## 接口契约
| 接口 | 输入 | 输出 | 文件 | 状态 |
|------|------|------|------|------|
| createXxx | CreateInput | Xxx | src/lib/xxx.ts | ✅ 已实现 |

## 关联模块
- [模块A](./module-a.md) — 依赖原因

## 变更记录
| 日期 | 版本 | 变更 | 提交 |
|------|------|------|------|
| YYYY-MM-DD | 1.0.0 | 初始设计 | - |
```

---

## 五、迷雾消除流程（开发现有模块时文档缺失）

**触发条件**：开发现有模块时，`docs/modules/{module}.md` 不存在或核心章节缺失。

```
C1: 发现迷雾 → 从代码分析接口/模型/依赖
C2: 汇报迷雾 → 展示缺失范围（🔴完全 🟡部分 🟢轻微）
C3: 头脑风暴 → AI 推断 + 用户确认（不猜测不虚构）
C4: 反推生成 → 以代码为事实，写入 docs/modules/{module}.md
    → 迷雾消除完成 → 进入正常开发
```

### 迷雾等级与处理策略

| 等级 | 条件 | 处理策略 |
|------|------|---------|
| 🔴 完全缺失 | 文档不存在 | 必须走完整迷雾消除流程（C1-C4） |
| 🟡 部分缺失 | 核心章节缺失 > 2 | 走迷雾消除，但只补缺失章节 |
| 🟢 轻微过时 | 接口/模型与代码有小差异 | 直接走 DOC SYNC 同步，不需要头脑风暴 |

### 关键原则

- **不阻断开发**：迷雾消除是开发的"前置准备"，不是"停工写文档"
- **渐进式补全**：每次开发只消除涉及的模块迷雾，不需要一次补全所有
- **代码即事实**：文档以代码为准，不虚构、不猜测
- **待确认可留白**：用户说"不清楚"的，标注 `🤔 待确认`，不阻塞后续开发
- **积累效应**：开发 N 个模块就消除 N 个迷雾，文档自然逐步完整

---

## 六、常见问题

### Q: 编码中发现文档描述有误怎么办？

**A: 停下来，先修正文档，再继续编码。**

这看似低效，但实际上是高效的：
- 修正文档让你重新审视设计，可能发现编码方向错误
- 文档修正确保后续开发者不会读到错误信息
- 记录"为什么文档是错的"本身就是有价值的知识

### Q: 小改动也需要走完整同步流程吗？

**A: 不需要。**

小改动（≤3 文件，单模块内）只需要：
1. 更新模块文档中对应的接口/模型描述
2. 添加变更记录
3. 不需要输出完整的同步报告

### Q: 文档同步和代码开发可以并行吗？

**A: 不可以。**

文档同步是编码的前置条件（DOC SYNC GATE 铁律）。但实际操作中：
- P0 内容必须在编码前完成
- P1 内容可以在编码的间隙完成
- P2/P3 内容可以在编码后完成

### Q: 已有的僵尸文档怎么处理？

**A: 发现即清理。**

- 代码已删除但文档还在 → 删除文档条目
- 接口已重构但文档还写旧签名 → 更新文档
- 模块已合并但文档还是两个文件 → 合并文档

### Q: 中途引入 SDD，现有模块文档完全缺失怎么办？

**A: 走迷雾消除流程，以代码为事实反推文档。**

### Q: 文档能放在 docs/ 之外的目录吗（如 specs/、frontend/specs/）？

**A: 不可以。**

所有文档的根目录是 `docs/`：

| 类型 | 唯一路径 | 禁止的变体 |
|------|---------|-----------|
| Spec | `docs/specs/` | `specs/`、`frontend/specs/`、`src/specs/`、`frontend/docs/specs/` |
| 模块文档 | `docs/modules/` | `docs/module/`、`modules/`、`src/docs/` |
| 全局文档 | `docs/` | `doc/`、`documentation/` |

发现文件写到了禁止路径 → 立即移动到正确路径。

详见上文"迷雾消除流程"。

---

## 七、V8 DOC SYNC 合并协议

> **V7 双写问题**：DOC SYNC #1（plan confirmed 后写内容）和 #2（review 后验证）两次写 modules/，容易产生重复和漂移。
>
> **V8 合并**：单写 + 标记流转。内容只写一次，用标记管理生命周期。

### 标记流转

```
Plan confirmed → DOC SYNC（写 modules/ 🟡 provisional）
     │
     ▼
  Code + Review（不改 modules/，只读契约）
     │
     ▼
Review PASS → Doc-Sync Confirm（验证一致性 + 🟡→🟢 confirmed）
     │
     ▼
  Commit
```

### 🟡 Provisional 写规则

DOC SYNC #1（plan confirmed 后）写入时：
- 新增模块 → 用 `status: provisional` 标记
- 修改现有模块 → 被修改段落用 `<!-- V8-provisional-start -->...<!-- V8-provisional-end -->` 包裹
- Cockpit 状态 → `🟡 modules/ 待验证`

### 🟢 Confirmed 验证规则

Doc-Sync Confirm（review PASS 后）验证时：
- 逐条检查 provisional 标记内容与代码/契约的一致性
- 一致 → 移除 provisional 标记，改为 `status: stable` 或正常文档内容
- 不一致 → 🛑 退回 implementer 修复漂移
- Cockpit 状态 → `🟢 modules/ 已验证`

### 合并 vs 双写对比

| 维度 | V7 双写 | V8 合并 |
|------|---------|---------|
| 写次数 | 2 次（#1 + #2） | 1 次（provisional write） |
| 漂移风险 | #1 和 #2 之间可能产生漂移 | 低（内容从同一个来源写入） |
| 标记 | 无（不知道哪些是 #1 写的） | 🟡 provisional → 🟢 confirmed |
| 回滚 | 困难（#1 和 #2 的内容混在一起） | 简单（移除所有 🟡 标记即可回滚） |
| 审计 | 无（不知道哪些是已确认的） | 可审计（🟢 = 已确认，🟡 = 待验证） |

---

## 八、Doc-Updater 详细场景步骤

> 被 `agents/doc-updater.md` 引用。含 8 个场景的完整步骤、代码块、路径说明。

### 场景 1: 生成 Codemap（V5 保留）

```
分析代码结构
    ↓
识别模块和依赖
    ↓
生成架构地图
    ↓
输出到 docs/CODEMAPS/
```

### 场景 2: 架构变更后更新（V5 保留）

```
检测架构变更
    ↓
重新分析依赖关系
    ↓
更新 codemaps + ARCHITECTURE.md
```

### 场景 3: Prototypes 回流（V7 NEW）

```
per-change 原型完成（develop 阶段结束）
    ↓
doc-updater 读取 per-change prototypes/
    ↓
提取可复用的组件/页面 → 写入 docs/prototypes/
    ↓
更新 docs/prototypes/ 的索引
    ↓
更新 Cockpit：prototypes/ ✅ 最新
```

**回流规则**：
- 纯新增组件 → 直接添加
- 覆盖已有组件 → 标记版本变化，保留旧版注释
- 仅本次变更使用的一次性原型 → 不回流入项目级（保持清洁）

### 场景 4: Archive 维护（V7 NEW）

#### 淘汰归档（archive/out/）

```
change 被 30% 合并/用户放弃/方向变更
    ↓
读取 change 所有工件 → 打包移动到 docs/archive/out/{change-name}/
    ↓
移除 docs/specs/changes/ 下的原目录
    ↓
更新 Cockpit：移除该 change 行
```

#### 完成归档（archive/done/）

```
change 验收通过 + 已合并到 module.md
    ↓
读取 change 的 design.md + tasks.md（保留决策推演）
    ↓
移动到 docs/archive/done/{change-name}/
    ↓
移除 docs/specs/changes/ 下的原目录
    ↓
更新 Cockpit：标记该 change 已完成
```

### 场景 5: test-plan/ 同步（V7 NEW）

```
测试策略变更 → 触发同步
    ↓
读取 docs/test-plan/ 现有内容
    ↓
根据架构变更更新测试策略
    ↓
更新 Cockpit：test-plan/ ✅ 已定义
```

### 场景 6: 文档索引重建（V8 NEW）— 所有场景末强制执行

```
任意场景完成（Codemap/Prototypes/Archive/test-plan）
    ↓
通过 doc-map-manager 技能更新文档索引（V9.1 NEW — 禁止直接编辑）
    ↓
先执行 DOC SYNC 缺口检测（V10 NEW）:
  build-index.py --git-diff → 自动发现新增/修改但未同步的文档
    ↓
确认文档索引文件已更新（通过 doc-map-manager 技能验证）
    ↓
检查 build-index.py 是否静默修改了 .gitignore
  → 如有修改 → 🛑 回退修改 + 报告（P0-2 教训）
    ↓
输出：[索引] N 个文件已更新
```

### 场景 7: Retro-Spec 完成 → 清除 Cockpit Bug（V8 NEW）

```
Bug 修复完成 + Retro-Spec 通过
    ↓
1. 读取 docs/specs/.state-card.md 的 🐛活跃缺陷段
2. 将状态为 ✅已修复 的 bug 行标记为 ~~删除线~~ 或移除
3. 保留 bug 历史一行注释: <!-- B{n}已修复于{date} -->
4. 更新 Cockpit 健康概览的阻塞数
```

**规则**：
- 已修复 bug 不移除历史（保留为注释），供后续审计
- 如果全部 bug 已修复 → 🐛段恢复为 "— 无活跃缺陷 —"

### 场景 8: 🔷 基石模块接入手册生成（V8 NEW）

> **触发条件**：spec-writer 或 contract-writer 在工件中标记此模块为 🔷 Foundational。

```
收到 🔷 Foundational 标记
    ↓
1. 读取 spec.md 中 "Published Interfaces" / "Integration Points" 段
2. 读取 contracts/ 中标记为 published 的接口定义
3. 生成接入手册模板 modules/{module}/integration.md:
   ├── 模块定位: 此模块提供什么基础能力
   ├── 接入步骤: Step-by-step 调用流程
   ├── 约定规范: 错误处理方式 / 命名规则 / 配置格式
   ├── 接口速查: 所有 published API 的签名 + 参数
   ├── 反例: 常见错误用法 (≥ 2 个)
   └── 示例: 最小可用接入代码
4. 在 modules/{module}.md 中标记 "🔷 Foundational → 接入手册: integration.md"
5. 更新 Cockpit 项目级工件: integration-manuals/: ✅ 最新
6. 更新 docs/integration-manuals/ 索引（如存在）
```

**判断基石模块的标准**：
- 定义了其他模块调用的公共 API/事件
- 定义了全局异常处理模式
- 定义了 UI/UX 组件库的接入约定
- 定义了数据模型的继承/扩展规范
- 定义了配置文件的格式和覆盖规则

**输出位置**:
- 模块目录已存在 → `modules/{module}/integration.md`
- 模块目录不存在 → `docs/integration-manuals/{module}.md`

### 输出格式参考

#### CODEMAPS 结构（V5 保留）

```
docs/CODEMAPS/
├── INDEX.md          # 架构总览
├── frontend.md       # 前端架构
├── backend.md        # 后端架构
├── database.md       # 数据库结构
└── integrations.md   # 外部集成
```

#### Prototypes 项目级结构（V7 NEW）

```
docs/prototypes/
├── README.md          # 组件速查索引
├── pages/             # 页面级原型
│   └── {page}.md
└── components/        # 共享组件
    └── {component}.md
```

#### Codemap 模板

```markdown
# [Area] 架构地图

**更新时间**: YYYY-MM-DD
**入口文件**: list of main files

## 核心模块
| 模块 | 职责 | 入口 | 依赖 |
|------|------|------|------|
| ... | ... | ... | ... |

## 数据流
[描述数据如何流动]

## 外部依赖
- package-name - 用途
```

---

## 九、DOC SYNC 禁止写入清单

> 核心原则：**项目级文档 = 地图（WHAT），施工记录 = change artifacts（HOW）。DOC SYNC 只写地图，不写施工日志。**

### 禁止写入项（写入前必须检查）

| # | 禁止写入内容 | 应放哪里 | 原因 |
|---|------------|---------|------|
| 1 | Review 评分 / 测试覆盖数 / commit hash | 留在 change 的 completion report | 施工日志，对理解系统无帮助 |
| 2 | DOC SYNC 时间戳 / 操作人 | 留在 change 的 .state-card.md | 流程元数据，不是架构知识 |
| 3 | Bug 修复过程描述 | 留在 change 的 spec 或 buglist | 修复过程不是系统描述 |
| 4 | 实现细节（算法选择、优化技巧、踩坑记录） | 留在 change 的设计文档 | 属于"怎么做的"，不是"是什么" |
| 5 | 已废弃的接口/版本 | 删除，不保留在模块文档 | 模块文档只描述当前状态 |
| 6 | per-change 的 task 列表 / 进度 | 留在 change 的 tasks.md | 施工进度不是架构 |
| 7 | 中间版本的设计方案 | 留在 change archive | 只保留最终决定 |
| 8 | 任何 `docs/archive/` 目录下的文件内容 | 不动（不读、不改、不修剪） | 归档文件 = 只读 git 历史，DOC SYNC 已提炼到项目级文档 |

### 允许写入项（仅以下内容可写）

| # | 允许写入 | 写入位置 | 粒度 |
|---|---------|---------|------|
| 1 | 模块新增/删除/重命名 | ARCHITECTURE.md / INDEX.md | 1-2 行 |
| 2 | 接口契约变更（@published） | modules/{module}.md 接口契约表 | 每接口 1 行 |
| 3 | 数据模型字段增删改 | modules/{module}.md 数据模型表 | 每字段 1 行 |
| 4 | 架构层级关系变化 | ARCHITECTURE.md 架构全景图 | 1 段 ≤10 行 |
| 5 | 新增关联模块依赖 | modules/{module}.md 关联模块表 | 每依赖 1 行 |
| 6 | 状态标记更新 | modules/{module}.md header | 1 行（status/version/last_updated） |
| 7 | 设计决策（仅最终决定） | ARCHITECTURE.md 或 ADR | ≤5 行摘要 + 指向 ADR |

### 检查方式

DOC SYNC 完成后，逐条自检：

```
[ ] 没有 Review 评分出现在项目级文档
[ ] 没有 DOC SYNC 时间戳出现在项目级文档
[ ] 没有 Bug 修复描述出现在项目级文档
[ ] 没有实现细节出现在项目级文档
[ ] 模块文档变更 ≤ 50 行（超出则说明写了实现细节）
[ ] ARCHITECTURE.md 变更 ≤ 10 行（超出则说明写了施工日志）
```

---

## 十、文档体积硬上限

> 每类项目级文档有硬上限。DOC SYNC 写入前检查，超出时必须先 prune 再写。

### 硬上限表

> 阈值来源 → [thresholds.md](thresholds.md)

| 文档 | 硬上限 | 超出时动作 | 检查频率 |
|------|:---:|------|:---:|
| `.state-card.md` | 80 行 | 执行重置（见 artifact-lifecycle.md §3） | 每次 DOC SYNC |
| `ARCHITECTURE.md` | 500 行 (doc-sync 特有) | 拆分实施状态段 → 对应 change archive，目标 ≤ 350 行 | 每次 DOC SYNC |
| `modules/*.md`（单个） | 300 行 (doc-sync 特有，与变更记录表 100 行不同) | 拆分子文档或提取独立 spec，目标 ≤ 200 行 | 每次 DOC SYNC |
| `.history.md` 索引表 | 20 行 (doc-sync 特有) | 归档旧条目到 `archive/history/` | 每次 Archive |
| `INDEX.md` | 10KB / 150 行 (doc-sync 特有) | 拆分到二级索引文件 | 每次 DOC SYNC |
| `completion report` | 30 天后 (doc-sync 特有) | 移至 `archive/reports/` 或删除 | 每次 intake 步骤 0 |

### Prune 优先级

```
超出硬上限
  │
  ├── 1. 找重复内容 → 删除（同一信息出现在多处）
  ├── 2. 找施工日志 → 迁移到 change archive
  ├── 3. 找过期信息 → 删除（已废弃接口/模块/决策）
  ├── 4. 找可压缩段 → 合并同类项
  └── 5. 仍超出 → 🛑 汇报用户，附带「为什么超出」分析
```

### 体积警告

Intake 步骤 0 健康快检时，如果文档接近硬上限的 80%，在 Cockpit 🐛 段写一条警告：

```
| B{n} | {文档名} 接近体积上限（{当前行数}/{上限}） | — | 🟡 | 建议下次 DOC SYNC 前 prune | {日期} |
```

---

## 十一、文档治理决策树

> Agent 发现文档问题时，按此树自主决策，只在最末层问用户。

### 步骤 0: 归档文件零级防火墙（最优先）

```
操作目标文件路径含以下前缀 → 🛑 立即停止，此文件不在治理范围内：
  docs/archive/done/
  docs/archive/out/
  docs/archive/history/
  docs/archive/reports/

原因: DOC SYNC 已将归档 change 的知识提炼到项目级文档（ARCHITECTURE/modules/）。
      归档文件 = 只读 git 历史记录，不读、不改、不修剪、不治理。
      唯一合法操作: 归档新品（archive phase），不是修剪旧品。
```

### 步骤 1: 严重度判定

```
发现文档问题
  │
  ├── 🔴 CRITICAL（任一）
  │     ├── .state-card.md > 80 行
  │     ├── 无 docs/INDEX.md
  │     ├── ARCHITECTURE.md 噪音占比 > 70%
  │     └── ARCHITECTURE.md > 500 行
  │     → 必须治理，不可推迟。记录到 Cockpit 🐛 段。
  │
  ├── 🟡 HIGH（任一）
  │     ├── ARCHITECTURE.md 噪音 > 50%
  │     ├── 单个 modules/*.md > 300 行
  │     ├── 模块文档 header 有实施标记（DOC SYNC 时间戳 / Review 评分）
  │     └── completion report > 30 天未清理
  │     → 治理变更最晚下一次 DOC SYNC 附带修复。
  │
  └── 🟢 LOW
        ├── 模块文档 header 轻微污染（≤3 行）
        └── 孤立文件 / 死链接
        → 记入 Cockpit 🐛 段，下次顺手修。
```

### 步骤 2: 范围 + 根因判定

```
严重度已定
  │
  ├── 范围
  │     ├── 1 个文件 → ponytail 直改（在当前上下文中直接修复）
  │     ├── 2-4 个文件 → 附加到当前活跃 change 的治理增量
  │     └── 5+ 个文件 → 建独立治理 change（mini proposal ≤10 行）
  │
  └── 根因
        ├── 历史遗留（以前没约束）→ 一次性清理
        ├── 流程缺失（协议没写禁止项）→ 清理 + 改协议文件
        └── 协议写了但 Agent 没遵守 → 不改协议，修 Agent 行为
```

### 步骤 3: 用户确认阈值

```
治理范围 ≤ 10 个文件 + 不改引用/protocol 文件 → Agent 自主执行，Cockpit 记录
治理范围 > 10 个文件 → 问用户确认范围
涉及改 protocol/reference 文件 → 问用户确认（展示改什么、为什么改）
涉及 archive/done/  → 不动（已归档视为已沉淀）
```

### 治理 change 简化链

```
纯文档治理（无 src/ 变更）→ ponytail 模式
  ├── 跳过 Contract/Plan/Review 委派
  ├── 主上下文直做变更
  └── 仅产出 completion report + 更新 Cockpit
```

---

## 十二、.history.md Append-Only 协议

> `.history.md` = 已完工 change 的签名簿。不是施工日志，不是 DOC SYNC 存档。

### §1 职责

| 它是 | 它不是 |
|------|--------|
| 已完成 change 的编号 + 名称 + 归档日期 | 每个 DOC SYNC 的逐文件变更清单 |
| 关键决策摘要（≤5 行） | Review 评分、测试数、commit hash |
| 归档路径（方便 agent 按需深挖） | 代码实现细节 |
| 对后续 agent 的意义/教训 | 完整验收报告 |

### §2 写入时机

**一个 change 一生只写一次**：Phase 9 Archive 归档时。

```
不是 Phase 5.5 DOC SYNC 写
不是 Phase 7 Review 写
不是每个中间事件写
不是 DOC SYNC 完成时写
只有 Archive 归档时写一条
```

### §3 写入方式

**APPEND ONLY — 禁止 Read 全文**：

```powershell
# ✅ Add-Content 直接追加，不读取文件
Add-Content -Path ".history.md" -Value "`n## NN-name (YYYY-MM-DD)"
Add-Content -Path ".history.md" -Value "`n- **结果**: ACCEPT 4.27/5.0"
Add-Content -Path ".history.md" -Value "`n- **关键决策**: ..."
Add-Content -Path ".history.md" -Value "`n- **归档路径**: ..."
Add-Content -Path ".history.md" -Value "`n- **对 agent 的意义**: ..."
```

```powershell
# ❌ 禁止：Read 全文 → 修改 → 写回（随文件增大必然击穿）
$content = Get-Content ".history.md"        # ← 31KB+ 击穿
$content += "new entry"
Set-Content ".history.md" $content
```

**索引表更新例外**：顶部索引表 ≤ 20 行，可以 Read 前 20 行后修改，但必须用 delimiter 包裹：

```markdown
<!-- HISTORY-INDEX-START -->
| Change | 归档日期 | 结果 |
|--------|---------|------|
| 00-base-prepare | 2026-07-06 | DONE |
<!-- HISTORY-INDEX-END -->
<!-- HISTORY-ENTRIES-START -->
## 00-base-prepare (2026-07-06)
...
<!-- HISTORY-ENTRIES-END -->
```

索引表 > 20 行时：归档最旧的 10 条到 `archive/history/`，索引表保持 ≤ 10 行。

### §4 条目模板

```markdown
## {NN}-{name} ({YYYY-MM-DD})

- **结果**: {ACCEPT 评分 \| DONE \| BLOCKED-XX} | {阻塞描述，无则省略}
- **关键决策**: {≤ 3 个决策，每个 ≤ 1 句话}
- **归档路径**: `archive/done/{NN}-{name}/`
- **对 agent 的意义**: {≤ 3 句话，告诉后续 agent 这个 change 产出了什么可复用的东西}
```

**单条 ≤ 50 行。不写**：
- ✗ Review 逐项评分
- ✗ 测试通过数 / 覆盖率
- ✗ DOC SYNC 文件变更清单
- ✗ 中间阶段的文档路径

### §5 Agent 使用协议

| 场景 | 操作 | 禁止 |
|------|------|------|
| "这个 change 做完了吗？" | `grep "NN-name" .history.md` | 禁止通读全文 |
| "16 的关键决定是什么？" | `grep -A 3 "16-" .history.md` | 禁止通读全文 |
| "近期归档了哪些？" | `head -20 .history.md`（只读索引表） | 禁止通读全文 |
| 写新条目 | `Add-Content`（不读） | 禁止先读后写 |
| "我想看完整历史" | 读索引表 → 按需 `grep` 目标条目 | 禁止 `cat .history.md` |

### §6 与 DOC SYNC 的边界

```
DOC SYNC 写的是: modules/*.md, ARCHITECTURE.md, .state-card.md
                → 描述"系统现在是什么"

.history.md 写的是: change 的完工签名
                → 记录"系统怎么变成现在这样的"（但只记名字和决策，不记过程）

两者互补，不是替代。DOC SYNC 不写 .history.md，Archive 不写 modules/。
```

---

## 十三、保真迁移协议

> 修剪/迁移项目级文档时，禁止丢失架构事实。三阶段机械验证：编目→执行→验证。任一阶段失败 = 回退，不继续。

### 核心原则

```
文档修剪 = 外科手术，不是斧劈
  └── 切掉的是噪音（Review 评分/实现细节/时间戳）
  └── 保留的是事实（架构决策/接口定义/模块职责/数据模型/不变量）
  └── 迁移的是历史（施工日志 → change archive / .history.md）
  └── 归档文件（archive/done/ + archive/out/）不在迁移范围内。DOC SYNC 已将其知识提炼到项目级文档。
    归档文件唯一合法操作是归档新品（archive phase），不修剪旧品。
```

### Phase A: 迁移前事实编目

**触发条件**：文档超过体积硬上限（§十），或噪音占比 > 50%。

**步骤**：

1. 读取目标文档全文
2. 提取所有**事实性断言**——对理解系统有意义的陈述。不包括元信息（时间戳/评分/操作人）。
3. 每一条事实标注分类：

```
[KEEP]   = 架构事实 → 留在原文档
[MOVE]   = 实施历史 → 迁移到 change archive 或 .history.md
[DELETE] = 死信息   → 删除（重复/过期/无意义）
```

4. 输出**事实编目表**（必须是可验证的编号列表）：

```markdown
| # | 事实摘要 | 来源行号 | 分类 | 目标 |
|---|---------|:---:|:---:|------|
| F01 | 系统采用 Event-Driven 架构，通过 MessageBus 解耦 | L12 | KEEP | ARCHITECTURE.md §1 |
| F02 | C14 拖拽跟手通过 requestAnimationFrame + delta 补偿实现 | L503 | MOVE | archive/done/10-app-shell/ |
| F03 | §V8 阶段编号映射表（V7→V8） | L9 | DELETE | —（已沉淀到 ADR-028） |
| F04 | 模块 03-task-queue 提供 TaskEnqueue/TaskDequeue 接口 | L245 | KEEP | ARCHITECTURE.md §2 |
```

### Phase B: 执行迁移

**B1. KEEP 事实 — 原地保留**

```
- 编辑目标文档，确保每个 [KEEP] 事实在新文档中可找到
- 对每个 KEEP 事实 → 在编目表标记 "✅ 已保留 @ 新行号"
- 如果某个 KEEP 事实无法在新的精简结构中自然呈现 → 🛑 回流 Phase A 重新分类
```

**B2. MOVE 事实 — 迁移+链接**

```
- 提取 [MOVE] 事实到目标位置（change archive / .history.md / ADR）
- 在源文档原位置保留 1 行交叉引用：
    > 实施详情见: archive/done/10-app-shell/specs/spec.md §C14
- 在编目表标记 "✅ 已迁移 → {路径}"
```

**B3. DELETE 事实 — 删除**

```
- 从源文档删除死信息
- 在编目表标记 "✅ 已删除"
- 死信息不保留副本（git history 可追溯原始版本）
```

### Phase C: 迁移后验证

**四项硬性检查，全部 PASS 才放行**：

| # | 检查 | 通过标准 | 失败处理 |
|---|------|---------|---------|
| C1 | **计数守恒** | KEEP 事实数 + MOVE 事实数 = 编目表总数（不含 DELETE） | 🛑 回退，逐个查找丢失事实 |
| C2 | **KEEP 审计** | 随机抽样 30%（至少 3 条）KEEP 事实，grep 验证在精简后文档中仍存在 | 🛑 回退，补全后重试 |
| C3 | **MOVE 链接** | 所有 MOVE 事实的交叉引用链接路径存在且可读 | 🛑 回退，修正链接 |
| C4 | **自洽性** | 新文档内部引用无断裂（`[modules/XX.md]` 指向文件存在） | 🟡 标记，继续（下次 DOC SYNC 修复） |

### 最小化原则

```
1. 一次只修剪一类问题（先清 ▲ARCHITECTURE 再清 ▲modules）
2. 一次修剪 ≤ 200 行变更（超出则分批）
3. 每批修剪后完整验证（Phase C），不跨批攒着一起验
4. 涉及 2 个以上文件的修剪 → 必须建独立治理 change
```

### 回退协议

```
Phase A FAIL（无法分类） → 缩小修剪范围，只处理明确可分类的行
Phase B FAIL（KEEP 无法保留）→ 回退该条 → 降级为 MOVE
Phase C FAIL（验证不通过）→ 回退整批修剪 → 用户决策: 修正重试 / 放弃
连续 2 批失败 → 🛑 停止，汇报用户: "文档结构需要重新设计，当前 trim 逻辑无法保证不失真"
```

### 快速自检清单（执行前打印到对话）

```
[ ] Phase A: 事实编目表已输出（含分类+目标）
[ ] Phase B: 每个 KEEP 已标记新行号 / 每个 MOVE 已标记目标路径
[ ] Phase C1: 计数守恒 = 是
[ ] Phase C2: KEEP 审计 ≥ 30% 通过
[ ] Phase C3: MOVE 链接全部可读
[ ] Phase C4: 内部引用无断裂
[ ] 修剪变更 ≤ 200 行（超出则分批）
```
