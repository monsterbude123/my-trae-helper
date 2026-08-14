# 意图路由工作流（Intent Routing）— 总览

> Stage -1 Intake 的核心工作流。识别用户意图 + 路由决策 + 状态卡初始化。
>
> **本文件为索引**，按 7 步流程拆分到 `intent-routing-detail/` 子文件。所有内容保真保留。

---

## 流程图

```
[用户输入]
  ↓
[Step 1] 加载 skill + 解析 depends_on
  ↓
[Step 2] Glob 1 次项目惯例（AGENTS.md / docs/ / .trae/rules/）
  ↓
[Step 3] 意图识别（5 种类型）
  ├─ 触发词命中 → 直接分类
  └─ 不命中 → AskUserQuestion
  ↓
[Step 4] Bug 录入触发词判断（仅问题类触发词）
  ├─ 命中 → 询问"是否录入 bug 单？"
  │   ├─ 同意 → Step 5(bug-fix)
  │   └─ 拒绝 → 状态卡 health=🟡 + 路由到 Stage 7 Project Health（自检）
  └─ 未命中 → 跳过
  ↓
[Step 5] 路由决策（5 种意图 → 5 种路径）
  ↓
[Step 6] 初始化状态卡（3 类）
  ↓
[Step 7] 交接下一 stage
```

---

## 7 步章节指针

| Step | 名称 | 文件 |
|------|------|------|
| Step 1 | 加载 Skill | [step1-load-skill.md](./intent-routing-detail/step1-load-skill.md) |
| Step 2 | 项目惯例勘察 | [step2-convention-survey.md](./intent-routing-detail/step2-convention-survey.md) |
| Step 3 | 意图识别（5 种类型）| [step3-intent-recognition.md](./intent-routing-detail/step3-intent-recognition.md) |
| Step 4 | Bug 录入触发词判断 | [step4-bug-trigger.md](./intent-routing-detail/step4-bug-trigger.md) |
| Step 5 | 路由决策 | [step5-routing-decision.md](./intent-routing-detail/step5-routing-decision.md) |
| Step 6 | 初始化状态卡（3 类）| [step6-state-card-init.md](./intent-routing-detail/step6-state-card-init.md) |
| Step 7 | 交接下一 stage | [step7-handoff.md](./intent-routing-detail/step7-handoff.md) |

---

## 必读

- 子代理委派时只 Read 当前需要的 Step 子文件，避免 context 击穿
- 流程图 + 总览在本文件即可获得全貌

---

## 关联引用

- [SKILL.md](../SKILL.md) — 阶段入口
- [bug-intake-flow.md](bug-intake-flow.md) — Bug 录入 6 字段工作流
- [project-convention-survey.md](project-convention-survey.md) — 项目惯例勘察工作流
- [intent-types.md](../references/intent-types.md) — 5 种意图类型详解
- [routing-decision-tree.md](../references/routing-decision-tree.md) — 路由决策树
- [state-card-protocol.md](../../../references/state-card-protocol.md) — 状态卡协议
