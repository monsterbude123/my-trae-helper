---
name: intake
description: "Stage -1 入口 — 全栈流程的意图受理 + 路由起点。识别用户意图（新功能 / Bug / 重构 / 文档同步 / 项目初始化）+ 路由决策 + 状态卡初始化 + Bug 录入触发 + 项目惯例勘察。触发词：初始化 / 新需求 / Bug 修复 / 重构 / 文档同步 / 报错 / 不工作 / 接入新项目。"
stage: -1
parent: fullstack4traev11
depends_on:
  skills: []
  stages: []
  references:
    - ../../references/state-card-protocol.md
    - ../../references/stage-interaction-protocol.md
    - ../../references/dependency-config.md
    - ../../references/document-layer.md
  scripts:
    - ../../scripts/stage-gate.py
    - ../../scripts/state-card-validator.py
---

# Stage -1 Intake — 意图受理 + 路由起点

> 第一性原则：**意图不明不路由，未勘察项目惯例不初始化**。Intake 是全栈流程的唯一入口，所有用户请求必须先经过意图识别 + 路由决策。

## 边界

| Intake 处理 | Intake 不处理（路由到其他 stage） |
|------------|-------------------------------|
| 意图识别 + 路由决策 | 计划制定 → Stage 0 Plan |
| 状态卡初始化 | 规格编写 → Stage 1 Spec |
| Bug 录入 6 字段 | Bug 根因分析 → Stage 6 Bug Fix |
| 项目惯例勘察 | 实施编码 → Stage 3 Implement |
| 触发词识别 | 文档撰写 → Stage 1 Spec / Stage 5 Accept |

## 铁律（10 条，按优先级）

```
1. 意图不明不路由       — 必须识别意图才能路由（5 种意图之一）
2. 未勘察不初始化       — 项目级 AGENTS.md / docs/ / .trae/rules/ 必须先 Glob 1 次
3. 状态卡不立不启动     — 每个 change 必须有状态卡才能进入下一 stage
4. Bug 录入必询问       — 用户反馈问题必问"是否作为 bug 单录入"（不默认创建）
5. 路由决策不臆断       — 模糊意图必 AskUserQuestion（不靠经验猜）
6. 路由必记录           — 路由决策表必须写入状态卡 next_stage
7. 编排器依赖空不空路由 — intake.skills/stages 都是空（自身是入口）
8. NEVER 默认创建 bug 单 — 用户拒绝时绝不强制创建
9. NEVER 跳过状态卡     — change / bug / project 三类必初始化其一
10. NEVER 静默路由      — 路由决策必须有 evidence（触发词 / Glob 命中 / 用户明确）
```

## 委派触发词

**主上下文识别触发词后必加载本 skill**:

```
意图类触发词:
  "初始化" / "新项目" / "项目 0→1"     → 路由: project-init
  "新需求" / "新增功能" / "加个 X"        → 路由: change-start
  "重构" / "改造" / "重新设计"            → 路由: change-start (refactor 子类)
  "文档同步" / "更新文档"                 → 路由: change-start (doc-sync 子类)

问题类触发词（V10.11 NEW）:
  "报错" / "错误" / "异常"               → 询问 bug 录入 → 路由: bug-fix
  "不工作" / "失败" / "崩溃"             → 询问 bug 录入 → 路由: bug-fix
  "应该出现 X 但出现 Y"                   → 询问 bug 录入 → 路由: bug-fix
  "期望 X 但实际 Y"                       → 询问 bug 录入 → 路由: bug-fix

模糊意图:
  不命中任何触发词 → AskUserQuestion（5 种意图选项）
```

## 骨架流程

```
Step 1: 加载本 skill + 解析 depends_on
Step 2: Glob 1 次项目惯例（AGENTS.md / docs/ / .trae/rules/）
Step 3: 识别用户意图（5 种类型）
Step 4: Bug 录入触发词判断（仅问题类触发词走此步）
Step 5: 路由决策（5 种意图 → 5 种路由路径）
Step 6: 初始化状态卡（project / change / bug）
Step 7: 交接给下一 stage（更新 next_stage 字段）
```

