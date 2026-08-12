# 状态卡模板 — V11

> V11 三类状态卡通用模板。Stage -1 Intake 初始化时按 `card_type` 选择对应模板。
>
> **路径映射**(完整协议见 [state-card-protocol.md](../../references/state-card-protocol.md)):
>
> | 类型 | 路径 |
> |------|------|
> | **project 级** | `{project}/docs/specs/.state-card.md` |
> | **change 级** | `{project}/docs/specs/changes/{change-id}/.state-card.md` |
> | **bug 级** | `{project}/docs/bugs/{bug-id}/.state-card.md` |
>
> 三类状态卡在不同目录,文件系统层无冲突(路径区分而非后缀区分)。
>
> **⚠️ V11.2 反例 — 蒸馏自 canvas-asset-folders 实战**:
> - ❌ **绝不能用 `.trae/state-card.md`**（V10 残留路径，V11 已迁移出 `.trae/`）
> - ❌ **绝不能用 `.state-card.change.md`** 后缀区分（路径区分已足够，后缀是过度设计）
> - 必须按 [state-card-protocol.md §1.1](../../references/state-card-protocol.md) 协议路径初始化

---

## 模板（3 类）

### project 级

```yaml
---
card_type: project
card_id: {project-name}
version: "1.0.0"
current_stage: 0/plan | 7/project-health
stage_status: pending
stage_started_at: {ISO 8601}
stage_ended_at: null
updated_at: {ISO 8601}
updated_by: 主上下文
health: "🟢 on-track"
artifacts:
  - path: {project}/docs/specs/.state-card.md
    type: file
    exists: true
    evidence: "状态卡初始化"
gate_result:
  status: PENDING
  gate: stage-gate.py
  output: null
  verified_at: null
next_stage:
  id: 0/plan | 7/project-health
  skill_name: skills/02-plan/SKILL.md | skills/13-project-health/SKILL.md
  expected_inputs: [意图分类结果 + 项目惯例表]
  prerequisites: [意图识别 PASS, 项目惯例勘察 PASS]
blocked_by: null
actor: 主上下文
duration_minutes: 0
notes: |
  路由决策证据:
    意图: {intent}
    触发词: {trigger_phrase}
    项目惯例要点: {conventions_summary}
---
```

### change 级

```yaml
---
card_type: change
card_id: {YYYY-MM-DD}-{slug}
version: "1.0.0"
current_stage: 0/plan | 0.5/test-plan | 1/spec | 1.5/prototype | 2/contract | 3/implement | 3.5/real-verify | 4/review | 4.5/rot-scan | 5/accept
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
  output: null
  verified_at: null
next_stage:
  id: {next-stage-id}
  skill_name: skills/{NN}-{name}/SKILL.md
  expected_inputs: [{input-1}, {input-2}]
  prerequisites: [{prereq-1}, {prereq-2}]
blocked_by: null
actor: 主上下文
duration_minutes: 0
parent_change: {parent-id | null}
related_changes: []
risk_level: LOW | MEDIUM | HIGH | CRITICAL
priority: P0 | P1 | P2 | P3
notes: |
  路由决策证据:
    意图: {intent}
    触发词: {trigger_phrase}
---
```

### bug 级

```yaml
---
card_type: bug
card_id: {module}-{NNN}-{slug}
version: "1.0.0"
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
  - path: docs/bugs/{bug-id}/.state-card.md
    type: file
    exists: true
    evidence: "Bug 状态卡初始化"
gate_result:
  status: PENDING
  gate: e2e-先行
  output: null
  verified_at: null
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

---

## 字段规则

| 字段 | 必填 | 规则 |
|------|:---:|------|
| `card_type` | ✅ | project / change / bug |
| `card_id` | ✅ | 唯一标识 |
| `current_stage` | ✅ | 见 stage_config 命名 |
| `stage_status` | ✅ | pending / working / completed / blocked / skipped |
| `updated_at` | ✅ | 每次更新必改 |
| `health` | ✅ | 🟢 / 🟡 / 🔴 |

## 关联引用

- [state-card-protocol.md](../../references/state-card-protocol.md) — 完整协议
- Stage -1 Intake: [../../skills/01-intake/SKILL.md](../../skills/01-intake/SKILL.md)
- state-card-init.md: [../../skills/01-intake/templates/state-card-init.md](../../skills/01-intake/templates/state-card-init.md)