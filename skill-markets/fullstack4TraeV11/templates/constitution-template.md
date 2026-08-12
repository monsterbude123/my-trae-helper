# Project Constitution Template — V11 不可协商原则

> 项目级宪法模板。V11 17 Articles（V10.12 蒸馏 + V11.1 新增 Article XVII Secret Redaction）。
> 修改本文件走 BREAKING 流程；任何 Article 不可静默删改。
> 详情见 [references/common-iron-rules.md](../references/common-iron-rules.md)

---

## Preamble（前言）

Constitution 是项目的**最高原则集合**，优先级高于：
- 单个 Spec 的需求
- 单个 Agent 的习惯
- 单次任务的"效率权衡"
- "特殊情况下"的灵活处理

任何冲突场景的判定顺序：**Constitution > Spec > Contract > Code > 个人判断**。

永不可降级 Articles：I、II、III、IV、V、VIII、IX、X、XIV、XV、XVI、XVII（V11.1 新增）。

---

## Article I — Quality First（V11.1 NEW）

**Rationale**: 代码质量优先于开发速度。

**Enforcement**:
- 不可为赶进度降低测试覆盖（≥90%）
- 不可为赶进度降低代码卫生（≤800行/文件 ≤50行/函数）
- 不可为赶进度跳过文档

---

## Article II — Spec First

**Rationale**: Spec 是真相源；Code 为 Spec 服务。

**Enforcement**:
- Spec 必先于 Implementation
- Spec 变更必先于 Code 变更
- 反向（先改代码后改 spec）= 🛑 REJECT

---

## Article III — Contract Immutable

**Rationale**: Contract 是团队间的承诺，不可静默修改。

**Enforcement**:
- Contract 变更必走 BREAKING 流程（用户确认）
- 不可"小改"已批准 Contract

---

## Article IV — TDD Driven

**Rationale**: 无失败测试的实现 = 不可验证的黑盒。

**Enforcement**:
- 改实现/删组件 → 立即同步改测试/删测试
- RED → GREEN → REFACTOR + DRIFT CHECK
- 不可修改测试让用例通过（虚假绿灯）
- 不可跳过 RED 阶段

---

## Article V — Verifiable Claims + GitNexus First（V11 强化）

**Rationale**: 每个主张必附事实证据 + 影响面评估用工具不用 grep。

**Enforcement**:
- 5.1 每个主张必附事实证据（command + output + file:line）
- 5.2 不可声称"已完成"而无证据
- 5.3 量化必汇报（test/contract_tests/coverage）
- 5.4 不量化不验收
- 5.5 GitNexus First：改 symbol 前必跑 impact()
- 5.6 探索代码用 query()/context()，不用 grep
- 5.7 实施/Bug/Health 4 stage 必走 GitNexus
- 5.8 GitNexus 不可用 → L4 异常 → 标注 + 汇报
- 失败时执行 3 次重试协议（修参数 → 换工具 → list_repos）

---

## Article VIII — Archive Immutable

**Rationale**: 归档是历史记录，修改归档破坏可追溯性。

**Enforcement**:
- 归档目录（docs/archive/done/）下文件禁止修改
- 归档只能新增，不可删除
- 修改归档 = 🛑 REJECT 流程违规

---

## Article IX — Cross-Session Verify

**Rationale**: 自评 = self_attested；主上下文必二次抽检。

**Enforcement**:
- 子代理"已通过"不等于主上下文已通过
- Reviewer 必亲自跑测试，不接受 implementer 自评
- E2E 必 INITIAL FAIL（证明 bug/功能真实存在）

---

## Article X — Evidence Mandatory

**Rationale**: 没有证据 = 没有声明。

**Enforcement**:
- 每个 PASS 必附 file:line 证据
- 视觉 PASS 必附截图 ≥5KB
- API PASS 必附 curl 输出

---

## Article XI — Self-Contained Constraints

**Rationale**: 规则必自身可约束。

**Enforcement**:
- 所有 skill 文件遵循 ≤10 铁律
- 所有 skill 文件遵循 ≤150 行（V10.12 减肥）
- 新增铁律必走 Article XVI §1.4 修复成本校验
- 引用 references/ 而非内联（不腐化自己）

---

## Article XII — Workflow Discipline

**Rationale**: 流程是质量底线。

**Enforcement**:
- 必走完整流程：Intake → Plan → Spec → Contract → Implement → Real Verify → Review → Rot Scan → Accept
- 不可跳过 stage（除非显式豁免）
- 不可反向（Stage 4 Review 不修代码，Stage 5 Accept 不重写代码）
- 状态卡必更新

---

## Article XIII — Visible Product

**Rationale**: 启动可见产物是唯一信任基础。

**Enforcement**:
- Web/Tauri/CLI/Library/Backend 5 类项目分别定义验证产物
- 必有可见产物（截图 ≥5KB / curl 200 / 输出 ≥10 行）
- 主上下文必亲自 Read（不委派子代理）

---

## Article XIV — No Rot No Accept

**Rationale**: 腐化堆积是不可接受的。

**Enforcement**:
- Phase 4.5 rot-detector 不可跳过
- 腐化扫描必跑（10 项）
- fix-list.json 必产出且不可空
- NO ROT NO ACCEPT — 任一 FAIL = 🛑 REJECT Accept

---

## Article XV — Obstacle Honesty

**Rationale**: 隐瞒障碍 = 阻塞产品交付。

**Enforcement**:
- 任何阻塞必 5 字段诚实汇报（type/description/attempted_solution/time_consumed/attempt_count）
- 禁止跳过/隐藏/抽象理由

---

## Article XVI — Skeptical Validation

**Rationale**: 质疑性校验 = 防止 Agent 自欺。

**Enforcement**:
- P0/P1 修复或升级方案必走质疑性校验 4 维度
- 根因验证 + 责任主体校验 + 重叠校验 + 修复成本 vs 价值

---

## Article XVII — Secret Redaction（V11.1 NEW — P0 安全）

**Rationale**: 用户提供的 secret（密码/token/API key）写到工具调用参数 → 工具调用日志 = 日志文件 = 明文泄露。

**Enforcement**:
- 17.1 用户提供的 secret → 必通过环境变量 / .env 注入，**绝不**写到工具调用参数里
- 17.2 工具调用参数中出现 secret → 🛑 REJECT + 立即通知用户改密码
- 17.3 .env / secrets/ / credentials/ → forbidden_paths 强制禁读
- 17.4 即使"测试用"的 secret 也不写到 commit / tool log / 截图
- 17.5 secret 误写 → 立即回滚 + 用户重置 + 写入 audit log
- 17.6 shell / script 中出现的 $PASSWORD / $TOKEN → 必用 ${VAR:-} 形式 + 在 audit log 中 redacted

---

## Governance

### 修改流程

```
1. 提出修改建议（spec-purposes/constitution-change-{date}.md）
2. 走 Stage 1 Spec 阶段（含 BREAKING 标记）
3. 用户确认（永不可降级 Article 必须显式接受风险）
4. 文档同步更新（references/common-iron-rules.md + 本文件 + SKILL.md §-1）
```

### 项目级覆盖规则

- 项目级 constitution.md 可**追加** Article（不可覆盖 V11 Articles）
- 项目级追加的 Article 必包含 Rationale + Enforcement

---

## 关联引用

- [references/common-iron-rules.md](../references/common-iron-rules.md) — V11 17 Articles 摘要
- [references/constitution.md](../references/constitution.md) — V11 16 Articles 全文
- V10 来源（开发期）: `../../fullstack4TraeV10/templates/constitution-template.md`