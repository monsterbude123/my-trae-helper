---
feature_name: {功能名称}
branch: {###-feature-name}
created: {YYYY-MM-DD}
status: draft | in-review | approved | implemented
spec_version: "10.1"
source: {proposal/issue 链接}
---

# {功能名称}

> 编号: L{层次}-{序号}
> 状态: draft
> 来源: {proposal/issue}

{1-2 句说明这个功能做什么 + 解决什么用户问题}

---

## Why *(mandatory)*

<!-- 用户意图层：解释"为什么"要做这个 change，spec-kit 没有这一段，V10 保留 -->

**问题陈述**: {用户当前遇到什么痛点 / 业务为什么需要这个能力}

**价值主张**: {做完后业务获得什么收益、用户获得什么改善}

**不做会怎样**: {不做这个 change 的代价 / 风险 / 机会成本}

---

## What Changes *(mandatory)*

<!-- 决策层：本 change 具体改什么 / 改不改什么，V10 保留 -->

### 必改项 (MUST)
- **WCH-001**: {具体的决策/契约改动，引用 contracts/ 路径}
- **WCH-002**: {模块/接口的增删改}

### 可选项 (MAY)
- **WCH-003**: {可选的增强项，明确触发条件}

### 明确不改 (WILL NOT)
- {明确排除的内容，避免范围蔓延}

### 影响面
- **模块**: {受影响的模块名}
- **契约**: {contracts/api-contracts.md / domain-models.md 路径}
- **文档**: {ARCHITECTURE.md / 模块文档}

---

## User Stories & Testing *(mandatory)*

<!--
  借鉴 spec-kit：User Story 必须 PRIORITIZED + INDEPENDENTLY TESTABLE。
  每个 user story 必须是可独立交付的 MVP 切片。
  Assign priorities (P1, P2, P3, etc.), P1 最关键。
  Think of each story as a standalone slice that can be:
  - Developed independently
  - Tested independently
  - Deployed independently
  - Demonstrated to users independently
-->

### User Story 1 - {简述} (Priority: P1) 🎯 MVP

{用自然语言描述这个用户旅程}

**Why this priority**: {解释价值和优先级理由}

**Independent Test**: {如何独立测试 — 例如"通过 X 操作可完整验证,交付 Y 价值"}

**Acceptance Scenarios**:

1. **Given** {初始状态}, **When** {动作}, **Then** {可观察结果}
2. **Given** {初始状态}, **When** {动作}, **Then** {可观察结果}

---

### User Story 2 - {简述} (Priority: P2)

{用自然语言描述这个用户旅程}

**Why this priority**: {解释价值和优先级理由}

**Independent Test**: {如何独立测试}

**Acceptance Scenarios**:

1. **Given** {初始状态}, **When** {动作}, **Then** {可观察结果}

---

### User Story 3 - {简述} (Priority: P3)

{用自然语言描述这个用户旅程}

**Why this priority**: {解释价值和优先级理由}

**Independent Test**: {如何独立测试}

**Acceptance Scenarios**:

1. **Given** {初始状态}, **When** {动作}, **Then** {可观察结果}

---

[按需添加更多 User Story，每个都有 P 编号]

---

## BDD Scenarios *(mandatory)*

<!--
  借鉴 spec-kit Given/When/Then 格式。
  每个 Scenario 必须是 BDD 三段式：Given（前置）+ When（动作）+ Then（可观察结果）。
  Then 必须是可观察的具体结果，不是"系统正常"这种抽象表述。
-->

### Scenario: {Happy Path 名称}
- **Given** {前置条件 — 明确可量化的状态}
- **When** {用户/系统执行的可执行动作}
- **Then** {可观察的具体结果 — 含数值/状态/响应}
- **And** {额外可观察结果}

### Scenario: {Error Case 名称}
- **Given** {异常前置条件}
- **When** {触发异常的动作}
- **Then** {系统 SHALL {具体错误处理行为}}
- **And** errors[] SHALL 包含 {错误信息}

### Scenario: {Boundary 名称}
- **Given** {边界前置条件 — 极值/空值/超限}
- **When** {触发边界的动作}
- **Then** {可观察的边界处理结果}

---

## Requirements *(mandatory)*

### Functional Requirements

<!-- 借鉴 spec-kit FR-NNN 编号体系 -->

- **FR-001**: System MUST {具体能力, e.g., "allow users to create accounts"}
- **FR-002**: System MUST {具体能力, e.g., "validate email addresses"}
- **FR-003**: Users MUST be able to {关键交互, e.g., "reset their password"}
- **FR-004**: System MUST {数据要求, e.g., "persist user preferences"}
- **FR-005**: System MUST {行为要求, e.g., "log all security events"}

*标注未澄清项:*
- **FR-006**: System MUST {行为} via [NEEDS CLARIFICATION: 待澄清项说明]

### Key Entities *(涉及数据时填写)*

- **{实体 1}**: {代表什么, 关键属性(无实现细节)}
- **{实体 2}**: {代表什么, 与其他实体的关系}

---

## Edge Cases *(mandatory)*

<!-- 至少 3 条边界/异常场景 -->

- {当 X 边界条件时,系统会如何？}
- {系统如何处理 X 错误场景？}
- {当并发/重试/超时发生时,行为是什么？}
- {当输入为空/极值/非法时,行为是什么？}

---

## Invariants *(mandatory)*

- INV-001: {不变量描述 — 系统任何状态下都成立的约束}
- INV-002: {不变量描述}

---

## Success Criteria *(mandatory)*

<!--
  借鉴 spec-kit：可量化、与技术无关、可度量。
  每个 SC 必须是数字/比例/时间等可观察指标。
-->

### Measurable Outcomes

- **SC-001**: {可量化指标, e.g., "用户可在 2 分钟内完成账户创建"}
- **SC-002**: {可量化指标, e.g., "系统可支撑 1000 并发用户无降级"}
- **SC-003**: {用户满意度, e.g., "90% 用户首次尝试即可完成主任务"}
- **SC-004**: {业务指标, e.g., "相关客服工单减少 50%"}

---

## Acceptance *(V10 满分硬门禁)*

<!-- V10 强制: 4 维全部 ✅ = PASS, 任一 ❌ = REJECT 整个 change -->

- [ ] 4 维评分全部满分(code 5.0 / api 5.0 / uiux 5.0 / boundary 5.0)
- [ ] 每个 User Story 有 Why this priority + Independent Test
- [ ] 所有 Acceptance Scenario 用 Given/When/Then BDD 格式
- [ ] Then 是可观察结果(不含"系统正常"等抽象表述)
- [ ] Edge Cases ≥ 3 条
- [ ] Success Criteria 可量化(含具体数字/比例/时间)
- [ ] 涉及 UI 时 prototypes/ 已存在并与本 spec 交互流程一致
- [ ] spec.md 与 contracts/api-contracts.md 接口签名一致
- [ ] spec.md 与 contracts/domain-models.md 实体一致

---

## E2E Scenarios

### E2E-001: {端到端场景}
- **用户故事**: 作为 {角色}，我想 {动作}，以便 {价值}
- **步骤**:
  1. {步骤 1}
  2. {步骤 2}
- **预期**: {结果}

---

## Out of Scope

<!-- 借鉴 spec-kit Assumptions: 明确边界,避免范围蔓延 -->

- {明确不做的内容}
- {依赖外部但本次不实现的}
- {未来版本考虑但本次排除的}
