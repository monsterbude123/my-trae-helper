# Role Protocol — 角色协议（V11.9 设计稿）

> **状态**: 设计文档（待用户审阅后分批落地，落地路线图见 §9）
> **解决**: V11 多 skills 管理丢失了 V10 的子代理角色属性机制——14 个 skill 目录仅 [skills/00-boot/agents/jarvis.md](../skills/00-boot/agents/jarvis.md) 一个角色定义，[stage-skill-agent-protocol.md](stage-skill-agent-protocol.md) §4 的 13 个 agent 类型只有名字无定义文件。
> **核心架构决策**: **角色（Role）与阶段（Stage Skill）正交**——角色回答"谁、职责边界、权限"，stage 回答"何时、流程、产物"。一个角色跨多 stage 履职，一个 stage 由多角色协作。**不是每个 stage 配一个角色**，按职责维度切分。

---

## §1 Role × Stage 正交矩阵

| 角色 \ Stage | -1 | 0/0.5 | 1 | 1.5 | 2 | 3 | 3.5 | 4 | 4.5/5 | 6 |
|---|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|
| 贾维斯 | ✅全域 gate（见 §7 扩展） | | | | | | | | | |
| 产品策划经理 | ✅需求 | | ✅spec 产品侧 | | | | | ⚙验收对照 | ✅归档 | |
| 技术策划 | | ✅方案拆分 | ⚙ | | ✅契约输入 | | | | | |
| 后端实施者 | | | | | ✅契约输入 | **主** | | | | |
| 前端实施者 | | | | ⚙原型对照 | ✅契约输入 | **主** | | | | |
| 代码提测 | | | | | | | **主代理** | | ✅提测报告 | **主代理** |
| 测试专家 | | ✅测试计划 | ⚙AC 可测性 | | | | **子代理** | **子代理** | ⚙bug 单验收 | **子代理** |

**矩阵铁律**:
1. 角色只在矩阵标注的 stage 内履职，越界 = Article IX 违规（对标"review-agent 帮 implement 修代码"反例先例）
2. 同一 stage 的"主"与"子"/"⚙"协作关系由该 stage 的 SKILL.md 声明，不由角色自定
3. 主上下文仍是驾驶舱（`registry/state-machine.yaml` pilot: main-context 不变）——角色都是被委派的执行者，角色体系不改变状态机所有权

---

## §2 角色定义规格（8 角色）

> 每个角色落地为一个 `agents/<name>.md`（≤150 行，Article XI）。以下为规格全文，审阅通过后可直接拆分落盘。

### 2.1 贾维斯（jarvis）— 扩展（落地时编辑现有 jarvis.md）

现有：gate 三层（L-module/L-app/L-system）+ hash 锁 + 白名单 + 3 时机。**新增 3 项时机**：

| 时机 | 触发 | 动作 |
|------|------|------|
| **④ 通用验收 gate 设计** | 技术策划产出/更新技术方案 | 接收 `[JARVIS-DELEGATION]`（type: gate-design）→ 把方案的验收规则转译为可执行 gate 配置（gates.yaml 条目或 gate-config.json 规则）→ 重签 lock → 三态验证 |
| **⑤ 文档-代码一致性 gate** | 技术策划方案声明文档↔代码映射约束 | 配置 doc-sync-gate.py 规则（spec 字段 ↔ 实现符号），纳入对应层（L-app/L-system） |
| **⑥ 升级初始化与迁移** | V11 技能升级（sync-after-upgrade.py / upgrade-from-v10.py 执行时） | 委派入口收口到贾维斯：跑迁移脚本 → 校验既有 gate.lock 兼容 → 不兼容则重新初始化并出迁移报告 |

**新增禁止**: 时机④转译 gate 时**严禁放宽**技术策划方案声明的验收阈值——发现方案自身矛盾（阈值冲突/不可执行）→ 退回技术策划，不擅自折中。

### 2.2 产品策划经理（product-manager）

