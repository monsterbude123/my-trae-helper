# Project Rules — Strict Mode V5.1

> **本项目启用 V5.1 严格模式。以下所有规则不可协商、不可跳过、不可"以后再说"。**
> **基于 fullstack v5.1（DOC FIRST + Contract-First + Spec-Driven + TDD + Prototype-First 五位一体）。**
> **V5.1 vs V5.0：spec-writer 在涉及 UI 时额外产出 `prototypes/`（模块化原型文档）。**

---

## 铁律（11 条）

```
1. NEVER edit code without gitnexus_impact() first
2. NEVER start without intake() — intake 是流水线第 0 步
3. NEVER implement without approved Spec
4. NEVER design without approved contracts/ — 协议先行
5. NEVER write production code without a failing test (TDD 🔴RED first)
6. NEVER skip CONTRACT TEST 骨架（对应契约的任务）
7. NEVER skip DRIFT CHECK（编码后强制契约 vs 代码自检）
8. NEVER approve without 7 维度量化打分卡（总分 < 4.0 不交付）
9. NEVER skip drift feedback — 发现漂移必须回流改 spec/契约
10. NEVER implement UI without approved prototypes/ — 涉及 UI 必先画原型（V5.1 NEW）
11. NEVER over-engineer — ponytail first, abstraction only when proven
```

违反任一条 → **立即停止，回退，重来。**

---

## 阶段门禁链（V5.1 六工件链）

| # | 阶段 | 前置门禁 | 不通过 |
|---|------|---------|--------|
| 0 | **Intake** | 流程定位卡已输出 + 状态卡已初始化 + 影响面清单已评估 | 🛑 不可进入 proposal |
| 1 | **Context** | `impact()` 完成 + 风险等级已汇报 | 🛑 不可进入编辑 |
| 2 | **Proposal** | proposal approved + Capabilities + Non-Goals 已声明 | 🛑 不可进入 spec |
| 3 | **Spec** | Spec approved + Out of Scope 已列出 + E2E 场景清单 + Test Skeleton Mapping + **涉及 UI 时 prototypes/ 已 approved**（V5.1 NEW） | 🛑 不可进入 contract |
| 4 | **Contract** | contracts/ approved（4 文件）+ contract test 骨架就绪 + **涉及 UI 时已参考 prototypes/ 推导字段**（V5.1 NEW） | 🛑 不可进入规划 |
| 5 | **Plan** | 文档影响清单 + 方案已确认 + P0 文档已同步 + 契约一致性检查 | 🛑 不可进入实现 |
| 6 | **Code** | DOC SYNC GATE + CONTRACT GATE + 🟡CONTRACT TEST + 🔴RED + 🟢GREEN + 🔍DRIFT CHECK + **涉及 UI 时已读取 prototypes/ 作为布局参考**（V5.1 NEW） | 🛑 不可进入审查 |
| 7 | **Review** | 7 维度打分卡 ≥ 4.0 + 契约漂移无严重 + 目标对齐 ≥ 90% + **涉及 UI 时原型 vs 实现一致性已验证**（V5.1 NEW） | 🛑 不可提交 |
| 8 | **Commit** | `detect_changes()` 后果符合预期 + ponytail 检查通过 | 🛑 不可 push |
| * | **Feedback Loop** | 任意阶段发现 spec/契约/目标漂移 → 强制回流 | 🛑 停下当前工作 |

---

## GitNexus 规则

> **详见 `.trae/rules/gitnexus-铁律.md` — 代码分析唯一入口。grep/glob 禁止用于理解代码。**

### MUST

- **intake 阶段影响面评估** → `gitnexus_impact({target: "symbolName", direction: "upstream"})` → 汇报调用者数量、受影响流程、风险等级
- **修改任何函数/类/方法前** → `gitnexus_impact()` → 汇报风险等级
- **提交前** → `gitnexus_detect_changes()` → 确认变更只影响预期符号
- **CRITICAL 风险** → 立即汇报用户，不继续编辑
- **重命名符号** → 使用 `gitnexus_rename`，禁止 find-replace
- **探索不熟悉代码** → `gitnexus_query()` 代替 grep
- **GitNexus 调用失败** → 执行重试协议（最多 3 次），禁止直接降级为 grep/glob

### NEVER

