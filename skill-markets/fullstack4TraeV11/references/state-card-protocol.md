# 状态卡协议

> **V11.7.0+ 设计入口**: [AC 核销门禁](../skills/09-review/SKILL.md) · [贾维斯门禁守护](../skills/00-boot/SKILL.md) · 评分制废除 → 门禁制 · 详见 [CHANGELOG.md V11.7.0](../CHANGELOG.md)


> 13 个 stage 的状态卡统一协议。状态卡是任务真相源之一，不允许说谎（Article XII）。

---

## 一、状态卡分类

> **核心区分**: V11 有两类状态卡,**职责不同,不可混用**:
> - `docs/specs/.state-card.md` = **项目级**(全局健康度 + 当前活跃 change 指针)
> - `docs/specs/changes/{change-id}/.state-card.md` = **change 级**(单个 change 的 stage 进度)
>
> **路径设计**: 项目级在 `docs/specs/` 根,change 级在 `docs/specs/changes/{id}/` 子目录。两类状态卡在不同目录,文件系统层无冲突。
>
> **类比**: 项目级 = 公司仪表盘 / change 级 = 单个项目任务卡

### 1.1 项目级状态卡

**位置**: `{project_root}/docs/specs/.state-card.md`

**作用**: 记录项目整体状态（当前活跃 change + 整体健康度 + 阻塞 + 下一步）

**生命周期**: 项目存在期间持续维护（不随 change 归档删除）

**字段重点**:
```yaml
current_change: "{change-id}"        # 当前活跃的 change（无则空）
current_stage: "{stage-name}"        # 当前活跃 change 的 stage
project_health: "green|yellow|red"   # 项目整体健康度
active_blockers: []                  # 项目级阻塞列表
next_action: "..."                   # 下一步行动
```

**谁维护**: Stage -1 Intake 初始化 / Stage 7 Project Health 更新 / 各 stage post-stage hook 同步指针

### 1.2 Change 级状态卡

**位置**: `{project_root}/docs/specs/changes/{change-id}/.state-card.md`

**作用**: 记录单个 change 的状态（当前 stage + 阶段产物 + 阶段门禁）

**生命周期**: change 启动 → Accept 归档（归档后冻结,不可改）

**字段重点**:
```yaml
change_id: "{change-id}"
stage: "{stage-name}"                 # 当前 stage（-1 到 5）
stage_status: "in_progress|done|blocked"
artifacts:                            # 本 stage 产物
  spec: "docs/specs/changes/{change-id}/spec.md"
  tests: "tests/..."
gate_result:                          # 本 stage 门禁结果
  status: "pass|fail"
  evidence: ["file:line", ...]
```

**谁维护**: 各 stage 的 post-stage hook 自动更新 / reviewer 验收时更新

### 1.3 Bug 单状态卡

**位置**: `{project_root}/docs/bugs/{bug-id}/.state-card.md`（可选）

**作用**: 记录 bug 修复进度（OPEN → CLOSED 状态机）

**生命周期**: bug 创建 → CLOSED（修复后归档）

**生命周期**: 用户反馈 → 修复 → 用户确认关闭

---

## 二、状态卡字段定义

### 2.1 必含字段（每张卡都必含）

```yaml
# === 身份 ===
card_type: {project | change | bug}
card_id: {项目名 / change-id / bug-id}
version: {语义版本号}

# === 当前状态 ===
current_stage: {stage_id}            # 如 -1/intake, 0/plan, 3.5/real-verify
stage_status: {pending | working | completed | blocked | skipped}
stage_started_at: {ISO 8601}
stage_ended_at: {ISO 8601 | null}

# === 元数据 ===
updated_at: {ISO 8601}
updated_by: {主上下文 | sub-agent name}
health: {🟢 on-track | 🟡 degraded | 🔴 blocked}

# === 产出物 ===
artifacts:
  - path: {产物路径}
    type: {file | dir | report | state-update}
    exists: {true | false}
    evidence: {file:line | 命令 | 截图}

# === 视觉证据（V11.2 NEW — Stage 3.5 → 4 硬门槛）===
visual_evidence:
  status: {verified | unverified | skipped}
  screenshots:
    - path: {截图路径}
      contains_change_components: {true | false}
      interactive_proof: {string, 如 "click folder-btn → API POST 200 → drawer opens"}
      read_by_main_context: {true | false}     # 主上下文亲自 Read PNG（禁止 AI 描述代替像素）
  verified_at: {ISO 8601 | null}
  failure_action: "FAIL → revert stage_status to in_progress + 清理虚假痕迹"

# === 门禁 ===
gate_result:
  status: {PASS | FAIL | N/A | PENDING}
  gate: {门禁脚本名}
  output: {门禁脚本输出片段}
  verified_at: {ISO 8601 | null}

# === 路由 ===
next_stage:
  id: {next stage_id}
  skill_name: {next stage skill name}
  expected_inputs: {下一 stage 需要的输入物清单}
  prerequisites: {启动前必含条件}

# === 阻塞 ===
blocked_by: {null | 5 字段阻塞报告}

# === 时间与人物 ===
actor: {主上下文 | sub-agent name}
duration_minutes: {整数}
```

