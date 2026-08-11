# 状态卡初始化模板

> Stage -1 Intake 初始化状态卡的标准模板。3 类（project / change / bug）共用一份骨架，按需替换字段。

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

## 字段填写规则

| 字段 | 必填 | 规则 |
|------|:---:|------|
| `card_type` | ✅ | project / change / bug |
| `card_id` | ✅ | 唯一标识 |
| `current_stage` | ✅ | 见 stage_config 命名 |
| `stage_status` | ✅ | pending / working / completed / blocked / skipped |
| `stage_started_at` | ✅ | ISO 8601（如 `2026-08-11T14:30:00`） |
| `updated_at` | ✅ | 同上，每次更新必改 |
| `updated_by` | ✅ | 主上下文 / sub-agent name |
| `health` | ✅ | 🟢 on-track / 🟡 degraded / 🔴 blocked |
| `artifacts` | ✅ | 至少含 1 项 |
| `gate_result` | ✅ | PENDING → PASS / FAIL |
| `next_stage` | ✅ | 含 id + skill_name |
| `blocked_by` | ✅ | null 或 5 字段阻塞报告 |
| `actor` | ✅ | 主上下文 / sub-agent name |

---

## 模板渲染示例

### project-init

```yaml
card_type: project
card_id: my-trae-helper
current_stage: 0/plan
stage_status: pending
stage_started_at: 2026-08-11T14:30:00
...
next_stage:
  id: 0/plan
  skill_name: skills/02-plan/SKILL.md
notes: |
  路由决策证据:
    意图: project-init
    触发词: "初始化"
    项目惯例要点: 已有 6 条自有铁律，stage_config.implement.skills 覆盖为 react-dev-skill
```

### change-start (feature)

```yaml
card_type: change
card_id: 2026-08-11-add-user-auth
current_stage: 0/plan
stage_status: pending
stage_started_at: 2026-08-11T15:00:00
...
next_stage:
  id: 0/plan
  skill_name: skills/02-plan/SKILL.md
notes: |
  路由决策证据:
    意图: change-start (feature)
    子意图: feature
    触发词: "新增"
    项目惯例要点: change-id 命名遵循 {YYYY-MM-DD}-{slug}
```

### bug-fix

```yaml
card_type: bug
card_id: auth-003-token-refresh-concurrency-500
current_stage: 6/bug-fix
stage_status: pending
stage_started_at: 2026-08-11T16:00:00
...
bug_id: auth-003-token-refresh-concurrency-500
bug_severity: P1
notes: |
  Bug 录入证据:
    触发词: "期望 X 但实际 Y"
    用户询问: 同意录入
    6 字段收集: 完整
    Bug 单编号: auth-003-token-refresh-concurrency-500
    路由目标: Stage 6 Bug Fix
```

---

## 校验脚本

```bash
python ../../scripts/state-card-validator.py {state-card-path}
# 输出: PASS / FAIL + 不一致项清单
```

**校验项**:
- [ ] 所有必填字段非空
- [ ] `artifacts[].exists` 与文件系统一致（LS 验证）
- [ ] `gate_result.status` 为 PENDING / PASS / FAIL / N/A 之一
- [ ] `current_stage` 在 13 stage 名单中
- [ ] `next_stage.skill_name` 在 `skills/` 目录中存在
- [ ] `blocked_by` 非空时 `stage_status` 不能是 completed
- [ ] `stage_status=completed` 时 `stage_ended_at` 必须有值

---

## 关联引用

- [SKILL.md](../SKILL.md) — Stage -1 入口
- [state-card-protocol.md](../../../references/state-card-protocol.md) — 状态卡协议（完整字段定义 + 更新时机 + 交叉验证）
- [intent-routing.md](../workflows/intent-routing.md) — 意图路由工作流
- [bug-state-machine.md](../references/bug-state-machine.md) — Bug 单状态机
- [bug-template.md](bug-template.md) — Bug 单文档模板
