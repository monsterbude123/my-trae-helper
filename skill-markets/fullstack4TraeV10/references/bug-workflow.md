# Bug 工作流

> Bug 录入与修复的完整路径。发现用户反馈问题时触发。
> V10.11：加 Phase B.0 录入（用户反馈 → bug 单）。

---

## Phase B.0 录入（V10.11 NEW — 用户反馈 → bug 单）

> 触发条件：用户反馈问题、报错、异常行为。
> 目的：将用户原始反馈结构化为可追踪的 bug 单。

### 录入流程

```
用户反馈问题
  ↓ 主上下文询问："是否作为 bug 单录入？"
  ├─ 用户拒绝 → 按"一般咨询"处理，不创建 bug 单
  └─ 用户同意 → 主上下文收集 6 字段信息
      ├─ 用户原话（必填）
      ├─ 用户操作（必填）
      ├─ 实际效果（必填）
      ├─ 关联项目文档的功能描述（可选）
      ├─ 期望（必填）
      └─ 状态（默认 OPEN）
  ↓ 生成 bug 单文档
  ↓ 输出："已录入 bug 单 {bug-id}"
```

### 6 字段定义

| 字段 | 必填 | 来源 | 说明 |
|------|:---:|------|------|
| **用户原话** | ✅ | 用户直接陈述 | 用户第一反应的原始描述（不加修饰） |
| **用户操作** | ✅ | 用户复述 | 用户如何触发问题的具体步骤 |
| **实际效果** | ✅ | 用户观察 | 问题发生的实际表现（截图/报错/异常行为） |
| **关联功能文档** | ⚪ | 主上下文搜索 | 项目文档中描述该功能的章节（帮助定位） |
| **期望** | ✅ | 用户期望 | 用户认为应该出现什么行为 |
| **状态** | ✅ | 主上下文判定 | OPEN（新录入）/ TRIAGE（待分诊）/ ASSIGNED（已分配） |

### Bug 单编号规则

```
格式: {模块}-{序号}-{简述}
示例: settings-009-config-key-case-mismatch

规则:
- 模块: 功能域（settings / assets / models / queue / diagnostic）
- 序号: 该模块下累计 bug 数（3 位，左补零）
- 简述: 问题简要描述（kebab-case，≤30 字符）
```

### Bug 单文档模板

```markdown
---
layer: fact
bug_id: {模块}-{序号}-{简述}
status: OPEN
severity: P1|P2|P3
created_at: {YYYY-MM-DD HH:mm}
---

# Bug: {简述}

## 用户原话

> {用户原始描述，不加修饰}

## 用户操作

1. {步骤1}
2. {步骤2}
3. ...

## 实际效果

- **现象**: {观察到的异常}
- **截图/报错**: {如有，附链接或引用}

## 关联功能文档

- {项目文档路径或章节名}

## 期望

{用户期望的行为}

## 状态流转

| 时间 | 状态 | 操作者 | 说明 |
|------|------|--------|------|
| {YYYY-MM-DD HH:mm} | OPEN | 主上下文 | 录入 |

## 根因诊断

> 待 debugger 填写

## 修复记录

> 待 implementer 填写
```

### MUST / NEVER

```
MUST: 用户原话字段不加修饰（保留原始表达）
MUST: 编号按规则生成（模块-序号-简述）
MUST: 状态默认 OPEN
MUST: bugs/{bug-id}.md 放 docs/bugs/ 目录下
MUST: 单文件结构，修复过程追加章节而非新建子目录
MUST: 严重度用 P0/P1/P2（与多 Bug 批量排序对齐）
NEVER: 代替用户填写期望（必须由用户确认）
NEVER: 在用户拒绝时强制创建 bug 单
```

### 状态机（V10.11 NEW）

```
OPEN → TRIAGE → ASSIGNED → IN_PROGRESS → FIXED → VERIFIED → CLOSED
  │       │         │            │          │        │         │
  │       │         │            │          │        │         └─ 用户确认关闭
  │       │         │            │          │        └─ Reviewer 验收通过
  │       │         │            │          └─ Implementer 修复完成
  │       │         │            └─ Debugger 定位根因，开始实施
  │       │         └─ 分配给具体 debugger/implementer
  │       └─ 主上下文评估优先级和影响面
  └─ 用户反馈录入
```

