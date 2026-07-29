# Spec 格式规范（含 Delta Spec）

> 内化自 OpenSpec（Fission-AI）的 spec 格式与 Delta Spec 机制
> 哲学：fluid not rigid, iterative not waterfall, specs grow not stack

---

## 一、Spec 核心结构

```markdown
# {功能名称}
> 来源: {proposal/issue}
> 状态: draft | review | approved | implemented

## 一句话描述
{1-2 句说明这个功能做什么}

## Requirements

### Requirement: {需求摘要}
{需求详细描述，使用 SHALL/MUST 表达规范}

#### Scenario: {场景名}
- **WHEN** {触发条件}
- **THEN** 系统 SHALL {预期行为}
- **AND** {额外预期}

#### Scenario: {Error Case 名}
- **WHEN** {异常条件}
- **THEN** 系统 SHALL {错误处理}

## Invariants
- INV-001: {不变量描述}

## E2E Scenarios
### E2E-001: {端到端场景}
- **步骤**: 1. ... 2. ...
- **预期**: {结果}

## Acceptance
- [ ] {可验证条件}
```

---

## 二、Delta Spec 格式（Brownfield 必用）

> 修改已有 spec 时使用，描述**变更**而非全量重写。

### 2.1 四种 Delta 操作

| 操作 | 含义 | 归档时行为 |
|------|------|-----------|
| `## ADDED Requirements` | 新增行为 | 追加到主 spec |
| `## MODIFIED Requirements` | 修改已有行为 | 替换主 spec 中对应 Requirement |
| `## REMOVED Requirements` | 废弃行为 | 从主 spec 删除 |
| `## RENAMED Requirements` | 仅改名 | 主 spec 中更新名称 |

### 2.2 Delta Spec 模板

```markdown
# Delta for {capability-name}

## ADDED Requirements

### Requirement: {新增需求名}
{需求描述}

#### Scenario: {场景名}
- **WHEN** {条件}
- **THEN** 系统 SHALL {行为}

## MODIFIED Requirements

### Requirement: {已有需求名（标题必须精确匹配主 spec）}
{完整的新版需求描述 — 非 diff，是替换后的最终版本}

#### Scenario: {场景名}
- **WHEN** {条件}
- **THEN** 系统 SHALL {行为}

## REMOVED Requirements

### Requirement: {废弃需求名}
**Reason**: {废弃原因}
**Migration**: {迁移方案（如适用）}

## RENAMED Requirements
- FROM: `{旧名称}` → TO: `{新名称}`
```

### 2.3 MODIFIED 操作铁律

> **关键**：MODIFIED 必须是完整 Requirement block，不是 diff。因为归档时直接替换。

```
1. 从主 spec 定位已有 Requirement（openspec/specs/{capability}/spec.md）
2. 复制 ENTIRE Requirement block（从 `### Requirement:` 到最后一条 Scenario）
3. 粘贴到 `## MODIFIED Requirements` 下，编辑为新行为
4. 确保标题精确匹配（大小写敏感，空白不敏感）
5. 如果只添加新关注点而不改已有行为 → 使用 ADDED，不是 MODIFIED
```

### 2.4 场景格式铁律

```
✅ 正确: #### Scenario: 成功登录       （4 个 #）
❌ 错误: ### Scenario: 成功登录        （3 个 # — 静默失败）
❌ 错误: - Scenario: 成功登录           （破折号 — 不解析）
❌ 错误: **Scenario**: 成功登录         （加粗 — 不解析）
```

每个 Requirement 必须 ≥ 1 个 Scenario。

---

## 三、SHALL 语义

| 关键词 | 含义 |
|--------|------|
| **SHALL** / **MUST** | 强制要求，不可协商 |
| **SHALL NOT** / **MUST NOT** | 强制禁止 |
| **SHOULD** | 推荐但非强制 |
| **MAY** | 可选 |

---

## 四、Spec 质量标准

每个 Spec 必须：
- [ ] 每个 Requirement 有 ≥ 1 个 Scenario
- [ ] WHEN 条件精确、THEN 断言可验证
- [ ] 覆盖重要错误/边界场景，不只 happy path
- [ ] 描述行为（what），不描述实现（how）
- [ ] 实现细节放 design.md，不混入 spec

---

## 五、门禁底线（Spec 通过前强制验证）

```
[ ] Requirement ≥ 2（单需求功能至少 1）
[ ] 每个 Requirement ≥ 1 Scenario（#### 格式）
[ ] E2E Scenario ≥ 2
[ ] Invariants ≥ 1
[ ] Acceptance 可验证条件 ≥ 3
[ ] Brownfield: 修改已有 spec 时用了 Delta 格式（ADDED/MODIFIED/REMOVED）
```

不满足 → 🛑 退回 spec-writer 补充。

---

## 六、关联模板

### Proposal 模板（define.md 输入源）

```markdown
## Why
{1-2 句说明动机}

## What Changes
{具体变更描述}

## Capabilities

### New Capabilities
- `{kebab-case-name}`: {描述}

### Modified Capabilities
- `{existing-name}`: {哪些 Requirement 在变}

## Impact
{受影响代码/API/依赖}
```

### Design 模板

```markdown
## Context
{背景 + 当前状态}

## Goals / Non-Goals
**Goals:** {目标}
**Non-Goals:** {明确不做}

## Decisions
{关键决策 + 理由（含替代方案对比）}

## Risks / Trade-offs
{已知风险 + 缓解措施}
```

### Tasks 模板

```markdown
## 1. {任务组名}
- [ ] 1.1 {任务描述}
- [ ] 1.2 {任务描述}

## 2. {任务组名}
- [ ] 2.1 {任务描述}
```

> checkbox 格式 `- [ ]` 是 apply 阶段进度跟踪的基础，必须遵守。
