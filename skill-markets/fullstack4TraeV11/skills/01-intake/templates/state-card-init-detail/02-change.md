# Change 级状态卡模板 — state-card-init.md 详情

> 父文件：[../state-card-init.md](../state-card-init.md)
> 来源：原 state-card-init.md 第 53-104 行（保留信息密度）

---

## Change 级（change）— 用于 change-start (feature/refactor/doc-sync)

```yaml
---
card_type: change
card_id: {{change_id}}  # 格式: {YYYY-MM-DD}-{slug}
version: "1.0.0"
current_stage: {{initial_stage}}  # 如 0/plan | 1/spec
stage_status: pending
stage_started_at: {{iso_8601_now}}
stage_ended_at: null
updated_at: {{iso_8601_now}}
updated_by: 主上下文
health: "🟢 on-track"
artifacts:
  - path: docs/specs/changes/{{change_id}}/plan.md
    type: file
    exists: false
    evidence: "待 Stage 0 Plan 创建"
  - path: docs/specs/changes/{{change_id}}/spec.md
    type: file
    exists: false
    evidence: "待 Stage 1 Spec 创建"
gate_result:
  status: PENDING
  gate: stage-gate.py
  output: null
  verified_at: null
next_stage:
  id: {{next_stage_id}}
  skill_name: {{next_stage_skill_name}}
  expected_inputs:
    - "状态卡 + 项目惯例表 + 意图分类结果"
  prerequisites:
    - "意图识别 PASS"
    - "项目惯例勘察 PASS"
    - "状态卡初始化 PASS"
blocked_by: null
actor: 主上下文
duration_minutes: 0
parent_change: {{parent_change_id | null}}
related_changes: []
risk_level: {{LOW | MEDIUM | HIGH}}
priority: {{P0 | P1 | P2 | P3}}
notes: |
  路由决策证据:
    意图: {{intent}}
    子意图: {{sub_intent}}
    触发词: {{trigger_phrase}}
    项目惯例要点: {{conventions_summary}}
---
```

---

## 关联引用

- 父文件：[../state-card-init.md](../state-card-init.md)
- state-card-protocol.md：[../../../references/state-card-protocol.md](../../../../references/state-card-protocol.md)
