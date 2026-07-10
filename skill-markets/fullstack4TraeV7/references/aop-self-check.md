# Agent 自省 AOP 机制（V7 NEW）

> Agent 自我切面：在每个产出完成后、移交前，自动触发结构化自检。不侵入 SKILL.md，不硬编码固定列表，Agent 根据上下文动态生成 Q。

---

## 不是"改 skill" — 是 Agent 的自我反思能力

AOP 机制不写入每个 Agent 的 SKILL.md 文件。它是 Agent **内化的行为模式**：

```
传统: Agent 写完 → 移交 → 下游发现上游问题 → 回流 → 修复 → 浪费时间
AOP:  Agent 写完 → 动态生成 QA → 自检 → 修正 → 通过 → 移交
```

区别在于：AOP 是 Agent 在移交前多了一步"我写的东西对吗？"的自问。

---

## AOP 切面模型

```
┌──────────────────────────────────────────┐
│           Agent 生命周期                   │
│                                           │
│  激活 → [PRE 前置切面]                    │
│         检查前置条件是否满足               │
│         如: 需要 contracts/ 存在吗？       │
│         需要用户确认吗？                   │
│              │                            │
│              ▼                            │
│          执行工作                          │
│         （写 proposal / spec / code ...） │
│              │                            │
│              ▼                            │
│        [POST 后置切面] ←── 重点缺失       │
│         Agent 对自己产出做 QA 自检         │
│              │                            │
│              ▼                            │
│          移交下游                          │
└──────────────────────────────────────────┘
```

当前 V7 只有 Cockpit 自检（会话切面）和 reviewer 打分卡（验收切面）。PRE 和 POST 切面**完全缺失**。

---

## POST 后置切面 — 核心机制

### 触发时机

Agent 完成产出后、移交下游前。

### 自省流程

```
1. Agent 回顾自己刚写的内容
2. 根据内容的类型（proposal / spec / contract / design / code）
   动态生成 3-8 个 Q（参考 templates/gate-qa-schema.md 格式）
3. 对每个 Q 逐项回答
4. 判定：全部期望结果 → 移交 / 有非期望结果 → 修正 → 重检
5. QA 汇总附在移交内容末尾
```

### Q 生成策略

Agent 根据**刚产出的内容类型**和**下游 Agent 的要求**动态生成 Q：

| 刚完成 | 下游需要 | 自问方向 |
|--------|---------|---------|
| proposal.md | spec-writer | Capabilities 全吗？Non-Goals 清楚吗？影响面评估了吗？ |
| spec.md | contract-writer | 每个 Requirement 有 error scenario 吗？SHALL 用了吗？ |
| contracts/ | planner | 每个接口有 contract test 骨架吗？domain-models 定义了吗？ |
| design.md | implementer | 每个决策有备选方案对比吗？tasks.md 有 [ ] 格式吗？ |
| 代码 | reviewer | tasks 全部 [x] 了吗？DRIFT CHECK 全过了吗？ |

**策略**：不是从某处复制 Q 列表，而是问自己"下游最关心我会遗漏什么？"

### 示例：contract-writer 自省

```
contract-writer 完成 contracts/ 写入

自省 Q 生成：
  "下游 planner 需要什么？"
  → 需要 domain-models 定义了实体
  → 需要 api-contracts 有明确的 endpoint + request/response
  → 需要 contract test 骨架存在
  → 需要所有接口有对应的 spec

动态生成的 Q:
Q: [POST][P-01][contracts/domain-models.md 是否包含本次变更涉及的所有实体][全部包含/部分包含]
Q: [POST][P-02][contracts/api-contracts.md 中每个 endpoint 是否有请求体和响应体定义][全部有/部分有]
Q: [POST][P-03][contract test 骨架文件是否存在且包含至少 1 个测试][存在/不存在/存在但为空]
Q: [POST][P-04][specs/ 中每个 capability 是否有对应的 contract][全部对应/部分对应]
```

---

## PRE 前置切面

### 触发时机

Agent 激活后、开始工作前。

### 自检流程

```
1. Agent 确认自己需要哪些前置工件
2. 动态生成 2-4 个 PRE Q
3. 检查这些工件是否存在 + 是否满足要求
4. 不满足 → 不开始工作，报告阻塞
```

### 示例：planner 前置切面

```
planner 激活，准备写 design.md

确认前置工件：
  → contracts/ 已 approved？
  → specs/ 已 approved？
  → roundtable meeting-notes 已收敛（如启用）？

Q: [PRE][R-01][contracts/ 四件套是否全部存在且 approved][全部存在且 approved/部分缺失/未 approved]
Q: [PRE][R-02][specs/ 所有 capability 是否已 approved][全部 approved/部分 pending]
Q: [PRE][R-03][roundtable 是否已收敛（如启用）][已收敛/未收敛/不适用]

→ 任何不满足 → 🛑 不开始设计，等待前置条件满足
```

---

## AOP 与 Schema QA 的关系

```
Schema QA (templates/gate-qa-schema.md) = 格式规范（怎么写 Q 和 A）
AOP 自省 (本文件)                        = 行为规范（什么时候自检、自检什么）
```

Agent 在 AOP 切面中使用 Schema QA 格式输出。

---

## AOP 与 report 的关系

```
AOP 自检 FAIL → 阻塞当前阶段 → 需要修正 → 修正成功 → 继续

AOP 自检 FAIL → 但无法自动修正 → 写 report
                报告：哪个 Q 失败了、为什么会失败、尝试了什么修正
                移交给用户决策
```

AOP 是**第一道防线**（自动拦截），report 是**第二道防线**（无法自动处理时升级为人人通信）。

---

## 已有 Agent 的 AOP 激活方式

Agent 不需要修改 SKILL.md。激活方式是**在 SKILL.md 的主指令中加入一条行为规则**：

```
当你完成任何产出后，在移交下游之前：
1. 自问：下游最关心我会遗漏什么？
2. 生成 3-8 个 Schema QA 格式的 Q 并逐条回答
3. 如发现非期望结果 → 修正 → 重新自检
4. 如无法修正 → 写 report-{0X}.md
5. QA 汇总附在移交内容末尾
```

这条规则已经在 V7 的执行原则中（原则 12 "主动建议 Hook 配置" 可以替换为 AOP 自省），不需要改动每个 Agent 文件。

---

## 与其他机制的对比

| 机制 | 何时触发 | 检查什么 | 谁来检查 |
|------|---------|---------|---------|
| Cockpit 自检 | 新会话 | 文件系统 vs 状态卡 | 主 Agent |
| AOP 前置切面 | Agent 激活 | 前置条件是否满足 | 当前 Agent |
| AOP 后置切面 | Agent 完成 | 产出是否满足下游要求 | 当前 Agent |
| Gate QA | 门禁 | 文档/契约/漂移 | implementer |
| Reviewer 打分 | 验收前 | 7 维度量化 | reviewer |
| Report | 异常/打断 | 不可自动恢复的问题 | 任何 Agent |
