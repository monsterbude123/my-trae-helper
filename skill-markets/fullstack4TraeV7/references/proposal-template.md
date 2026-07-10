# proposal-template.md — Proposal 模板

> 用于 fullstack-proposal-writer Agent。proposal 回答"Why"和"What"，不涉及"How"。
>
> **变更名推荐** `{迭代号}-{序号}-{描述}` 格式（如 `04-22-workbench-integration`），
> 不强制，但推荐。详见 SKILL.md 变更名规范。

---

## 完整模板

```markdown
# Proposal: {变更名称}

> 创建日期: YYYY-MM-DD
> 状态: draft → review → approved

## Why（为什么）

{1-3 段描述动机和根因。回答：什么触发了这个变更？现在有什么问题？不做会怎样？}

## What Changes（具体变更）

- **{模块名}**: {变更描述}
- **{模块名}**: {变更描述}

## Capabilities（能力声明）

> **关键区分**：能力名 ≠ 变更名。能力名描述系统功能（如 `publish-validation`），
> 不是工作代号（如 `workbench-refactor`）。每个能力对应一个独立的 spec.md。

| 能力 | 描述 | 类型 |
|------|------|------|
| {能力名} | {一句话描述这个能力做什么——面向用户的功能} | NEW |
| {能力名} | {一句话描述} | MODIFIED |

> 将在 `docs/specs/changes/{变更名}/specs/{能力名}/spec.md` 创建。

## Non-Goals（不在本次范围）

- 不涉及 {X}
- 不修改 {Y}
- 不处理 {Z}

## Impact（影响面）

| 维度 | 内容 |
|------|------|
| 代码文件 | {预计涉及的文件数量/列表} |
| 模块文档 | {需更新的 docs/modules/ 文档} |
| API 变更 | {新增/修改的接口} |
| 上下游依赖 | {受影响的服务/模块/前端页面} |

## Open Questions

- [ ] {待确认问题}
- [ ] {另一个待确认问题}
```

---

## 轻量模板（小变更用）

```markdown
# Proposal: {变更名称}

## Why
{一句话根因}

## What
- {具体变更 1}
- {具体变更 2}

## Capabilities
- {capability}: {描述} (NEW/MODIFIED)

## Non-Goals
- 不涉及 {X}
```

---

## 完整示例

```markdown
# Proposal: api-error-code-semantic-split

> 创建日期: 2026-06-15
> 状态: approved

## Why

`content` 模块的发布校验管道对三种语义不同的失败返回相同 `code=40000`，导致前端必须遍历 `errors[]` 数组判断分支。这违反了"响应码是一级路由"原则，并因此产生 Bug #82864（重复发布弹窗误触发）。

## What Changes

- **shared/common**: BizCode 新增 `PRECONDITION_REQUIRED(40900)`、`PREREQUISITE_NOT_READY(40911)`
- **content**: PublishValidationService 从单体拆分为三段（参数 → 前置条件 → 幂等）
- **content**: ExceptionHandler 根据 ValidationLevel 枚举路由分发
- **content**: 兼容策略 —— errors 数组字段结构不变

## Capabilities

| 能力 | 描述 | 类型 |
|------|------|------|
| api-error-response-semantics | 错误响应按 bizCode 一级路由，前端不通过 errors 数组判断业务分支 | NEW |

## Non-Goals

- 不涉及 account、assistant、auth、statistics 模块
- 不修改 HTTP 状态码
- 不修改前端代码（仅同步契约文档）

## Impact

| 维度 | 内容 |
|------|------|
| 代码文件 | ~8 个文件（shared 2 + content 6） |
| 模块文档 | docs/modules/content.md 更新 |
| API 变更 | 无（仅 bizCode 语义细化，schema 不变） |
| 上下游依赖 | 前端需同步确认新 errorCode 映射（**用户驱动**） |

## Open Questions

- [ ] 前端新 errorCode 映射时间线？
```

---

## 质量检查清单

- [ ] Why 不空洞（有具体根因，不是"优化系统"）
- [ ] What 列出具体模块名（不是"多处改动"）
- [ ] Capabilities 每个可测试（不是"系统稳定性"）
- [ ] Non-Goals 不为空（必须画边界）
- [ ] Impact 每个维度有内容
- [ ] 不超过 500 词（详细技术设计留给 design.md）
