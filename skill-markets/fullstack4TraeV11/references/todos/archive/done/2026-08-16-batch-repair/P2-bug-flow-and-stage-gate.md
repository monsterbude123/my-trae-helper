# P2 — Bug Fix 流程 / repair-flow / stage-gate 实际调用

> 状态(2026-08-16 蒸馏):
> - P2-1(AUDIT-#3 visual_evidence into 4/review):**done**(子代理 B 2026-08-16 完成)
> - P2-2(AUDIT-#5 repair-flow-gate --strict + SKILL.md 串接):**done**(子代理 B 2026-08-16 完成)
> - P2-3(AUDIT-#14 pre-stage.sh stage-gate 强制调用):**in_progress** — dependent on P0-2(stage-gate.py --next-stage 已修) + 另一独立子代理改动 `templates/hooks/pre-stage.sh`(与本委派子代理不在同一上下文,边界外禁动)
>
> 当 P0-2 + pre-stage.sh 子代理 done,P2-3 自动 done。本文件 3 条。

---

## P2-1 — repair-flow-gate.py 无 Stage 6 调用

```yaml
---
id: AUDIT-#5
title: repair-flow-gate.py 加 --strict + Stage 6 SKILL.md 串接
status: done
priority: P2
discovered_at: 2026-08-16
discovered_by: 子代理 B
protocol_ref: registry/repair-flow.yaml L97-110(4 steps + terminal_condition)
              scripts/README.md L39/L54(修复流程程序化门禁)
parser_ref: scripts/repair-flow-gate.py 文件存在但只支持 --validate-only / --list-steps / --step,无 callers
fix_path: skills/12-bug-fix/SKILL.md 强制 step 1 → 4 顺序;step-4 跑前必 step 1-3 PASS
completed_at: 2026-08-16T
evidence: scripts/repair-flow-gate.py 加 --strict/--evidence-paths 参数 + P2_2_STEP_ORDER + validate_strict_evidence() + check_step_order_against_paths();skills/12-bug-fix/SKILL.md 加 Step 0 4 步流程门禁串接段;tests/unit/test_repair_flow_strict.py 16 用例全 PASS;主上下文兜底跑 --step step-4-user-confirm --strict exit 1 含清晰 6 错误
---
```

### 背景

`scripts/repair-flow-gate.py` 文件存在,支持 `--validate-only / --list-steps / --step <id>`。但 grep `repair-flow-gate.py` 在 `scripts/` 与 `templates/hooks/` 中**零调用方**。`registry/repair-flow.yaml` 定义 4 步流程 + terminal_condition,但 4 步完全是 md 文本,无机械串联。

### 协议层证据

`registry/repair-flow.yaml` L97-110:triggers + 4 steps + terminal_condition。

`scripts/README.md` L39/L54:
> 修复流程程序化门禁

### 解析层证据

```bash
$ grep -rn "repair-flow-gate.py" scripts/ templates/hooks/ skills/
# 仅 README + CHANGELOG + evolution 引用,无真正调用
```

### 影响范围

- Stage 6 bug-fix 4 步流程全是 md 文本,Step 1-4 无机械串联
- 任何 stage 直接跳到 step-4 / "完成修复"都无人拦截
- Bug 修复流程"程序化"承诺失约

### 建议路径

`services/repair-flow-gate.py` 加 `--strict` 参数;`skills/12-bug-fix/SKILL.md` Step 1/2/3/4 入口加 `python repair-flow-gate.py --step step-N --strict --evidence-path <bug>/<step>.md` 硬约束。Step-4 跑前必前 3 步 PASS,否则 `exit 1` 阻断 stage 流转。

跑真反例:

```bash
# 真反例 1:直接跑 --step step-4 但缺 step-1 → 期望 FAIL
# 真反例 2:--strict 但 step-3 的 evidence 文件不存在 → 期望 FAIL
# PASS:4 步全 evidence 文件存在 → 期望 PASS
```

---

## P2-2 — Stage 4 Review 进入时不校验 visual_evidence

```yaml
---
id: AUDIT-#3
title: state-card-validator.py 进入 4/review 时校验 visual_evidence
status: done
priority: P2
discovered_at: 2026-08-16
discovered_by: 子代理 B
protocol_ref: SKILL.md L120-130 §0.5.2(visual_evidence.status = verified 是 3.5 → 4 推进硬门槛)
              references/state-card-protocol.md L102-111(visual_evidence 子字段 + failure_action)
parser_ref: scripts/state-card-validator.py L121-130(仅在 current_stage == 3.5/real-verify / 3 + completed)
fix_path: scripts/state-card-validator.py L121 扩 current_stage == "4/review" 也校验
---
```

### 背景

SKILL.md §0.5.2 明确"visual_evidence.status = verified 是 Stage 3.5 → 4 推进硬门槛",但 validator 只在 `current_stage == "3.5/real-verify"` 或 `(3/implement, completed)` 时校验。进入 `4/review` 时不校验 → 错过了"3.5 已 verified 仍能进入 4" 的实际进入校验。

### 协议层证据

`SKILL.md` L120-130:
> V11.2 visual_evidence.status = verified 是 Stage 3.5 → 4 推进硬门槛

`state-card-protocol.md` L102-111:`failure_action: "FAIL → revert stage_status to in_progress"`

### 解析层证据

`scripts/state-card-validator.py` L121-130:
```python
if current_stage == "3.5/real-verify" or (current_stage == "3/implement" and stage_status == "completed"):
    ve = fields.get("visual_evidence", {})
    ve_status = ve.get("status", "missing") if isinstance(ve, dict) else "missing"
    if ve_status != "verified":
        errors.append(...)
```

只检查 3.5 + 3 进入点,缺 4 进入点。

### 影响范围

- 进入 4/review 时未校验 visual_evidence 已经 verified
- Stage 4 Reviewer 实际可能拿到没有 visual_evidence 的状态卡,违反 §3.7 #8(评审疏漏)

### 建议路径

`scripts/state-card-validator.py` L123 改为:

```python
if current_stage in ("3.5/real-verify", "4/review") or (current_stage == "3/implement" and stage_status == "completed"):
    ve_status = ...
    if ve_status != "verified":
        errors.append(...)
```

---

## P2-3 — stage-gate.py 是 13 stage 通用入口但无人调用

```yaml
---
id: AUDIT-#14
title: templates/hooks/pre-stage.sh 强制调用 stage-gate.py
status: done
priority: P2
discovered_at: 2026-08-16
discovered_by: 子代理 B
protocol_ref: SKILL.md L213-218(Stage 子层阶段门禁)
              scripts/README.md L18(stage-gate.py 所有 stage 切换前必跑)
parser_ref: grep `stage-gate.py --state-card\|subprocess.*stage-gate` 在 scripts/ + templates/hooks/ 中零命中
fix_path: templates/hooks/pre-stage.sh 加 stage-gate.py 强制调用
resolved_at: 2026-08-16T23:59
resolved_by: V11.8.6 主上下文落地
evidence:
  - templates/hooks/pre-stage.sh L137-171 Step 3 真调用 stage-gate.py --state-card --project-root + EXPECTED_NEXT_STAGE 时加 --next-stage
  - V11.8.6 commit `06269ae` V12 physical rollout 6 步落地
  - templates/hooks/pre-stage.sh V12.0.0 L173-201 Step 3.5 process-layer-guard.sh 物理路径校验
---
```

### 背景

`scripts/stage-gate.py` 是 V11 §0.1.2 阶段门禁的官方实现,但 `templates/hooks/pre-stage.sh` / `post-stage.sh` 都没调用它。hooks-fidelity.py 校验 hook 存在 ≠ 校验 hook 内容含 stage-gate 调用。

### 协议层证据

`SKILL.md` L213-218 §0.1.2:Stage 子层 (pre-stage / post-stage / pre-accept) 必须先跑 stage-gate。

### 解析层证据

```bash
$ grep -rn "stage-gate.py --state-card\|subprocess.*stage-gate" scripts/ templates/hooks/
# 零命中
```

### 影响范围

- Stage 切换前没有任何脚本阻断
- §3.7 #4 阶段门禁放水反例(主上下文看到 "Stage 3 implementer 已返回" → 直接放行 3.5)

### 建议路径

`templates/hooks/pre-stage.sh` 加:

```bash
python "$V11_SCRIPTS/stage-gate.py" \
    --state-card "${STATE_CARD:-docs/specs/.state-card.md}" \
    --stage "${EXPECTED_STAGE:-}" \
    || { echo "🛑 stage-gate FAIL — 阻断 stage 切换"; exit 1; }
```

跑真反例:`pre-stage.sh EXPECTED_STAGE=99/illegal docs/specs/.fake-card.md` 应 exit 1。

---

## P2-3 状态:dependent on P0-2 + pre-stage.sh sub-agent;ready for both

> **2026-08-16 子代理 B 蒸馏结论**:
>
> P2-3 的原始修复点 `templates/hooks/pre-stage.sh` 是**边界外文件**(本委派子代理的 forbidden 清单里)。按 P2-3 任务委派头部要求,本子代理**不重复做**实际代码改动,只写依赖说明给主上下文兜底识别用。

### 依赖关系

| 依赖项 | 状态 | 触发 |
|--------|------|------|
| **P0-2 stage-gate.py --next-stage** | **done**(P0-2 子代理 2026-08-16 已完成) | `scripts/stage-gate.py` 已加 `--next-stage` / `--registry-dir` / `--project-root` / `validate_transition()` 串接 |
| **pre-stage.sh 加 stage-gate.py 强制调用** | **in_progress**(另一独立子代理在改) | 边界外文件,本委派子代理禁动 |
| **P2-3 done 自动触发** | conditional | 当 P0-2 + pre-stage.sh 子代理两者都 done,P2-3 自动 done |

### P2-3 done 判定标准(主上下文兜底验证)

```bash
# 1. 验证 stage-gate.py --next-stage 已就绪
python scripts/stage-gate.py --state-card <card> --next-stage 4.5/rot-scan
# 期望:exit 0(PASS) 或 2(N/A,无 card),不能 exit 1(说明 P0-2 没修)

# 2. 验证 pre-stage.sh 含 stage-gate.py 强制调用
grep -n "stage-gate.py" templates/hooks/pre-stage.sh
# 期望:命中 1+ 次(不在 README/CHANGELOG,而在 shell 主体)

# 3. 真反例:pre-stage.sh 跑非法 stage 应 exit 1
EXPECTED_STAGE=99/illegal bash templates/hooks/pre-stage.sh docs/specs/.fake-card.md
# 期望:exit 1
```

### 状态卡校验联动

P2-3 涉及 `pre-stage.sh` 与 `scripts/stage-gate.py` 联动,完成后也建议在
`scripts/state-card-validator.py` 加一个 "informational" 提示:状态卡文件中
`current_stage` 切换前必含 `gate_result.status` 已记录 "stage-gate" 调用结果。
当前未实装,留作 future 迭代项(本子代理本次不做)。

### status

- **status: in_progress**(已切到 `in_progress` 而非 `pending`)
- **discovered_by: 子代理 B**
- **expected_owner: pre-stage.sh 子代理**(不在本委派边界)
- **done auto-trigger**: P0-2 已完成 + pre-stage.sh 子代理提交后,主上下文可手动切 `done`

