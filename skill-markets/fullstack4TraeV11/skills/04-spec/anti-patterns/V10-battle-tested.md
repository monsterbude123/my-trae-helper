# 反例 V10-battle-tested — Stage 1 Spec 实战蒸馏(V12.0.0 NEW — V12 多卡语义)

> **V12.0.0+ 设计入口**: [AC 核销门禁](../skills/09-review/SKILL.md) · [贾维斯门禁守护](../skills/00-boot/SKILL.md) · 评分制废除 → 门禁制 · 详见 [CHANGELOG.md V12.0.0](../CHANGELOG.md)


> V10 实战蒸馏的 Stage 1 Spec 专项反例集。区别于现有 3 条"理论分类"反例(INV 凭空 / Clarify 跳过 / Spec 写实施),本文件聚焦"主流程走完但状态卡/产物仍漏字段"等系统性缺陷。
>
> **来源**:V10.10-V10.16 实战 casebook(已蒸馏到 V12 references)+ 03-test-plan / 04-spec 自检报告(2026-08-12 / 2026-08-15)实战案例。
>
> **V12.0.0 UPDATE**: V12 多卡语义下,反例 4/5/7 改写为 V12 版(原 V11 单卡概念失效);反例 6/8 保留(V12 仍适用)。

---

## 反例 4:Spec 写完不刷 updated_at(V12 多卡语义 — Stage 1 卡独立维护)

**违反**:铁律 12(DOC HONEST)+ state-card-stage1-fields.md §2 强约束(updated_at 必刷新)
**严重度**:P1(Stage 1 卡缺 updated_at = 主上下文无法判断"是真完成还是遗留数据")

### 现象(V12 多卡)

```markdown
# 状态卡(V12 反例版本)
路径: docs/specs/changes/{id}/stage/1/spec/.state-card.md
current_stage: 1/spec
stage_status: completed
stage_ended_at: 2026-08-15T00:30:00
# ↑ updated_at 字段缺失,V12 多卡下本 stage 卡必须独立维护 updated_at
```

**识别信号**:
- `stage/1/spec/.state-card.md` 缺 `updated_at` 字段
- Stage 4 Review 跑 proactive-scan.py 报"Stage 1 卡陈旧"
- 主上下文读 Stage 1 卡无法判断"是真的完成还是遗留数据"

### 根因

- **认知维度**:把"status card update"当成"一次性写入",而非"持续维护"
- **流程维度**:跳过 state-card-stage1-fields.md §4 Step 6.2 updated_at 刷新
- **责任维度**:主上下文未在 Stage 1 完成后立即刷 updated_at

### V12 多卡 vs V11 单卡差异

| 维度 | V11 单卡(已废) | V12 多卡 |
|------|---------------|---------|
| 陈旧检测 | 24h 跨 stage 阈值(`腐烂点 16`) | 每 stage 卡独立维护,V12 **无跨 stage 陈旧阈值** |
| 必刷字段 | 单卡的 `updated_at` | 每 stage 卡的 `updated_at`(Stage 1 = `stage/1/spec/.state-card.md`) |
| 检测方式 | 跨 stage 时间差 | 字段缺失即反例 |

### 教训

- **V12 实战**:spec.md 写完后主上下文没跑 state-card-validator.py → Stage 1 卡缺 `updated_at` → Stage 4 Review 卡 stage_status 陈旧(虽然实际 V12 多卡下无 24h 阈值,但缺字段 = 不完整) → 主上下文答"已完成" → 翻 Stage 1 卡发现无 `updated_at` → 失信腐烂(腐烂点 12)
- **真实场景**:Stage 1 Spec 完成后用户放 2 天度假,回来看 Stage 1 卡 `updated_at` 缺失 → 必须立刻补刷

### 正确替代(V12)

```yaml
# ✅ 正确:V12 多卡下 Stage 1 卡独立维护 updated_at
路径: stage/1/spec/.state-card.md

stage_ended_at: 2026-08-15T00:30:00  # 实际完成时间
updated_at: 2026-08-15T00:30:00       # ← 与 stage_ended_at 一致(V12 多卡独立维护)
updated_by: spec-writer                # 或 sub-agent name
```

