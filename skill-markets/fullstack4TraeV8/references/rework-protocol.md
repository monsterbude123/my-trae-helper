# 返工回流协议（Rework Protocol V8 NEW）

> **定位**：Review FAIL 后的回流深度判定与下游重置。解决"返工到哪里、重走哪些阶段、已执行的知识回流是否作废"。
>
> **触发**：reviewer 判定 REJECT（总分 < 4.0 / 单维度 < 3.0 / 安全 < 4.0 / 闭环 FAIL）

---

## 一、核心命题

**Review FAIL ≠ 随便改改重新审。根因层级决定返工范围。**

```
传统做法:  Review FAIL → implementer 改代码 → 重新 Review
问题:      如果根因在 spec 定义错了，implementer 改代码是错误导向

正确做法:  Review FAIL → 判定根因层级 → 回流对应 Agent → 重走受影响下游
```

---

## 二、回流深度判定树（5 层）

```
Review FAIL
    ↓
判定 FAIL 项的根因属于哪一层？
    │
    ├── L1 实现层（代码写错，spec/contract/plan 都对）
    │    例: 边界条件漏处理、空指针、测试断言写错
    │    回流目标: implementer
    │    重走范围: 🔴RED → 🟢GREEN → 🔍DRIFT CHECK → 重新 Review
    │    无需重置: spec/contract/plan/DOC SYNC
    │
    ├── L2 契约层（契约定义错，spec 对但接口/类型定义有误）
    │    例: api-contracts.md 缺少错误码、字段类型与 spec 不一致
    │    回流目标: contract-writer
    │    重走范围: contract → plan（确认契约一致性）→ DOC SYNC #1（重回流）→ implement → review
    │    需重置: contracts/ 版本号递增、plan 的契约一致性检查、DOC SYNC #1 重新执行
    │
    ├── L3 规格层（spec BDD 场景写错，不符合用户意图）
    │    例: spec.md 的 Scenario 遗漏关键路径、行为定义有歧义
    │    回流目标: spec-writer
    │    重走范围: spec → contract → plan → DOC SYNC #1 → implement → review
    │    需重置: spec.md 版本、contracts/ 重新生成、DOC SYNC #1 重新执行
    │
    ├── L4 目标层（整个方向偏了，proposal 的 What/Why 有问题）
          例: Capabilities 列表遗漏核心功能、Non-Goals 排除了不该排除的
          回流目标: proposal-writer → 用户重新确认
          重走范围: proposal → spec → contract → plan → DOC SYNC #1 → implement → review
          需重置: 整个 change 目录的所有工件
    └── L5 UI/UX 层（页面结构与 prototype 不一致）
          例: 布局方向错、卡片字段缺失、状态只做了部分
          回流目标: implementer
          重走范围: UI 重写 → 重新 Review（Visual Gate 重跑）
          需重置: Visual Gate 截图/报告、acceptance-scorecard UI/UX 维度
```

---

## 三、知识回流重置规则

| 回流层级 | DOC SYNC #1 状态 | 处理方式 |
|---------|:---:|---------|
| L1 实现层 | 无需重置 | modules/ 已同步的是正确的，代码修正即可 |
| L2 契约层 | ⚠️ 需重新回流 | modules/ 中的接口描述可能过时，DOC SYNC #1 重新执行 |
| L3 规格层 | 🛑 需重新回流 | modules/ 中的能力/场景可能错误，DOC SYNC #1 重新执行 |
| L4 目标层 | 🛑 全部作废 | 整个 change 可能方向错误，modules/ 中的相关条目标记为 ⚠️ 待确认 |
| L5 UI/UX | 无需重置 | 代码修正即可，DOC SYNC 状态不变 |

**DOC SYNC #2** 在 L2/L3/L4 返工后必须重新执行，因为代码重新实现了。

---

## 四、下游重置清单

返工发生时，由 reviewer 输出"下游重置清单"，主上下文负责强制执行：

```markdown
# 🔄 返工重置清单: {change-name}

## 回流判定
- FAIL 根因层级: L{N}
- 回流目标: {Agent}
- 重走范围: {阶段列表}

## 重置动作
| # | 工件 | 动作 | 执行者 |
|---|------|------|--------|
| 1 | spec.md 版本号 | 递增 | spec-writer |
| 2 | contracts/ | 重新生成 | contract-writer |
| 3 | design.md 契约一致性段 | 重新验证 | planner |
| 4 | DOC SYNC #1 | 重新执行 | doc-updater |
| 5 | tasks.md 勾选 | 全部回退为 [ ] | planner |
| 6 | DOC SYNC #2 | 重新执行 | doc-updater |

## 旧知识清理
| # | 位置 | 动作 |
|---|------|------|
| 1 | modules/ 中过时条目 | 标记 ⚠️ 待确认 / 删除 |
| 2 | ARCHITECTURE.md 过时段落 | 回退到返工前版本 |
```

---

## 五、3 次返工上限

```
同一 change 的 Review FAIL 计数:
  第 1 次 → 按层级回流，重走
  第 2 次 → 按层级回流，重走 + 主上下文输出警告
  第 3 次 → 🛑 停止，标记 change 为 🔴 高风险
           通知用户: "此变更已 3 次未通过 Review，建议拆分/重新评估"
           用户决定: 继续（主上下文手动放行）还是放弃（归档到 archive/out/）
```

---

## 六、与 feedback-loop 的关系

| 机制 | 触发时机 | 严重度 | 处理 |
|------|---------|--------|------|
| **Rework Protocol** | Review FAIL（打分判定） | 结构性失败 | 按层级重走流水线 |
| **Feedback Loop** | 任意阶段发现漂移 | 局部不一致 | 回流修正后继续 |
| **关系** | Review FAIL 可能包含漂移，但 Review FAIL 的范围更大（包括代码质量、测试覆盖等非漂移问题） | | |

如果 Review FAIL 的根因是契约漂移（contract vs 代码不一致），先走 feedback-loop 判定漂移方向（改契约还是改代码），再走 rework-protocol 回流。

---

## 七、检查清单

- [ ] FAIL 根因层级已判定（L1/L2/L3/L4）
- [ ] 回流目标 Agent 已指定
- [ ] 重走范围已明确
- [ ] 下游重置清单已输出
- [ ] DOC SYNC 重置决策已明确
- [ ] 返工计数已更新
- [ ] 3 次上限未触及
