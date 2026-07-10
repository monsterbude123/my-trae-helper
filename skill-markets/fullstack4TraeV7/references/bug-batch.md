# Bug-Batch 轻量缺陷修复链路

> **定位**：Bug 修复的认知顺序与功能开发相反。功能开发是"先规划后建造"，Bug 修复是"先调查修复后总结"。强行走完整链 = 用手术方案模板去套急诊。
>
> **适用**：单个或批量 bug 修复。不适用：新功能、重构、跨模块架构调整。
>
> **上游**：用户报 bug（口语化）
> **下游**：buglist.md → per-bug debugger → retro-spec.md + DOC SYNC

---

## 一、核心命题

```
功能开发:  Plan → Spec → Contract → Code     (先想清楚再动手)
Bug 修复:   Fix → Retro-Spec → DOC SYNC       (先动手修，再总结归档)
```

**为什么 Bug 修复不能走完整链？**

| 痛点 | 走完整链的后果 | Bug-Batch 的解药 |
|------|-------------|-----------------|
| 修一个 typo 也要写 proposal | 写 proposal 的时间是修 bug 的 10 倍 | buglist 一句话描述即可 |
| Bug 根因不知道就要写 spec | spec 描述的是"预想的正确行为"，bug 的根因是未知的 | 先 debug 找根因，再 retro-spec 记录 |
| 修 3 个相关 bug 要 3 份 proposal + 3 份 spec | 文档爆炸，3 个 change 目录互相引用 | 1 个 buglist 管 N 个 bug，1 份 retro-spec 汇总 |
| 线上紧急修复不能等 | 走完整链要 8 个阶段，等不了 | Bug-Batch 3 步：列清单→修→总结 |

---

## 二、Bug-Batch 三阶段

```
Phase B.1: Buglist      intake-light: bug识别 → buglist.md + 影响面 + 状态卡
Phase B.2: Fix          逐个 debugger: 复现→根因→🔴RED→🟢GREEN→回归
Phase B.3: Retro-Spec   修复后评估: retro-spec.md + DOC SYNC + 回归全绿
```

**单 bug 也可以走 Bug-Batch**：buglist 只有 1 个条目，流程不变。

---

## 三、Phase B.1: Buglist

### 3.1 输出工件

`docs/specs/changes/{change}/buglist.md`：

```markdown
# Buglist — {change-name}

> 创建日期: {YYYY-MM-DD}

## 总览

- Bug 总数: {N}
- 严重度分布: 🔴严重{N} 🟡中等{N} 🟢轻微{N}

## Bug 列表

| # | 标题 | 严重度 | 复现步骤 | 影响面 | 状态 |
|---|------|--------|---------|--------|------|
| B1 | {一句话描述} | 🔴/🟡/🟢 | {简述或"已知"} | {涉及文件/模块} | ⏳/✅ |
| B2 | ... | | | | |

## 影响面汇总

- 涉及文件: [list]
- 涉及模块: [list]
- 风险点: [如有契约变更则标注 HIGH]

## 修复顺序

{B1 → B2 → B3 的原因：依赖关系 / 严重度排序}
```

### 3.2 状态卡

轻量版状态卡，持久化到 `docs/specs/changes/{change}/.state-card.md`：

```markdown
# 📍 当前状态卡

## 基本信息
- **变更**: {change-name}
- **链路**: bug-batch
- **当前阶段**: B.1 Buglist
- **最后产出**: {YYYY-MM-DD HH:MM}

## Bug 进度
| # | 标题 | 状态 |
|---|------|------|
| B1 | xxx | ⏳ |
| B2 | xxx | ⏳ |

## 下一步
→ B.2 Fix: 加载 debugger 修复 B1

## 阻塞
- 无
```

### 3.3 跳过项

Bug-Batch 明确跳过的阶段（不需理由，链路本身定义如此）：

| 跳过阶段 | 原因 |
|---------|------|
| Proposal | Bug 没有 "Why"，bug 就是问题本身 |
| Spec（前置） | 根因未知时无法写出正确行为的 spec |
| Contract | Bug 修复不应引入新契约；如有契约变更 → 不是纯 bug，退回 intake 重新分类 |
| Plan / Design | buglist 本身就是执行计划 |
| Closure-Define | 不需要业务闭环定义 |

---

## 四、Phase B.2: Fix（逐个 debugger）

### 4.1 逐 bug 修复

每个 bug 走 [debugger agent](../agents/debugger.md) 完整流程：

```
per bug:
  1. 复现问题（门禁 1）
  2. 收集证据（门禁 2）
  3. 验证假设 → 根因证据清单（门禁 3）
  4. 🔴RED: 编写失败测试
  5. 🟢GREEN: 最简修复
  6. 回归验证（当前 bug 测试 + 之前已修 bug 测试 + 全量回归）
```

### 4.2 修复顺序

按 buglist 中的顺序逐个修复，不并行（避免合并冲突）。每修完一个 bug，更新状态卡。

### 4.3 回归策略

```
修 B1 → 跑 B1 测试（通过）→ 跑全量回归（确认无回归）
修 B2 → 跑 B1+B2 测试（通过）→ 跑全量回归
...
修 BN → 跑全部 B1..BN 测试（通过）→ 跑全量回归
```

