# State Card Protocol — 状态卡协议

> V11 13 stage 通用状态卡协议。所有 stage 必读。

---

## 3 类状态卡

### 1. project 级（Stage -1 Intake 初始化）

用于整个项目的健康度追踪。

### 2. change 级（Stage -1 Intake 新建 change 时创建）

用于单个 change（feature/bugfix）的 13 stage 流转。

### 3. bug 级（Stage -1 Intake 新建 bug 单时创建）

用于单个 bug 的 Stage 6 Bug Fix 流转。

---

## 必填字段（V11 13 stage 通用）

```yaml
必填字段:
  card_type: ["project", "change", "bug"]
  card_id: "唯一标识"
  version: "1.0.0"
  current_stage: 见 stage_config 命名（-1/intake, 0/plan, ..., 7/project-health）
  stage_status: ["pending", "working", "completed", "blocked", "skipped"]
  stage_started_at: ISO 8601
  updated_at: ISO 8601（每次更新必改）
  updated_by: "主上下文"
  health: ["🟢 on-track", "🟡 degraded", "🔴 blocked"]
  artifacts: [path, type, exists, evidence]
  gate_result:
    status: ["PENDING", "PASS", "FAIL", "N/A"]
    gate: "stage-gate.py"
    output: null
    verified_at: null
  next_stage:
    id: "{stage-id}"
    skill_name: "skills/{NN}-{name}/SKILL.md"
    expected_inputs: [string]
    prerequisites: [string]
  blocked_by: null（必填但允许 null）
  actor: "主上下文" | "sub-agent-{name}"
  duration_minutes: 0
  notes: |
    路由决策证据
```

---

## Stage ID 命名规范（13 stage）

| Stage | 命名 | SKILL.md 路径 |
|-------|------|---------------|
| -1 | `-1/intake` | `skills/01-intake/SKILL.md` |
| 0 | `0/plan` | `skills/02-plan/SKILL.md` |
| 0.5 | `0.5/test-plan` | `skills/03-test-plan/SKILL.md` |
| 1 | `1/spec` | `skills/04-spec/SKILL.md` |
| 1.5 | `1.5/prototype` | `skills/05-prototype/SKILL.md` |
| 2 | `2/contract` | `skills/06-contract/SKILL.md` |
| 3 | `3/implement` | `skills/07-implement/SKILL.md` |
| 3.5 | `3.5/real-verify` | `skills/08-real-verify/SKILL.md` |
| 4 | `4/review` | `skills/09-review/SKILL.md` |
| 4.5 | `4.5/rot-scan` | `skills/10-rot-scan/SKILL.md` |
| 5 | `5/accept` | `skills/11-accept/SKILL.md` |
| 6 | `6/bug-fix` | `skills/12-bug-fix/SKILL.md` |
| 7 | `7/project-health` | `skills/13-project-health/SKILL.md` |

---

## 状态卡流转规则

### 推进规则

```
stage_status = "completed" 时 →
  ├ 推进到 next_stage.id
  ├ 改 current_stage = next_stage.id
  ├ stage_status = "pending"
  └ updated_at = now()
```

### 回退规则

```
发现上游错误时 →
  ├ current_stage 回退到出错 stage
  ├ stage_status = "working"
  ├ notes 必含回退原因
  └ updated_at = now()
```

### 阻塞规则

```
遇到阻塞时 →
  ├ stage_status = "blocked"
  ├ blocked_by = 5 字段阻塞报告（Article XV）
  ├ health = "🔴 blocked"
  └ 状态卡进入 STOP 状态
```

### 归档规则（Stage 5 Accept）

```
Stage 5 Accept PASS 时 →
  ├ current_stage = "5/accept"
  ├ stage_status = "completed"
  ├ health = "🟢 on-track"
  └ (可选) 创建 archive/ 副本
```

---

## 状态卡陈旧检测

```
陈旧阈值: updated_at 距今 > 30 分钟
  └ 且 stage_status != "completed"/"skipped"
  └ → 报警（V10.11 V11 §腐化扫描 #7）

修复: updated_at = now()（手动或脚本）
```

---

## stage-gate.py 集成

```bash
# 验证当前状态卡
python scripts/stage-gate.py --state-card .trae/state-card.md

# 验证特定 stage
python scripts/stage-gate.py --state-card .trae/state-card.md --stage 3/implement
```

输出:
- ✅ PASS — 进入 stage 工作
- ❌ FAIL — 阻塞报告（Article XV 5 字段）

---

## 关联引用

- [constitution.md](constitution.md) — Article XII workflow discipline
- [common-iron-rules.md](common-iron-rules.md) — 12.4 状态卡必更新
- [../scripts/stage-gate.py](../scripts/stage-gate.py) — 状态卡门禁脚本
- [../scripts/state-card-validator.py](../scripts/state-card-validator.py) — 字段校验脚本
- V10 来源（开发期）: `../../fullstack4TraeV10/references/state-card-protocol.md`