### 2.2 可选字段（按需）

```yaml
# === Change 关联 ===
parent_change: {父 change id | null}
related_changes: {关联 change id 列表}

# === Bug 关联 ===
bug_id: {bug-id | null}
bug_severity: {P0 | P1 | P2 | null}

# === 评估 ===
risk_level: {LOW | MEDIUM | HIGH}
priority: {P0 | P1 | P2 | P3}

# === 备注 ===
notes: {Markdown 备注}
```

---

## 三、状态卡更新时机

### 3.1 必更新场景

| 场景 | 触发时机 | 更新字段 |
|------|---------|---------|
| 阶段启动 | Stage 进入 working | current_stage, stage_status, stage_started_at |
| 阶段产物落地 | 关键文件写入 | artifacts, updated_at |
| 阶段门禁通过 | gate PASS | gate_result, stage_status |
| 阶段门禁失败 | gate FAIL | gate_result, blocked_by |
| 阻塞发生 | 任何阶段遇到阻塞 | health=🔴, blocked_by |
| 阻塞解除 | 阻塞解决 | health=🟢/🟡, blocked_by=null |
| 阶段切换 | 进入下一 stage | current_stage, stage_ended_at, next_stage |
| 状态卡刷新 | 任何字段更新 | updated_at, updated_by |

### 3.2 自动更新机制

```yaml
# 每个 stage skill 完成后调用
post_stage:
  - shell: echo {当前时间} > {state-card updated_at}
  - python: scripts/update_state_card.py --stage {stage_id} --status {status}
```

### 3.3 手动更新机制

主上下文或 sub-agent 直接 Edit 状态卡字段，遵守：
- 必更新 `updated_at` 和 `updated_by`
- 必更新 `current_stage` 和 `stage_status`
- 必更新 `artifacts` 清单
- 必更新 `next_stage` 路由

---

## 四、状态卡与文件系统交叉验证

### 4.1 验证规则

```yaml
# 每个 stage 切换前必跑
verification:
  - rule: artifacts 列出的文件必须存在 (LS)
  - rule: gate_result.status=PASS 时 gate 脚本必须真的跑过
  - rule: blocked_by=非空时 stage 状态不能是 completed
  - rule: stage_status=completed 时 stage_ended_at 必须有值
  - rule: current_stage 必含在 13 stage 名单中
```

### 4.2 验证脚本

```bash
python scripts/state-card-validator.py {state-card.md}
# 输出: PASS / FAIL + 不一致项清单
```

### 4.3 不一致处理

```yaml
不一致项:
  - file_missing: 主上下文亲自 LS 验证 → 标记缺失 → 触发 sub-agent 修复
  - gate_lie: 检查 gate 脚本是否真跑 → 重跑 → 修正 gate_result
  - status_lie: 主上下文亲自分析 → 修正 stage_status
  - wrong_stage: 检测路由 → 重置 current_stage
```

---

## 五、状态卡模板

### 5.1 项目级

