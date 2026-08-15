# 计划追问点工作流（Plan Clarification）

> Stage 0 Plan 在 3 路探索后、产出 plan.md 前必走。识别未明确的追问点 + AskUserQuestion 澄清。

---

## 流程

```
[3 路探索完成]
  ↓
[追问点扫描]
  ├─ 架构约束冲突？
  ├─ 能力边界模糊？
  ├─ Non-Goals 不明确？
  ├─ 影响面风险等级 ≥ HIGH？
  ├─ Closure 闭环步骤 > 5？
  └─ 用户需求有歧义？
  ↓
[生成追问清单]
  ↓
[AskUserQuestion 一次性问完（≤ 4 题）]
  ↓
[用户回答]
  ├─ 全答 → 汇总 → plan.md
  ├─ 部分答 → 标注"待确认" → plan.md 标注假设
  └─ 拒绝答 → 状态卡 health = 🟡 + 阻塞报告
```

---

## 追问点类型（6 类）

### 类型 1：架构约束冲突

**识别信号**: 3 路探索发现现有架构与新需求冲突。

**追问模板**:
```
Q: 探索发现现有架构约束 X 与您的需求 Y 冲突，请选择处置：
  1. 修改架构（接受 X 变更）
  2. 修改需求（保留 X，调整 Y）
  3. 绕过约束（创建新模块 X'）
```

### 类型 2：能力边界模糊

**识别信号**: Capabilities 边界不清，可能超出 5 项或含灰色术语。

**追问模板**:
```
Q: 以下能力哪些是本次必须做的？
  □ [能力 1]
  □ [能力 2]
  □ [能力 3]
  □ [能力 4]（灰色，可能不是）
  □ [能力 5]（灰色，可能不是）
```

### 类型 3：Non-Goals 不明确

**识别信号**: 用户没说什么不做，导致 Capabilities 蔓延。

**追问模板**:
```
Q: 哪些事情明确不做（Non-Goals）？
  □ [候选 1]
  □ [候选 2]
  □ [候选 3]
```

### 类型 4：影响面风险 ≥ HIGH

**识别信号**: GitNexus impact 显示 HIGH/CRITICAL 风险。

**追问模板**:
```
Q: GitNexus impact 显示风险等级 HIGH（影响 N 个符号 + M 个下游），请决策：
  1. 接受风险，继续完整方案
  2. 缩小范围，分阶段实施（先低风险）
  3. 增加 buffer（更多测试 + 更长 review）
```

### 类型 5：Closure 闭环步骤 > 5

**识别信号**: P0 闭环需要 > 5 步才能完成，超出铁律 9。

**追问模板**:
```
Q: P0 闭环步骤过多（当前 N 步），如何拆分？
  1. 拆成多个 change（每个 ≤ 5 步）
  2. 保持单 change 但放宽铁律（需用户批准）
  3. 缩减 P0 范围（非关键步骤降级到 P1）
```

### 类型 6：用户需求有歧义

**识别信号**: 用户原话含多义词或前后矛盾。

**追问模板**:
```
Q: 您说的"X"我理解有两种可能，请确认：
  1. 解释 A（基于 3 路探索推断）
  2. 解释 B（基于字面意思）
  3. 都不是，我重新说明
```

---

## AskUserQuestion 最佳实践

- **批量问**: 一次 AskUserQuestion（≤ 4 题），不分散追问（避免打断用户）
- **选项不超过 4**: 每个问题 ≤ 4 选项 + "Other"
- **推荐项首位**: 高频选项放第一位 + 标注 (Recommended)
- **不重复问**: 已答过的问题不再问（避免反模式 1）

---

## 追问后处理

### 全答

```yaml
plan.md:
  - Why: [整合用户回答]
  - Capabilities: [用户选择的能力]
  - Non-Goals: [用户明确不做的]
  - Tasks: [基于回答生成]
  - Closure: [基于回答生成]
  - Impact: [整合探索 + 风险决策]
```

### 部分答

```yaml
plan.md:
  - Why: [整合用户回答]
  - 标注: "## 待确认\n- [问题]: 用户暂未回答，按假设 H 处理（如有变更请告知）"
  - 状态卡 notes: 记录待确认问题
```

### 拒绝答

```yaml
状态卡:
  health: "🟡 degraded"
  blocked_by:
    type: "用户未回答追问"
    questions: [list of unanswered]
    next_action: "等用户回答后继续"
```

---

## 反模式

### 反例 A：跳过追问直接出 plan.md

```
主上下文: 探索完成 → 直接写 plan.md  # ❌ 未澄清就规划
正确: 探索 → 追问 → 澄清 → plan.md
```

### 反例 B：一次性问 10 个问题

```
主上下文: AskUserQuestion 10 题  # ❌ 用户疲劳
正确: ≤ 4 题，分批（下一批等 plan.md v1 后再问）
```

### 反例 C：用经验主义臆断歧义

```
用户: "我要重构 X"
主上下文: "我理解您的意思" → 直接出 plan  # ❌ 违反 Article XVI §1.1（根因验证）
正确: AskUserQuestion 澄清 X 的边界
```

---

## 关联引用

- [SKILL.md §铁律 7](../SKILL.md) — SKEPTICAL VALIDATION
- [three-path-exploration.md](three-path-exploration.md) — 3 路探索
- [plan-template.md](../templates/plan-template.md) — plan.md 模板
- 公共铁律 Article XVI: [../../../references/common-iron-rules.md](../../../references/common-iron-rules.md)
