# Agents 引用指南 — V8

**如何在项目 rules 中引用 fullstack 技能包的 Agent（V8）。**

---

## 1. 技能包概览（V8 — Cockpit + 10 Agent + Roundtable + DOC SYNC + Buglist-Cockpit）

| Agent | 触发词 | 输入 → 输出 | 工具集 |
|-------|--------|------------|--------|
| **Cockpit 驾驶舱**（V8） | 会话启动 / 状态 / 驾驶舱 | 项目级 .state-card.md → Cockpit 快照 + 自检结果 | Read, Grep, Glob |
| `fullstack-intake` | 任意需求起始 / 定位 / 在哪一步 | 用户需求 → 流程定位卡 + 去重报告 + 影响面清单 + 两层状态卡 | Read, Grep, Glob, SearchCodebase, TodoWrite, AskUserQuestion, Write |
| **Bug-Batch 链**（V8） | bug 修复 / 报错 / 缺陷批量 / 紧急修复 | buglist.md → per-bug debugger → retro-spec.md + DOC SYNC + Buglist-Cockpit 联动 | intake(light) + debugger + doc-updater |
| `fullstack-proposal-writer` | 提案 / proposal / 新功能 / 需求分析 | intake 输出 → proposal.md | Read, Write, Grep, Glob, TodoWrite, AskUserQuestion |
| `fullstack-spec-writer` | 写规格 / 写spec / 需求文档 / E2E / 画原型 / 线框图 | proposal → specs/{capability}/spec.md + prototypes/{module}.md（涉及 UI 时） | Read, Write, Grep, Glob, TodoWrite, AskUserQuestion |
| **圆桌会议**（V8） | 圆桌 / 多角色 / 评审 / 头脑风暴 | specs → 6 子代理并行评审 → meeting-notes/round-{N}.md | Task（子代理）, Read, Write |
| `fullstack-contract-writer` | 写契约 / 定义接口 / 协议先行 / contract | specs + meeting-notes → contracts/ 四件套 + contract test 骨架 | Read, Write, Grep, Glob, TodoWrite, AskUserQuestion |
| `fullstack-planner` | 规划 / 设计 / 架构 / 重构 | contracts + specs → design.md（编号决策 + 契约一致性）+ tasks.md | Read, Write, Grep, Glob, TodoWrite, AskUserQuestion |
| `fullstack-implementer` | 实现 / 开发 / 写代码 / TDD | design + tasks + contracts + test 骨架 → 代码 + 测试 + tasks 全部 [x] + 量化汇报 | Read, Write, SearchReplace, RunCommand, GetDiagnostics, Grep, Glob |
| `fullstack-reviewer` | 审查 / 验证 / 检查 / review / 打分 | 代码 diff + 量化汇报 → 7 维度打分卡 + 漂移报告 + 目标对齐报告 | Read, Grep, Glob, RunCommand, GetDiagnostics, Write |
| `fullstack-debugger` | 调试 / debug / bug / 报错 | 错误描述 → 根因证据 + 修复代码 | Read, Write, SearchReplace, RunCommand |
| `fullstack-doc-updater` | 文档 / codemap / 架构图 / 同步文档 / 归档（V8） | 代码库 → CODEMAPS/ + prototypes/ 回流 + archive/ 维护 + test-plan/ 同步 | Read, Write, SearchReplace, Grep, Glob |
| `feedback-loop` | 漂移 / spec 错了 / 契约不对 / 目标失真 | 漂移报告 → 回流到对应 Agent | 详见 `references/feedback-loop.md` |
| **report-growth**（V8） | 写报告 / report / 总结反思 | 实战经验 → report-{0X}.md | Write |

---

## 2. V8 流水线总览