- ❌ 不跑 impact 就编辑
- ❌ intake 阶段跳过影响面评估
- ❌ 忽略 HIGH/CRITICAL 警告
- ❌ find-replace 重命名符号
- ❌ 提交前不跑 detect_changes
- ❌ GitNexus 失败 1 次就降级为 grep/glob
- ❌ 用 grep/glob 理解代码调用链/结构/影响面

---

## fullstack v5 规则

### Intake Gate（intake — V5 NEW）

```
MUST:   任何需求先经 intake 30 秒四步（意图识别→影响面评估→流程选择→状态卡初始化）
MUST:   输出流程定位卡 + 影响面清单 + .state-card.md
MUST:   影响面评估优先用 GitNexus，其次 Grep+Glob
CANNOT: 跳过 intake 直接写 proposal
CANNOT: intake 阶段做技术决策
```

### Proposal Gate（proposal-writer）

```
MUST:   需求 → proposal.md（Why + What + Capabilities + Non-Goals）
MUST:   影响面基于 intake 清单深化（技术影响面 + 业务影响面）
MUST:   更新 .state-card.md
CANNOT: approved 前进入 spec
CANNOT: "高可用""性能好""以后再说" 等模糊词
```

### Spec Gate（spec-writer）

```
MUST:   proposal → specs/{capability}/spec.md（approved）
MUST:   BDD 场景 (WHEN-THEN-AND + SHALL/SHALL NOT)
MUST:   Invariants 不变量声明
MUST:   E2E 场景清单 + E2E 覆盖矩阵（标出缺失项）
MUST:   Test Skeleton Mapping（每个 Scenario 映射 unit/contract/e2e 测试名）
MUST:   Out of Scope 显式列出
MUST:   涉及 UI 时产出 prototypes/（V5.1 NEW）
        ├── prototypes/README.md（索引）
        └── prototypes/{module}.md（每个页面/模块一个独立文件，含 4 状态 ASCII 线框图）
MUST:   原型文档 5 段完整：线框图 + 交互说明 + 样式说明 + 状态变化 + 移交 ui-ux-pro-max 清单
MUST:   ASCII 线框图标实际文字和按钮（禁止 [按钮] 占位符）
MUST:   4 状态齐全：默认 / 加载中 / 空数据 / 错误
CANNOT: approved 前进入 contract
CANNOT: 模糊词禁止
CANNOT: 涉及 UI 但跳过原型
CANNOT: 所有页面塞一个原型文件（必须模块化）
CANNOT: 只画默认状态（必须 4 状态齐全）
CANNOT: fullstack 阶段做详细视觉设计（配色/动效移交 ui-ux-pro-max）
```

### Contract Gate（contract-writer — V5 NEW）

```
MUST:   spec approved → 产出独立 contracts/ 目录
        ├── domain-models.md   (领域模型 + 公共变量/类型 + 不变量)
        ├── api-contracts.md   (接口契约 + 错误码 + 契约测试映射)
        ├── event-contracts.md (如适用)
        └── validation-rules.md(如适用)
MUST:   生成 contract test 骨架（tests/contracts/*.contract.test.ts）
MUST:   契约 approved 才能进 design
MUST:   契约不可变，变更走流程（ADDITIVE / BREAKING）
CANNOT: 跳过 contract 直接进 design
CANNOT: 把契约写在 design.md §4.3 子章节
CANNOT: 契约未 approved 就让 implementer 编码
```

### Plan Gate（planner）

```
MUST:   基于 contracts/ 做设计（引用不重写）
MUST:   文档影响清单 → 方案对比 ≥ 2（含契约一致维度）→ 实施计划
MUST:   编号决策 D1..Dn，每个决策附契约一致性检查
MUST:   §4.3 接口契约引用 contracts/api-contracts.md
MUST:   §4.4 领域模型引用 contracts/domain-models.md
MUST:   §4.5 不变量约束段
MUST:   tasks.md 每个任务标注对应契约（如有）
MUST:   新模块 = 模块文档草稿，新 UI = prototypes/ 已 approved（V5.1 NEW）
CANNOT: 用户确认前进入实现
CANNOT: "文档稍后补"
CANNOT: 在 design.md 重新定义接口契约
```

### Code Gate（implementer）

