# Acceptance Checklist — 需求的单元测试

<!--
  借鉴 spec-kit 理念：checklist 验证 spec 写得好不好，不是验证代码。
  用途：在 Spec 阶段产物完成后、Contract 阶段开始前，由 spec-writer 或 reviewer 逐项打勾。
  任何 ❌ 项 = 退回 spec-writer 修正。
-->

**功能**: {spec.md 链接 / 路径}
**审查人**: {reviewer/agent 名}
**审查时间**: {ISO_8601}
**V10 规则**: 4 维全部 ✅ = PASS；任一 ❌ = REJECT 整个 change

---

## 完整性 (Completeness) — 满分 5.0

<!-- 验证 spec 是否覆盖了必要结构 -->

- [ ] CHK-C01 每个 User Story 有 **Why this priority** 段
- [ ] CHK-C02 每个 User Story 有 **Independent Test** 段
- [ ] CHK-C03 每个 Acceptance Scenario 用 **Given/When/Then BDD 格式**
- [ ] CHK-C04 **Edge Cases ≥ 3 条**（边界/异常/并发/空值/超限）
- [ ] CHK-C05 **Success Criteria 可量化**（含具体数字/比例/时间）
- [ ] CHK-C06 Functional Requirements 全部用 FR-NNN 编号
- [ ] CHK-C07 涉及数据时填了 Key Entities 段
- [ ] CHK-C08 Why / What Changes 段都已填写（V10 核心）
- [ ] CHK-C09 涉及 UI 时 **prototypes/** 目录已存在并与本 spec 引用
- [ ] CHK-C10 至少包含一个 **Happy Path + Error Case + Boundary** Scenario

---

## 一致性 (Consistency) — 满分 5.0

<!-- 验证 spec 与契约/原型/术语的一致性 -->

- [ ] CHK-S01 **spec.md 与 contracts/api-contracts.md 接口签名一致**（路径/方法/参数/响应）
- [ ] CHK-S02 spec.md 与 contracts/domain-models.md 实体一致（字段名/类型/必填）
- [ ] CHK-S03 spec.md 与 contracts/events.md 事件名/载荷一致
- [ ] CHK-S04 prototype/ui-ux-logic.md 与 spec.md 交互流程一致
- [ ] CHK-S05 同一概念在全文用同一术语（无"用户/客户/account 混用"等）
- [ ] CHK-S06 What Changes 中的 WCH-NNN 编号与 contracts/ 引用一一对应
- [ ] CHK-S07 **不含模糊词**（"可能"、"大概"、"似乎"、"差不多"、"尽量"等）
- [ ] CHK-S08 编号 L{层次}-{序号} 唯一且未与历史冲突
- [ ] CHK-S09 Out of Scope 与 What Changes WILL NOT 段不矛盾
- [ ] CHK-S10 引用的外部模块/接口/服务都标注了完整路径

---

## 可测性 (Testability) — 满分 5.0

<!-- 验证 spec 写出来的内容是否真的能用于驱动测试 -->

- [ ] CHK-T01 每个 Acceptance Scenario 有 **明确的 Given**（前置条件可量化,不模糊）
- [ ] CHK-T02 每个 When 是 **可执行动作**（不是"用户操作"这种抽象）
- [ ] CHK-T03 每个 Then 有 **可观察结果**（不是"系统正常"这种抽象）
- [ ] CHK-T04 Success Criteria 含**客观测量方法**（不靠主观判断）
- [ ] CHK-T05 至少 1 个 E2E Scenario 包含**完整步骤列表**
- [ ] CHK-T06 BDD Scenario 可直接映射为 contract test / integration test 用例
- [ ] CHK-T07 Invariants 可被单元测试断言验证（不变量有明确数值边界）
- [ ] CHK-T08 Edge Cases 每条都有预期行为描述,不是只提问
- [ ] CHK-T09 [NEEDS CLARIFICATION] 标记项已列出,可在 contract 阶段追问用户
- [ ] CHK-T10 未澄清项 ≤ 2 条（过多 = spec 质量不达标,需回流 proposal）

---

## 边界性 (Boundary) — 满分 5.0

<!-- V10 第 4 维度：边界场景和约束完整性 -->

- [ ] CHK-B01 至少 1 个 Scenario 覆盖**空输入**行为
- [ ] CHK-B02 至少 1 个 Scenario 覆盖**超限/越界**输入行为
- [ ] CHK-B03 至少 1 个 Scenario 覆盖**并发/重试**行为
- [ ] CHK-B04 至少 1 个 Scenario 覆盖**权限不足/未认证**行为
- [ ] CHK-B05 至少 1 个 Scenario 覆盖**外部依赖失败**（API 不可用/超时）行为
- [ ] CHK-B06 不变量 (Invariants) 至少 3 条且都不可违反
- [ ] CHK-B07 错误响应 (errors[]) 含错误码、message、可选 details 字段
- [ ] CHK-B08 数据/接口契约标注了**最大并发/最大负载/最长响应时间**上限
- [ ] CHK-B09 Scope 边界清晰：Out of Scope 列举 ≥ 2 项
- [ ] CHK-B10 性能/资源约束写入了 Success Criteria 或 Invariants

---

## V10 评分与门禁

### 4 维评分

| 维度 | 总项 | 通过项 | 评分 (通过/总项 × 5.0) |
|------|------|--------|----------------------|
| 完整性 (Completeness) | 10 | __ | __ / 5.0 |
| 一致性 (Consistency) | 10 | __ | __ / 5.0 |
| 可测性 (Testability) | 10 | __ | __ / 5.0 |
| 边界性 (Boundary) | 10 | __ | __ / 5.0 |
| **总分** | **40** | **__** | **__ / 5.0** |

### 硬门禁判定

- [ ] **4 维全部满分 (5.0/5.0) = ✅ PASS** → 可进入 Contract 阶段
- [ ] **任一维度 < 5.0 = 🛑 REJECT 整个 change** → 退回 spec-writer 修正
- [ ] **禁止 N/A 计入分母**（不适用维度须在 Plan 阶段显式锁定,本模板默认全部适用）
- [ ] **禁止"非阻塞 P1"、"降级验收"、"部分扣分"灰色术语**

---

## 审查记录

| 时间 | 审查人 | 结果 | 备注 |
|------|--------|------|------|
| {ISO_8601} | {agent} | PASS / REJECT | {退回原因 / 备注} |
