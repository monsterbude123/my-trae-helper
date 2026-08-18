---
name: fullstack-02-plan
description: "Stage 0 探索 + 规划 — 项目现状 3 路并行探索（文档/代码/依赖）+ GitNexus impact + 追问点 + plan.md 产出。触发词：plan / 规划 / 设计 / 分析 / 评估 / 重构。"
stage: 0
parent: fullstack4traev11
depends_on:
  skills: [gitnexus4Trae]
  stages: [-1/intake]
  references:
    - ../../references/state-card-protocol.md
    - ../../references/stage-interaction-protocol.md
    - ../../references/common-iron-rules.md
    - ../../references/common-anti-patterns.md
    - ../../references/gate-configuration-protocol.md   # V11.7.0 NEW 贾维斯 SOP
  scripts:
    - ../../scripts/stage-gate.py
    - ../../scripts/spec-purge.py
    - ../../scripts/gate-integrity-guard.py   # V11.7.0 NEW hash 锁校验
---

> **V12.0.0+ 设计入口**:
> - **AC 核销门禁(Stage 4 Review)** → [skills/09-review/SKILL.md](../09-review/SKILL.md) + [acceptance-baseline-extract.md](../09-review/workflows/acceptance-baseline-extract.md)
> - **贾维斯门禁守护(防 agent 改标准)** → [skills/00-boot/SKILL.md](../00-boot/SKILL.md) + [agents/jarvis.md](../00-boot/agents/jarvis.md) + [gate-configuration-protocol.md](../../references/gate-configuration-protocol.md)
> - **变更**: 评分制废除 → 门禁制;4 维详情转附加检查;`registry/gates.yaml` v1.2.0 加 layer 分层字段

# Stage 0 Plan — 探索 + 规划

> 第一性原则：**探索先于规划，禁止凭空设计**。Plan 阶段的核心是发现而非创作。

## 边界

| Plan 处理 | Plan 不处理（路由到其他 stage） |
|----------|-------------------------------|
| 项目现状探索（文档/代码/依赖）| 意图识别 → Stage -1 Intake |
| GitNexus impact 评估 | 规格编写 → Stage 1 Spec |
| 追问点收集 | 实施编码 → Stage 3 Implement |
| plan.md 产出 | 验收 → Stage 4 Review |
| spec-purge（重构场景） | 归档 → Stage 5 Accept |

## 铁律（10 条）

```
1. EXPLORE FIRST       — 探索项目现状后再规划，禁止凭空设计
2. SUBAGENT ONLY       — 所有探索操作委派子代理，禁止主上下文直行
3. IMPACT BY TOOL      — 影响面评估用 GitNexus impact()，禁止手动 grep
4. DEDUP BY ATOM       — 需求去重，> 50% 重叠 → 合并，< 50% → 新建
5. PURGE ON REFACTOR   — 重构场景先调 spec-purge.py 清除旧产物
6. DUAL SEARCH         — 主上下文不直行代码 = 主上下文不直行探索（双委派）
7. SKEPTICAL VALIDATION — P0/P1 规划按 [skeptical-validation-protocol.md](../../references/skeptical-validation-protocol.md) 走质疑性校验（4 维度 + 强制声明格式）
8. PLAN ≤ 80 LINES     — plan.md ≤ 80 行，Capabilities ≤ 5 项
9. CLOSURE ≤ 5 STEPS   — P0 闭环步骤 ≤ 5 步
10. NEVER ACT ON PLAN  — plan.md 是规划不是实施，禁止根据 plan 直接改代码
```

## 委派触发词

**主上下文识别触发词后加载本 skill**:

```
意图类: "plan" / "规划" / "设计" / "分析" / "评估"
重构类: "重构" / "改造" / "重新设计" / "拆分" → 走 PURGE 路径
```

## 骨架流程（6 步）

```
Step 0: Cockpit 读取（docs/specs/.state-card.md → 识别活跃 change / 阻塞 / 健康度）
Step 1: 意图识别 + 选链（新功能 / 重构 / Bug 修复 / 文档更新）
Step 2: 去重检查（docs/specs/ 活跃子目录 + archive/done/ 同名功能扫描）
Step 3: 3 路并行探索（子代理 A 文档 + 子代理 B 代码 + 子代理 C 依赖）
Step 4: 重构场景 → spec-purge.py（先清除旧产物）
Step 5: 产出 plan.md（spec-kit 格式）
Step 6: 状态卡更新（current_stage=0/plan completed, next=0.5/test-plan）
```

**详细工作流**: [workflows/three-path-exploration.md](workflows/three-path-exploration.md)

## 关键产物

| 产物 | 路径 | 模板 |
|------|------|------|
| plan.md | `docs/specs/changes/{id}/plan.md` | [templates/plan-template.md](templates/plan-template.md) |
| 状态卡更新 | `docs/specs/changes/{id}/.state-card.md` | — |

