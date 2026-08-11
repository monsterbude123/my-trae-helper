# 意图路由工作流（Intent Routing）

> Stage -1 Intake 的核心工作流。识别用户意图 + 路由决策 + 状态卡初始化。

---

## 流程图

```
[用户输入]
  ↓
[Step 1] 加载 skill + 解析 depends_on
  ↓
[Step 2] Glob 1 次项目惯例（AGENTS.md / docs/ / .trae/rules/）
  ↓
[Step 3] 意图识别（5 种类型）
  ├─ 触发词命中 → 直接分类
  └─ 不命中 → AskUserQuestion
  ↓
[Step 4] Bug 录入触发词判断（仅问题类触发词）
  ├─ 命中 → 询问"是否录入 bug 单？"
  │   ├─ 同意 → Step 5(bug-fix)
  │   └─ 拒绝 → 状态卡 health=🟡 + 路由到 Stage 7 Project Health（自检）
  └─ 未命中 → 跳过
  ↓
[Step 5] 路由决策（5 种意图 → 5 种路径）
  ↓
[Step 6] 初始化状态卡（3 类）
  ↓
[Step 7] 交接下一 stage
```

---

## Step 1：加载 Skill

```python
# 主上下文必走
1. Skill 工具加载 skills/01-intake/SKILL.md
2. 解析 depends_on:
   - skills: []（自身是入口，无外部依赖）
   - stages: []（无前置 stage）
   - references: [9 个公共 references]
   - scripts: [stage-gate.py, state-card-validator.py]
3. 加载 9 个公共 references（来自编排器 §0.5）
```

**校验**:
- 编排器 stage_config.intake.skills 必须为空 → ✅
- 编排器 stage_config.intake.stages 必须为空 → ✅

---

## Step 2：项目惯例勘察（Glob 1 次）

```bash
# 主上下文亲自执行（Article IV 委派纪律）
Glob patterns:
  - {project}/AGENTS.md
  - {project}/docs/constitution.md
  - {project}/docs/INDEX.md
  - {project}/.trae/rules/*.md
  - {project}/.trae/fullstack4traev11.config.yaml
```

**输出**: 项目惯例表

```yaml
project_conventions:
  naming:
    change_id_format: "{YYYYMMDD}-{slug}"  # 例: 2026-08-11-add-user-auth
    bug_id_format: "{module}-{number}-{slug}"  # 例: settings-009-config-key
  custom_rules:
    - .trae/rules/coding-standards.md
    - .trae/rules/归档路径防护.md
  stage_config_override:
    # 项目级 stage_config 覆盖（V11 dependency-config §3 层优先级）
  forbidden_paths:
    - docs/archive/**
    - .trae/tmp/**
```

**详细工作流**: [project-convention-survey.md](project-convention-survey.md)

---

## Step 3：意图识别（5 种类型）

### 3.1 触发词命中（直接分类）

| 触发词 | 意图类型 | 路由目标 |
|--------|---------|---------|
| "初始化" / "新项目" / "项目 0→1" | project-init | Stage 0 Plan |
| "新需求" / "新增功能" / "加个 X" | change-start (feature) | Stage 0 Plan |
| "重构" / "改造" / "重新设计" | change-start (refactor) | Stage 0 Plan |
| "文档同步" / "更新文档" | change-start (doc-sync) | Stage 1 Spec 或 Stage 5 Accept (lite) |
| "报错" / "错误" / "异常" | 触发 Bug 录入判断 → bug-fix | Stage 6 Bug Fix |
| "不工作" / "失败" / "崩溃" | 触发 Bug 录入判断 → bug-fix | Stage 6 Bug Fix |
| "应该出现 X 但出现 Y" | 触发 Bug 录入判断 → bug-fix | Stage 6 Bug Fix |
| "期望 X 但实际 Y" | 触发 Bug 录入判断 → bug-fix | Stage 6 Bug Fix |
| "自检" / "健康度" / "诊断" | project-health | Stage 7 Project Health |

### 3.2 触发词不命中（AskUserQuestion）

```python
# 反模式: 经验主义臆断意图（Article V 违反）
# 正确: AskUserQuestion 列出 5 种意图
AskUserQuestion(
  question="我识别到的意图不明确，请选择您要做的事情：",
  options=[
    {"label": "初始化项目（0→1）", "description": "从零开始一个新项目"},
    {"label": "新增功能 / 重构", "description": "在现有项目上加新功能或重构"},
    {"label": "修复 Bug", "description": "用户反馈的报错/不工作问题"},
    {"label": "文档同步", "description": "更新 spec / api 文档"},
    {"label": "项目健康度自检", "description": "异步自检项目状态"}
  ]
)
```

---

## Step 4：Bug 录入触发词判断

**仅当 Step 3 命中问题类触发词才走此步**。

```
问题类触发词命中
  ↓
主上下文必问："是否作为 bug 单录入？"
  ├─ 用户同意 → 走 [bug-intake-flow.md](bug-intake-flow.md) → Step 5(bug-fix)
  └─ 用户拒绝 → 按"一般咨询"处理
      ├─ 状态卡 health = 🟡 degraded
      ├─ notes: "用户拒绝 bug 录入，按一般咨询处理"
      └─ 路由: Stage 7 Project Health（异步自检）
```

