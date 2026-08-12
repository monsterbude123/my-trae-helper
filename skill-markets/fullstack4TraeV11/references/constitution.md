# Constitution — 17 Articles 宪法

> V11 总编排器与所有 stage skill 必读的宪法文件。V10.10 增 XV/XVI，V11 全数继承。

---

## 17 Articles 全文

### Article I — Quality First
代码质量优先于开发速度。不可为赶进度降低测试覆盖 / 代码卫生 / 文档质量。

### Article II — Spec First
无 approved spec 不写代码。spec 是契约的来源，契约是实现的真相。

### Article III — Contract Immutable
契约 approved 后不可单方面改。破坏性变更（BREAKING）必用户确认。

### Article IV — TDD Driven
TDD 三步循环（RED → GREEN → REFACTOR + DRIFT CHECK）是实施唯一路径。

### Article V — Verifiable Claims
每个主张必附事实证据（command + output + file:line）。不可声称"已完成"而无证据。

### Article VI — No Hidden Code
- 桩代码必返回明确错误：`raise NotImplementedError("STUB: ...")`
- 魔法数字必命名常量
- 重复代码 ≥3 处必提取公共函数

### Article VII — No Fixed Artifacts
- 日期必动态生成（`datetime.now()`），不可硬编码
- 不可写死端口 / 路径 / 凭证

### Article VIII — Archive Immutable
归档目录（`docs/archive/done/{change-id}/`）下文件禁止修改。归档只能新增，不可删除。

### Article IX — Cross-Session Verify
自评 = `self_attested`，主上下文必二次抽检。子代理"已通过"不等于主上下文已通过。

### Article X — Evidence Mandatory
每个验收结论必含 evidence：command / output / exit_code / file:line。

### Article XI — Self-Contained Constraints
所有 skill 文件遵循 ≤10 铁律 + ≤150 行（V10.12 减肥后恢复）。新增铁律必走 Article XVI 质疑性校验。

### Article XII — Workflow Discipline
必走完整流程：Intake → Plan → Spec → Contract → Implement → Real Verify → Review → Rot Scan → Accept。不可跳过。

### Article XIII — Visible Product
启动可见产物是唯一信任基础，不接受自评。5 类项目（Web / Tauri / CLI / Library / Backend）分别定义验证产物。

### Article XIV — No Rot No Accept
Phase 4.5 rot-detector 不可跳过。腐化扫描必跑，fix-list.json 必产出且不可空。

### Article XV — Obstacle Honesty（V10.10 NEW）
任何阻塞必 5 字段诚实汇报（type / description / attempted_solution / time_consumed / attempt_count）。禁止：
- ❌ 跳过（"先继续，回头再看"）
- ❌ 隐藏（"等下修，先标完成"）
- ❌ 抽象理由（"理解偏差"/"流程裁剪"/"心理障碍"）

### Article XVI — Skeptical Validation（V10.10 NEW）
任何 P0/P1 修复或升级方案必走质疑性校验 4 维度：
- [1] 根因验证（每个主张是否真实存在，附 file:line）
- [2] 责任主体校验（修复点是否在正确层）
- [3] 重叠校验（与已有规则是否重叠，差异化论证）
- [4] 修复成本 vs 价值校验

新增铁律/铁律新增条目必走 Article XVI §1.4 修复成本校验。

---

## 关联引用

- [SKILL.md §-1](../SKILL.md) — 编排器 17 Articles 引用
- [common-iron-rules.md](common-iron-rules.md) — 公共铁律 Article 摘要
- V10 来源（开发期，已蒸馏）：见 V11 references 与 anti-patterns