## 3 路并行探索

| 子代理 | 任务 | 输出 | 工具 |
|--------|------|------|------|
| **A 文档探索** | 读 docs/INDEX → ARCHITECTURE → spec → 模块文档 | 已有能力清单 + 架构约束 + 受影响模块 | Read + Glob |
| ├─ spec-writer 必产双产物检查(仅 UI 涉及 change,V11.2.1 NEW — 蒸馏自 V10): | | | |
| │  ├─ 启发式判定 UI 涉及: spec.md 含 UI/UX/页面/组件/视觉/交互/前端/prototypes 关键字 → 涉及 | | | |
| │  ├─ Read docs/specs/changes/{id}/prototypes/design-prompt.md(仅 UI 涉及) | | | |
| │  ├─ Read docs/specs/changes/{id}/prototypes/ui-ux-logic.md(仅 UI 涉及) | | | |
| │  ├─ 缺 1 份 → 标 P0 阻塞(待 spec-writer 在 Stage 1.5 补) | | | |
| │  ├─ 纯后端/API/CLI change → 跳过整个 prototypes/ 检查,不视为缺失 | | | |
| │  └─ 产出: prototypes_status.json("ui_involved": true/false, "design-prompt": "exists|missing|skipped", "ui-ux-logic": "exists|missing|skipped") | | | |
| **B 代码探索** | GitNexus impact + context 分析 | 受影响符号列表 + 调用链图 + 风险等级 | gitnexus MCP |
| **C 依赖探索** | 检测公共模块/工具/可复用组件 | 可复用资源清单 + 需新建模块 | Read + Grep |

**约束**: 探索过程不在主上下文进行（防止上下文击穿）

## 交付协议（4 件套）

```yaml
hand_over:
  stage_id: "0/plan"
  stage_skill: skills/02-plan/SKILL.md
  status: completed
  health: "🟢 on-track"
  artifacts:
    - path: docs/specs/changes/{id}/plan.md
      type: file
      evidence: "plan.md ≤ 80 行 + 3 路探索 evidence + Capabilities ≤ 5"
    - path: docs/specs/changes/{id}/.state-card.md
      type: file
      evidence: "current_stage=0.5/test-plan + next_stage 填写"
  gate_result:
    status: PASS
    gate: stage-gate.py
    output: "plan.md 行数 + Capabilities 数 + 探索 evidence 数 PASS"
  next_stage:
    id: "0.5/test-plan"
    skill_name: skills/03-test-plan/SKILL.md
    expected_inputs: [plan.md + 3 路探索 evidence + GitNexus impact 报告]
    prerequisites: [意图识别 PASS, 去重检查 PASS, 3 路探索全完成]
```

**Completion Report（子代理返回必填 4 字段）**:
```
## Completion Report
- artifacts: [docs/specs/{feature}/plan.md, docs/specs/changes/{id}/.state-card.md]
- explored_docs: [{N} files]
- explored_code: [{N} symbols via GitNexus]
- explored_deps: [{N} reusable modules]
- risk_level: LOW|MEDIUM|HIGH|CRITICAL
- spec_purged: yes|no
- status: ✓ | ⚠️ | ✗
```

## 反模式（4 条）

| 反例 | 简述 | 详细 |
|------|------|------|
| 无探索直接规划 | 凭经验写 plan.md | [anti-patterns/01-no-exploration.md](anti-patterns/01-no-exploration.md) |
| GitNexus 可用却 grep | 手动 grep 找影响面 | [anti-patterns/02-grep-instead-of-gitnexus.md](anti-patterns/02-grep-instead-of-gitnexus.md) |
| 重构不 purge | 直接覆盖旧产物 | [anti-patterns/03-refactor-without-purge.md](anti-patterns/03-refactor-without-purge.md) |
| plan.md 超长 | > 80 行 / > 5 Capabilities | [anti-patterns/04-plan-too-long.md](anti-patterns/04-plan-too-long.md) |

## 参考索引

| 资源 | 路径 |
|------|------|
| Stage 元信息（第一性原则） | [README.md](README.md) |
| 3 路并行探索工作流 | [workflows/three-path-exploration.md](workflows/three-path-exploration.md) |
| 计划追问点工作流 | [workflows/plan-clarification.md](workflows/plan-clarification.md) |
| 原子级去重 | [references/dedup-by-atom.md](references/dedup-by-atom.md) |
| GitNexus 影响面评估 | [references/impact-assessment.md](references/impact-assessment.md) |
| plan.md 模板 | [templates/plan-template.md](templates/plan-template.md) |
| 公共铁律 | [../../references/common-iron-rules.md](../../references/common-iron-rules.md) |
| 状态卡协议 | [../../references/state-card-protocol.md](../../references/state-card-protocol.md) |
| 阶段交互协议 | [../../references/stage-interaction-protocol.md](../../references/stage-interaction-protocol.md) |