**详细工作流**: [workflows/intent-routing.md](workflows/intent-routing.md)

## 5 种意图类型（路由目标）

| 意图 | 路由目标 | 状态卡类型 |
|------|---------|-----------|
| **project-init** | Stage 0 Plan → ... → Stage 5 Accept | project |
| **change-start**（新功能/重构）| Stage 0 Plan | change |
| **change-start**（doc-sync）| Stage 1 Spec 或 Stage 5 Accept | change |
| **bug-fix** | Stage 6 Bug Fix（独立支线）| bug |
| **project-health** | Stage 7 Project Health（异步自检）| project |

**详细分类**: [references/intent-types.md](references/intent-types.md)

## 关键产物

| 产物 | 路径 | 模板 |
|------|------|------|
| 状态卡（project） | `{project}/docs/specs/.state-card.md` | [templates/state-card-init.md](templates/state-card-init.md) |
| 状态卡（change） | `docs/specs/changes/{id}/.state-card.md` | [templates/state-card-init.md](templates/state-card-init.md) |
| 状态卡（bug） | `docs/bugs/{id}/.state-card.md` | [templates/state-card-init.md](templates/state-card-init.md) |
| Bug 单 | `docs/bugs/{id}.md` | [templates/bug-template.md](templates/bug-template.md) |

## 交接协议（必含 4 件套）

```yaml
hand_over:
  stage_id: "-1/intake"
  stage_skill: skills/01-intake/SKILL.md
  status: completed
  health: "🟢 on-track"
  artifacts:
    - path: docs/specs/.state-card.md / docs/specs/changes/{id}/.state-card.md
      type: file
      evidence: "状态卡初始化 + next_stage 路由"
    - path: docs/bugs/{id}.md（仅 bug-fix 路由）
      type: file
      evidence: "Bug 单 6 字段齐全"
  gate_result:
    status: PASS
    gate: state-card-validator.py
    output: "状态卡字段完整 + 文件存在性 OK"
  next_stage:
    id: "0/plan" | "6/bug-fix" | "7/project-health"
    skill_name: skills/02-plan/SKILL.md | skills/12-bug-fix/SKILL.md | skills/13-project-health/SKILL.md
    expected_inputs: [状态卡 + 路由决策表]
    prerequisites: [意图识别 PASS + 状态卡初始化 PASS]
```

**详细协议**: [../../references/stage-interaction-protocol.md §二](../../references/stage-interaction-protocol.md)

## 反模式（4 条）

| 反例 | 简述 | 详细 |
|------|------|------|
| 无意图识别直接动手 | 收到需求立即写 spec | [anti-patterns/01-no-intent-recognition.md](anti-patterns/01-no-intent-recognition.md) |
| 跳过状态卡初始化 | 不立状态卡直接进 stage | [anti-patterns/02-skip-state-card.md](anti-patterns/02-skip-state-card.md) |
| 强制创建 bug 单 | 用户拒绝时仍创建 | [anti-patterns/03-force-create-bug.md](anti-patterns/03-force-create-bug.md) |
| 未勘察项目惯例 | 不 Glob 就初始化 | [anti-patterns/04-no-convention-survey.md](anti-patterns/04-no-convention-survey.md) |

## 参考索引

| 资源 | 路径 |
|------|------|
| Stage 元信息（第一性原则 + 完整骨架） | [README.md](README.md) |
| 意图路由工作流 | [workflows/intent-routing.md](workflows/intent-routing.md) |
| Bug 录入 6 字段工作流 | [workflows/bug-intake-flow.md](workflows/bug-intake-flow.md) |
| 项目惯例勘察工作流 | [workflows/project-convention-survey.md](workflows/project-convention-survey.md) |
| 5 种意图类型详解 | [references/intent-types.md](references/intent-types.md) |
| 路由决策树 | [references/routing-decision-tree.md](references/routing-decision-tree.md) |
| Bug 单状态机 | [references/bug-state-machine.md](references/bug-state-machine.md) |
| 状态卡协议 | [../../references/state-card-protocol.md](../../references/state-card-protocol.md) |
| 阶段交互协议 | [../../references/stage-interaction-protocol.md](../../references/stage-interaction-protocol.md) |