**状态字段位置**：bug 单 frontmatter `status` 字段（fact 层）。

**状态流转要求**：
- 每个状态变更必须在 bug 单"状态流转"表新增一行
- 必须含时间、状态、操作者、说明

### 修复完成回写协议（V10.11 NEW — B.3 Review 强制）

```
Phase B.3 Review 完成 → 必须回写 bug 单：

1. 更新 frontmatter:
   status: VERIFIED → CLOSED

2. 填写"修复记录"段:
   ## 修复记录
   - 根因: {实际根因}
   - 修复: {commit hash + 1 句描述}
   - 回归: {N} 通过 / {M} 总数
   - 验收: {reviewer id} {时间}

3. 状态流转表新增一行:
   | {时间} | VERIFIED | reviewer | 验收通过 |
   | {时间} | CLOSED | 主上下文 | 用户确认关闭 |

MUST: 修复完成未回写 bug 单 = 🛑 流程违规
```

### B.1 Intake 联动协议（V10.11 NEW — 复用录入信息）

```
Phase B.1 Intake 收到 bug 任务 → 必须按顺序：

Step 1: 读 bug 单（docs/bugs/{bug-id}.md）
  ├─ 期望字段（已录入）→ 不再询问用户
  ├─ 关联功能文档（已录入）→ 优先读这些文档
  └─ 用户操作（已录入）→ 直接作为复现步骤

Step 2: GitNexus context() 定位根因
  └─ 使用 bug 单的"关联功能文档"作为入口

Step 3: 评估影响面
  └─ 输出 LOW / MEDIUM / HIGH（与严重度 P0/P1/P2 对齐）

MUST: 重复询问用户"期望是什么" = 🛑 浪费时间
MUST: 忽略 bug 单的"关联功能文档"字段 = 🛑 探索冗余
```

---

## 任务类型路由（V10.6 新）

```
收到 Bug 相关任务 → 先判类型：

├─ 修 bug（代码有缺陷，需修复）
│  → 走 Phase B.1-B.3 全流程
│
├─ 补文档（commit 已存在，仅 docs/ 不同步）
│  → 跳过 B.1/B.2，仅同步 contracts/ + 模块文档
│  → 不重跑 e2e（除非契约改动）
│  → 不读历史 diagnose.md / fix_result.md
│
├─ 审查（验证已修复 bug 是否真修好）
│  → 反向走 B.3 → B.1（从回归测试反推根因）
│  → 独立审计，不信前次 agent 的 PASS
│
└─ 重构（代码结构变更，非 bug 修复）
   → 走 impact() + 全量回归
   → 不走 B.2 RED→GREEN（重构不改行为）
```

---

## 快速链（Bug 修复）

> 高层概览；详细执行见下方"5 步精简流程"。

```
Phase B.1 Intake(轻量): 确认可复现 + 主上下文读历史提取≤5 行事实 + 委派 debugger 注入根因摘要（不传历史文件路径）+ GitNexus context() 定位根因 + 评估影响面 LOW/MEDIUM/HIGH
  - debugger 不主动读 docs/bugs/{id}/ 下的过程文档（layer=log）
Phase B.2 Implement: 🔴 RED 写失败测试重现 → 🟢 GREEN 最简修复 → 全量回归无新破坏
Phase B.3 Review(轻量): 回归全绿 + 无新漂移 + 更新模块文档（涉及接口变更时）+ Bug 修复过程放 commit message（layer=log）
```

---

## 多 Bug 批量处理

```
1. 按严重度排序（P0 崩溃 > P1 功能异常 > P2 体验问题）
2. 逐 Bug 走快速链
3. 全量回归只跑一次（最后）
```

---

## 根因报告模板

```
Bug: {简要描述}
根因: {根本原因，非表象}
影响面: {直接 + 间接影响}
修复: {修复方式，1 句}
回归: {N} 通过 / {M} 总数
```

---

## 约束

- 根因不明不提交修复
- 涉及接口变更必须走 ADDITIVE/BREAKING 流程
- 修复后必须更新相关文档

---

## e2e 先行铁律（V10.8 NEW）

> 与 TDD RED 的关系: bug 修复用 e2e 先行（高维复现），功能开发用单测 TDD RED（细粒度验证）。

