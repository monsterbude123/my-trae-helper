# proposal-template.md — Proposal 模板

> 用于 fullstack-proposal-writer Agent。proposal 回答"Why"和"What"，不涉及"How"。
>
> **变更名推荐** `{迭代号}-{序号}-{描述}` 格式（如 `04-22-workbench-integration`），
> 不强制，但推荐。详见 SKILL.md 变更名规范。

---

## 苏格拉底式提问（Why 驱动）

写 proposal 前，先通过 4 问澄清动机：

1. **根因**: "是什么触发了这个变更？（Bug#、用户反馈、技术债）"
2. **现状**: "现在的行为是什么？为什么不够好？"
3. **成功标准**: "变完之后，世界有什么不同？可量化吗？"
4. **不做的影响**: "如果不做这个变更，会发生什么？"

---

## 能力声明详细说明

> **关键区分**：能力名 ≠ 变更名。
> - 变更名：这次工作的代号（如 `04-22-workbench-refactor`）
> - 能力名：系统提供给用户的功能契约（如 `publish-validation`、`email-verification`）
> - 一个变更可能涉及多个能力，一个能力对应一个 `specs/{能力名}/spec.md`

一个能力 = 一个可独立测试、可独立描述的行为集合。

**正确示例**：
```
变更名: 04-22-workbench-panel-refactor
能力: unified-panel-orchestration — 统一面板编排引擎
能力: panel-hot-reload — 面板热加载
能力: state-bridge — 跨面板状态桥接
```

**错误示例**（不要把变更名当能力名）：
```
能力: workbench-refactor — 这会直接变成 specs/workbench-refactor/spec.md，无意义
```

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

## Impact（影响面）（V5）

> 来源 fullstack-intake: {intake 流程定位卡简要引用}

### 技术影响面（来自 fullstack-intake）

| 维度 | 内容 |
|------|------|
| 直接影响 | {文件/模块/契约列表} |
| 间接影响 | {调用方/测试/文档列表} |
| 风险点 | {高/中/低风险列表} |

### 业务影响面（proposal-writer 深化）

| 维度 | 内容 |
|------|------|
| 业务影响 | {对用户/业务流程的影响} |
| 兼容性 | {对现有功能的兼容性影响} |
| 迁移影响 | {是否需要数据/配置迁移} |
| 文档影响 | {需更新哪些文档} |

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

### 技术影响面（来自 fullstack-intake）

| 维度 | 内容 |
|------|------|
| 直接影响 | shared/common (BizCode)、content (PublishValidationService, ExceptionHandler) |
| 间接影响 | 前端调用方（需同步新 errorCode 映射） |
| 风险点 | 低 — schema 不变，向后兼容 errors 数组 |

### 业务影响面（proposal-writer 深化）

| 维度 | 内容 |
|------|------|
| 业务影响 | 前端可由 bizCode 一级路由判断业务分支，减少 Bug |
| 兼容性 | errors 数组字段结构不变，旧前端不受影响 |
| 迁移影响 | 无数据迁移，仅 bizCode 语义细化 |
| 文档影响 | docs/modules/content.md 更新 |

## Open Questions

- [ ] 前端新 errorCode 映射时间线？
```

---

## 大规格 Proposal 拆分指南

> 详见 [progressive-disclosure.md](progressive-disclosure.md) §2 proposal.md

当 Why+What+Capabilities+Non-Goals 总长度超过 150 行，或任一 section 可以独立阅读时，拆分为多文件：

```
proposal.md           ← 决策概要（What 摘要 + Capabilities 一览 + 结论）
proposal/
  why.md              ← 业务动机详细论证
  capabilities.md     ← 每个 capability 2-3 段详细描述
  non-goals.md        ← 边界说明（含排除理由）
  impact.md           ← 影响面分析
```

**proposal.md（父文件）参考 thresholds.md proposal.md 父文件默认值**，包含：
- What 一段摘要（3 句）
- Capabilities 一览表（一行一行）
- Non-Goals 摘要（一行一条）
- 指向子文件的链接

> 阈值配置 → [thresholds.md](thresholds.md)

Agent 读 proposal.md → 2 分钟理解全景 → 按需深入子文件。

---

## AOP 后置自检

> 删除所有版本/状态附注后，Why/What/Capabilities/Non-Goals 四段是否仍然完整可读？否 → 不合格。

产出 proposal.md 后、移交 spec-writer 前，结构化自检：

```
Q: [POST][P-01][Why 段是否建立了清晰的业务动机][清晰/笼统/缺失]
Q: [POST][P-02][每个 Capability 是否可验证且有明确的完成标准][可验证/部分可验证/不可验证]
Q: [POST][P-03][Non-Goals 是否排除了容易被误解为遗漏的内容][是/否/未声明]
Q: [POST][P-04][影响面是否区分了技术影响和业务影响][已区分/仅技术/仅业务/未评估]
Q: [POST][P-05][proposal 是否只写增量（无架构文档全文复制）][是/否]
Q: [POST][P-06][删除版本附注后核心四段是否仍然完整可读][是/否—核心段被替代]
```

> 全部通过 → 移交 spec-writer。有失败项 → 修正 → 重新自检 → 仍失败 → 写 report-{0X}.md。