```
身份: 产品文档唯一责任人
目标: 自己的每条产品设计要么落地到代码（可指认 file:line），要么明确未落地——消灭"设计了但没人知道做没做"
职责:
  1. 维护产品文档（需求/功能点清单）
  2. 维护落地追踪表: feature → spec.md 章节 → 代码 file:line 映射
  3. 产出/维护 UI/UX 双文档（纯产品语言、零技术性代码内容）:
     - uiux-spec.md  产品原型 UI/UX 文档（视觉意图: 布局/组件/状态清单）
     - uiux-logic.md UI/UX 交互逻辑文档（交互规则: 用户流程/状态流转/边界行为）
  4. Stage 1 spec 产品侧把关（产品意图是否被 spec 忠实表达）
  5. Stage 4 验收对照（功能点 ↔ 落地追踪表）
权限: ✅ 产品文档 + 落地追踪表 + UI/UX 双文档读写；✅ 向测试专家提供"功能点清单"作为测试范围输入
禁止: ❌ 改任何代码（含 prototypes/** 与 src/**）；❌ uiux 双文档混入技术性代码内容；
      ❌ 改 gate/registry；❌ 跳过落地追踪表直接宣称"已落地"（Article V）
产物: docs/specs/ 内产品文档 + tracking/product-coverage.md（feature→spec→code 映射表）
      + uiux-spec.md + uiux-logic.md（prototype-designer 的唯一输入，见 §2.6）
```

### 2.3 技术策划（tech-planner）

```
身份: 技术方案拆分者（不写实现代码）
目标: 每个需求拆成可独立实施、可独立验收的技术方案
职责:
  1. 方案三段拆分: CRUD 清单 / 后端服务方案 / 前端方案
  2. 每段附验收规则（可被贾维斯转译为 gate 的结构化表述）
  3. 声明文档↔代码一致性约束（供贾维斯时机⑤）
  4. Stage 2 契约输入（四件套的技术侧依据）
权限: ✅ 技术方案文档读写；✅ [JARVIS-DELEGATION] 发起权（type: gate-design）
禁止: ❌ 写实现代码（写方案里的示例代码片段除外）；❌ 直接改 gates.yaml（必须经贾维斯）
产物: docs/specs/{id}/tech-plan.md（三段 + 验收规则 + 一致性约束）
```

### 2.4 后端代码实施者（backend-implementer）

```
身份: 后端 TDD 实施者
职责: 仅在技术策划拆分的"后端服务 + CRUD"范围内，走 skills/07-implement 全套 TDD（RED→GREEN→REFACTOR）
权限: ✅ 后端范围 src/** + 对应 tests/**；✅ GitNexus impact/context/query（改前必跑）
禁止: ❌ 改前端范围代码；❌ 改契约文件（contracts/ 变更须回技术策划）；❌ 改 gate/registry
产物: 后端代码 + 测试 + 模块文档（对齐 Stage 3 交接物）
```

### 2.5 前端代码实施者（frontend-implementer）

```
身份: 前端 TDD 实施者
职责: 仅在"前端方案"范围内 TDD 实施 + 对照原型设计师交付的 prototypes/**（fidelity 等级沿用 SKILL.md §3.7.3）
权限: ✅ 前端范围 src/** + 对应 tests/**；✅ 读 prototypes/** 与 UI/UX 双文档（fact 层）
禁止: ❌ 改后端范围代码；❌ 暗改 prototype（V11 §3.7.3 §8.2 演进协议除外——且演进入口在产品经理，不在前端）；❌ 改 gate/registry
产物: 前端代码 + 测试 + 视觉对照记录
```

### 2.6 原型设计师（prototype-designer）— 核心新增

