# Bug 工作流

> Bug 修复的轻量处理路径。发现 Bug 时触发。
> V10.6：加任务类型路由 + 主上下文过滤历史档案。

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
