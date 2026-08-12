# 反例 2：跳过状态卡初始化

> Stage -1 Intake 必须初始化状态卡（project / change / bug 之一）。跳过 = 任务真相源缺失。

---

## 现象

```
主上下文: 直接进入 Stage 0 Plan 或 Stage 6 Bug Fix
（未初始化任何状态卡）
```

**识别信号**:
- `docs/specs/.state-card.md` 不存在或为空
- `docs/specs/changes/{id}/.state-card.md` 不存在
- `docs/bugs/{id}/.state-card.md` 不存在
- 后续 stage 切换时无法读取 current_stage
- 30 分钟内无产 = 疑似假性完成（编排器 §3 原则）

---

## 根因

| 根因 | 占比 | 说明 |
|------|:---:|------|
| 觉得状态卡"是文档工作" | 50% | 认为跳过更快 |
| 不知道 V11 状态卡协议 | 30% | 未读 [state-card-protocol.md](../../../references/state-card-protocol.md) |
| 任务简单"不需要状态卡" | 20% | 小任务流线化误判 |

---

## 教训

**状态卡是任务真相源之一（Article XII 文档诚实）。无状态卡 = 后续 stage 无法判断起点。**

真实案例（2026-08-09 蒸馏）:
- 主上下文未初始化 change 状态卡，直接进入 Stage 0 Plan
- planner sub-agent 返回后，主上下文不知道"哪个 change 的产物"
- 后续 5 个 stage 全部错乱 → 返工 4 轮

---

## 正确替代

```
Step 6: 初始化状态卡（3 类必选其一）
  ├─ project → {project}/docs/specs/.state-card.md
  ├─ change → docs/specs/changes/{id}/.state-card.md
  └─ bug → docs/bugs/{id}/.state-card.md + docs/bugs/{id}.md
```

**MUST**: 每个 change / bug / project 任务必初始化状态卡。

**NEVER**:
- ❌ 跳过状态卡直接进 stage
- ❌ 状态卡字段填写不完整（缺 current_stage / next_stage / artifacts）
- ❌ 状态卡更新不同步（产物写入但未更新状态卡）

---

## 检测方法

```yaml
checklist:
  - [ ] 状态卡文件存在？LS 验证
  - [ ] current_stage 字段已设置？（非 null）
  - [ ] next_stage.id + skill_name 已填写？
  - [ ] artifacts 数组至少含 1 项？
  - [ ] gate_result.status 已设置？
  - [ ] state-card-validator.py PASS？
```

任一未勾选 → 触发本反例 → 回到 Step 6 重新初始化。

---

## 状态卡初始化模板

**详细模板**: [../templates/state-card-init.md](../templates/state-card-init.md)

**3 类速查**:
- project 级 → `{project}/docs/specs/.state-card.md`
- change 级 → `docs/specs/changes/{id}/.state-card.md`
- bug 级 → `docs/bugs/{id}.md` + `docs/bugs/{id}/.state-card.md`

---

## 关联引用

- [SKILL.md §铁律 3](../SKILL.md) — 状态卡不立不启动
- [SKILL.md §铁律 9](../SKILL.md) — NEVER 跳过状态卡
- [state-card-protocol.md](../../../references/state-card-protocol.md) — 状态卡协议（完整字段定义）
- [state-card-init.md](../templates/state-card-init.md) — 状态卡初始化模板
- [intent-routing.md Step 6](../workflows/intent-routing.md) — 初始化状态卡步骤