```
用户需求
  → [00-cockpit]   Cockpit           — 读项目级状态卡，输出全局快照 + 新会话自检（V7 NEW）
  → [00-intake]    Intake            — 意图识别 + 30%原子化去重 + 影响面 + 选链 + 两层状态卡（V7 强化）
  ├── Bug → [bug-batch]  Bug-Batch   — Buglist → Fix(debugger) → Retro-Spec + DOC SYNC（V7.2 NEW）
  ├── Feature → [00-proposal]  Proposal-writer — Why + What + Capabilities + Non-Goals + 影响面
  │   → [00-product]   Spec-writer       — BDD spec + E2E 场景 + 测试骨架 + 原型（涉及 UI 时）
  → [00-roundtable] 圆桌会议（可选）  — 6 子代理并行评审，meeting-notes 落盘（V7 NEW）
  → [01-contract]  Contract-writer   — 领域模型 + API 契约 + 事件契约 + 验证规则 + contract test 骨架
  → [10-design]    Planner           — design.md（编号决策 + 契约一致性）+ tasks.md
  → [12-docsync]   DOC SYNC (🟡→🟢)    — 知识回流持久化文档
  → [15-closure]   Closure-Define    — closure-checklist.md P0 闭环步骤
  → [20-dev]       Implementer       — CONTRACT GATE → TDD 五段式 → 量化汇报
  → [40-review]    Reviewer          — 7 维度打分卡 + 契约漂移 + 目标对齐
  → [40-accept]    Acceptance        — E2E + 性能 + 安全
  → [loop]         Feedback-loop     — 漂移强制回流
  → [report]       Report-growth     — 随时触发 + 交付整理（V7 NEW）
```

---

## 3. 在项目 rules 文件中引用

### 3.1 最小引用（复制粘贴即用）

```markdown
## AI 行为规则

本项目使用 fullstack V8 全栈文档驱动开发技能包，遵循 DOC FIRST + Contract-First + Spec-Driven + TDD + Cockpit 驾驶舱方法论。

### 开发流程

1. **Cockpit 先定位**：Agent 激活时先读项目驾驶舱，输出全局快照（V8）
2. **Intake 定位+去重**：任何需求先经 intake 定位意图 + 30% 原子化去重 + 初始化两层状态卡
3. **Proposal 声明意图**：Why + What + Capabilities + Non-Goals
4. **Spec 行为契约**：BDD 场景化 spec + E2E 场景 + 测试骨架 + 原型（涉及 UI 时）
5. **圆桌会议评审**（可选）：6 角色子代理并行审查，meeting-notes 落盘（V8）
6. **Contract 协议先行**：领域模型 + API 契约 + 事件契约 + 验证规则 + contract test 骨架
7. **Design 编号决策**：基于契约的 design.md + tasks.md
8. **DOC SYNC (🟡→🟢)**：单写+标记机制，知识回流持久化文档（V8）
9. **Closure-Define**：closure-checklist.md P0 闭环步骤定义（V8）
10. **TDD 五段式编码**：CONTRACT TEST → RED → GREEN → REFACTOR → DRIFT CHECK
11. **量化审查验收**：reviewer 7 维度打分卡（≥ 4.0）→ acceptance 验收
12. **漂移回流 + Report 生长**：发现漂移强制回流；磕绊写 report，交付必整理（V8）

### 通用约束

- 优先级链：contracts/ > 模块文档 > Spec > 代码
- 所有变更存入 docs/specs/changes/，完成后移入 archive/done/，淘汰的移入 archive/out/
- TDD 覆盖率 > 80%，关键路径 100%
- 状态卡双层：Cockpit（项目级）+ per-change（工位级）（V8）
- 新会话必须自检状态卡真实性（V8）
- 需求重叠 > 30% 必须合并（V8）
- 量化汇报 + 量化验收（不打分不交付）
```

### 3.2 标准引用（按阶段分工）