```
铁律: 修 bug 前必须写 e2e 验收脚本
  - e2e 初始必须 FAIL（证明 bug 真实存在）
  - e2e 一跑就 PASS = 没理解 bug 或 bug 已不存在 → 不可进修复阶段
  - e2e 必含期望断言（字段非空 / 值匹配 / 状态码）
  - 修复后 e2e 必须 PASS（证明 bug 真修复）
```

禁止:
- ❌ 不写 e2e 先改代码
- ❌ e2e 脚本无期望断言
- ❌ e2e 初始状态 PASS（说明没理解 bug）

---

## 类型系统陷阱（V10.8 NEW）

> 数据"看起来对"但验证失败时，检查实际存储格式 vs 预期格式，不要只看文本表示。
> **触发信号**: "mismatch" / "invalid format" / "type error" / 数据展示正确但程序逻辑失败。

**3 步诊断**:

```
Step 1 确认实际格式: SQLite SELECT typeof(c), HEX(c) / PostgreSQL SELECT pg_typeof(c), encode(c,'hex') / MySQL SELECT c, HEX(c)
Step 2 对比预期 vs 实际: 文本 hex vs 二进制 blob / JSON 字符串 vs 对象 / 带/不带编码标记
Step 3 用正确格式写入: SQLite X'hex' / PostgreSQL decode('hex','hex') / MySQL UNHEX('hex')
```

**大小写不敏感比较铁律**: 任何 hash / ID / token 字符串比较必须用大小写不敏感方法（如 Rust `eq_ignore_ascii_case`），禁止严格 `==`。

### 反例: blake3 hash 严格 == 失败

```
现象: 用户提交大写 BLAKE3，hasher 输出小写，严格 == 比较误判为不匹配
根因: 严格 == 比较对 hash/ID/token 字符串大小写敏感
教训: hash/ID/token 比较必须用 eq_ignore_ascii_case（或等价方法）
```

### 反例: SQLite BLOB 写入用文本字符串

```
现象: checksum 显示为 hex 字符串但下游解析失败
根因: UPDATE table SET col='7f5f...' 存为 UTF-8 文本，下游期望二进制 blob
教训: BLOB 列必须用 X'hex_value' 语法写入，写入后 SELECT HEX() 验证
```

---

## 5 步精简流程（V10.8 NEW）

> 整合 e2e 先行 + 采集 vs 解析二分 + TDD + 实际运行验收。替代 7 Phase 重流程。

```
Step 1 理解期望: 读需求+bug → 期望行为+判定标准 → 期望内容文档（不可留空）
Step 2 e2e 先行: 写 e2e 验收脚本 → 跑 → 必须 FAIL（证明 bug 真实存在）
  禁止: 不写 e2e 先改代码 / e2e 初始 PASS
Step 3 数据分析（采集 vs 解析二分）: 拿 raw_payload → 字段存在+非空=改 parser / 字段不存在=改 crawler
  禁止: 跨层修复 / 不看 raw_payload 直接判断
Step 4 实施修复（TDD 🔴→🟢）: RED 用真实样本 FAIL → GREEN 最简修复(diff ≤30 行) PASS → REFACTOR 全量回归 PASS
Step 5 验收（实际运行+退出码+输出）: 本地 e2e PASS + 测试环境 e2e PASS（如有）+ 退出码=0 + DRIFT CHECK ✅
```

任一步未通过 → 不可进入下一步。

---

## Intake 防御（V10.8 补丁 — 探索成本防御）

> 来源: 实战项目蒸馏（项目特定 ID 已脱敏）。Bug 修复时主上下文靠"记忆找模板"，探索性读取占总耗时 ~15%。
> 通用思想: 接到 bug 任务走固定入口，不靠记忆找模板。

### 接到 bug 任务的固定入口（通用 5 步）

```
[ ] 1. 确认 bug 目录结构: ls docs/bugs/{id}/ → 已存在则读 .state-card.md，不存在则创建
[ ] 2. 选模板: ls 同类 bug 目录 → 选最近 1 个作为模板参考（不复用判定结论，只参考结构）
[ ] 3. 提取关键信息: bug ID + 重现步骤 + 期望行为 + 涉及接口/模块
[ ] 4. GitNexus 索引检查: npx gitnexus status → 过期则先 analyze（避免子代理兜底浪费）
[ ] 5. 预建测试目录: mkdir -p tests/.../{bug-id}/ → 准备样本目录
```

