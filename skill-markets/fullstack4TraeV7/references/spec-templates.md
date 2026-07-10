# spec-templates.md — Spec 模板库（V3）

> 用于 fullstack-spec-writer Agent。V3 采用 BDD 场景化 + 能力级拆分。

---

## Spec 目录结构

```
docs/specs/changes/{change-name}/specs/
├── {capability-a}/
│   └── spec.md       ← 每个能力一个 spec
├── {capability-b}/
│   └── spec.md
└── ...
```

---

## Spec 编号体系（L0-L4，底层到应用）

```
L0 (001-049): 基础设施 — 中间件、公共错误码、日志、配置
L1 (050-099): 业务核心 — 核心领域模型、业务规则引擎
L2 (100-149): 业务应用 — 具体业务功能、使用场景
L3 (150-199): 集成网关 — API 网关、外部服务集成、消息队列
L4 (200-249): 前端页面 — UI 交互、状态管理、路由
```

同一层次内序号递增，如 L1-050, L1-051, L1-052... 
编号写入 spec.md 头部的 `> L{层次}-{序号}` 行。

---

## 完整 Spec 模板

```markdown
# {Capability Name}
> L{层次}-{序号}  ← L0-L4 编号
> 来源 Proposal: docs/specs/changes/{change-name}/proposal.md
> 状态: draft → review → approved → implemented

{1-2 句能力概述}

## ADDED Requirements

### Requirement: {需求摘要}

{1-2 句描述这个需求的意图和范围}

#### Scenario: {Happy Path — 正常场景名}

- **GIVEN** {前置条件}
- **WHEN** {触发动作}
- **THEN** 系统 SHALL {预期行为}
- **AND** {额外预期}

#### Scenario: {Error Case — 异常场景名}

- **WHEN** {异常触发条件}
- **THEN** 系统 SHALL {预期错误处理}
- **AND** errors[] SHALL 包含 {错误信息}

#### Scenario: {Edge Case — 边界场景名}

- **GIVEN** {特殊前置条件}
- **WHEN** {触发动作}
- **THEN** 系统 SHALL {边界行为}

---

### Requirement: {另一个需求摘要}

#### Scenario: {场景名}

- **WHEN** {动作}
- **THEN** 系统 SHALL {预期}

#### Scenario: {另一个场景}

- **WHEN** {动作}
- **THEN** 系统 SHALL NOT {禁止的行为}

---

## MODIFIED Requirements

> 仅当修改已有能力时使用

### Requirement: {被修改的需求名}

> 来源: docs/specs/archive/{原变更}/specs/{capability}/spec.md
> 变更: {一句话描述变更}

#### Scenario: {场景名}

- **WHEN** {动作}
- **THEN** 系统 SHALL {新的预期行为}
```

---

## 场景编写规范

### SHALL 语义

| 关键词 | 含义 | 使用场景 |
|--------|------|---------|
| **SHALL** | 强制要求，不可协商 | 核心行为、安全约束、API 契约 |
| **SHALL NOT** | 强制禁止 | 安全边界、数据约束、权限 |
| **SHOULD** | 推荐但非强制 | 最佳实践、UX 建议 |
| **MAY** | 可选 | 非核心功能 |

### 场景质量标准

每个 Requirement 必须：

- [ ] 至少 1 个 Happy Path 场景（正常流程）
- [ ] 至少 1 个 Error Case 场景（异常处理）
- [ ] 场景可独立映射为测试用例
- [ ] WHEN 条件精确（不是"当用户操作时"）
- [ ] THEN 断言可验证（不是"系统表现良好"）

---

## 完整示例

> 以下示例中：
> - **变更名**: `05-02-error-code-semantic-split`（工作代号）
> - **能力名**: `error-response-semantics`（功能契约）
> - 注意：specs/ 下的目录用能力名，不是变更名

```markdown
# error-response-semantics

> L1-051
> 来源 Proposal: docs/specs/changes/05-02-error-code-semantic-split/proposal.md
> 状态: approved

系统 SHALL 在统一响应包装 Result 中以业务码 code 字段一级路由区分三类失败语义，
禁止前端通过 errors[] 数组内容判断业务分支。

## ADDED Requirements

### Requirement: 校验参数失败返回 40400

参数校验、必填缺失等请求级错误 SHALL 返回 bizCode=40400。

#### Scenario: 必填参数缺失

- **WHEN** 客户端提交缺少必填字段的请求
- **THEN** 系统 SHALL 返回 HTTP 200 + code=40400
- **AND** errors[] SHALL 包含缺失字段名称和原因

#### Scenario: 参数格式非法

- **WHEN** 客户端提交格式非法的参数（如 email 格式错误）
- **THEN** 系统 SHALL 返回 code=40400
- **AND** errors[] SHALL 包含非法字段和约束说明

### Requirement: 前置条件未满足返回 40900

发布内容的前置条件未满足（如未生成图片）SHALL 返回 bizCode=40900。

#### Scenario: 未生成图片时发布

- **WHEN** 用户发布内容但尚未生成配图
- **THEN** 系统 SHALL 返回 code=40900
- **AND** errors[] SHALL 提示"请先生成配图"

#### Scenario: 前置条件已满足正常通过

- **WHEN** 所有前置条件已满足
- **THEN** 系统 SHALL 继续后续业务流程
- **AND** SHALL NOT 返回 40900

### Requirement: 重复发布触发确认返回 40911

幂等性冲突（如重复发布同一内容）SHALL 返回 bizCode=40911，由前端弹出确认弹窗。

#### Scenario: 重复发布同一内容

- **WHEN** 用户提交已发布过的相同内容
- **THEN** 系统 SHALL 返回 code=40911
- **AND** errors[] SHALL 提示"该内容已发布，是否继续？"

#### Scenario: 用户确认后允许重复发布

- **GIVEN** 系统返回了 40911
- **WHEN** 用户在确认弹窗中点击"继续发布"
- **THEN** 系统 SHALL 接受请求并执行发布
```

---

## 轻量 Spec 模板（小功能用）

```markdown
# {Capability Name}

> 轻量 Spec — 快速启动
> 状态: approved

## ADDED Requirements

### Requirement: {需求}

#### Scenario: {Happy Path}
- **WHEN** {动作}
- **THEN** 系统 SHALL {预期}

#### Scenario: {Error}
- **WHEN** {异常}
- **THEN** 系统 SHALL {错误处理}

## Acceptance

- [ ] {可验证的验收条件 1}
- [ ] {可验证的验收条件 2}
```

---

## 反面范例

| 反面（禁止） | 正确（必须） |
|---|---|
| "系统应该表现良好" | THEN 系统 SHALL 返回 code=200, data.id 非空 |
| "用户操作时可能会出错" | WHEN errors[] 非空, THEN 系统 SHALL 返回对应 bizCode |
| 只有一个 Happy Path 场景 | 每个 Requirement 至少 happy path + error case |
| "提升用户体验" | 可测试的 THEN 断言 |
| 所有能力塞一个 spec.md | 每个能力一个 specs/{capability}/spec.md |
