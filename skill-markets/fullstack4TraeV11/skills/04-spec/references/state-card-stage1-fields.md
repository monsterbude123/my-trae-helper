# Stage 1 Spec 状态卡字段约束（V12.0.0 NEW — 主版本升级后强制多卡模式）

> **V12.0.0+ 设计入口**: [AC 核销门禁](../../../skills/09-review/SKILL.md) · [贾维斯门禁守护](../../../skills/00-boot/SKILL.md) · 评分制废除 → 门禁制 · 详见 [CHANGELOG.md V12.0.0](../../../CHANGELOG.md)


> 04-spec 完成时,V12 多卡模式下 Stage 1 状态卡 (`stage/1/spec/.state-card.md`) 必含以下字段,缺一即对应 stage 卡不完整。
>
> 完整协议见 [state-card-protocol.md §二](../../../references/state-card-protocol.md) + [references/state-card-protocol.md §三 必更新场景](../../../references/state-card-protocol.md)。

## §1 V12 多卡模式 Stage 1 状态卡路径

**位置(V12 多卡强制)**: `docs/specs/changes/{change-id}/stage/1/spec/.state-card.md`

**项目级副本(V12 多卡强制)**: `docs/specs/changes/{change-id}/fact/.state-card.md`(只读)

**V11 单卡路径(已废,不得新增)**: `docs/specs/changes/{change-id}/.state-card.md`

## §2 必含字段(Stage 1 完成时,V12 多卡语义)

```yaml
---
card_type: change                          # 必填
card_id: "{YYYY-MM-DD}-{slug}"              # 必填
version: "1.0.0"
current_stage: "1/spec"                     # Stage 1 Spec 完成时 = 1/spec
stage_status: "completed"                  # 完成时必为 completed
stage_started_at: "{ISO 8601}"             # Stage 1 启动时间
stage_ended_at: "{ISO 8601}"               # Stage 1 完成时间(本次刷新)
updated_at: "{ISO 8601}"                   # ← 必刷新(V12 多卡语义下每 stage 卡独立维护 updated_at)
updated_by: "{agent-name}"                 # 必填(主上下文 / sub-agent)
health: "🟢 on-track"                       # 异常时降级为 🟡 / 🔴
artifacts:                                  # Stage 1 必产物(V12 fact/ 物理布局)
  - path: docs/specs/changes/{id}/fact/spec.md
    type: file
    exists: true
    evidence: "Stage 1 spec.md 完成"
  - path: docs/specs/changes/{id}/fact/ac_list.md
    type: file
    exists: true
    evidence: "AC 提取完成"
  - path: docs/specs/changes/{id}/fact/edge_cases.md
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
  expected_inputs: [fact/spec.md, fact/ac_list.md, fact/edge_cases.md]   # 必含 3 产物(V12 fact/ 路径)
  prerequisites: ["AC ≥ 3", "INV ≥ 1", "E2E ≥ 2", "spec-validate-hook PASS"]
handoff_out:                                 # V12 NEW — 桥接到下 stage
  next: "1.5/prototype"
  note: "spec 提取完成,可启动 prototype 流程"
blocked_by: null
actor: 主上下文
duration_minutes: N
notes: |
  Stage 1 Spec 完成:
    - enhanced acceptance 规则验证 PASS
    - clarify ≥ 2 轮协议完成
    - fact/spec.md INV ≥ 1 + E2E ≥ 2
---
```

## §3 Stage 1 特有字段(强约束,V12 多卡语义)