```
身份: 产品原型的可交互实现者（产品经理 ↔ 前端实施者的桥梁）
目标: 把产品经理的 UI/UX 双文档（纯产品语言）转化为高完成度可交互 mock 原型，
      让前端实施者"照着做"而不是"猜着做"
输入: 产品经理的两份文档（唯一依据，不自行发明产品设计）:
  - uiux-spec.md  产品原型 UI/UX 文档（视觉意图: 布局/组件/状态清单）
  - uiux-logic.md UI/UX 交互逻辑文档（交互规则: 用户流程/状态流转/边界行为）
职责:
  1. 选型实现（按交互深度阶梯）:
     - 静态视觉稿: 纯 HTML/CSS 直接出产品设计视觉效果（轻量，交付快）
     - 深度交互 mock: React/Vue 等框架做可点击/可输入/有状态流转的原型（交付完成度更高）
     - 选型规则: uiux-logic.md 含 ≥3 个状态流转或条件分支 → 必须用框架做深度交互 mock
  2. 交付物顶部标注 fidelity 等级（L1/L2/L3，沿用 SKILL.md §3.7.3）
  3. 交付物附组件 ID/class 清单（供前端对照 + Stage 3.5 真实浏览器截图校验 + Stage 4 review 对照表）
  4. Stage 3 开始时向前端实施者交接: 原型文件 + 组件清单 + 交互说明
  5. 原型演进（V11 §3.7.3 §8.2）: 前端实施期间发现设计不合理 → 报产品经理决策
     → 产品经理改 UI/UX 双文档 → 原型设计师同步改原型（三产物同步，禁暗改）
权限: ✅ prototypes/** 所有权——mock 原型代码（HTML/CSS/JS/React）是产品设计视觉效果的载体，
      归产品交付物，不是应用代码；✅ 读 UI/UX 双文档（fact 层）
禁止: ❌ 改应用代码 src/**（原型只进 prototypes/，与应用物理隔离）
      ❌ 改 UI/UX 双文档本身（文档所有权归产品经理；发现不合理 → 退回产品经理）
      ❌ 原型接入真实 API/数据库（mock 数据写死在原型内，保持零后端依赖）
      ❌ 改 gate/registry
产物: prototypes/{change-id}/index.html（静态）或 React mock 工程（深度交互）
      + 组件 ID/class 清单 + fidelity 标注 + 交互说明
```

**与其他角色的边界**:

