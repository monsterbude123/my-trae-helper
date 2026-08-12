# 交接协议 — README.md 详情

> 父文件：[../README.md](../README.md)
> 来源：原 README.md 第 140-192 行（保留信息密度）

---

## 完整交接协议

### Intake → Stage 0 Plan（change-start / project-init）

```yaml
hand_over:
  stage_id: "-1/intake"
  stage_skill: skills/01-intake/SKILL.md
  status: completed
  health: "🟢 on-track"
  artifacts:
    - path: docs/specs/changes/{id}/.state-card.md
      type: file
      evidence: "状态卡初始化（change 级）+ next_stage=0/plan"
    - path: docs/specs/changes/{id}/spec.md（project-init 才有）
      type: file
      evidence: "项目级 spec 初始化"
  gate_result:
    status: PASS
    gate: state-card-validator.py
    output: "状态卡字段完整 + 路由决策表齐全"
  next_stage:
    id: "0/plan"
    skill_name: skills/02-plan/SKILL.md
    expected_inputs: [状态卡 + 项目惯例表 + 意图分类结果]
    prerequisites: [意图识别 PASS, 状态卡初始化 PASS, Glob 项目惯例 PASS]
```

### Intake → Stage 6 Bug Fix（bug-fix）

```yaml
hand_over:
  stage_id: "-1/intake"
  stage_skill: skills/01-intake/SKILL.md
  status: completed
  health: "🟢 on-track"
  artifacts:
    - path: docs/bugs/{id}.md
      type: file
      evidence: "Bug 单 6 字段齐全（症状/期望/复现/影响/环境/触发词）"
    - path: docs/bugs/{id}/.state-card.md
      type: file
      evidence: "Bug 状态卡初始化 + next_stage=6/bug-fix"
  gate_result:
    status: PASS
    gate: state-card-validator.py
    output: "Bug 单状态卡字段完整"
  next_stage:
    id: "6/bug-fix"
    skill_name: skills/12-bug-fix/SKILL.md
    expected_inputs: [Bug 单 + 状态卡 + 复现步骤]
    prerequisites: [Bug 单 6 字段齐全, 状态卡 OPEN 状态]
```

---

## 关联引用

- 父文件：[../README.md](../README.md)
- SKILL.md：[../SKILL.md](../SKILL.md)
