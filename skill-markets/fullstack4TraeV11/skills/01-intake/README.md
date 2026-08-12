# Stage -1 Intake — 元信息

> 第一性原则：**意图不明不路由，未勘察项目惯例不初始化**。

---

## 第一性原则（3 条）

### 原则 1：意图是路由的唯一输入

```
用户输入 → 意图识别 → 路由决策 → 状态卡初始化 → 下一 stage
```

意图不明 = 路由失败 = Intake 阻塞。必须 AskUserQuestion 澄清，不可臆断。

### 原则 2：状态卡是 Intake 的唯一产出

Intake 不写 spec / 不写 plan / 不改代码。Intake 只产生 3 类状态卡之一：
- project（项目级）
- change（单个功能 / 重构）
- bug（用户反馈问题）

状态卡初始化 = Intake 完成。

### 原则 3：项目惯例勘察不可跳过

未 Glob 1 次项目自身的 AGENTS.md / docs/ / .trae/rules/ → 不可初始化状态卡。理由：
- 项目可能有自命名规则（编号 / 日期格式）
- 项目可能有自规则（铁律 / 反例 / 安全审查）
- 项目可能有自脚本（lighthouse / e2e）

未勘察 = 与项目惯例冲突 = 后续 stage 返工。

---

## 完整骨架流程

```
Step 1: 加载本 skill + 解析 depends_on
        ├─ 加载 9 个公共 references（constitution / iron-rules / anti-patterns / state-card / stage-interaction / dependency-config / document-layer / report-growth / ask-question-anti-patterns）
        └─ 校验编排器 stage_config.intake 字段（空依赖符合预期）

Step 2: 项目惯例勘察（Glob 1 次）
        ├─ Glob: AGENTS.md / docs/constitution.md / docs/INDEX.md
        ├─ Glob: .trae/rules/*.md / .trae/fullstack4traev11.config.yaml
        └─ 输出: 项目惯例表（命名规则 / 铁律 / 自定义 stage_config / 反模式）

Step 3: 意图识别（5 种类型）
        ├─ 触发词命中 → 直接分类
        └─ 不命中 → AskUserQuestion（5 种意图选项）

Step 4: Bug 录入触发词判断（仅问题类触发词走此步）
        ├─ 命中 → 询问"是否作为 bug 单录入？"
        │   ├─ 用户同意 → 走 Step 5(bug-fix)
        │   └─ 用户拒绝 → 按"一般咨询"处理 + 状态卡 health=🟡 degraded
        └─ 未命中 → 跳过

Step 5: 路由决策
        ├─ project-init → Stage 0 Plan
        ├─ change-start（新功能/重构）→ Stage 0 Plan
        ├─ change-start（doc-sync）→ Stage 1 Spec 或 Stage 5 Accept（lite）
        ├─ bug-fix → Stage 6 Bug Fix（独立支线）
        └─ project-health → Stage 7 Project Health（异步自检）

Step 6: 初始化状态卡（3 类选其一）
        ├─ project 级 → {project}/docs/specs/.state-card.md
        ├─ change 级 → docs/specs/changes/{id}/.state-card.md
        └─ bug 级 → docs/bugs/{id}.md + .state-card.md

Step 7: 交接下一 stage
        ├─ 状态卡 next_stage 字段填写
        ├─ state-card-validator.py 校验 PASS
        └─ stage-gate.py 切换确认
```

---

## 完整铁律（10 条）

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

---

## 完整反例（4 条）

### 反例 1：无意图识别直接动手

**现象**: 收到需求立即写 spec.md，跳过意图识别。

**根因**: 觉得"用户说啥就是啥"，不假思索。

**教训**: 跳过意图识别 = 路由错误概率上升 → 后续 stage 返工。

**正确替代**: 永远先识别意图（5 种类型），不确定就 AskUserQuestion。

### 反例 2：跳过状态卡初始化

**现象**: 不立状态卡直接进 Stage 0 Plan。

**根因**: 觉得状态卡"是文档工作"，跳过更快。

