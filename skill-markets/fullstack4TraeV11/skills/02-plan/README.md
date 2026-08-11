# Stage 0 Plan — 元信息

> 第一性原则：**探索先于规划，禁止凭空设计**。

---

## 第一性原则（3 条）

### 原则 1：探索是规划的输入

```
项目现状（文档 + 代码 + 依赖）→ 影响面评估 → 追问点 → plan.md
```

无探索 = 无 plan 依据 = 凭空设计 = 后续返工 3-5 倍。

### 原则 2：子代理探索 + 主上下文汇总

主上下文不直行 Read / Grep / impact 探索（防止上下文击穿）。委派 3 个 sub-agent 并行，主上下文只做汇总。

### 原则 3：plan.md 是规划不是实施

plan.md 必含 Why + Capabilities + Non-Goals + Tasks + Closure + Impact。
plan.md 不写代码、不改文件、不调命令。plan.md 是 Stage 1 Spec 的输入。

---

## 完整骨架流程（6 步）

```
Step 0: Cockpit 读取
        ├─ 读 {project}/.trae/state-card.md
        ├─ 识别活跃 change（如有 → 🔴 阻塞则先汇报用户）
        └─ 校验 stage=-1/intake completed（前置 stage PASS）

Step 1: 意图识别 + 选链
        ├─ 触发词扫描（"规划"/"设计"/"重构"/"分析"）
        ├─ 意图分类: 新功能 / 重构 / Bug 修复 / 文档更新
        └─ 选链:
            ├─ 新功能 → 完整 13 stage（Plan → Spec → ... → Accept）
            ├─ 重构 → spec-purge → 完整 13 stage
            ├─ Bug 修复 → 不走 Plan，直接 Stage 6 Bug Fix
            └─ 文档更新 → ponytail 直改（跳过 Plan）

Step 2: 去重检查（原子级）
        ├─ 扫描 docs/specs/changes/ 下活跃子目录
        ├─ 扫描 docs/specs/archive/done/ 同名功能
        ├─ 原子级比较（> 50% 重叠 → 合并 / < 50% → 新建）
        └─ 输出: 去重决策表

Step 3: 3 路并行子代理探索（核心）
        ├─ 子代理 A — 文档探索（exploration-task）
        │   ├─ Read docs/INDEX.md → docs/ARCHITECTURE.md → 相关 spec
        │   ├─ Read 模块文档 docs/modules/{affected}/
        │   └─ 产出: docs_summary.json（已有能力 + 架构约束 + 受影响模块）
        │
        ├─ 子代理 B — 代码探索（exploration-task）
        │   ├─ GitNexus impact({target}) → 影响面
        │   ├─ GitNexus context({target}) → 调用链
        │   ├─ GitNexus query({concept}) → 概念相关
        │   └─ 产出: code_summary.json（受影响符号 + 调用链图 + 风险等级）
        │
        └─ 子代理 C — 依赖探索（exploration-task）
            ├─ 检测已有公共模块 / 工具函数 / 可复用组件
            ├─ Read 关键 lib / util / helper
            └─ 产出: deps_summary.json（可复用资源 + 需新建模块）

Step 4: 重构场景 → spec-purge.py（仅重构走此步）
        ├─ python ../../scripts/spec-purge.py --feature {name} [--dry-run]
        ├─ 确认清除成功
        └─ 当成全新需求，重新走 Step 3 探索

Step 5: 产出 plan.md（spec-kit 格式）
        ├─ Why（为什么做）
        ├─ Capabilities（能力清单 ≤ 5 项）
        ├─ Non-Goals（非目标）
        ├─ Tasks（checkbox 清单 ≤ 20 项）
        ├─ Closure（P0 闭环步骤 ≤ 5 步）
        └─ Impact（受影响代码/API/依赖 + 风险等级）

Step 6: 状态卡更新
        ├─ current_stage: 0/plan → completed
        ├─ next_stage: 0.5/test-plan → pending
        ├─ stage_ended_at: now
        └─ state-card-validator.py PASS
```

---

## 完整铁律（10 条）

```
1. EXPLORE FIRST       — 探索项目现状后再规划，禁止凭空设计
2. SUBAGENT ONLY       — 所有探索操作委派子代理，禁止主上下文直行
3. IMPACT BY TOOL      — 影响面评估用 GitNexus impact()，禁止手动 grep
4. DEDUP BY ATOM       — 需求去重，> 50% 重叠 → 合并，< 50% → 新建
5. PURGE ON REFACTOR   — 重构场景先调 spec-purge.py 清除旧产物
6. DUAL SEARCH         — 主上下文不直行代码 = 主上下文不直行探索
7. SKEPTICAL VALIDATION — P0/P1 规划按 Article XVI 走质疑性校验
8. PLAN ≤ 80 LINES     — plan.md ≤ 80 行，Capabilities ≤ 5 项
9. CLOSURE ≤ 5 STEPS   — P0 闭环步骤 ≤ 5 步
10. NEVER ACT ON PLAN  — plan.md 是规划不是实施
```

---

## 完整反例（4 条）

### 反例 1：无探索直接规划