```markdown
## AI 行为规则

### Cockpit 阶段（V8）
- Agent: 主 Agent
- 产出: Cockpit 快照（全局状态 + 自检结果）
- 约束: 新会话必须自检文件系统 vs 状态卡；假性完成标记 🛑

### Intake 阶段
- Agent: fullstack-intake
- 产出: 流程定位卡 + 去重报告 + 影响面清单 + 两层状态卡
- 约束: 30% 原子化去重必须执行；Cockpit 必须先读；状态卡含最后产出时间

### 提案阶段
- Agent: fullstack-proposal-writer
- 产出: proposal.md
- 约束: Capabilities + Non-Goals 必填；影响面基于 intake 深化

### 规格阶段
- Agent: fullstack-spec-writer
- 产出: specs/{capability}/spec.md + prototypes/{module}.md（涉及 UI 时）
- 约束: BDD 场景 + E2E 场景 + 测试骨架 + 不变量；涉及 UI 必须画原型

### 圆桌会议（V8，可选）
- Agent: 主 Agent 主持 6 子代理
- 产出: meeting-notes/round-{N}.md
- 约束: config 控制开关；干净上下文子代理；用户裁决分歧

### 协议阶段
- Agent: fullstack-contract-writer
- 产出: contracts/ 四件套 + contract test 骨架
- 约束: 契约 approved 才能进 design；契约不可单方面修改

### 规划阶段
- Agent: fullstack-planner
- 产出: design.md（D1..Dn + 契约一致性）+ tasks.md
- 约束: 引用 contracts/ 不重写

### DOC SYNC 阶段（V8）
- Agent: fullstack-doc-updater
- 产出: 知识回流持久化文档（🟡→🟢 标记切换）
- 约束: 单写+标记机制；diff 为空不可进 Closure

### Closure-Define 阶段（V8）
- Agent: fullstack-planner
- 产出: closure-checklist.md P0 闭环步骤
- 约束: P0 闭环步骤非空才可进实现

### 实现阶段
- Agent: fullstack-implementer
- 产出: 代码 + 测试 + tasks 全部 [x] + 量化汇报
- 约束: CONTRACT GATE 必须过；TDD 五段式

### 审查阶段
- Agent: fullstack-reviewer
- 产出: 7 维度打分卡 + 契约漂移报告 + 目标对齐报告
- 约束: 不信自评，独立验证；总分 < 4.0 不交付

### 验收阶段
- Agent: acceptance-discipline
- 产出: 验收报告 + 门禁结果
- 约束: 接收 reviewer 打分卡 + 漂移报告

### 归档阶段（V8）
- Agent: fullstack-doc-updater
- 产出: archive/out/ 或 archive/done/ + prototypes/ 回流 + Cockpit 更新
```

### 3.3 严格引用（含门禁清单）

```markdown
## AI 行为规则 — 严格模式

### 阶段门禁（V8）

| 阶段 | 门禁 | 不通过时行为 |
|------|------|------------|
| Cockpit → Intake | Cockpit 已读取 + 新会话自检完成 | 回到 Cockpit |
| Intake → Proposal | 流程定位卡 + 去重报告 + 两层状态卡 | 回到 Intake |
| Proposal → Spec | proposal approved + Capabilities 已声明 | 回到 Proposal |
| Spec → Roundtable | specs approved + roundtable.enabled 检查 | 回到 Spec / 跳过 |
| Specs/Roundtable → Contract | specs approved + 圆桌收敛 | 回到 Specs/Roundtable |
| Contract → Design | contracts/ approved + contract test 骨架就绪 | 回到 Contract |
| Design → DOC SYNC | 用户确认方案 | 回到 Design |
| DOC SYNC → Closure | 🟡→🟢 标记切换 + diff 非空 | 回到 DOC SYNC |
| Closure → Code | closure-checklist.md P0 非空 + CONTRACT GATE 通过 | 回到 Closure |
| Code → Review | tasks 全部 [x] + TDD 五段标记 + 量化汇报 | 回到 Code |
| Review → Accept | 7 维度总分 ≥ 4.0 + 无严重漂移 + 目标对齐 ≥ 90% | 回到 Code |
| Accept → Archive | 验收通过 | 回到 Code |
| 任意阶段漂移 | feedback-loop 触发 → 回流对应 Agent | 强制停下 |
| 交付 | report 汇总 + 用户处理状态检查 | 提醒用户 |

### 严禁行为
- ❌ 不读 Cockpit 直接干活（V8）
- ❌ 跳过 Intake 直接 Proposal
- ❌ 不做 30% 去重检查（V8）
- ❌ 跳过 Spec 直接写代码
- ❌ 跳过 contracts/ 直接进 design
- ❌ 没有 CONTRACT TEST 骨架就写业务测试
- ❌ 没有 RED 标记就写实现
- ❌ 没有 DRIFT CHECK 就标记 [x]
- ❌ 不量化汇报就移交审查
- ❌ 发现漂移不报告，静默迁就
- ❌ 不打分就批准
- ❌ 涉及 UI 的能力不画原型
- ❌ 原型用占位符，不标实际文字
- ❌ 只画默认状态，漏掉加载/空/错误状态
- ❌ per-change 原型完成后不回流到项目级 prototypes/（V8）
- ❌ 归档不分类（out/done）（V8）
- ❌ 状态卡不更新最后产出时间（V8）
- ❌ 磕绊不写 report（V8）
```

