# Stage 1 Spec 状态卡字段约束(V11.2 NEW — 蒸馏自 04-spec 自检报告)

> 04-spec 完成时,change 级状态卡 (`docs/specs/changes/{id}/.state-card.md`) 必含以下字段,缺一即腐烂点 16 状态卡陈旧。
>
> 完整协议见 [state-card-protocol.md §二](../../references/state-card-protocol.md) + [references/state-card-protocol.md §三 必更新场景](../../references/state-card-protocol.md)。

## §1 必含字段(Stage 1 完成时)

```yaml
---
card_type: change                          # 必填
card_id: "{YYYY-MM-DD}-{slug}"              # 必填
version: "1.0.0"
current_stage: "1/spec"                     # Stage 1 Spec 完成时 = 1/spec
stage_status: "completed"                  # 完成时必为 completed
stage_started_at: "{ISO 8601}"             # Stage 1 启动时间
stage_ended_at: "{ISO 8601}"               # Stage 1 完成时间(本次刷新)
updated_at: "{ISO 8601}"                   # ← 必刷新(腐烂点 16 阈值 24h)
updated_by: "{agent-name}"                 # 必填(主上下文 / sub-agent)
health: "🟢 on-track"                       # 异常时降级为 🟡 / 🔴
artifacts:                                  # Stage 1 必产物
  - path: docs/specs/changes/{id}/spec.md
    type: file
    exists: true
    evidence: "Stage 1 spec.md 完成"
  - path: docs/specs/changes/{id}/ac_list.md
    type: file
    exists: true
    evidence: "AC 提取完成"
  - path: docs/specs/changes/{id}/edge_cases.md
    type: file
    exists: true
    evidence: "边界提取完成"
gate_result:
  status: "PASS"                            # spec-validate-hook PASS
  gate: "spec-validate-hook"
  output: "spec-validate-hook: 字段齐全 + AC ≥ 3 + INV ≥ 1 + E2E ≥ 2"
  verified_at: "{ISO 8601}"                # 与 updated_at 一致
next_stage:
  id: "1.5/prototype"
  skill_name: "skills/05-prototype/SKILL.md"
  expected_inputs: [spec.md, ac_list.md, edge_cases.md]   # 必含 3 个产物
  prerequisites: ["AC ≥ 3", "INV ≥ 1", "E2E ≥ 2", "spec-validate-hook PASS"]
blocked_by: null
actor: 主上下文
duration_minutes: N
notes: |
  Stage 1 Spec 完成:
    - enhanced acceptance 规则验证 PASS
    - clarify ≥ 2 轮协议完成
    - spec.md INV ≥ 1 + E2E ≥ 2
---
```

## §2 Stage 1 特有字段(强约束)

| 字段 | 强约束 | 反例(腐烂点 16 触发) |
|------|-------|--------------------|
| `updated_at` | Stage 1 完成时**必刷新**,阈值 24h | updated_at 比 stage_started_at 旧 = 状态卡陈旧 |
| `artifacts` | 必含 spec.md + ac_list.md + edge_cases.md | 缺 ac_list = 下游 Prototype 漂移风险 |
| `gate_result.gate` | 必填 `spec-validate-hook` | 缺失 = 不可信验收(违反 Article X Evidence Mandatory) |
| `gate_result.verified_at` | 与 updated_at 一致 | 不一致 = 状态卡伪造时间戳(腐烂点 12 失信) |
| `next_stage.id` | 必填 `1.5/prototype` | 填错 stage id = 下游 stage-gate.py FAIL |
| `next_stage.expected_inputs` | 必含 3 个产物路径 | 缺 ac_list/edge_cases = 下游 stage 收不到结构化 AC |
| `e2e_count` | Stage 1 特有,≥ 2(从 AC 提取) | < 2 = 不满足 Enhanced Acceptance 规则 |
| `inv_count` | Stage 1 特有,≥ 1(从 INV 提取) | 0 = spec.md 缺不变量描述 |

> **e2e_count + inv_count 是 Stage 1 特有字段**,其他 stage 不使用。其他 stage 字段详见各自 stage 的 references/state-card-stageN-fields.md(待逐 stage 自检后补)。

## §3 Step 6 子步骤(替代 SKILL.md §骨架流程 Step 6 的粗粒度描述)

```
6.1 写 change 级状态卡:
    current_stage = "1/spec"
    stage_status = "completed"
    stage_ended_at = {ISO 8601} (本次)
    updated_at = {ISO 8601} (本次)
    artifacts 必含 spec.md + ac_list.md + edge_cases.md
    gate_result = { status: "PASS", gate: "spec-validate-hook", ... }
    next_stage = { id: "1.5/prototype", expected_inputs: [...], ... }
    e2e_count + inv_count 填实际值

6.2 刷新 updated_at + updated_by:
    updated_at = {ISO 8601}
    updated_by = {agent-name}

6.3 设 next_stage = 1.5/prototype:
    next_stage.id = "1.5/prototype"
    next_stage.expected_inputs = [spec.md, ac_list.md, edge_cases.md]

6.4 跑 validator:
    python ../../scripts/state-card-validator.py docs/specs/changes/{id}/.state-card.md
    → 必须 PASS

6.5 反腐烂点 16 自检:
    阈值 24h: 若 updated_at 距今 > 24h,立即刷新(腐烂点 16)
```

## §4 反例(腐烂点 16 具体触发场景)

| 场景 | 触发 | 反腐烂行动 |
|------|------|-----------|
| A: Stage 1 完成未刷 updated_at | updated_at 距今 > 24h 但 stage_status=completed | rot-scan 触发腐烂点 16 警报 |
| B: artifacts 缺 ac_list | next_stage.expected_inputs 含 ac_list 但 artifacts 不含 | 下游 Prototype stage-gate.py FAIL |
| C: gate_result 缺 verified_at | gate_result.status=PASS 但 verified_at=null | 失信腐烂(腐烂点 12) |
| D: next_stage.id 拼写错 | next_stage.id="2/contract" 而非 "1.5/prototype" | stage-gate.py FAIL(7 stage 编号唯一) |

## §5 关联引用

- [state-card-protocol.md §二](../../references/state-card-protocol.md) — 完整字段定义
- [state-card-protocol.md §三](../../references/state-card-protocol.md) — 必更新场景
- [stage-interaction-protocol.md §V11 各 stage 移交约定](../../references/stage-interaction-protocol.md) — 产物清单
- [stage-card-protocol.md §必填字段](../../references/stage-card-protocol.md) — 流转规则
- [../../references/common-iron-rules.md Article XII](../../references/common-iron-rules.md) — 文档诚实铁律