```bash
# 强制校验:V12 多卡下 Stage 1 卡
required
# → 必须 PASS,且 updated_at 与 stage_ended_at 一致
```

---

## 反例 5:e2e_count / inv_count 字段填"诚实数字"而非"最低门槛"(V12 多卡)

**违反**:铁律 2-3(E2E ≥ 2 + INV ≥ 1)+ state-card-stage1-fields.md §3 强约束
**严重度**:P2(数值漂移,但 Stage 4 Review 必查)

### 现象

```yaml
# 状态卡(反例版本)
e2e_count: 2   # ← 实际写 3 个 E2E,只填最低门槛
inv_count: 1   # ← 实际写 4 个 INV,只填最低门槛
# ↑ 数值漂移 = spec.md 写 3 E2E + 4 INV,但状态卡写 2 + 1
```

**识别信号**:
- `fact/spec.md` §Acceptance 含 3 个 E2E-1/E2E-2/E2E-3,但 `stage/1/spec/.state-card.md` `e2e_count: 2`
- `fact/spec.md` §Invariants 含 4 个 INV-1/INV-2/INV-3/INV-4,但 `stage/1/spec/.state-card.md` `inv_count: 1`
- 主上下文 grep `fact/spec.md` 数 E2E/INV,与 Stage 1 卡字段对比不一致

### 根因

- **认知维度**:把 `e2e_count / inv_count` 当作"是否达标"的二值,未当作"实际计数"
- **流程维度**:跳过 state-card-stage1-fields.md §3 "≥ 2" 解读为"精确 2"
- **责任维度**:主上下文未在 Stage 1 完成时 grep spec.md 实际数

### V12 多卡字段语义(V12.0.0 NEW)

- `e2e_count` / `inv_count` 是 **V12 Stage 1 特有字段**,落 `stage/1/spec/.state-card.md`
- 其他 stage 卡(V12 13 stage 各自独立卡)**不**含这两个字段
- 字段语义 = "实际计数",非"达标二值"
- Stage 1.5 prototype 卡含 `component_count` 等 prototype 特有字段(各自定义)

### 教训

- **V12 实战**:Stage 1 卡 `e2e_count: 2` 但 `fact/spec.md` 写 3 E2E → Stage 4 Review 追问"第 3 个 E2E 在哪" → 主上下文 grep `fact/spec.md` → 发现遗漏 1 个 → Stage 1 卡刷 → 返工 1 小时
- **真实场景**:`inv_count: 1` 但 `fact/spec.md` 实际写 4 个 INV(认证 / 资金 / 数据一致性 / 业务规则)→ Stage 4 Review 4 维评分只覆盖 1 维 → 质疑式校验触发 Article XVI

### 正确替代(V12)

```yaml
# ✅ 正确:V12 多卡 Stage 1 卡从 fact/spec.md 实际数 grep 后填

e2e_count: 3   # grep "^- \*\*E2E-" docs/specs/changes/{id}/fact/spec.md | wc -l
inv_count: 4   # grep "^- \*\*INV-" docs/specs/changes/{id}/fact/spec.md | wc -l
```

```bash
# Stage 1 完成时自动提取(必走,V12 fact/ 路径)
grep -c "^- \*\*E2E-" docs/specs/changes/{change-id}/fact/spec.md
grep -c "^- \*\*INV-" docs/specs/changes/{change-id}/fact/spec.md
# → 把数字填入 stage/1/spec/.state-card.md
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
- `gate_result.gate` 不等于 `spec-validate-hook`(V11/V12 Stage 1 规定)
- Stage 4 Review 调 evidence 抽检时,找不到具体脚本日志
- 主上下文重跑 gate 脚本时,无法对比"上次跑 vs 这次跑"的输出差异

### 根因

- **认知维度**:把 `gate` 当作"标签"而非"evidence 引用"
- **流程维度**:未读 state-card-stage1-fields.md §2 强约束 L60 `gate_result.gate 必填 spec-validate-hook`
- **责任维度**:spec-writer 写状态卡时未跑真实脚本,凭印象填"已通过"

### 教训

- **V11/V12 实战**:Stage 4 Review 调 evidence 抽检,主上下文查 `gate_result.gate: validator` → 找不到脚本名 → 询问 spec-writer → 答"我跑了 validator" → Article X Evidence Mandatory 不通过 → REJECT
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
  docs/specs/changes/{change-id}/fact/spec.md
# → exit 0 = PASS,exit 1 = FAIL
```

---

## 反例 7:next_stage.expected_inputs 缺 ac_list.md / edge_cases.md(V12 多卡 — handoff-in 替代)

**违反**:铁律 12(DOC HONEST)+ state-card-stage1-fields.md §2 强约束(expected_inputs 必含 3 产物)
**严重度**:P2(下游 Prototype stage-gate.py FAIL)

### 现象(V12 多卡)

```yaml
# 状态卡(反例版本,V12 多卡路径)
路径: stage/1/spec/.state-card.md
next_stage:
  id: 1.5/prototype
  skill_name: skills/05-prototype/SKILL.md
  expected_inputs: [fact/spec.md]    # ← 只含 spec.md,缺 ac_list + edge_cases
  prerequisites: [AC ≥ 3]
# ↑ Stage 1.5 Prototype 启动时发现 fact/ac_list.md 缺失 → stage-gate.py FAIL
```

**V12 handoff-out 必填字段(V12.0.0 NEW)**

```yaml
# V12 多卡语义下,Stage 1.5 启动门禁 = next_stage.expected_inputs + handoff-out.md
# 缺 handoff-out.md → 下游 stage 启动门禁 FAIL
路径: stage/1/spec/handoff-out.md
# 必含 ≤200 字摘要 + 链接到 fact/spec.md / fact/ac_list.md / fact/edge_cases.md
```

**识别信号**:
- Stage 1.5 Prototype stage-gate.py 报"expected_inputs 含 `fact/ac_list.md` / `fact/edge_cases.md`,但文件系统不存在"
- `stage/1/spec/handoff-out.md` 缺失或 < 50 字
- 主上下文回滚查 Stage 1 状态卡,发现 expected_inputs 只列 `[fact/spec.md]`

### 根因

- **认知维度**:把 `expected_inputs` 当作"建议清单",而非"下游 stage 启动门禁"
- **流程维度**:跳过 state-card-stage1-fields.md §2 L64 "expected_inputs 必含 3 产物"
- **V12 新责任**:未写 `handoff-out.md`(V12 桥接文件,V11 不存在)
- **责任维度**:spec-writer 写 expected_inputs 时未与 Stage 1.5 Prototype SKILL.md 对齐

### 教训

- **V12 实战**:Stage 1.5 Prototype 启动 → stage-gate.py FAIL → 询问 spec-writer → 答"我只写了 fact/spec.md" → 返工 1 天写 `fact/ac_list.md` + `fact/edge_cases.md` + `stage/1/spec/handoff-out.md`
- **真实场景**:expected_inputs 只含 `[fact/spec.md]` + handoff-out.md 缺失 → Stage 1.5 收到 spec.md → designer-handoff 时发现没有 AC 列表 → 自行推导 → 与 `fact/spec.md` §Acceptance 不一致 → 漂移腐烂

### 正确替代(V12 多卡)

```yaml
# ✅ 正确:V12 多卡 Stage 1 卡 + handoff-out.md 桥接
# 1. stage/1/spec/.state-card.md
next_stage:
  id: 1.5/prototype
  skill_name: skills/05-prototype/SKILL.md
  expected_inputs: [fact/spec.md, fact/ac_list.md, fact/edge_cases.md]   # ← 3 个产物
  prerequisites: [AC ≥ 3, INV ≥ 1, E2E ≥ 2, spec-validate-hook PASS]
handoff_out:
  next: "1.5/prototype"
  note: "Stage 1 spec 提取完成,3 产物齐全,可启动 prototype"
```