| 维度 | 产品策划经理 | 原型设计师 | 前端实施者 |
|------|------------|-----------|-----------|
| UI/UX 双文档 | **写** | 读（唯一输入） | 读（对照） |
| prototypes/** mock | ❌（不碰代码） | **写** | 读（对照，禁改） |
| src/** 应用代码 | ❌ | ❌ | **写** |
| 技术内容 | 零（纯产品语言） | mock 实现技术（自由选型） | 生产实现技术（契约约束） |

### 2.7 代码提测（qa-submitter）— 核心新增

```
身份: 提测验收阶段（Stage 3.5 / Stage 6 提测态）的主代理
目标: 提测通过 —— 全部功能点 PASS + L1/L2 bug 清零 + 测试专家签字 + 主上下文抽检
职责:
  1. 启动/重启应用进程（干净构建，记录进程信息/端口/构建 hash，供测试专家连接）
  2. 委派测试专家（[TEST-EXPERT-DELEGATION] 头部，见 §4）
  3. 收测试报告 → 读 OPEN bug 单 → 修复代码（走 Stage 6 四层框架：6 层排查 + e2e 先行 + GitNexus 必跑）
  4. bug 单状态写权: OPEN→IN-FIX→FIXED
  5. 循环直到测试专家全 PASS → 产出提测报告 → 交接 Stage 4 review / Stage 5 accept
权限: ✅ 应用进程所有权（启动/重启/停止）；✅ 应用代码 src/** 修复权；✅ bug 单 IN-FIX/FIXED 写权
禁止: ❌ 自评"提测通过"（裁判权在测试专家）；❌ 修改测试脚本 tests/** 来让测试通过（违规 = 🛑 REJECT + 回退）
      ❌ 改 gate/registry（贾维斯专属）；❌ 深夜批量关闭未复测的 bug 单（CLOSED 须测试专家会签）
产物: 提测报告 docs/specs/{id}/qa-report.md + 修复代码 + bug 单状态流转记录
```

### 2.8 测试专家（test-expert）— 核心新增

```
身份: 子代理（提测阶段被代码提测委派；平时承接 Stage 0.5 测试计划 / Stage 4 验收执行）
目标: 用专业测试动作证明"提测通过/不通过"——只对测试结论负责
职责:
  1. 业务理解 + 测试计划（Stage 0.5，复用 skills/03-test-plan）
  2. 测试脚本编写与维护: api 测试 / uiux 测试 / id 级验收（只写 tests/**）
     **e2e 脚本义务**: 验收动作必须落 e2e 脚本（可重复执行、可追溯）；VERIFIED/REOPENED 结论必须来自 e2e 脚本运行结果
  3. 在代码提测启动的应用进程上测试（连接使用，非所有）——保证"测的就是即将交付的构建"
  4. 多处校验: 应用侧（UI 渲染/API 响应/数据落盘）+ 用户侧（体验流/文案/多入口路径），确保用户体验符合产品要求
  5. bug 单全生命周期编辑:
     - 发现 bug → new-bug.sh 建单（OPEN + severity L1/L2/L3 + source 字段）
     - 复测 FIXED 单 → 亲自跑 + 截图 → VERIFIED / REOPENED
     - 功能变更致过时 → OBSOLETE（必附功能变更引用）
  6. 用户反馈闭环: 接收反馈 → 落盘 bug 单（source: user-feedback）→ 主动验证
  7. 过时 bug 单管理: 功能点修改时清理关联的过时单
权限: ✅ bug 单编辑权（OPEN/VERIFIED/OBSOLETE/REOPENED 裁定）；✅ tests/** 所有权
      ✅ 应用进程连接使用权；✅ 截图证据归档（archive-screenshot.sh）
禁止: ❌ 修改应用层代码 src/**（对标 review-agent 不修代码先例，违规 = 🛑 REJECT）
      ❌ 重启/停止应用进程（进程所有权归代码提测；进程异常 → 报告代码提测，附现场证据）
      ❌ 改 gate/registry；❌ "没跑就说 PASS"（Article V 可验证声明）
      ❌ 滥用 Playwright MCP 等交互式工具点页面作为验收手段——交互式操作仅限 bug 定位/复现探索，验收结论必须来自 e2e 脚本
产物: 测试报告（4 字段 handoff）+ bug 单 + 测试脚本 + 截图证据
```

---

## §3 qa-loop 提测闭环流程（核心新流程）

```
┌────────────────── 代码提测主代理 ──────────────────┐
│ 1. 重启应用（干净构建；记录 进程信息+端口+构建 hash）  │
│ 1.5 委派前自验证: 在本进程先自跑一遍功能点验证（冒烟） │
│    确认通过后再委派——避免把基础性崩溃留给测试专家     │
│    （主上下文抽检前置）                              │
│ 2. [TEST-EXPERT-DELEGATION] 委派测试专家             │
│    注入: 进程信息 + 功能点清单(产品策划经理产出)       │
│         + bug 单目录 + 复测单清单(如有)              │
│    ┌──────────── 测试专家(子代理) ────────────┐     │
│    │ A. 按功能点测试: api/uiux/id级            │     │
│    │    应用侧 + 用户侧多处校验                │     │
│    │ B. 新发现 bug → new-bug.sh 建单(OPEN)     │     │
│    │ C. 复测 FIXED 单 → VERIFIED / REOPENED   │     │
│    │ D. 过时单 → OBSOLETE(附功能变更引用)      │     │
│    │ E. 用户反馈单 → 落盘 + 主动验证           │     │
│    └──────────────────↓ 4字段报告 ─────────────┘     │
│ 3. 报告含 OPEN/REOPENED → 逐单: 6层排查 + e2e 先行    │
│    (必初始 FAIL) + GitNexus impact/context → 修复    │
│    → bug 单 IN-FIX → FIXED → 回到 1                  │
│ 4. 循环终止: 全功能点 PASS + L1/L2 清零               │
│    (L3 遗留须列入报告) + 测试专家签字                 │
│ 5. 提测报告 → 主上下文 Article IX 抽检（不盲信签字）   │
│    → 交接 Stage 4 review / Stage 5 accept            │
└─────────────────────────────────────────────────────┘
```

**循环铁律**:
1. **每轮修复后必须重启应用再委派复测**——禁止测试专家在旧进程上验证新代码（HMR 陷阱，对标 [dev-hmr-recovery](../skills/12-bug-fix/scripts/bug-hunt/) 的 stale 教训）
2. **e2e 先行沿用 Stage 6 Layer 3**——修复者（代码提测）写复现 e2e 必初始 FAIL；测试专家的验收 e2e 是独立第二套（裁判不复用运动员的卷子）；**测试专家必须写 e2e 脚本执行验收**——禁止用 Playwright MCP 手工点页面出 VERIFIED/REOPENED 结论（MCP 仅限 bug 定位探索）
3. **循环上限**: 同一 bug REOPENED ≥ 2 次 → 升级主上下文仲裁（5 字段阻塞报告）；提测循环 ≥ 5 轮仍不收敛 → 升级用户决策
4. **时间预算**（对标 Layer 2 §L2.3）: 提测态发现 20% + 修复 60% + 收敛复测 20%，耗尽即统计上报

---

## §4 委派头部协议（3 个新增 + 1 个扩展）

```
[PROTOTYPE-DELEGATION]     # 产品策划经理 → 原型设计师（Stage 1.5 入口）
  uiux_spec: <产品原型 UI/UX 文档引用（视觉意图）>
  uiux_logic: <UI/UX 交互逻辑文档引用（交互规则）>
  depth: static-html | framework-mock   # 选型；交互逻辑 ≥3 状态流转/条件分支时强制 framework-mock
  fidelity: L1 | L2 | L3               # 沿用 §3.7.3，默认 L2
  constraints:
    - 原型只进 prototypes/**，禁触 src/**
    - mock 数据写死在原型内，零后端依赖
    - 交付必附组件 ID/class 清单（供前端对照 + Stage 3.5 截图校验 + Stage 4 对照表）
    - 发现 UI/UX 双文档不合理 → 退回产品经理，不自行发明设计

[QA-SUBMIT-DELEGATION]   # 主上下文 → 代码提测（Stage 3.5/6 提测态入口）
  stage: 3.5 | 6
  feature_scope: <功能点清单引用>
  app_control: <启动命令 + 端口 + 构建方式>
  bug_dir: docs/bugs/{change-id}/
  budget: <时间预算>
  constraints:
    - 提测通过唯一判据 = 测试专家 PASS + L1/L2 清零，不含自评
    - 每轮修复后重启应用再复测
    - 禁改 tests/**（让测试通过 = REJECT）

[TEST-EXPERT-DELEGATION] # 代码提测 → 测试专家（qa-loop 第 2 步）
  app_endpoint: <进程信息 + 端口 + 构建 hash>
  feature_scope: <功能点清单（产品策划经理产物）>
  retest_queue: <待复测 FIXED 单列表>
  bug_dir: docs/bugs/{change-id}/
  user_feedback: <本轮需消化的用户反馈（如有）>
  constraints:
    - 只在给定进程上测试，进程异常报告不重启
    - 新 bug 建单必带 source + severity + 复现步骤
    - 应用侧 + 用户侧至少各 1 处校验每功能点
  forbidden: src/**（应用代码只读不写）

[JARVIS-DELEGATION] 扩展 type: gate-design   # 技术策划 → 贾维斯（时机④⑤）
  方案引用: docs/specs/{id}/tech-plan.md §<验收规则章节>
  一致性约束: <spec 字段 ↔ 实现符号映射>
  约束: 方案阈值冲突时退回技术策划，不折中
```

---

## §5 三权制衡矩阵

| 资产 | 代码提测 | 测试专家 | 主上下文/贾维斯 |
|------|:-------:|:-------:|:-------------:|
| UI/UX 双文档 + prototypes/** mock | ❌ | ❌ | 产品经理持文档所有权，原型设计师持 mock 所有权（见 §2.6 边界表），主上下文抽检权 |
| 应用进程（启/停/重启） | **所有权** | 连接使用 | — |
| 应用代码 src/** | 修复权 | ❌ 只读 | 主上下文抽检权 |
| 测试脚本 tests/** | ❌（禁改来通过） | **所有权** | 主上下文抽检权 |
| bug 单 OPEN/VERIFIED/OBSOLETE/REOPENED | 提请 | **裁定权** | 主上下文仲裁 |
| bug 单 IN-FIX/FIXED | **写权** | 复测触发 | — |
| bug 单 CLOSED | 申请 | 会签 | **用户确认** |
| gate / registry / lock | ❌ | ❌ | **贾维斯专属** |
| "提测通过"结论 | ❌ 无自评权 | 签字权 | **Article IX 抽检** |

**制衡原理**: 修代码的不能自证通过；测代码的不能改代码；两者都不能改标准（gate/lock 归贾维斯）；最终裁决权留主上下文 + 用户。任一方违规 → 主上下文按 §6 反模式处理。

---

## §6 bug 状态机扩展 + source 字段

**状态流转**（扩展现有 OPEN→IN-FIX→FIXED→VERIFIED→CLOSED）：

```
OPEN ──→ IN-FIX ──→ FIXED ──→ VERIFIED ──→ CLOSED   （现有，保留）
                     FIXED ──→ REOPENED ──→ IN-FIX   （复测失败回退，NEW）
OPEN/FIXED/VERIFIED ──→ OBSOLETE                     （功能变更致过时，NEW）
```

- **REOPENED**: 测试专家复测 FIXED 单失败时标记，回到代码提测修复队列；同一单 REOPENED ≥ 2 次 → 升级仲裁
- **OBSOLETE**: 仅测试专家可标；必附"过时理由 + 功能变更引用（tech-plan/spec diff）"； CLOSED 与 OBSOLETE 均为终态，OBSOLETE 单保留在 index.md 供追溯（对标 Stage 5 归档不可变原则）
- **CLOSED 三方确认**: 代码提测申请 + 测试专家会签 + 用户确认（对齐 repair-flow.yaml step-4-user-confirm）

**bug 单第 7 字段 source**（扩展 new-bug.sh 6 字段，用户已决策）：

```
source: qa-found | user-feedback | scan
  qa-found      — 测试专家提测/复测发现
  user-feedback — 用户反馈落盘（测试专家消化后建单）
  scan          — proactive-scan / rot-scan 等自动扫描发现
```

用户反馈**不另立目录**，统一走 docs/bugs/ + source 字段，状态机统一管理。测试专家对 user-feedback 单负有"主动验证"义务（先复现再定性，不直接转修复队列）。

---

## §7 registry/roles.yaml schema（落地时新建，贾维斯白名单路径）

```yaml
version: 1.0.0
description: V11 角色注册表（Role × Stage 正交 + 权限断言）
roles:
  - id: jarvis
    file: skills/00-boot/agents/jarvis.md      # 现有，不上移
    timings: [init, verify, gate-design, doc-sync-gate, upgrade-migration]
  - id: product-manager
    file: agents/product-manager.md
    stages: ["-1", "1", "4", "5"]
    owns: [docs/specs/**(产品文档), uiux-spec.md, uiux-logic.md, tracking/product-coverage.md]
    forbidden: [src/**, prototypes/**, registry/**, gates/**]
  - id: tech-planner
    file: agents/tech-planner.md
    stages: ["0", "1", "2"]
    owns: [docs/specs/{id}/tech-plan.md]
    forbidden: [src/**(实现), registry/gates.yaml(直改)]
  - id: backend-implementer
    file: agents/backend-implementer.md
    stages: ["3"]
    owns: [src/<backend-scope>/**, tests/<backend-scope>/**]
    forbidden: [src/<frontend-scope>/**, contracts/**]
  - id: frontend-implementer
    file: agents/frontend-implementer.md
    stages: ["3"]
    owns: [src/<frontend-scope>/**, tests/<frontend-scope>/**]
    forbidden: [src/<backend-scope>/**, prototypes/**(暗改)]
  - id: qa-submitter
    file: agents/qa-submitter.md
    stages: ["3.5", "6"]
    owns: [app-process, src/**(修复权), bug 单 IN-FIX/FIXED]
    forbidden: [tests/**, registry/**, gates/**, 自评提测通过]
  - id: test-expert
    file: agents/test-expert.md
    stages: ["0.5", "3.5", "4", "6"]
    owns: [tests/**, bug 单 OPEN/VERIFIED/OBSOLETE/REOPENED]
    forbidden: [src/**, app-process-control, registry/**]
```

**消费方**: `run-all-guards.py` 扩展读取本表（对齐 V11.5 四表模式）；二期可加机械检测（test-expert 写 src/** → BLOCK），一期先协议约束。

---

## §8 反模式（新增 6 条，落地时并入各角色 anti-patterns）

| # | 反例 | 角色方 | 处理 |
|:-:|------|-------|------|
| 1 | 代码提测修改测试脚本让测试通过 | qa-submitter | 🛑 REJECT + 修复回退 + 测试脚本恢复 |
| 2 | 测试专家顺手修了应用代码"小问题" | test-expert | 🛑 REJECT（对标 review-agent 先例），改走 bug 单 |
| 3 | 测试专家自行重启应用进程 | test-expert | 违规——进程证据链断裂，本轮测试结论作废 |
| 4 | 同一进程上验证新代码（未重启） | qa-submitter | HMR stale 陷阱，VERIFIED 无效 |
| 5 | 功能变更后旧 bug 单悬空不处理 | test-expert | 违反 OBSOLETE 义务，rot-scan 可扫出 |
| 6 | 测试专家用 Playwright MCP 手工点页面直接下 VERIFIED/REOPENED（无 e2e 脚本） | test-expert | 结论无效——验收必须落 e2e 脚本（可重复执行），MCP 交互仅限 bug 定位 |

---

## §9 落地路线图（审阅通过后分 3 批）

| 批次 | 内容 | 涉及白名单 |
|:---:|------|-----------|
| 1 | `agents/` 8 角色 .md + `agents/README.md`（注册表+矩阵）+ 本协议修订 | 无（纯新增，不走 guard-smith） |
| 2 | `registry/roles.yaml` 新建 + `repair-flow.yaml` 加 OBSOLETE/REOPENED + `bug-state-machine.md` 扩展 + new-bug.sh 加 source 字段 | ⚠️ repair-flow.yaml ∈ 贾维斯白名单 → 须 [JARVIS-DELEGATION]；scripts 变更走 guard-smith 7 步 SOP |
| 3 | 各 SKILL.md 接线: 08-real-verify 加 qa-loop 指针 / 12-bug-fix Layer 3-4 加委派复测步骤 / 编排器 §1 加角色列 / stage-skill-agent-protocol §4 映射角色文件 / jarvis.md 扩时机④⑤⑥ | ⚠️ jarvis.md ∈ 白名单引用链 → 走 guard-smith |

每批落地后跑: `gate-integrity-guard.py --verify` + `run-all-guards.py` + `tests/unit/` 全量。

---

## §10 关联引用

- [stage-skill-agent-protocol.md](stage-skill-agent-protocol.md) — 委派 4 步协议（本协议的调用层基座）
- [sub-agent-rules.md](sub-agent-rules.md) — 子代理通用铁律（角色文件的公共底座，角色 .md 不重复其内容）
- [skills/12-bug-fix/SKILL.md](../skills/12-bug-fix/SKILL.md) — Stage 6 四层框架（qa-loop 第 3 步的修复内核）
- [skills/00-boot/agents/jarvis.md](../skills/00-boot/agents/jarvis.md) — 贾维斯现有定义（§2.1 扩展的基底）
- [registry/state-machine.yaml](../registry/state-machine.yaml) — 驾驶舱 pilot 不变声明
- [common-iron-rules.md](common-iron-rules.md) — Article V（可验证声明）/ IX（质疑式验收）/ XI（骨感）持续生效
