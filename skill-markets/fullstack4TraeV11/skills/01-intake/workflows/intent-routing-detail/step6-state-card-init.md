# Step 6：初始化状态卡 — intent-routing.md 详情

> 父文件：[../intent-routing.md](../intent-routing.md)
> 来源：原 intent-routing.md 第 155-261 行（保留信息密度）

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

**完整状态卡协议**: [../../../references/state-card-protocol.md](../../../../references/state-card-protocol.md)
**状态卡初始化模板**: [../../templates/state-card-init.md](../../templates/state-card-init.md)

---

## 关联引用

- 父文件：[../intent-routing.md](../intent-routing.md)
- state-card-protocol.md：[../../../references/state-card-protocol.md](../../../../references/state-card-protocol.md)
- state-card-init.md：[../../templates/state-card-init.md](../../templates/state-card-init.md)
- SKILL.md：[../../SKILL.md](../../SKILL.md)