```bash
# Stage 1 完成时交叉验证(V12 多卡 + fact/ 路径)
ls -1 docs/specs/changes/{change-id}/fact/{spec.md,ac_list.md,edge_cases.md}
ls -1 docs/specs/changes/{change-id}/stage/1/spec/handoff-out.md
# → 3 个 fact/ 文件 + 1 个 handoff-out.md = 下游 stage 启动门禁完整
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

- **V11/V12 实战**:stage_ended_at=null 但 stage_status=completed → state-card-validator.py FAIL → Stage 4 Review 质疑式校验触发 → 询问主上下文"Stage 1 什么时候完成的" → 无法回答 → 失信腐烂
- **真实场景**:3 个月后回看 Stage 1 状态卡,不知道"完成"是哪天 → 无法做 time-tracking → 漂移腐烂

### 正确替代

```yaml
# ✅ 正确:stage_ended_at 必填,且与 updated_at 一致

stage_status: completed
stage_ended_at: 2026-08-15T00:30:00  # ← 必填
updated_at: 2026-08-15T00:30:00      # ← 与 stage_ended_at 一致
```

```bash
# state-card-validator.py 自动校验(V12 多卡路径)
python ~/.trae-cn/skills/fullstack4TraeV11/scripts/state-card-validator.py \
  stage/1/spec/.state-card.md
# → exit 0 = PASS(包含 stage_ended_at 校验)
```

---

## 反例类型汇总(V12 多卡语义)

| 反例 | V11 单卡 → V12 多卡差异 | 触发场景 |
|------|--------------------------|----------|
| 4:updated_at 不刷 | V11 24h 阈值 → V12 字段缺失即反例 | Stage 1 卡缺 `updated_at` = 反例 |
| 5:e2e_count/inv_count 填最低门槛 | 同(Stage 1 卡字段) | 数值漂移,Article XVI 触发 |
| 6:gate_result.gate 模糊 | 同(V12 仍适用) | evidence 抽检失败 |
| 7:expected_inputs 缺产物 + handoff-out.md 缺失 | V11 单卡 → V12 多卡 + handoff-out.md 桥接 | 下游启动门禁失败 |
| 8:stage_ended_at=null | 同(V12 仍适用) | 状态卡自检失败 |

## Stage 4 Review 验证协议(V10-battle-tested 实战蒸馏,V12 多卡版)

```yaml
# reviewer 必走(在现有 4 维评分之上,V12 多卡校验)
1. updated_at 与 stage_ended_at 一致?(反例 4 + 反例 8)
2. e2e_count 与 fact/spec.md §Acceptance 实际 E2E 数一致?(反例 5)
3. inv_count 与 fact/spec.md §Invariants 实际 INV 数一致?(反例 5)
4. gate_result.gate = "spec-validate-hook"?(反例 6)
5. gate_result.verified_at 与 updated_at 一致?(反例 6)
6. next_stage.expected_inputs 含 [fact/spec.md, fact/ac_list.md, fact/edge_cases.md]?(反例 7)
7. stage/1/spec/handoff-out.md 存在且 ≥50 字?(反例 7 V12 NEW)
8. 任一项 ❌ → 🛑 REJECT 状态卡,要求 spec-writer 修正后重新走 Stage 4
```

## 关联引用

- [state-card-stage1-fields.md §2 强约束](../references/state-card-stage1-fields.md) — Stage 1 状态卡 8 字段强约束(V12 多卡)
- [state-card-protocol.md §4.1 验证规则](../../../references/state-card-protocol.md) — 状态卡与文件系统交叉验证(V12 多卡)
- [state-card-protocol.md §10 V12 多卡对比](../../../references/state-card-protocol.md) — V12 多卡 vs V11 单卡
- 腐烂点 16 状态卡陈旧 — V12 多卡下该反例改写(无跨 stage 阈值,字段缺失即反例)
- 公共铁律 Article V / X / XII — 可验证声明 + Evidence Mandatory + 文档诚实