### MUST / NEVER

```
MUST: 5 步全执行 → 缺一即返退
MUST: 每步 ≤ 30 秒 → 超时立即停下汇报用户
MUST: GitNexus 索引过期 → 必须先 analyze 再委派子代理
NEVER: 靠记忆/Glob 找模板（探索冗余）
NEVER: 复用其他 bug 的判定结论（每个 bug 独立验证）
```

---

## Phase 交接协议（V10.8 补丁 — 串行流程交接验证）

> 来源: 实战项目 4 Phase 流程蒸馏。每阶段交接需主上下文做交接验证，避免产物漂移。

| Phase | 交接产物 | 主上下文验证 |
|-------|---------|------------|
| Intake | bug 目录 + .state-card.md | 存在性 + 关键信息提取完整 |
| 期望+e2e | expected.md + e2e 脚本 | **e2e 初始必须 FAIL**（grep `passed` 不得出现） |
| 数据分析 | diagnose.md + 证据链 | 根因层判定明确（采集 vs 解析） + 证据链完整 |
| 修复+验收 | fix_result.md + e2e PASS | 本地 PASS + 测试环境 PASS（如有）+ DRIFT CHECK ✅ |

### Phase 切换汇报模板（≤300 字符）

```
{Phase N} → {Phase N+1} | 通过: {关键门禁} | 下一步: {委派谁做什么}
```

---

## 跨层修复最小化范式（V10.8 补丁 — 实战蒸馏）

> 来源: 实战项目（项目特定 ID 已脱敏）。字段缺失时 crawler+router+parser+schema 4 层全改 80+ 行，DRIFT FAIL。
> 通用思想: 跨层修复走"提升→兜底→零改→文档"4 层零侵入，禁止 4 层全改。

```
跨层字段缺失修复路径（优先级从高到低）:
  1. 上游提升: 能在上游采集层加字段吗? → 改 crawler（根因修复）
  2. 中游兜底: 能在路由/分发层补传吗? → 改 router（最小侵入）
  3. 下游零改: parser 层能不加防御吗? → 不改 parser（保持 ponytail 复用性）
  4. 文档同步: schema 文档补字段说明 → 改文档（事实同步）

禁止: 4 层全改（diff > 30 行 / DRIFT FAIL / 破坏复用性）
```

---

## Ponytail bug 修复决策阶梯（V10.8 补丁）

> 来源: 实战项目 bug-fix-workflow。修复前先考虑不修复/最小修复。

```
1. 能不改吗? → 确认是否真的需要修复（可能是上游业务数据，非 bug）
2. 能用已有字段吗? → 检查 raw_payload 是否已含期望字段
3. 能加防御吗? → 下游层加 null 处理优先于改上游
4. 必须改上游? → 写注释论证为什么下游层无法解决
```

---

## 反例库补充（V10.8 补丁 — 实战蒸馏）

### 反例 4: e2e 断言语义污染

```
现象: expected.md 用具体业务名称断言「应/不应出现」→ 把上游真实业务数据误判为 bug
根因: 未区分「上游业务数据」与「程序 bug」，按具体名称硬过滤而非按 schema 契约断言
教训: e2e 断言按 schema 契约（分类字段 + 数量 + 必要字段），不按具体业务名称。
      expected.md 必含「上游业务数据说明」段，区分上游数据 vs bug。
```

### 反例 5: 测试目标锁定缺失

```
现象: 子代理用非 bug 重现步骤的测试目标跑 e2e 出 PASS → 报告完成 → 切换到 bug 目标立即 FAIL
根因: 缺少「测试目标锁定」契约，子代理可自由切换测试目标
教训: live e2e 测试目标必须等于 bug 重现步骤的目标。子代理切换测试目标必须显式说明理由。
```

### 反例 6: 跨层字段缺失 4 层全改

```
现象: 字段缺失 → crawler+router+parser+schema 4 层全加防御 → 80+ 行 → DRIFT FAIL
根因: 缺少跨层修复最小化范式，不知道「提升→兜底→零改→文档」4 层零侵入路径
教训: 跨层字段缺失走「跨层修复最小化范式」，总改动 ≤30 行
```
