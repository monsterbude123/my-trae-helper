# Project 级状态卡模板 — state-card-init.md 详情

> 父文件：[../state-card-init.md](../state-card-init.md)
> 来源：原 state-card-init.md 第 7-49 行（保留信息密度）

---

## 项目级（project）— 用于 project-init / project-health

```yaml
---
card_type: project
card_id: {{project_name}}
version: "1.0.0"
current_stage: {{initial_stage}}  # 如 0/plan | 7/project-health
stage_status: pending
stage_started_at: {{iso_8601_now}}
stage_ended_at: null
updated_at: {{iso_8601_now}}
updated_by: 主上下文
health: "🟢 on-track"
artifacts:
  - path: {{artifact_path}}
    type: {{file | dir | report}}
    exists: {{true | false}}
    evidence: "{{evidence_text}}"
gate_result:
  status: PENDING
  gate: stage-gate.py
  output: null
  verified_at: null
next_stage:
  id: {{next_stage_id}}
  skill_name: {{next_stage_skill_name}}
  expected_inputs:
    - {{input_1}}
    - {{input_2}}
  prerequisites:
    - {{prereq_1}}
    - {{prereq_2}}
blocked_by: null
actor: 主上下文
duration_minutes: 0
notes: |
  路由决策证据:
    意图: {{intent}}
    触发词: {{trigger_phrase}}
    项目惯例要点: {{conventions_summary}}
---
```

---

## 关联引用

- 父文件：[../state-card-init.md](../state-card-init.md)
- state-card-protocol.md：[../../../references/state-card-protocol.md](../../../../references/state-card-protocol.md)