**现象**: 收到需求立即写 plan.md，不做任何探索。

**根因**: 觉得"用户说啥就是啥"，不假思索。

**教训**: 跳过探索 = 凭空设计 = 后续返工 3-5 倍。

**正确替代**: Step 3 必走 3 路并行子代理探索。

### 反例 2：GitNexus 可用却用 grep

**现象**: 手动 grep 找代码影响面，忽略 GitNexus MCP 工具。

**根因**: 不熟悉 GitNexus / 觉得 grep 更快。

**教训**: 违反 Article V（GitNexus First）+ 影响面评估不准。

**正确替代**: 使用 GitNexus impact({target}) / context({target}) / query({concept})。

### 反例 3：重构不 purge

**现象**: 用户说"重构 X"，主上下文直接覆盖旧产物。

**根因**: 不知道重构场景需要先 spec-purge。

**教训**: 旧产物污染 + 后续 spec.md 漂移 + 归档不可追溯。

**正确替代**: Step 4 必走 spec-purge.py → 清除旧产物 → 重新探索。

### 反例 4：plan.md 超长

**现象**: plan.md 写到 200+ 行，Capabilities 写到 10+ 项。

**根因**: 把所有细节都塞进 plan.md，不区分规划 vs 实施。

**教训**: plan.md 是规划不是实施，超长 = Stage 1 Spec 失去输入价值。

**正确替代**: plan.md ≤ 80 行 + Capabilities ≤ 5 项 + 细节留给 Stage 1 Spec。

---

## 完整交付协议（4 件套）

```yaml
hand_over:
  stage_id: "0/plan"
  stage_skill: skills/02-plan/SKILL.md
  status: completed
  health: "🟢 on-track"
  artifacts:
    - path: docs/specs/changes/{id}/plan.md
      type: file
      evidence: "plan.md ≤ 80 行 + 3 路探索 evidence + Capabilities ≤ 5 + Risk 等级标注"
    - path: docs/specs/changes/{id}/.state-card.md
      type: file
      evidence: "current_stage=0.5/test-plan + next_stage 填写 + updated_at 更新"
    - path: docs/specs/changes/{id}/exploration/（可选）
      type: dir
      evidence: "3 路探索子代理产出（docs_summary / code_summary / deps_summary）"
  gate_result:
    status: PASS
    gate: stage-gate.py
    output: "plan.md 行数 + Capabilities 数 + 探索 evidence 数 PASS"
  next_stage:
    id: "0.5/test-plan"
    skill_name: skills/03-test-plan/SKILL.md
    expected_inputs: [plan.md, 3 路探索 evidence, GitNexus impact 报告]
    prerequisites: [意图识别 PASS, 去重检查 PASS, 3 路探索全完成]
```

### Completion Report（3 路探索子代理必返）

```yaml
## Completion Report - Sub-agent A（文档探索）
- agent: planner-doc-explorer
- artifacts: [docs/specs/changes/{id}/exploration/docs_summary.json]
- explored_docs: [{N} files]
- key_findings: [{capability_1}, {capability_2}, ...]
- status: ✓ | ⚠️ | ✗

## Completion Report - Sub-agent B（代码探索）
- agent: planner-code-explorer
- artifacts: [docs/specs/changes/{id}/exploration/code_summary.json]
- explored_symbols: [{N} via GitNexus]
- impact_graph: [调用链描述]
- risk_level: LOW|MEDIUM|HIGH|CRITICAL
- status: ✓ | ⚠️ | ✗

## Completion Report - Sub-agent C（依赖探索）
- agent: planner-deps-explorer
- artifacts: [docs/specs/changes/{id}/exploration/deps_summary.json]
- reusable_modules: [{N} found]
- new_modules_needed: [{name}, {name}, ...]
- status: ✓ | ⚠️ | ✗
```

### AOP 移交自检

```
- [ ] 子代理探索全完成（3/3），产出可验证
- [ ] GitNexus impact() 已执行，风险等级已标注
- [ ] 重构场景 → spec-purge.py 已执行
- [ ] plan.md ≤ 80 行，Capabilities ≤ 5 项
- [ ] 状态卡已更新 current_stage + next_stage
- [ ] state-card-validator.py PASS
```

任一项 ❌ → 修正后重新移交。

---

## 启动检查清单

```
[ ] Step 0: Cockpit 读取完成（state-card 无 🔴 阻塞）
[ ] Step 1: 意图识别 + 选链完成（4 类之一）
[ ] Step 2: 去重检查完成（合并 / 新建决策）
[ ] Step 3: 3 路并行探索全完成（3/3 sub-agent 返回 Completion Report）
[ ] Step 4: 重构场景已走 spec-purge.py（如适用）
[ ] Step 5: plan.md 已产出（≤ 80 行 + Capabilities ≤ 5）
[ ] Step 6: 状态卡已更新 + validator PASS
```

---

## 关联引用

- SKILL.md 入口：[SKILL.md](SKILL.md)
- 工作流：[workflows/](workflows/)
- 方法论：[references/](references/)
- 模板：[templates/](templates/)
- 反例：[anti-patterns/](anti-patterns/)
- 公共 references：[../../references/](../../references/)