| 字段 | 强约束 | 反例 |
|------|-------|------|
| `updated_at` | Stage 1 完成时**必刷新**(本 stage 卡独立维护,无跨 stage 陈旧阈值) | V11 单卡时代的"24h 腐烂点 16"概念在 V12 多卡下失效 — V12 单 stage 卡完成即刷,不跨 stage 维护 |
| `artifacts` | 必含 `fact/spec.md` + `fact/ac_list.md` + `fact/edge_cases.md` | 缺 `fact/ac_list.md` = 下游 Prototype 漂移风险 |
| `gate_result.gate` | 必填 `spec-validate-hook` | 缺失 = 不可信验收(违反 Article X Evidence Mandatory) |
| `gate_result.verified_at` | 与 `updated_at` 一致 | 不一致 = 状态卡伪造时间戳 |
| `next_stage.id` | 必填 `1.5/prototype` | 填错 stage id = 下游 stage-gate.py FAIL |
| `next_stage.expected_inputs` | 必含 3 个产物路径(V12 `fact/` 路径) | 缺 ac_list/edge_cases = 下游 stage 收不到结构化 AC |
| `e2e_count` | Stage 1 特有,≥ 2(从 AC 提取) | < 2 = 不满足 Enhanced Acceptance 规则 |
| `inv_count` | Stage 1 特有,≥ 1(从 INV 提取) | 0 = spec.md 缺不变量描述 |
| `handoff_out.next` | V12 NEW,必填 `1.5/prototype`(下游 stage 名) | 缺失 = 下游 stage 启动门禁收不到桥接信息 |

> **e2e_count + inv_count 是 Stage 1 特有字段**,其他 stage 不使用。其他 stage 字段详见各自 stage 的 references/state-card-stageN-fields.md(V12 每 stage 一自检)。

## §4 V12 步骤 6 子步骤(替代 SKILL.md §骨架流程 Step 6 的粗粒度描述)

```
6.1 写 Stage 1 状态卡 (V12 多卡):
    路径: stage/1/spec/.state-card.md
    current_stage = "1/spec"
    stage_status = "completed"
    stage_ended_at = {ISO 8601} (本次)
    updated_at = {ISO 8601} (本次)
    artifacts 必含 fact/spec.md + fact/ac_list.md + fact/edge_cases.md
    gate_result = { status: "PASS", gate: "spec-validate-hook", ... }
    next_stage = { id: "1.5/prototype", expected_inputs: [...], ... }
    handoff_out = { next: "1.5/prototype", note: "..." }
    e2e_count + inv_count 填实际值

6.2 刷新 updated_at + updated_by:
    updated_at = {ISO 8601}
    updated_by = {agent-name}

6.3 设 next_stage = 1.5/prototype:
    next_stage.id = "1.5/prototype"
    next_stage.expected_inputs = [fact/spec.md, fact/ac_list.md, fact/edge_cases.md]

6.4 写 handoff-out.md (V12 NEW):
    stage/1/spec/handoff-out.md
    必含 ≤200 字给下 stage 的摘要

6.5 跑 validator:
    python ../../scripts/state-card-validator.py stage/1/spec/.state-card.md
    → 必须 PASS
```

## §5 反例(V12 多卡语义)

| 场景 | 触发 | 反 V12 行动 |
|------|------|------------|
| A: Stage 1 完成未刷 updated_at | `stage/1/spec/.state-card.md` 的 `updated_at` 缺失 | V12 单 stage 卡独立维护,缺 `updated_at` = 立即补(V12 无跨 stage 陈旧阈值) |
| B: artifacts 缺 `fact/ac_list.md` | next_stage.expected_inputs 含 ac_list 但 artifacts 不含 | 下游 Prototype stage-gate.py FAIL |
| C: gate_result 缺 verified_at | gate_result.status=PASS 但 verified_at=null | 失信腐烂 |
| D: next_stage.id 拼写错 | next_stage.id="2/contract" 而非 "1.5/prototype" | stage-gate.py FAIL(7 stage 编号唯一) |
| E: V11 单卡路径复活 | `docs/specs/changes/{id}/.state-card.md`(整张卡塞 13 stage) | V12.0.0 永久废弃,V12 必走多卡 = 🛑 REJECT |

## §6 关联引用

- [state-card-protocol.md §二](../../../references/state-card-protocol.md) — 完整字段定义(V12 多卡)
- [state-card-protocol.md §三](../../../references/state-card-protocol.md) — 必更新场景
- [state-card-protocol.md §10](../../../references/state-card-protocol.md) — V12 多卡 vs 单卡对比
- [stage-interaction-protocol.md §V12 各 stage 移交约定](../../../references/stage-interaction-protocol.md) — 产物清单
- [stage-physical-isolation.md §2](../../../references/stage-physical-isolation.md) — V12 物理隔离规范
- [../../references/common-iron-rules.md Article XII](../../../references/common-iron-rules.md) — 文档诚实铁律