**教训**: 状态卡是任务真相源之一（Article XII）。无状态卡 = 后续 stage 无法判断起点。

**正确替代**: 每个 change 必初始化状态卡（state-card-init.md 模板）。

### 反例 3：强制创建 bug 单

**现象**: 用户说"报错"，主上下文直接创建 bug 单，不询问。

**根因**: 觉得"报错 = bug"，自动归类。

**教训**: 用户可能只是想咨询，不是要修 bug。强制创建 = 后续维护负担 + 用户被冒犯。

**正确替代**: 询问"是否作为 bug 单录入？" → 用户同意才创建。

### 反例 4：未勘察项目惯例

**现象**: 不 Glob 项目 AGENTS.md / docs/ 就直接初始化。

**根因**: 不知道 V11 §0.5 加载协议要求。

**教训**: 项目惯例可能与 V11 默认不同（如命名规则 / 铁律 / stage_config 覆盖）。未勘察 = 与项目惯例冲突。

**正确替代**: Step 2 必走 Glob 1 次（AGENTS.md / docs/ / .trae/rules/）。

---

## 完整交接协议

### Intake → Stage 0 Plan（change-start / project-init）

```yaml
hand_over:
  stage_id: "-1/intake"
  stage_skill: skills/01-intake/SKILL.md
  status: completed
  health: "🟢 on-track"
  artifacts:
    - path: docs/specs/changes/{id}/.state-card.md
      type: file
      evidence: "状态卡初始化（change 级）+ next_stage=0/plan"
    - path: docs/specs/changes/{id}/spec.md（project-init 才有）
      type: file
      evidence: "项目级 spec 初始化"
  gate_result:
    status: PASS
    gate: state-card-validator.py
    output: "状态卡字段完整 + 路由决策表齐全"
  next_stage:
    id: "0/plan"
    skill_name: skills/02-plan/SKILL.md
    expected_inputs: [状态卡 + 项目惯例表 + 意图分类结果]
    prerequisites: [意图识别 PASS, 状态卡初始化 PASS, Glob 项目惯例 PASS]
```

### Intake → Stage 6 Bug Fix（bug-fix）

```yaml
hand_over:
  stage_id: "-1/intake"
  stage_skill: skills/01-intake/SKILL.md
  status: completed
  health: "🟢 on-track"
  artifacts:
    - path: docs/bugs/{id}.md
      type: file
      evidence: "Bug 单 6 字段齐全（症状/期望/复现/影响/环境/触发词）"
    - path: docs/bugs/{id}/.state-card.md
      type: file
      evidence: "Bug 状态卡初始化 + next_stage=6/bug-fix"
  gate_result:
    status: PASS
    gate: state-card-validator.py
    output: "Bug 单状态卡字段完整"
  next_stage:
    id: "6/bug-fix"
    skill_name: skills/12-bug-fix/SKILL.md
    expected_inputs: [Bug 单 + 状态卡 + 复现步骤]
    prerequisites: [Bug 单 6 字段齐全, 状态卡 OPEN 状态]
```

---

## 启动检查清单（必走）

```
[ ] Step 1 完成: 加载本 skill + 9 个 references
[ ] Step 2 完成: Glob 项目惯例（AGENTS.md / docs/ / .trae/rules/）
[ ] Step 3 完成: 意图识别（5 种类型之一）
[ ] Step 4 完成: Bug 录入触发词判断（如适用）
[ ] Step 5 完成: 路由决策（写入状态卡 next_stage）
[ ] Step 6 完成: 状态卡初始化（3 类选其一）
[ ] Step 7 完成: state-card-validator.py PASS
[ ] Step 7 完成: stage-gate.py 切换确认
```

---

## 关联引用

- SKILL.md 入口：[SKILL.md](SKILL.md)
- 工作流：[workflows/](workflows/)
- 方法论：[references/](references/)
- 模板：[templates/](templates/)
- 反例：[anti-patterns/](anti-patterns/)
- 公共 references：[../../references/](../../references/)
