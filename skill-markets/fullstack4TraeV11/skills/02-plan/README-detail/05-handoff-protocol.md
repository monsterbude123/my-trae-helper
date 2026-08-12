# 交付协议 + Completion Report + AOP 自检 — README.md 详情

> 父文件：[../README.md](../README.md)
> 来源：原 README.md 第 152-217 行（保留信息密度）

---

## 完整交付协议（4 件套）

```yaml
hand_over:
  stage_id: "0/plan"
  stage_skill: skills/02-plan/SKILL.md
  status: completed
  health: "🟢 on-track"
  artifacts:
    - path: docs/specs/changes/{id}/plan.md
      type: file
      evidence: "plan.md ≤ 80 行 + 3 路探索 evidence + Capabilities ≤ 5 + Risk 等级标注"
    - path: docs/specs/changes/{id}/.state-card.md
      type: file
      evidence: "current_stage=0.5/test-plan + next_stage 填写 + updated_at 更新"
    - path: docs/specs/changes/{id}/exploration/（可选）
      type: dir
      evidence: "3 路探索子代理产出（docs_summary / code_summary / deps_summary）"
  gate_result:
    status: PASS
    gate: stage-gate.py
    output: "plan.md 行数 + Capabilities 数 + 探索 evidence 数 PASS"
  next_stage:
    id: "0.5/test-plan"
    skill_name: skills/03-test-plan/SKILL.md
    expected_inputs: [plan.md, 3 路探索 evidence, GitNexus impact 报告]
    prerequisites: [意图识别 PASS, 去重检查 PASS, 3 路探索全完成]
```

### Completion Report（3 路探索子代理必返）

```yaml
## Completion Report - Sub-agent A（文档探索）
- agent: planner-doc-explorer
- artifacts: [docs/specs/changes/{id}/exploration/docs_summary.json]
- explored_docs: [{N} files]
- key_findings: [{capability_1}, {capability_2}, ...]
- status: ✓ | ⚠️ | ✗

## Completion Report - Sub-agent B（代码探索）
- agent: planner-code-explorer
- artifacts: [docs/specs/changes/{id}/exploration/code_summary.json]
- explored_symbols: [{N} via GitNexus]
- impact_graph: [调用链描述]
- risk_level: LOW|MEDIUM|HIGH|CRITICAL
- status: ✓ | ⚠️ | ✗

## Completion Report - Sub-agent C（依赖探索）
- agent: planner-deps-explorer
- artifacts: [docs/specs/changes/{id}/exploration/deps_summary.json]
- reusable_modules: [{N} found]
- new_modules_needed: [{name}, {name}, ...]
- status: ✓ | ⚠️ | ✗
```

### AOP 移交自检

```
- [ ] 子代理探索全完成（3/3），产出可验证
- [ ] GitNexus impact() 已执行，风险等级已标注
- [ ] 重构场景 → spec-purge.py 已执行
- [ ] plan.md ≤ 80 行，Capabilities ≤ 5 项
- [ ] 状态卡已更新 current_stage + next_stage
- [ ] state-card-validator.py PASS
```

任一项 ❌ → 修正后重新移交。

---

## 关联引用

- 父文件：[../README.md](../README.md)
- SKILL.md：[../SKILL.md](../SKILL.md)
