# 委派注入模板（Delegation Injection Template）

> V9.2 NEW — 根因修复：fullstack skill 定义了阶段门禁和子代理类型，但没定义主上下文委派时必须在 prompt 中注入什么强制步骤。导致多次委派系统性遗漏关键项。
>
> **原则**：agent 自己的 SKILL.md 定义"agent 应该做什么"（自我约束）。本模板定义"主上下文必须在委派时告诉 agent 做什么"（注入约束）。两者互补，缺一不可。

---

## 使用方式

主上下文在委派子代理时，**必须**将对应 agent 的注入模板追加到委派 prompt 末尾：

```
委派 implementer:
  → 确定 subagent_type: general_purpose_task（🛑 硬约束，不协商）
  → 原始任务描述
  → [MUST] 编码前执行 GitNexus impact() 并汇报风险等级
  → [MUST] 编码后执行 detect_changes() 并确认变更范围
  → [MUST] 前端代码必须包含测试（jest/vitest，文件非空，覆盖率 > 0%）
  → [MUST] Rust 集成测试必须实现（contract test skeleton → tests/ 独立文件，非空）
  → [MUST] 端口/地址从环境变量读取，禁止硬编码
```

主上下文不注入 → 🛑 委派无效，禁止开始。

### 🛑 subagent_type 强制规则

```
所有 coding agent 必须使用 subagent_type=general_purpose_task:
  implementer, contract-writer, spec-writer, planner,
  doc-updater, proposal-writer, prototype-writer, reviewer

仅 intake 可以使用 subagent_type=search（纯信息搜索，无需写文件）

错误的 subagent_type → agent 工具集受限 → "结构性失败"
→ 视为主上下文路由错误，不扣 agent 失败计数，立即用正确 subagent_type 重新委派
```

---

## implementer 注入模板

```
[MUST] 编码前执行 GitNexus impact(target=..., direction="upstream") 并汇报风险等级
[MUST] 编码后执行 detect_changes() 并确认变更范围符合预期
[MUST] 前端代码（tsx/ts/jsx/js）每个组件/页面必须有对应 __tests__ 目录，文件非空
[MUST] Rust 集成测试：contract test skeleton 必须实现为 tests/ 独立文件，非空
[MUST] 端口/地址/密钥从环境变量读取，禁止硬编码。检查 grep localhost: 等模式
[MUST] Completion Report 必须包含「GitNexus 验证」段（impact + detect_changes）
[MUST] 编码前，加载 doc-map-manager 技能并查询:
  └── query-index.py --grab "测试陷阱" → 读取 test-plan/pitfalls.md 的已知问题
[MUST] 🚫 绝对禁止操作文档索引文件 — 通过 `doc-map-manager` 技能查询
```

**注入触发条件**：委派 implementer 进行任何编码任务时。

---

## reviewer 注入模板

```
[MUST] 合规性回溯验证（Compliance Back-Trace）:
  ├── 检查 __tests__/ 目录：每个前端源文件是否有对应测试文件（文件存在 + 非空）
  ├── 检查 tests/ 集成测试目录：是否存在 contract test 对应的独立测试文件（文件非空）
  ├── 检查硬编码端口：grep -rn "localhost:\d+" 前端 + grep -rn "127.0.0.1:\d+" 后端
  └── 以上任一为空/缺失 → FAIL（不存在 N/A 或"非阻塞"）
[MUST] 空目录 = FAIL。__tests__/ 存在但 0 个测试文件 → 🛑 REJECT
[MUST] Checklist "测试文件存在于对应 __tests__ 目录" 的质量阈值：文件数 > 0 且文件内容非空
[MUST] 审查时，加载 doc-map-manager 技能:
  ├── build-index.py --git-diff → 检测 DOC SYNC 缺口（替代裸命令）
  └── query-index.py --grab "{变更概念}" → 反向查交叉引用，验证 implementer 文档影响清单完整性
[MUST] 🚫 绝对禁止操作文档索引文件 — 通过 `doc-map-manager` 技能查询
```

**注入触发条件**：委派 reviewer 进行代码审查时。

---

## doc-updater 注入模板

```
[MUST] 文档索引必须通过 doc-map-manager 技能更新
[MUST] 禁止直接执行 python build-index.py 或手动编辑索引文件
[MUST] 索引更新后通过 doc-map-manager 技能验证
[MUST] 🚫 绝对禁止操作文档索引文件 — 通过 `doc-map-manager` 技能查询
[MUST] 文档同步前，加载 doc-map-manager 技能执行 DOC SYNC 缺口检测:
  └── build-index.py --git-diff → 自动发现新增/修改但未同步的文档
```

**注入触发条件**：委派 doc-updater 且任务涉及文档索引更新时。

---

## spec-writer 注入模板

