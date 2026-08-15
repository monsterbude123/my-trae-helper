# 反例 V10-battle-tested — Stage 1 Spec 实战蒸馏(V11.2 NEW)

> V10 实战蒸馏的 Stage 1 Spec 专项反例集。区别于现有 3 条"理论分类"反例(INV 凭空 / Clarify 跳过 / Spec 写实施),本文件聚焦"主流程走完但状态卡/产物仍漏字段"等系统性缺陷。
>
> **来源**:V10.10-V10.16 实战 casebook(已蒸馏到 V11 references)+ 03-test-plan / 04-spec 自检报告(2026-08-12 / 2026-08-15)实战案例。

---

## 反例 4:Spec 写完不刷 updated_at(腐烂点 16 触发)

**违反**:铁律 12(DOC HONEST)+ state-card-stage1-fields.md §2 强约束(updated_at 必刷新 24h 阈值)
**严重度**:P1(直接导致腐烂点 16 状态卡陈旧警报 + Stage 4 Review 质疑式校验触发 Article V 不通过)

### 现象

```markdown
# 状态卡(反例版本)
updated_at: 2026-08-12T10:00:00
current_stage: 1/spec
stage_status: completed
stage_ended_at: 2026-08-12T10:00:00
# ↑ updated_at 与 stage_ended_at 一致 = 24h 后腐烂点 16 触发
```

**识别信号**:
- 状态卡 `updated_at` 距今 > 24h 但 `stage_status: completed`
- Stage 4 Review 跑 proactive-scan.py 报"状态卡陈旧"
- 主上下文读状态卡无法判断"是真的完成还是遗留数据"

### 根因

- **认知维度**:把"status card update"当成"一次性写入",而非"持续维护"
- **流程维度**:跳过 state-card-stage1-fields.md §3 Step 6.5 反腐烂点 16 自检
- **责任维度**:主上下文未在 Stage 1 完成后立即刷 updated_at

### 教训

- **V11 实战**:spec.md 写完后主上下文没跑 state-card-validator.py,24h 后 rot-scan 触发"状态卡陈旧"警报 → 用户问"Spec 写完了吗" → 主上下文答"写完了" → 翻状态卡发现 updated_at 是 36h 前 → 失信腐烂(腐烂点 12)
- **真实场景**:Stage 1 Spec 完成后用户放 2 天度假,回来看 updated_at 是 60h 前 → rot-scan 报腐烂点 16 + 腐烂点 12 → 必须立刻刷新

### 正确替代

```yaml
# ✅ 正确:Stage 1 完成时立即刷 updated_at(腐烂点 16 阈值 24h)

stage_ended_at: 2026-08-15T00:30:00  # 实际完成时间
updated_at: 2026-08-15T00:30:00       # ← 与 stage_ended_at 一致
updated_by: spec-writer                # 或 sub-agent name
```

```bash
# 强制校验:Stage 1 完成后立即跑
python ~/.trae-cn/skills/fullstack4TraeV11/scripts/state-card-validator.py \
  docs/specs/changes/{change-id}/.state-card.md
# → 必须 PASS,且 updated_at 与 stage_ended_at 一致
```

---

## 反例 5:e2e_count / inv_count 字段填"诚实数字"而非"最低门槛"

**违反**:铁律 2-3(E2E ≥ 2 + INV ≥ 1)+ state-card-stage1-fields.md §2 强约束
**严重度**:P2(数值漂移,但 Stage 4 Review 必查)

### 现象

```yaml
# 状态卡(反例版本)
e2e_count: 2   # ← 实际写 3 个 E2E,只填最低门槛
inv_count: 1   # ← 实际写 4 个 INV,只填最低门槛
# ↑ 数值漂移 = spec.md 写 3 E2E + 4 INV,但状态卡写 2 + 1
```

**识别信号**:
- spec.md §Acceptance 含 3 个 E2E-1/E2E-2/E2E-3,但 .state-card.md `e2e_count: 2`
- spec.md §Invariants 含 4 个 INV-1/INV-2/INV-3/INV-4,但 .state-card.md `inv_count: 1`
- 主上下文 grep spec.md 数 E2E/INV,与状态卡字段对比不一致

### 根因

- **认知维度**:把 `e2e_count / inv_count` 当作"是否达标"的二值,未当作"实际计数"
- **流程维度**:跳过 state-card-stage1-fields.md §2 "≥ 2" 解读为"精确 2"
- **责任维度**:主上下文未在 Stage 1 完成时 grep spec.md 实际数

### 教训

- **V11 实战**:状态卡 `e2e_count: 2` 但 spec.md 写 3 E2E → Stage 4 Review 追问"第 3 个 E2E 在哪" → 主上下文 grep spec.md → 发现遗漏 1 个 → 状态卡刷 → 返工 1 小时
- **真实场景**:`inv_count: 1` 但 spec.md 实际写 4 个 INV(认证 / 资金 / 数据一致性 / 业务规则)→ Stage 4 Review 4 维评分只覆盖 1 维 → 质疑式校验触发 Article XVI