```yaml
---
card_type: project
card_id: my-project
version: "1.0.0"
current_stage: 0/plan
stage_status: working
stage_started_at: 2026-08-11T13:00:00
stage_ended_at: null
updated_at: 2026-08-11T13:30:00
updated_by: 主上下文
health: 🟢 on-track
artifacts:
  - path: docs/specs/changes/2026-08-11-add-user-auth/
    type: dir
    exists: true
    evidence: "ls 验证"
visual_evidence:                       # V11.2 NEW — Stage 3.5 → 4 硬门槛
  status: unverified
  screenshots: []
  verified_at: null
gate_result:
  status: PENDING
  gate: stage-gate.py
  output: null
  verified_at: null
next_stage:
  id: 0.5/test-plan
  skill_name: skills/03-test-plan/SKILL.md
  expected_inputs: [plan.md]
  prerequisites: [plan.md 存在]
blocked_by: null
actor: 主上下文
duration_minutes: 30
---
```

### 5.2 Change 级

```yaml
---
card_type: change
card_id: 2026-08-11-add-user-auth
version: "1.0.0"
current_stage: 3/implement
stage_status: working
stage_started_at: 2026-08-11T14:00:00
stage_ended_at: null
updated_at: 2026-08-11T15:30:00
updated_by: implementer
health: 🟢 on-track
artifacts:
  - path: docs/specs/changes/2026-08-11-add-user-auth/plan.md
    type: file
    exists: true
    evidence: "docs/specs/changes/2026-08-11-add-user-auth/plan.md:1-120"
  - path: docs/specs/changes/2026-08-11-add-user-auth/spec.md
    type: file
    exists: true
    evidence: "docs/specs/changes/2026-08-11-add-user-auth/spec.md:1-200"
  - path: docs/specs/changes/2026-08-11-add-user-auth/contracts/api-contracts.md
    type: file
    exists: true
    evidence: "docs/specs/changes/2026-08-11-add-user-auth/contracts/api-contracts.md:1-80"
visual_evidence:                       # V11.2 NEW — Stage 3.5 → 4 硬门槛
  status: unverified
  screenshots: []
  verified_at: null
gate_result:
  status: PASS
  gate: contract-gate.py
  output: "contract-gate.py: 4 件套齐全 + 测试骨架 PASS"
  verified_at: 2026-08-11T14:55:00
next_stage:
  id: 3.5/real-verify
  skill_name: skills/08-real-verify/SKILL.md
  expected_inputs: [代码 + tests/ + docs/modules/]
  prerequisites: [TDD GREEN, DRIFT CHECK ✅]
blocked_by: null
actor: implementer
duration_minutes: 90
parent_change: null
related_changes: []
risk_level: MEDIUM
priority: P1
notes: 后端 API + 前端 + DB schema 协同改动
---
```

### 5.3 Bug 单

```yaml
---
card_type: bug
card_id: settings-009-config-key-case-mismatch
version: "1.0.0"
current_stage: 6/bug-fix
stage_status: working
stage_started_at: 2026-08-11T15:00:00
stage_ended_at: null
updated_at: 2026-08-11T16:30:00
updated_by: debugger
health: 🟢 on-track
artifacts:
  - path: docs/bugs/settings-009-config-key-case-mismatch.md
    type: file
    exists: true
    evidence: "docs/bugs/settings-009-config-key-case-mismatch.md:1-150"
  - path: tests/integration/test_settings_009.py
    type: file
    exists: true
    evidence: "tests/integration/test_settings_009.py:1-30 (初始 FAIL 验证)"
gate_result:
  status: PENDING
  gate: e2e-先行
  output: "初始 FAIL 已确认"
  verified_at: 2026-08-11T15:30:00
next_stage:
  id: 6/bug-fix
  skill_name: skills/12-bug-fix/SKILL.md
  expected_inputs: [修复代码 + 回归测试 + bug 单更新]
  prerequisites: [e2e 初始 FAIL, 6 层排查完成]
blocked_by: null
actor: debugger
duration_minutes: 90
bug_id: settings-009-config-key-case-mismatch
bug_severity: P1
notes: 涉及 regex 宽松校验，需前后端契约三方同步
---
```

### §5.8 子代理擅自升级状态协议（V11.2.1 NEW — 蒸馏自 canvas-asset-folders）

> **位置说明**: 本章节按任务编号 §5.8 追加到 §5（状态卡模板）末尾，但本质是"协议"而非"模板"。后续 V11.3 重排时可考虑移到独立 §七、状态卡写入权限章节。
>
> **问题**：Round 2 implementer 完成后**未经主上下文审核**就把状态卡 `stage_status` 从 `in_progress` 改成 `completed` + `health: 🟢 healthy` — 主上下文发现后强制纠正。V11 state-card §5 强制重置协议未涵盖此场景。