```
[MUST] Spec 的 Out of Scope 段必须明确列出本阶段不适用的检查项（供后续阶段 N/A 预声明验证）
[MUST] 涉及 UI 时必须委派 fullstack-prototype-writer 子代理产出 prototypes/:
  ├── [MUST] 不自行画原型，委派 prototype-writer
  ├── [MUST] 传入 spec.md BDD 场景 + proposal.md
  └── [MUST] 接收 Completion Report 后验证 prototypes/ 非空
[MUST] 不涉及 UI 的纯后端/API 变更 → 在 Out of Scope 中声明 "无 UI，跳过原型"
[MUST] 编写 spec 前，加载 doc-map-manager 技能并查询已有文档:
  ├── query-index.py --grab "{能力名/概念}" → 确认已有文档中是否存在相关描述
  ├── query-index.py --lookup "{关键词1} {关键词2}" → 发现分散在多个文件中的相关内容
  └── query-index.py --file ARCHITECTURE.md → 定位与本次变更相关的架构章节
[MUST] 若 --grab 返回已有内容 → 判定增量/扩展关系，在 spec.md 中标注复用引用
[MUST] 若 --grab 无结果 + --lookup 无结果 → 标注为全新能力，在 spec.md Out of Scope 中记录
[MUST] 🚫 绝对禁止操作文档索引文件 — 通过 `doc-map-manager` 技能查询
[MUST] DELTA ONLY（V11 NEW）: spec.md 只写此变更的增量 BDD 场景。禁止将 ARCHITECTURE.md/模块文档/已有契约内容全文复制到 spec.md。引用路径格式: `参阅 [ARCHITECTURE.md](../../../ARCHITECTURE.md#section)`。
```

**注入触发条件**：委派 spec-writer 编写 spec 时。

---

## prototype-writer 注入模板

```
[MUST] 4 条铁律不可跳过（UI MUST HAVE PROTOTYPE / REAL TEXT NOT PLACEHOLDER / ALL STATES DRAWN / MODULAR NOT MONOLITHIC）
[MUST] 每个原型文件必须包含 5 段（线框图/交互说明/样式说明/状态变化/移交清单），缺一段 → 退回
[MUST] 线框图标实际文字和按钮（禁止 [按钮] [按钮] 等占位符）
[MUST] 每个页面/模块 4 状态各一张 ASCII 图（默认/加载中/空数据/错误）
[MUST] 每个页面/模块一个独立文件 + prototypes/README.md 索引
[MUST] 只做层次 1+2（线框图+交互+样式），不做配色/动效（层次 3 是 ui-ux-pro-max 的活）
[MUST] 产出 Completion Report（含 required_artifacts + artifacts_produced）
[MUST] 🚫 绝对禁止操作文档索引文件 — 通过 `doc-map-manager` 技能查询
```

**注入触发条件**：spec-writer 委派 prototype-writer 产出 prototypes/ 时。

---

## contract-writer 注入模板

```
[MUST] contracts/ 四件套（domain-models.md + api-contracts.md + events.md + validation.md）必须齐全
[MUST] api-contracts.md 必须包含 contract test 骨架（每个 endpoint 至少 1 个 happy path + 1 个 error case）
[MUST] 编写契约前，加载 doc-map-manager 技能并查询已有文档:
  ├── query-index.py --grab "{领域模型名}" → 确认无同名/冲突的 domain model
  ├── query-index.py --lookup "domain-models" → 发现所有已有的领域模型定义
  └── query-index.py --grab "{API 概念}" → 确认无冲突的 API endpoint 定义
[MUST] 发现已有同名 domain model → 引用复用，非重复定义
[MUST] 发现冲突 → 回流 spec-writer 而非自行裁决
[MUST] DELTA ONLY（V11 NEW）: contracts/ 只写此变更新增/修改的领域模型和接口。项目级通用类型（如 UserID、Timestamp）和已有领域模型引用 docs/ 路径，禁止全文复制到 contracts/ 下。引用格式: `> 基础类型定义见 [domain-models.md](../../../domain-models.md#common-types)`。
```

**注入触发条件**：委派 contract-writer 编写契约时。

---

## planner 注入模板

```
[MUST] 编写 design.md 前，加载 doc-map-manager 技能并查询已有文档:
  ├── query-index.py --grab "{架构模式}" → 引用已有设计模式作为方案对比论据
  ├── query-index.py --lookup "{技术选型关键词}" → 确认 ADR 决策不冲突
  └── query-index.py --file MODULES.md → 获取所有模块实施状态
[MUST] 文档影响清单中的模块列表必须通过 query-index.py --lookup 确认（非手动枚举）
[MUST] DELTA ONLY（V11 NEW）: design.md 只写此变更的技术决策增量（D1, D2...）。禁止将 ARCHITECTURE.md/模块文档/已有 ADR 全文复制到 design.md。架构背景引用 docs/ 路径，只写本次变更相关的决策。
```

**注入触发条件**：委派 planner 进行设计规划时。

---

## proposal-writer 注入模板（V11 NEW）

```
[MUST] 词数上限: 简单变更 ≤ 300 / 中等变更 ≤ 500 / 复杂变更 ≤ 800。超过上限 = FAIL
[MUST] Capabilities 表每个能力必须可验证（拒绝模糊的能力声明）
[MUST] Non-Goals 必须明确列出"不做什么"，拒绝空 Non-Goals
[MUST] 影响面必须区分技术影响（来自 intake）和业务影响（proposal-writer 深化）
[MUST] DELTA ONLY（V11 NEW）: proposal.md 只写 Why/What/Capabilities/Non-Goals 增量。禁止复制 ARCHITECTURE.md/模块文档/已有 Spec 全文到 proposal。背景引用 docs/ 路径即可。
```

**注入触发条件**：委派 proposal-writer 撰写提案时。

---

## 铁律

```
1. 主上下文委派时未注入对应模板 → 🛑 禁止委派（先注入再委派）
2. 注入模板中的 [MUST] 项不可被 agent 跳过或标记 N/A
3. 注入模板与 agent 自身 SKILL.md 冲突时 → 以注入模板为准（主上下文权威）
4. 新增 agent 类型 → 必须同步新增注入模板
5. 所有 agent 的注入模板必须包含 DOC-MAP-QUERY 项（V10 NEW）: 未包含 → 🛑 禁止委派该 agent
6. prototype-writer 委派前必须注入原型铁律（V10 NEW）: 未注入 → 🛑 禁止委派 prototype-writer
7. 所有 agent 的注入模板必须包含索引文件禁令（V10.1 NEW）: 未包含 → 🛑 禁止委派该 agent
```
