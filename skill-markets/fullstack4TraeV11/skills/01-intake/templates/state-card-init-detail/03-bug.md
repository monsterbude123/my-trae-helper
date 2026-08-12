# Bug 级状态卡模板 — state-card-init.md 详情

> 父文件：[../state-card-init.md](../state-card-init.md)
> 来源：原 state-card-init.md 第 108-159 行（保留信息密度）

---

## Bug 级（bug）— 用于 bug-fix

```yaml
---
card_type: bug
card_id: {{bug_id}}  # 格式: {module}-{NNN}-{slug}
version: "1.0.0"
current_stage: 6/bug-fix
stage_status: pending
stage_started_at: {{iso_8601_now}}
stage_ended_at: null
updated_at: {{iso_8601_now}}
updated_by: 主上下文
health: "🟢 on-track"
artifacts:
  - path: docs/bugs/{{bug_id}}.md
    type: file
    exists: true
    evidence: "Bug 单 6 字段齐全（症状/期望/复现/影响/环境/触发词）"
  - path: docs/bugs/{{bug_id}}/.state-card.md
    type: file
    exists: true
    evidence: "Bug 状态卡初始化 + next_stage=6/bug-fix"
gate_result:
  status: PENDING
  gate: e2e-先行
  output: null
  verified_at: null
next_stage:
  id: 6/bug-fix
  skill_name: skills/12-bug-fix/SKILL.md
  expected_inputs:
    - "Bug 单 + 复现步骤"
  prerequisites:
    - "Bug 单 6 字段齐全"
    - "状态卡 OPEN 状态"
    - "state-card-validator.py PASS"
blocked_by: null
actor: 主上下文
duration_minutes: 0
bug_id: {{bug_id}}
bug_severity: {{P0 | P1 | P2}}
notes: |
  Bug 录入证据:
    触发词: {{trigger_phrase}}
    用户询问: 同意录入
    6 字段收集: 完整
    Bug 单编号: {{bug_id}}
    路由目标: Stage 6 Bug Fix
    决策时间: {{iso_8601_now}}
---
```

---

## 关联引用

- 父文件：[../state-card-init.md](../state-card-init.md)
- state-card-protocol.md：[../../../references/state-card-protocol.md](../../../references/state-card-protocol.md)
- bug-template.md：[../bug-template.md](../bug-template.md)