**铁律**：

```
MUST: stage_status / current_stage / gate_result.status / health / next_stage.id
      这 5 个字段只能由主上下文亲自 Edit,子代理禁止直接写入。

MUST: 子代理只能在 Completion Report 中"建议"状态变更,主上下文亲自 Edit。

NEVER: implementer / reviewer / debugger 等 sub-agent 直接 Edit .state-card.md 关键字段。

NEVER: sub-agent 自动推 stage_status = completed。
```

**机械化校验**（[state-card-validator.py](../scripts/state-card-validator.py) V11.2.1 NEW）：
- 状态卡 git diff 检测：状态卡字段变更必须仅来自主上下文 Edit
- 缺审计 → 标 FAIL（V11.2.1 + 反例 §7 §8 项目级补全）

**失败处理**：
1. 立即 revert 状态卡字段
2. 委派 implementer 重做（仅输出代码 + 截图 + Completion Report,不触碰状态卡）
3. 记录到 anti-patterns/08（项目级）
4. 主上下文亲自 Edit 状态卡

**反例**：2026-08-12 canvas-asset-folders Round 2
- 当时做了: implementer 未经主上下文审核 Edit stage_status: completed + health: 🟢
- 导致后果: 虚假完成 + 主上下文需强制纠正
- 教训: 状态卡写入权是主上下文独有权限,违反者按反例 §7 §8 处理

---

## 六、状态卡反例

### 反例 1: 状态卡说谎

**现象**: 状态卡显示 `stage_status: completed`，但 `artifacts` 路径 LS 不存在。

**根因**: 维护者未亲自验证产物，只更新状态字段。

**教训**: 状态卡必须经过 state-card-validator.py 校验。

### 反例 2: 状态卡永远🟢 on-track

**现象**: 任何阶段都显示 `health: 🟢 on-track`，从不降级。

**根因**: 维护者不知道 blocked_by 字段怎么填。

**教训**: 🟡/🔴 是阻塞状态可视化机制，不用 = 失去价值。

### 反例 3: 状态卡无 next_stage

**现象**: 状态卡显示 stage=completed，但没有 next_stage 路由。

**根因**: 当前 stage 完成后未路由到下一 stage。

**教训**: 阶段切换必须包含 next_stage 字段。

### 反例 4: 状态卡无 updated_at

**现象**: 状态卡停留在初始版本，没有时间戳。

**根因**: 维护者没想到加 updated_at。

**教训**: state-card-staleness 是腐烂点 16，必须有 updated_at。

---

## 七、强制重置协议（Force Reset Protocol）

> **触发场景**: 用户明确要求"重置状态卡到 X 阶段之前 + 删除所有产物"（如 2026-08-12 canvas-asset-folders 实战）。
> **原则**: 状态卡 + 文档可重置,**代码 + 归档不可逆**(Article VIII)。

### 7.1 重置前必走 3 步

```
Step 1: 确认归档状态
  - 检查 docs/archive/done/{change-id}/ 是否有旧归档
  - 存在 → 不能删(Article VIII),但需在新状态卡 notes 标注归档路径
  - 不存在 → 跳过此步

Step 2: 确认代码状态(AskUserQuestion 必问)
  - 代码已合并到 main?
  - 方案 A: revert 旧代码 + 新 branch 重做
  - 方案 B: 保留旧代码 + 新 branch 增强
  - 方案 C: 旧代码不变 + 只重做文档/测试
  - agent 不能自决 → 用户决策

Step 3: 确认保留产物
  - 用户明确说"保留 plan.md" → 保留
  - 用户没说 → agent 用 AskUserQuestion 问
```

### 7.2 重置操作 5 步