```
MUST:   DOC SYNC GATE 通过（P0 文档已同步）
MUST:   CONTRACT GATE 通过（契约 approved + contract test 骨架就绪）
MUST:   intake 影响面清单已读取
MUST:   涉及 UI 时已读取 prototypes/{module}.md 作为布局参考（V5.1 NEW）
MUST:   🟡CONTRACT TEST 确认（对应契约的任务）→ 才能写业务测试
MUST:   🔴RED 确认已输出 → 才能写实现
MUST:   🟢GREEN 确认已输出 → 才能声称完成
MUST:   🔍DRIFT CHECK 确认已输出 → 才能标记 tasks.md [x]
MUST:   类型检查 0 errors between RED and GREEN
MUST:   覆盖率 > 80%，关键路径 100%
MUST:   完成时输出量化汇报（4 维度自评 + 证据 + 影响面对照表 + 契约漂移自检）
CANNOT: "先写代码后补测试"
CANNOT: "契约先放一边，功能优先"
CANNOT: "DRIFT CHECK 跳过，编码完一起查"
CANNOT: 修改测试让测试通过
CANNOT: 发现漂移不报告，静默迁就
CANNOT: 不量化汇报就移交审查
```

### Review Gate（reviewer）

```
MUST:   不信 implementer 自评，独立验证证据
MUST:   7 维度量化打分卡（Spec对齐20% + 契约一致20% + 测试质量20% + 代码质量15% + 文档一致10% + 安全10% + 影响面5%）
MUST:   契约漂移检测（contracts/ vs 代码 6 项对比）
MUST:   目标对齐检查（vs proposal.md 原始目标，≥ 90%）
MUST:   构建通过 + 类型检查 0 + 测试 100% + Lint 0
MUST:   安全扫描无 HIGH（无密钥泄露、无 console.log）
MUST:   文档与代码一致（接口/模型/依赖三检）
MUST:   接手 debugger 产出 → 阶段 0 根因验证
MUST:   涉及 UI 时审查原型 vs 实现一致性（布局/交互/状态/字段 4 维度对照）（V5.1 NEW）
MUST:   打分卡归档 acceptance-scorecard-{YYYYMMDD}.md
CANNOT: 总分 < 4.0 批准
CANNOT: 单一维度 < 3.0 批准
CANNOT: 安全 < 4.0 批准（一票否决）
CANNOT: 严重契约漂移未修批准
CANNOT: 目标对齐 < 70% 不回流 proposal
CANNOT: 有关键问题时批准
```

### Debug Gate（debugger）

```
MUST:   问题已复现 → 才能分析
MUST:   根因证据清单 7 项完整 → 才能修复
MUST:   检查根因是否涉及契约（涉及则走契约变更流程）
MUST:   🔴RED 失败测试重现 Bug → 才能写修复代码
MUST:   回归测试全部通过 → 才能移交 reviewer
MUST:   🔍DRIFT CHECK：确认修复未引入新漂移
CANNOT: "我觉得根因是 X"（无代码证据）
CANNOT: 3 次修复失败仍继续 → 停止，质疑架构
```

### Feedback Loop Gate（V5 NEW）

```
MUST:   任意阶段发现 spec/契约/文档/目标漂移 → 立即停下
MUST:   输出 Spec Drift Report（即使无漂移也输出 🟢）
MUST:   严重漂移 → 回流对应 Agent（spec→spec-writer / 契约→contract-writer / 代码→implementer / 目标→proposal-writer）
MUST:   BREAKING 漂移修复需用户确认
MUST:   每个阶段切换跑目标对齐检查点（≥ 90% 继续 / 70-89% 用户确认 / < 70% 强制回流）
CANNOT: 发现漂移静默继续
CANNOT: 改代码迁就 spec（应改 spec）
CANNOT: 严重漂移继续往前冲
CANNOT: 阶段切换不检查目标对齐
CANNOT: 汇报"已完成"但漂移未修
```

---

## 状态卡规则（V5 NEW）

```
MUST:   每个变更目录维护 .state-card.md
MUST:   6 种触发时机更新：intake 初始化 / 阶段切换 / 工件完成 / 健康度变化 / 阻塞发生 / 用户询问
MUST:   5 段格式：基本信息 + 工件进度 + 健康度 + 下一步 + 阻塞
MUST:   状态符号统一：✅⏳❌—🚫🟢🟡🔴
CANNOT: 不更新状态卡就移交下游
CANNOT: 状态卡与实际阶段不一致
```