### 正确替代

```yaml
# ✅ 正确:从 spec.md 实际数 grep 后填

e2e_count: 3   # grep "^- \*\*E2E-" docs/specs/changes/{id}/spec.md | wc -l
inv_count: 4   # grep "^- \*\*INV-" docs/specs/changes/{id}/spec.md | wc -l
```

```bash
# Stage 1 完成时自动提取(必走)
grep -c "^- \*\*E2E-" docs/specs/changes/{change-id}/spec.md
grep -c "^- \*\*INV-" docs/specs/changes/{change-id}/spec.md
# → 把数字填入状态卡 frontmatter
```

---

## 反例 6:gate_result.gate 字段填"已跑"而非"具体脚本名"

**违反**:state-card-stage1-fields.md §2 强约束(`gate_result.gate` 必填 `spec-validate-hook`)
**严重度**:P1(违反 Article X Evidence Mandatory:gate 脚本名是 evidence 的一部分)

### 现象

```yaml
# 状态卡(反例版本)
gate_result:
  status: PASS
  gate: "validator"           # ← 模糊
  output: "PASS"
  verified_at: 2026-08-15T00:30:00
# ↑ gate 字段填"validator"或"已验证",无法 evidence 抽检
```

**识别信号**:
- `gate_result.gate` 不等于 `spec-validate-hook`(V11 Stage 1 规定)
- Stage 4 Review 调 evidence 抽检时,找不到具体脚本日志
- 主上下文重跑 gate 脚本时,无法对比"上次跑 vs 这次跑"的输出差异

### 根因

- **认知维度**:把 `gate` 当作"标签"而非"evidence 引用"
- **流程维度**:未读 state-card-stage1-fields.md §2 强约束 L60 `gate_result.gate 必填 spec-validate-hook`
- **责任维度**:spec-writer 写状态卡时未跑真实脚本,凭印象填"已通过"

### 教训

- **V11 实战**:Stage 4 Review 调 evidence 抽检,主上下文查 `gate_result.gate: validator` → 找不到脚本名 → 询问 spec-writer → 答"我跑了 validator" → Article X Evidence Mandatory 不通过 → REJECT
- **真实场景**:gate_result.gate 填"已通过"或"已验证" → 3 个月后维护者翻状态卡,不知道 Stage 1 用什么脚本验证 → 无法回归 → 失信腐烂

### 正确替代

```yaml
# ✅ 正确:gate_result.gate 必填 spec-validate-hook(具体脚本名)

gate_result:
  status: PASS
  gate: "spec-validate-hook"   # ← 具体脚本路径
  output: "spec-validate-hook: 字段齐全 + AC ≥ 3 + INV ≥ 1 + E2E ≥ 2"
  verified_at: 2026-08-15T00:30:00   # ← 与 updated_at 一致
```

```bash
# Stage 1 完成时必跑(具体脚本名固定)
python ~/.trae-cn/skills/fullstack4TraeV11/templates/hooks/spec-validate-hook.py \
  docs/specs/changes/{change-id}/spec.md
# → exit 0 = PASS,exit 1 = FAIL
```

---

## 反例 7:next_stage.expected_inputs 缺 ac_list.md / edge_cases.md

**违反**:铁律 12(DOC HONEST)+ state-card-stage1-fields.md §2 强约束(expected_inputs 必含 3 产物)
**严重度**:P2(下游 Prototype stage-gate.py FAIL)

### 现象

```yaml
# 状态卡(反例版本)
next_stage:
  id: 1.5/prototype
  skill_name: skills/05-prototype/SKILL.md
  expected_inputs: [spec.md]    # ← 只含 spec.md,缺 ac_list + edge_cases
  prerequisites: [AC ≥ 3]
# ↑ Stage 1.5 Prototype 启动时发现 ac_list.md 缺失 → stage-gate.py FAIL
```

**识别信号**:
- Stage 1.5 Prototype stage-gate.py 报"expected_inputs 含 ac_list.md / edge_cases.md,但文件系统不存在"
- 主上下文回滚查 Stage 1 状态卡,发现 expected_inputs 只列 [spec.md]

### 根因

- **认知维度**:把 `expected_inputs` 当作"建议清单",而非"下游 stage 启动门禁"
- **流程维度**:跳过 state-card-stage1-fields.md §2 L64 "expected_inputs 必含 3 产物"
- **责任维度**:spec-writer 写 expected_inputs 时未与 Stage 1.5 Prototype SKILL.md 对齐

### 教训

- **V11 实战**:Stage 1.5 Prototype 启动 → stage-gate.py FAIL → 询问 spec-writer → 答"我只写了 spec.md" → 返工 1 天写 ac_list.md + edge_cases.md
- **真实场景**:expected_inputs 只含 [spec.md] → Stage 1.5 收到 spec.md → designer-handoff 时发现没有 AC 列表 → 自行推导 → 与 spec.md §Acceptance 不一致 → 漂移腐烂