```
1. 状态卡重置:
   - current_stage: "<target-stage>"  # 如 -1/intake
   - stage_status: "pending"
   - stage_started_at / stage_ended_at: null
   - gate_result: 清零
   - next_stage: 清空
   - artifacts: 仅留用户指定的保留产物
   - notes: 必含"FORCE RESET" 标记 + 原因 + 日期 + 保留清单 + Git 决策

2. change 级状态卡同步重置(同 change 级 `docs/specs/changes/{change-id}/.state-card.md`)

3. 删除 plan 之后的所有 docs(按用户指定):
   - test-plan.md / spec.md / prototype.md
   - contracts/ / prototypes/ / verifications/ 目录
   - IMPLEMENT_*_REPORT.md / REAL_VERIFY_*_REPORT.md
   - review-report*.md / rot-scan-*.md / ACCEPT_REPORT.md
   - tasks.md

4. 同步清理(仅 docs/ 下的副本,不动代码/归档):
   - docs/verifications/{change-id}/
   - docs/prototypes/{change-id}/(如果存在)

5. change README 更新:
   - Stage 流转复选框全部清空
   - "当前 Stage" 改回用户指定的目标 stage
   - 加 "⚠️ FORCE RESET 记录" 章节
```

### 7.3 不允许操作（红线）

```
❌ 删 docs/archive/done/{change-id}/    (Article VIII 不可变)
❌ 删 docs/archive/out/stub-pileup/     (V11 归档不可变)
❌ revert 已合并到 main 的代码          (agent 不能自决,需用户决策)
❌ 删 tests/ 下的真实测试代码            (用户没明确说删代码时)
❌ 跳过 Step 1-3 直接执行重置            (缺确认)
```

### 7.4 状态卡 reset_history 字段

```yaml
# 状态卡新增字段(可选,记录重置历史)
reset_history:
  - date: "2026-08-12T15:00:00"
    from_stage: "5/accept"
    to_stage: "-1/intake"
    reason: "用户强制重置 + 测试状态重置"
    preserved_artifacts: ["plan.md"]
    removed_artifacts: ["test-plan.md", "spec.md", ...]
    archive_note: "docs/archive/done/2026-08-11-canvas-asset-folders/ (不可变,保留)"
    git_decision: "方案 B: 保留旧代码,新 branch 增强"
    reset_by: "user"
```

### 7.5 重置后从哪开始

```
状态卡重置到 -1/intake 后,agent 应:
  1. 不重写 plan.md(用户说保留)
  2. 直接进入 0.5/test-plan(重新生成测试用例)
  3. 后续 1/spec / 1.5/prototype / 2/contract / 3/implement 全部重走

状态卡重置到 0/plan 后:
  1. 重新走 plan.md
  2. 后续 stage 全部重走

状态卡重置到 N/其他 stage 后:
  1. 保留之前的产物(spec/contract/...)
  2. 从 N stage 重新开始
```

### 7.6 反例（agent 必走 V16 质疑性校验）

```
❌ 不确认归档状态就删归档目录 → 违反 Article VIII
❌ 不问用户就自决 revert 代码 → 误删用户工作
❌ 状态卡重置但 change README 不更新 → 文档不一致(腐烂点)
❌ 删除 tests/ 下真实测试代码 → 丢失回归保护
❌ reset_history 字段不写 → 无审计痕迹,违反 Article XII 文档诚实
❌ agent 嘴上说"重置完成"但没主上下文亲自验证 → 验收盲信(反例 6)
```

---

## 八、关联引用

- 公共铁律: [common-iron-rules.md](common-iron-rules.md) — Article XII 文档诚实
- 公共反例: [common-anti-patterns.md](common-anti-patterns.md) — 反例 4 状态卡说谎
- 阶段交互协议:

---

## 九、状态机 + 驾驶舱（V11.5 NEW — flow 层程序化）

> 状态卡本质是状态机。current_stage 是当前状态，next_stage 是转换。驾驶舱角色（主上下文）是唯一允许改状态字段的 actor（已在 §5.8 铁律 5 字段）。

### 状态机定义
[registry/state-machine.yaml](../registry/state-machine.yaml)（flow 层，程序化解析）
- initial_state: -1/intake
- terminal_states: [5/accept]
- pilot: 主上下文（驾驶舱）

### 驾驶舱角色
- 主上下文是唯一允许改 stage_status / current_stage / gate_result.status / health / next_stage.id 的 actor
- 子代理只能"建议"状态变更，主上下文亲自 Edit
- 状态转换必须通过 validate_transition() 校验

### 程序化校验
- _lib_state_card.load_state_machine() 加载状态机
- _lib_state_card.validate_transition() 校验转换合法性
- _lib_state_card.is_terminal_state() 判断终止态
- run-all-guards.py 统一消费（Agent-D 实现）
