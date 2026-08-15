# Stage Interaction Protocol — stage 间交互协议

> **V11.7.0+ 设计入口**: [AC 核销门禁](../skills/09-review/SKILL.md) · [贾维斯门禁守护](../skills/00-boot/SKILL.md) · 评分制废除 → 门禁制 · 详见 [CHANGELOG.md V11.7.0](../CHANGELOG.md)


> V11 13 stage 间必走的交互协议。每两个 stage 之间必走 4 步。

---

## 4 步交互协议

```
Stage A 完成
  ↓
[1] 报告：Completion Report（4 字段：artifacts / status / evidence / next_stage）
  ↓
[2] 移交自检：AOP 移交自检清单（V11 各 stage SKILL.md §移交自检）
  ↓
[3] 状态卡更新：current_stage + stage_status + updated_at + artifacts
  ↓
[4] 启动 Stage B：主上下文委派 sub-agent-{B} 加载 skills/{NN}-{B}/SKILL.md
```

---

## Completion Report 模板

```yaml
## Completion Report - {agent-name}

artifacts:
  - {path-1}
  - {path-2}
  - {path-3}

status: "✅ | ⚠️ | 🛑"

evidence:
  - command: "{cmd}"
    output: "{output}"
    exit_code: 0
  - file: "{file}:line"

next_stage:
  id: "{stage-id}"
  prerequisites_met: true
  blockers: []
```

---

## AOP 移交自检清单（每 stage 通用）

```yaml
aop_handoff_checklist:
  - [ ] 必填产物已生成（artifact 列表非空）？
  - [ ] 每个产物附 evidence（file:line / command output）？
  - [ ] 状态卡字段完整（current_stage + stage_status + updated_at + artifacts）？
  - [ ] 状态卡 next_stage 指向下一 stage？
  - [ ] 任一项 ❌ → 修正后重新移交
```

---

## Sub-Agent 委派协议

```
主上下文:
  1. 加载 Stage B 的 SKILL.md
  2. 注入上下文（当前状态卡 + 上游 Completion Report + artifacts 路径）
  3. 委派 sub-agent-{B}
  4. 等待 Completion Report
  5. 验收（必走 9 CROSS-SESSION VERIFY，亲自跑 evidence 命令）
```

---

## V11 各 stage 移交约定

| From → To | 必含产物 | 移交门禁 |
|-----------|---------|---------|
| -1 Intake → 0 Plan | intent_class + project_convention + change_id | ✅ |
| 0 Plan → 0.5 Test Plan | plan.md + capabilities + non_goals | ✅ |
| 0.5 Test Plan → 1 Spec | test_plan.md + coverage_matrix + e2e_plan | ✅ |
| 1 Spec → 1.5 Prototype | spec.md + ac_list + edge_cases | ✅ |
| 1.5 Prototype → 2 Contract | ui_ux_logic + prototype_linkage + design_handoff | ✅ |
| 2 Contract → 3 Implement | domain_models + api_contracts + events + validation + orphan_test_sweep | ✅ |
| 3 Implement → 3.5 Real Verify | code + tests + 量化汇报（test/contract_tests/coverage）| ✅ |
| 3.5 Real Verify → 4 Review | startup_verification + visual_evidence + blockage_report | ✅ |
| 4 Review → 4.5 Rot Scan | review_report + 4 维评分 + 失败标签 | ✅ |
| 4.5 Rot Scan → 5 Accept | rot_scan_report + fix_list.json + self_diagnose | ✅ |
| 5 Accept → (archived) | spec_purge + knowledge_extract + index_update | ✅ |
| 6 Bug Fix → (closed) | bug_fix + e2e_test + root_cause + bug_id_closed | ✅ |
| 7 Project Health → (async) | project_health_report + priority_list | ✅ |

---

## 关联引用

- [stage-card-protocol.md](state-card-protocol.md) — 状态卡流转
- [common-iron-rules.md](common-iron-rules.md) — Article XII workflow discipline
- [ask-question-anti-patterns.md](ask-question-anti-patterns.md) — AskUserQuestion 反模式
- V10 来源（开发期，已蒸馏）：见 V11 references 与 anti-patterns