### 正确替代

```yaml
# ✅ 正确:expected_inputs 必含 3 个产物(与 SKILL.md §关键产物对齐)

next_stage:
  id: 1.5/prototype
  skill_name: skills/05-prototype/SKILL.md
  expected_inputs: [spec.md, ac_list.md, edge_cases.md]   # ← 3 个产物
  prerequisites: [AC ≥ 3, INV ≥ 1, E2E ≥ 2, spec-validate-hook PASS]
```

```bash
# Stage 1 完成时交叉验证(必走)
ls -1 docs/specs/changes/{change-id}/{spec.md,ac_list.md,edge_cases.md}
# → 3 个文件都存在 = expected_inputs 完整
```

---

## 反例 8:stage_status=completed 但 stage_ended_at=null

**违反**:state-card-protocol.md §4.1 L199 `stage_status=completed 时 stage_ended_at 必须有值`
**严重度**:P1(state-card-validator.py FAIL + Article V Verifiable Claims 不通过)

### 现象

```yaml
# 状态卡(反例版本)
current_stage: 1/spec
stage_status: completed
stage_started_at: 2026-08-15T00:00:00
stage_ended_at: null                # ← 字段缺失
updated_at: 2026-08-15T00:30:00
# ↑ 矛盾:status=completed 但 ended_at=null
```

**识别信号**:
- state-card-validator.py 报"stage_status=completed 必须 stage_ended_at 非空"
- Stage 4 Review 调 evidence 抽检,不知道 Stage 1 实际结束时间

### 根因

- **认知维度**:把 `stage_ended_at` 当作"可选项"
- **流程维度**:跳过 state-card-protocol.md §4.1 L199 强约束
- **责任维度**:主上下文写状态卡时未强制校验

### 教训

- **V11 实战**:stage_ended_at=null 但 stage_status=completed → state-card-validator.py FAIL → Stage 4 Review 质疑式校验触发 → 询问主上下文"Stage 1 什么时候完成的" → 无法回答 → 失信腐烂
- **真实场景**:3 个月后回看 Stage 1 状态卡,不知道"完成"是哪天 → 无法做 time-tracking → 漂移腐烂

### 正确替代

```yaml
# ✅ 正确:stage_ended_at 必填,且与 updated_at 一致

stage_status: completed
stage_ended_at: 2026-08-15T00:30:00  # ← 必填
updated_at: 2026-08-15T00:30:00      # ← 与 stage_ended_at 一致
```

```bash
# state-card-validator.py 自动校验
python ~/.trae-cn/skills/fullstack4TraeV11/scripts/state-card-validator.py \
  docs/specs/changes/{change-id}/.state-card.md
# → exit 0 = PASS(包含 stage_ended_at 校验)
```

---

## 反例类型汇总(V11.2 实战蒸馏)

| 反例 | 来源 | 触发场景 |
|------|------|---------|
| 4:updated_at 不刷 | 腐烂点 16 | 24h 后 rot-scan 警报 |
| 5:e2e_count/inv_count 填最低门槛 | Stage 4 Review 质疑 | 数值漂移,Article XVI 触发 |
| 6:gate_result.gate 模糊 | Article X Evidence | evidence 抽检失败 |
| 7:expected_inputs 缺产物 | Stage 1.5 stage-gate.py FAIL | 下游启动门禁失败 |
| 8:stage_ended_at=null | state-card-validator FAIL | 状态卡自检失败 |

## Stage 4 Review 验证协议(V10-battle-tested 实战蒸馏)

```yaml
# reviewer 必走(在现有 4 维评分之上)
1. updated_at 与 stage_ended_at 一致?(反例 4 + 反例 8)
2. e2e_count 与 spec.md §Acceptance 实际 E2E 数一致?(反例 5)
3. inv_count 与 spec.md §Invariants 实际 INV 数一致?(反例 5)
4. gate_result.gate = "spec-validate-hook"?(反例 6)
5. gate_result.verified_at 与 updated_at 一致?(反例 6)
6. next_stage.expected_inputs 含 [spec.md, ac_list.md, edge_cases.md]?(反例 7)
7. 任一项 ❌ → 🛑 REJECT 状态卡,要求 spec-writer 修正后重新走 Stage 4
```

## 关联引用

- [state-card-stage1-fields.md §2 强约束](../references/state-card-stage1-fields.md) — Stage 1 状态卡 8 字段强约束
- [state-card-protocol.md §4.1 验证规则](../../../references/state-card-protocol.md) — 状态卡与文件系统交叉验证
- [腐烂点 16 状态卡陈旧](../../../references/glossary.md) — V11 反腐烂点
- [公共铁律 Article V / X / XII](../../../references/common-iron-rules.md) — 可验证声明 + Evidence Mandatory + 文档诚实