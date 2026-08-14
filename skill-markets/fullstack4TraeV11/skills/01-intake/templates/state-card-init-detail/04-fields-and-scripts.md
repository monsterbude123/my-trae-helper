# 字段规则 + 渲染示例 + 校验脚本 — state-card-init.md 详情

> 父文件：[../state-card-init.md](../state-card-init.md)
> 来源：原 state-card-init.md 第 163-261 行（保留信息密度）

---

## 字段填写规则

| 字段 | 必填 | 规则 |
|------|:---:|------|
| `card_type` | ✅ | project / change / bug |
| `card_id` | ✅ | 唯一标识 |
| `current_stage` | ✅ | 见 stage_config 命名 |
| `stage_status` | ✅ | pending / working / completed / blocked / skipped |
| `stage_started_at` | ✅ | ISO 8601（如 `2026-08-11T14:30:00`） |
| `updated_at` | ✅ | 同上，每次更新必改 |
| `updated_by` | ✅ | 主上下文 / sub-agent name |
| `health` | ✅ | 🟢 on-track / 🟡 degraded / 🔴 blocked |
| `artifacts` | ✅ | 至少含 1 项 |
| `gate_result` | ✅ | PENDING → PASS / FAIL |
| `next_stage` | ✅ | 含 id + skill_name |
| `blocked_by` | ✅ | null 或 5 字段阻塞报告 |
| `actor` | ✅ | 主上下文 / sub-agent name |

---

## 模板渲染示例

### project-init

```yaml
card_type: project
card_id: my-trae-helper
current_stage: 0/plan
stage_status: pending
stage_started_at: 2026-08-11T14:30:00
...
next_stage:
  id: 0/plan
  skill_name: skills/02-plan/SKILL.md
notes: |
  路由决策证据:
    意图: project-init
    触发词: "初始化"
    项目惯例要点: 已有 6 条自有铁律，stage_config.implement.skills 覆盖为 react-dev-skill
```

### change-start (feature)

```yaml
card_type: change
card_id: 2026-08-11-add-user-auth
current_stage: 0/plan
stage_status: pending
stage_started_at: 2026-08-11T15:00:00
...
next_stage:
  id: 0/plan
  skill_name: skills/02-plan/SKILL.md
notes: |
  路由决策证据:
    意图: change-start (feature)
    子意图: feature
    触发词: "新增"
    项目惯例要点: change-id 命名遵循 {YYYY-MM-DD}-{slug}
```

### bug-fix

```yaml
card_type: bug
card_id: auth-003-token-refresh-concurrency-500
current_stage: 6/bug-fix
stage_status: pending
stage_started_at: 2026-08-11T16:00:00
...
bug_id: auth-003-token-refresh-concurrency-500
bug_severity: P1
notes: |
  Bug 录入证据:
    触发词: "期望 X 但实际 Y"
    用户询问: 同意录入
    6 字段收集: 完整
    Bug 单编号: auth-003-token-refresh-concurrency-500
    路由目标: Stage 6 Bug Fix
```

---

## 校验脚本

```bash
python ../../scripts/state-card-validator.py {state-card-path}
# 输出: PASS / FAIL + 不一致项清单
```

**校验项**:
- [ ] 所有必填字段非空
- [ ] `artifacts[].exists` 与文件系统一致（LS 验证）
- [ ] `gate_result.status` 为 PENDING / PASS / FAIL / N/A 之一
- [ ] `current_stage` 在 13 stage 名单中
- [ ] `next_stage.skill_name` 在 `skills/` 目录中存在
- [ ] `blocked_by` 非空时 `stage_status` 不能是 completed
- [ ] `stage_status=completed` 时 `stage_ended_at` 必须有值

---

## 关联引用

- 父文件：[../state-card-init.md](../state-card-init.md)
- state-card-protocol.md：[../../../references/state-card-protocol.md](../../../../references/state-card-protocol.md)