---

## ponytail 规则

### 决策阶梯（遇到任何实现选择时）

```
1. 能不写吗？ → 删掉
2. 标准库能做吗？ → 用标准库
3. 已有的能做吗？ → 复用
4. 简单实现能做吗？ → 写
5. 必须要引入新依赖/模式吗？ → 写注释论证
```

### 代码标记

```
// ponytail: {说明} | 触发条件: {什么情况要升级} | 添加日期: {date}
```

### 审查

- 每次 reviewer 阶段 → 叠加 ponytail-review 扫描过度工程
- 无可删除代码、无可替代依赖、无过度抽象 → 通过

---

## 禁止行为清单

以下行为在本项目中**绝对禁止**，发现即阻断：

| 禁止行为 | 后果 |
|---------|------|
| 跳过 intake 直接写 proposal | 🛑 停止，回退到 intake |
| 不跑 impact 就编辑代码 | 🛑 停止，回退 |
| 跳过 contracts/ 直接进 design | 🛑 停止，回退到 contract-writer |
| 没有 CONTRACT TEST 骨架就写业务测试 | 🛑 停止，先填契约测试骨架 |
| 不写测试直接写实现 | 🛑 停止，回退，先写测试 |
| Spec 未 approved 就实现 | 🛑 停止，退回 spec-writer |
| contracts/ 未 approved 就编码 | 🛑 停止，退回 contract-writer |
| 跳过 DRIFT CHECK 就标记 [x] | 🛑 停止，回退做 DRIFT CHECK |
| 发现漂移不报告 | 🛑 停止，输出漂移报告 |
| 不量化汇报就移交审查 | 🛑 停止，补量化汇报 |
| 不打分就批准 | 🛑 停止，跑 7 维度打分卡 |
| "先快修以后重构" | 🛑 停止，走正常流程 |
| 修改测试让用例通过 | 🛑 停止，重写测试 |
| 提交前不跑 detect_changes | 🛑 阻止提交 |
| 引入非必要依赖 | 🛑 停止，用 ponytail 替代方案 |
| 文档省略/延迟 | 🛑 停止，先同步文档 |
| 不更新状态卡就移交下游 | 🛑 停止，先更新状态卡 |
| **涉及 UI 但跳过原型直接写代码**（V5.1 NEW） | 🛑 停止，回退到 spec-writer 画原型 |
| **原型用 [按钮] 占位符而非实际文字**（V5.1 NEW） | 🛑 停止，重画线框图标真实文字 |
| **原型只画默认状态漏掉加载/空/错误状态**（V5.1 NEW） | 🛑 停止，补齐 4 状态 |
| **所有页面塞一个原型文件**（V5.1 NEW） | 🛑 停止，按模块拆分成 prototypes/{module}.md |
| 指令添加 `2>&1` | 🛑 停止，回退（会掩盖错误导致盲目尝试） |
| **GitNexus 可用却用 grep/glob 分析代码**（V5.2 NEW） | 🛑 停止，回退到 GitNexus。详见 `gitnexus-铁律.md` |
| **GitNexus 参数错 1 次就放弃降级**（V5.2 NEW） | 🛑 停止，强制执行重试协议（3 次）。详见 `gitnexus-铁律.md` |

---

## 不造轮子 — 决策树

```
标准库能覆盖？→ 用标准库 → 框架/运行时内置？→ 用内置 → 项目已有模块封装？→ 用封装
→ 知名社区库？→ 引入（先确认项目无同功能依赖）→ 以上都不满足 → 才自己写
```

纪律：写 `connect()` 前看项目有无统一 DB 入口；写 `fetch()` 前看有无 API client；写 `print()` 前看有无 logger；改 conftest 前看已有 fixture 范式；引入新依赖前看已有依赖能否覆盖。

---

## TRAE Hook 自动化门禁（V5 NEW）

本项目配置 8 种 Hook 自动化门禁：