---

## 4. 场景化规则配置

### 4.1 新项目启动

```markdown
## AI 行为规则 —— 新项目模式

- 先创建 docs/specs/config.yaml 声明技术栈 + 圆桌开关
- 初始化 docs/specs/.state-card.md（空 Cockpit）
- 所有需求经 Cockpit → intake → proposal → spec → [圆桌] → contract → design → tasks 完整链路
- 涉及 UI 时必须画原型
- 配置 TRAE Hook: contract-gate + drift-detect + doc-sync-gate
```

### 4.2 日常迭代

```markdown
## AI 行为规则 —— 日常迭代模式

- 小变更使用轻量 Spec（2-3 个 Requirement + 1-2 个 E2E 场景）
- 中大型走完整链路（含 contract + 圆桌）
- DOC SYNC GATE + CONTRACT GATE 必须通过
- 状态卡双层实时更新（V8）
- Intake 30% 去重必须执行
```

### 4.3 紧急修复

```markdown
## AI 行为规则 —— 紧急修复模式

- 可跳过 proposal/specs/contract，必须走 debugger 流程
- 检查根因是否涉及契约：涉及则走契约变更流程
- 修复后必须补文档（24h 内）
- 仍需 DRIFT CHECK
```

---

## 5. V7 → V8 升级要点

1. **DOC SYNC #1+#2 合并**：两次写入合并为单次 DOC SYNC，🟡→🟢 标记机制替代分阶段校验
2. **Agent 文件全量瘦身**：所有 Agent 定义文件精简至 ≤150 行，核心铁律 + 骨架引用
3. **References 合并**：43 个引用文件精简至 36 个，消除冗余
4. **基石模块 🔷 接入手册**：新增基石模块接入手册，规范跨模块依赖
5. **Buglist-Cockpit 联动**：Bug-Batch 链与 Cockpit 驾驶舱状态联动
6. **Closure 审 维度**：新增 Closure-Define 阶段，P0 闭环步骤非空门禁

---

## 6. 参考

| 资源 | 路径 |
|------|------|
| 技能包入口 | [SKILL.md](SKILL.md) |
| 操作指南 | [GUIDE.md](GUIDE.md) |
| Agent 定义 | [agents/](agents/) |
| 方法论详解 | [references/](references/) |
| 工作流全景 | [workflows/](workflows/) |
| 配置模板 | [templates/config.yaml](templates/config.yaml) |
| Cockpit 模板 | [templates/cockpit-state-card.md](templates/cockpit-state-card.md) |
| 状态卡模板 | [templates/state-card.md](templates/state-card.md) |
| 契约模板 | [templates/contracts/](templates/contracts/) |
| 圆桌模板 | [templates/meeting-notes.md](templates/meeting-notes.md) |
| Report 模板 | [templates/report.md](templates/report.md) |
| 漂移报告模板 | [templates/drift-report.md](templates/drift-report.md) |
| 验收打分卡模板 | [templates/acceptance-scorecard.md](templates/acceptance-scorecard.md) |
| Hook 配置 | [templates/hooks/README.md](templates/hooks/README.md) |
| 质量验证 | [evals/evals.json](evals/evals.json) / [evals/grader.md](evals/grader.md) |
| 脚本工具 | [scripts/README.md](scripts/README.md) |