**详细 Bug 录入流程**: [bug-intake-flow.md](bug-intake-flow.md)

---

## Step 5：路由决策

| 意图类型 | 路由目标 | 状态卡类型 | next_stage |
|---------|---------|-----------|-----------|
| **project-init** | Stage 0 Plan → Stage 5 Accept | project | `0/plan` |
| **change-start (feature/refactor)** | Stage 0 Plan → Stage 5 Accept | change | `0/plan` |
| **change-start (doc-sync)** | Stage 1 Spec → Stage 5 Accept (lite) | change | `1/spec` |
| **bug-fix** | Stage 6 Bug Fix（独立支线）| bug | `6/bug-fix` |
| **project-health** | Stage 7 Project Health（异步自检）| project | `7/project-health` |

**详细路由决策树**: [references/routing-decision-tree.md](references/routing-decision-tree.md)

---

## Step 6：初始化状态卡（3 类选其一）

### 6.1 project 级（project-init / project-health）

```yaml
---
card_type: project
card_id: {project-name}
current_stage: 0/plan | 7/project-health
stage_status: pending
stage_started_at: {ISO 8601}
stage_ended_at: null
updated_at: {ISO 8601}
updated_by: 主上下文
health: "🟢 on-track"
artifacts:
  - path: docs/specs/changes/{change-id}/
    type: dir
    exists: true
    evidence: "ls 验证"
gate_result:
  status: PENDING
  gate: stage-gate.py
next_stage:
  id: 0/plan | 7/project-health
  skill_name: skills/02-plan/SKILL.md | skills/13-project-health/SKILL.md
  expected_inputs: [意图分类结果 + 项目惯例表]
  prerequisites: [意图识别 PASS, 项目惯例勘察 PASS]
blocked_by: null
actor: 主上下文
duration_minutes: 0
---
```

### 6.2 change 级（change-start）

```yaml
---
card_type: change
card_id: {YYYYMMDD}-{slug}
current_stage: 0/plan | 1/spec
stage_status: pending
stage_started_at: {ISO 8601}
stage_ended_at: null
updated_at: {ISO 8601}
updated_by: 主上下文
health: "🟢 on-track"
artifacts:
  - path: docs/specs/changes/{change-id}/plan.md
    type: file
    exists: false
    evidence: "待 Stage 0 Plan 创建"
gate_result:
  status: PENDING
  gate: stage-gate.py
next_stage:
  id: 0/plan | 1/spec
  skill_name: skills/02-plan/SKILL.md | skills/04-spec/SKILL.md
  expected_inputs: [意图分类结果 + 项目惯例表]
  prerequisites: [意图识别 PASS, 项目惯例勘察 PASS]
blocked_by: null
actor: 主上下文
duration_minutes: 0
parent_change: null
related_changes: []
risk_level: MEDIUM
priority: P1
notes: {意图分类 + 项目惯例要点}
---
```

### 6.3 bug 级（bug-fix）

```yaml
---
card_type: bug
card_id: {module}-{number}-{slug}
current_stage: 6/bug-fix
stage_status: pending
stage_started_at: {ISO 8601}
stage_ended_at: null
updated_at: {ISO 8601}
updated_by: 主上下文
health: "🟢 on-track"
artifacts:
  - path: docs/bugs/{bug-id}.md
    type: file
    exists: true
    evidence: "Bug 单 6 字段齐全"
gate_result:
  status: PENDING
  gate: e2e-先行
next_stage:
  id: 6/bug-fix
  skill_name: skills/12-bug-fix/SKILL.md
  expected_inputs: [Bug 单 + 复现步骤]
  prerequisites: [Bug 单 6 字段齐全, 状态卡 OPEN]
blocked_by: null
actor: 主上下文
duration_minutes: 0
bug_id: {bug-id}
bug_severity: P0 | P1 | P2
---
```

**完整状态卡协议**: [../../references/state-card-protocol.md](../../references/state-card-protocol.md)
**状态卡初始化模板**: [../templates/state-card-init.md](../templates/state-card-init.md)

---

## Step 7：交接下一 stage

```
[ ] state-card-validator.py PASS（状态卡字段完整 + 文件存在）
[ ] stage-gate.py PASS（路由切换确认）
[ ] next_stage 字段已填写
[ ] blocked_by = null
[ ] 主上下文向用户汇报："已路由到 {next_stage.skill_name}，预计 X 分钟"
```

**禁止**:
- ❌ 主上下文 Edit/Write 代码（Article IV）
- ❌ 跳过 stage-gate.py 直接交接
- ❌ 状态卡说谎（Article XII 文档诚实）

---

## 关联引用

- [SKILL.md](../SKILL.md) — 阶段入口
- [bug-intake-flow.md](bug-intake-flow.md) — Bug 录入 6 字段工作流
- [project-convention-survey.md](project-convention-survey.md) — 项目惯例勘察工作流
- [intent-types.md](../references/intent-types.md) — 5 种意图类型详解
- [routing-decision-tree.md](../references/routing-decision-tree.md) — 路由决策树
- [state-card-protocol.md](../../references/state-card-protocol.md) — 状态卡协议