---

## 五、Phase B.3: Retro-Spec（修复后评估）

> **核心思想**：修完后反向输出一份 retro-spec，记录"实际修了什么、为什么这样修、影响是什么"。
> 这不是前置的 spec，而是后置的**修复总结**。

### 5.1 输出工件

`docs/specs/changes/{change}/retro-spec.md`：

```markdown
# Retro-Spec — {change-name}

> 修复日期: {YYYY-MM-DD}
> 关联 buglist: buglist.md

## 修复总览

| Bug | 根因 | 修复方式 | 涉及文件 | 测试 |
|-----|------|---------|---------|------|
| B1 | {根因简述} | {修复简述} | {files} | {test files} |
| B2 | ... | | | |

## 修复详情

### B1: {标题}

- **根因**: {具体代码行 + 为什么是根因}
- **修复**: {修复了什么，最简 diff 描述}
- **测试**: {新增/修改的测试文件 + 覆盖场景}
- **影响面**: {只改了哪些地方}

### B2: ...

## 回归验证

- 全量测试: {N} passed, {M} failed, {X} skipped
- 覆盖: 新增回归测试 {N} 个

## 文档同步（DOC SYNC）

- [ ] 模块文档变更记录已更新
- [ ] 如涉及接口变更 → 契约已更新
- [ ] docs/specs/changes/{change}/ 路径下无残留引用
```

### 5.2 DOC SYNC

修复完成后必须同步文档：

```
1. 更新 docs/modules/{module}.md 的变更记录
2. 如接口签名变更 → 更新 contracts/ 对应契约
3. 更新 .state-card.md 为 completed
```

---

## 六、门禁链

| 阶段 | 必须满足 | 不通过则 |
|------|---------|---------|
| Buglist | buglist.md 非空 + 影响面清单 + 状态卡 | 不进 Fix |
| Fix (per bug) | 根因证据清单完整 + 🔴RED + 🟢GREEN + 回归通过 | 不进下一 bug |
| Retro-Spec | retro-spec.md 完整 + DOC SYNC 完成 + 全量回归绿 | 不提交 |

---

## 七、与完整链的对比

| 维度 | fullstack 完整链 | Bug-Batch 链 |
|------|-----------------|-------------|
| 阶段数 | 9 (0→8) | 3 (B.1→B.3) |
| Proposal | 需要 | 不需要 |
| 前置 Spec | 需要 | 不需要（后置 retro-spec） |
| Contract | 需要 | 不需要（除非 bug 涉及契约变更） |
| Plan/Design | 需要 | 不需要（buglist 替代） |
| TDD | 🔴RED→🟢GREEN | 🔴RED→🟢GREEN（不变） |
| DOC SYNC | 前置 + 后置 | 仅后置 |
| Review | 7 维度量化打分 | 可选轻量 review |
| 适用场景 | 新功能 / 重构 / 架构变更 | Bug 修复 / 紧急修复 |

---

## 八、边界情况

### 8.1 Bug 修复中发现需要改契约

🛑 立即停止。这不是纯 bug，是"因设计缺陷导致的行为异常"。退回 intake 重新分类为"重构"或"变更"，走完整链的简化链（跳过 proposal）。

### 8.2 修复中引入新 bug

修复 B1 时发现 B1 的修复导致 B3 → 在 buglist 中追加 B3，标记为"fix-induced"，继续逐 bug 修复。如果连续引入 3 个以上新 bug → 🛑 停止，质疑修复方向。

### 8.3 单 bug 修复

buglist 只有 1 个条目，流程不变。B.1 → B.2 → B.3 照常执行。单 bug 也不走完整链——因为根因未知时无法写 spec。

---

## 九、检查清单

**Buglist 阶段**：
- [ ] buglist.md 已创建，所有 bug 已列出
- [ ] 每个 bug 有严重度 + 影响面 + 状态
- [ ] 修复顺序已确定
- [ ] 状态卡已初始化

**Fix 阶段**（per bug）：
- [ ] 问题已复现
- [ ] 根因证据清单完整
- [ ] 🔴RED 确认
- [ ] 🟢GREEN 确认
- [ ] 回归通过

**Retro-Spec 阶段**：
- [ ] retro-spec.md 完整（每个 bug 有根因 + 修复 + 测试）
- [ ] DOC SYNC 完成（模块文档 + 变更记录）
- [ ] 全量回归全绿
- [ ] 状态卡更新为 completed

---

## 十、反面范例

| 反面（禁止） | 正确（必须） |
|---|---|
| 修 typo 写 proposal | Bug-Batch 链，buglist 一条描述即可 |
| 不确定根因就写 spec 描述"正确行为" | Retro-spec 后置，先 debug 找根因 |
| 3 个相关 bug 建 3 个 change 目录 | 1 个 change，1 个 buglist，1 个 retro-spec |
| Bug 修复改契约不回流 intake | 🛑 退回 intake 重新分类 |
| 修完不写 retro-spec | 必须写，这是唯一的知识沉淀 |
| 修完不跑全量回归 | 逐 bug 累加回归 |
