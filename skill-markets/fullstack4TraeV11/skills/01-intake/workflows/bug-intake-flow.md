# Bug Intake Flow — Stage -1 Intake

> **V11.7.0+ 设计入口**: [AC 核销门禁](../skills/09-review/SKILL.md) · [贾维斯门禁守护](../skills/00-boot/SKILL.md) · 评分制废除 → 门禁制 · 详见 [CHANGELOG.md V11.7.0](../CHANGELOG.md)


> Stage -1 Intake 处理 bugfix 意图时必走。6 字段必含。

---

## 6 字段 Bug 单模板

```yaml
---
bug_id: {module}-{NNN}-{slug}
title: "{一句话描述}"
severity: P0 | P1 | P2
status: OPEN
created_at: {ISO 8601}
reporter: "主上下文"
symptom: "{用户看到的现象}"
expected: "{正确行为}"
reproduction_steps:
  - "{步骤 1}"
  - "{步骤 2}"
  - "{步骤 3}"
environment: "{OS / 浏览器 / 版本}"
impacted_users: "{受影响用户/范围}"
trigger_phrase: "{原始用户输入}"
---
```

---

## 必走流程

```
Step 1: 用户报 bug → Intake 创建 bug_id（基于 module + slug）
Step 2: 6 字段齐全（含 reproduction_steps 至少 3 步）
Step 3: 状态卡 .state-card.md 初始化（card_type=bug, current_stage=6/bug-fix）
Step 4: 启动 Stage 6 Bug Fix（e2e 先行）
```

---

## 状态流转

```
OPEN → IN_PROGRESS → CLOSED
  ↑           │
  └───────────┘
       (回退条件: e2e INITIAL PASS / 修复失败)
```

---

## 反例

### 反例 A：6 字段不全

```
bug_id: 缺少 NNN 编号
reproduction_steps: 缺少 3 步
```

后果: Stage 6 Bug Fix 无法启动（e2e 写不出）。

正确: Intake 必含 6 字段完整 + 状态卡 PASS。

### 反例 B：跳过 Intake 直接修

```
debugger: 用户报 bug → 立即修代码 → 没创建 bug 单
```

后果: 无追溯链 → Stage 4 Review 失真。

正确: Intake 必先录入 OPEN bug 单。

---

## 关联引用

- [SKILL.md](../SKILL.md)
- [Stage 6 Bug Fix](../../12-bug-fix/SKILL.md)
- [stage-card-protocol.md](../../../references/state-card-protocol.md)
