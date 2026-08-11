# 状态卡协议

> 13 个 stage 的状态卡统一协议。状态卡是任务真相源之一，不允许说谎（Article XII）。

---

## 一、状态卡分类

### 1.1 项目级状态卡

**位置**: `{project_root}/.trae/state-card.md`

**作用**: 记录项目整体状态（当前 stage + 整体健康度 + 阻塞 + 下一步）

**生命周期**: 项目存在期间持续维护

### 1.2 Change 级状态卡

**位置**: `{project_root}/docs/specs/changes/{change-id}/.state-card.md`

**作用**: 记录单个 change 的状态（当前 stage + 阶段产物 + 阶段门禁）

**生命周期**: change 启动 → Accept 归档

### 1.3 Bug 单状态卡

**位置**: `{project_root}/docs/bugs/{bug-id}/.state-card.md`（可选）

**作用**: 记录 bug 修复进度（OPEN → CLOSED 状态机）

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
health: {�� on-track | �� degraded | �� blocked}

# === 产出物 ===
artifacts:
  - path: {产物路径}
    type: {file | dir | report | state-update}
    exists: {true | false}
    evidence: {file:line | 命令 | 截图}

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
| 阻塞发生 | 任何阶段遇到阻塞 | health=��, blocked_by |
| 阻塞解除 | 阻塞解决 | health=��/��, blocked_by=null |
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
health: �� on-track
artifacts:
  - path: docs/specs/changes/2026-08-11-add-user-auth/
    type: dir
    exists: true
    evidence: "ls 验证"
gate_result:
  status: PENDING
  gate: stage-gate.py
  output: null
  verified_at: null
next_stage:
  id: 0.5/test-plan
  skill_name: skills/02-test-plan/SKILL.md
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
health: �� on-track
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
gate_result:
  status: PASS
  gate: contract-gate.py
  output: "contract-gate.py: 4 件套齐全 + 测试骨架 PASS"
  verified_at: 2026-08-11T14:55:00
next_stage:
  id: 3.5/real-verify
  skill_name: skills/04-real-verify/SKILL.md
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
health: �� on-track
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
  skill_name: skills/07-bug-fix/SKILL.md
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

---

## 六、状态卡反例

### 反例 1: 状态卡说谎

**现象**: 状态卡显示 `stage_status: completed`，但 `artifacts` 路径 LS 不存在。

**根因**: 维护者未亲自验证产物，只更新状态字段。

**教训**: 状态卡必须经过 state-card-validator.py 校验。

### 反例 2: 状态卡永远��

**现象**: 任何阶段都显示 `health: �� on-track`，从不降级。

**根因**: 维护者不知道 blocked_by 字段怎么填。

**教训**: ��/�� 是阻塞状态可视化机制，不用 = 失去价值。

### 反例 3: 状态卡无 next_stage

**现象**: 状态卡显示 stage=completed，但没有 next_stage 路由。

**根因**: 当前 stage 完成后未路由到下一 stage。

**教训**: 阶段切换必须包含 next_stage 字段。

### 反例 4: 状态卡无 updated_at

**现象**: 状态卡停留在初始版本，没有时间戳。

**根因**: 维护者没想到加 updated_at。

**教训**: state-card-staleness 是腐烂点 16，必须有 updated_at。

---

## 七、关联引用

- 公共铁律: [common-iron-rules.md](common-iron-rules.md) — Article XII 文档诚实
- 公共反例: [common-anti-patterns.md](common-anti-patterns.md) — 反例 4 状态卡说谎
- 阶段交互协议: