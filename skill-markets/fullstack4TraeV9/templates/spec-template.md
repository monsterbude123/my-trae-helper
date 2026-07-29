# {功能名称}
> 来源: {proposal/issue}
> 状态: draft
> 编号: L{层次}-{序号}

{1-2 句说明这个功能做什么}

---

## 需求清单

### Requirement: {需求摘要}

{需求详细描述}

#### Scenario: {Happy Path}
- **WHEN** {触发条件}
- **THEN** 系统 SHALL {预期行为}
- **AND** {额外预期}

#### Scenario: {Error Case}
- **WHEN** {异常条件}
- **THEN** 系统 SHALL {错误处理}
- **AND** errors[] SHALL 包含 {错误信息}

---

## Invariants
- INV-001: {不变量描述}
- INV-002: {不变量描述}

---

## E2E Scenarios

### E2E-001: {端到端场景}
- **用户故事**: {作为 X，我想 Y，以便 Z}
- **步骤**:
  1. {步骤 1}
  2. {步骤 2}
- **预期**: {结果}

---

## Acceptance
- [ ] {可验证条件 1}
- [ ] {可验证条件 2}

---

## Out of Scope
- {明确不做的内容}