| 事件 | Hook | 说明 |
|------|------|------|
| SessionStart | `session-start` | 注入项目上下文 + 注入状态卡 |
| PreToolUse | `doc-sync-gate` | 写代码前检查 DOC SYNC GATE |
| PreToolUse | `contract-gate`（V5 NEW） | 写代码前检查 CONTRACT GATE |
| PostToolUse | `spec-validate-hook` | 写 spec 后自动校验 BDD 格式 |
| PostToolUse | `drift-detect`（V5 NEW） | 编码后契约漂移检测 |
| PostToolUse | `auto-test` | 编码后自动跑测试（TDD RED/GREEN 自检提醒） |
| Stop | `tasks-integrity` | 任务结束检查 tasks.md 完整性（证据强制检查） |
| UserPromptSubmit | `complexity-guard`（可选） | 需求复杂度评估 |

---

## 项目初始化检查清单

新成员加入或新模块启动时，逐项确认：

```
[ ] GitNexus 索引已建立（npx gitnexus analyze 或等效命令）
[ ] .trae/rules/ 已配置（本文件 + 6 个子规则文件）
[ ] .trae/hooks.json 已配置（8 种 Hook）
[ ] docs/modules/ 目录已建立
[ ] docs/specs/changes/ 目录已建立
[ ] docs/specs/changes/{change}/prototypes/ 模板已就位（V5.1 NEW 原型目录）
[ ] 测试框架已配置（覆盖率 80%）
[ ] tests/contracts/ 目录已建立（V5 NEW 契约测试）
[ ] CI/CD 已集成 reviewer 门禁（含 7 维度打分卡 + 原型一致性检查 V5.1 NEW）
[ ] Pre-commit hook: detect_changes + lint + typecheck + drift-detect
```

---

## V5.1 原型设计速查（NEW）

### 三层次原型分工

```
层次 1: ASCII 线框图         fullstack 负责（用 ┌┐└┘├┤│┬┴┼─ 画页面布局）
层次 2: 交互说明 + 样式说明   fullstack 负责（每个可交互元素的行为 + 布局方式）
层次 3: 详细视觉设计          移交 ui-ux-pro-max（配色/组件库/间距/动效/响应式细节）
```

### 触发判断

```
spec 的 BDD 场景涉及用户可见的界面吗？
  ├── 是 → 产出 prototypes/{module}.md（每个页面/模块一个独立文件）
  │     ├── 有共享组件？→ 共享组件单独一个原型文件
  │     └── 产出 prototypes/README.md 索引
  └── 否（纯后端/纯 API）→ 跳过原型
```

### 4 条原型铁律

```
1. UI MUST HAVE PROTOTYPE       涉及 UI 必先画原型
2. REAL TEXT NOT PLACEHOLDER    线框图标实际文字，禁止 [按钮] 占位符
3. ALL STATES DRAWN             4 状态齐全（默认/加载中/空数据/错误）
4. MODULAR NOT MONOLITHIC       每个页面/模块一个独立文件，不塞单文件
```

### 原型文档目录结构

```
docs/specs/changes/{change}/
└── prototypes/                  # V5.1 NEW
    ├── README.md                # 原型索引（列出所有页面/模块）
    ├── {page-login}.md          # 登录页原型
    ├── {page-dashboard}.md      # 仪表盘原型
    └── {component-search-bar}.md # 共享组件原型
```

详见 `.trae/rules/原型设计.md` 完整规则 + 技能包 `references/prototype.md` + `templates/prototypes/page-module.md`。

---

## 开发运维规则

### 运维操作

0. 指令禁止：`2>&1`
1. 测试：用项目标准测试命令验证（参考项目 README 或 CI 配置）
2. 操作变更前：先停止可能锁定的进程
3. Docker：本地验证时确保 docker 已停止
4. 数据库：只用业务代码操作，不直接操作 DB；垃圾数据直接覆盖
5. 修复中遇到脏逻辑 → 记录提醒，方便后续代码治理
6. 优先使用业界已有轮子

### E2E 验收原则

1. e2e 过程中即时用 vision-audit 看界面，不要把问题堆积起来
2. 已知存在问题的情况下，跑全量 e2e 没意义，Workflow B 即时诊断优先
3. e2e 全量太重，只提醒用户主动触发，不要自己尝试

### 关键教训

1. SDD 驱动（Spec-Driven Development）
2. DOC SYNC：完成 TDD CODE 后，扫描代码变更涉及的模块文档并更新
3. VERIFY：完成后调用 code-review skill 或 reviewer agent 审查

### 网络环境

如遇包管理器/仓库超时 → 准备镜像源或故障转移配置。
