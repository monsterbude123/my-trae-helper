# 00-fullstack-intake / 定位环节方法论（fullstack-intake）

> **定位**：fullstack 流水线的新第 0 步。在 proposal 之前先"定位"——明确意图、评估影响面、选流水线、产出状态卡。
>
> **上游**：用户原始需求（口语化）
> **下游**：`00-proposal/fullstack-proposal-writer.md`（基于 fullstack-intake 输出做提案）

---

## 一、核心命题

**没有定位就开干 = AI 绕路。AI 之所以"先绕一会"，是因为它不知道该走哪条路。定位环节是 30 秒决策，省掉 30 分钟绕路。**

```
无 fullstack-intake：  用户需求 → AI 直接 proposal → 写到一半发现是 bug 不是新功能 → 返工
有 fullstack-intake：  用户需求 → fullstack-intake 定位 → 识别为 bug 修复 → 走 fullstack-debugger 链路 → 直接修复
```

业界标准（agent-rules-books、AGENTS.md、DeerFlow）一致要求：Agent 接到需求后第一件事是"分类+定位+影响面评估"，而不是直接进入工作。

---

## 二、为什么需要定位环节

| 痛点 | 不做 fullstack-intake 的后果 | fullstack-intake 的解药 |
|------|------------------|--------------|
| AI 不知道走哪条链 | 全部走 proposal→spec→dev 重型流水线，简单 bug 也走全流程 | 30 秒分类：fullstack / ponytail / fullstack-debugger |
| AI 不评估影响面 | 改了一处影响十处，验收时崩盘 | fullstack-intake 强制评估影响面（grep / GitNexus） |
| AI 不发状态卡 | 用户问"进度"要重新推理 | fullstack-intake 产出第一版状态卡 |
| 用户反复提醒 fullstack | AI 不会自动激活 fullstack | fullstack-intake 输出"流程定位卡"，明确告知进入 fullstack |
| 大需求走轻量流程 | 简单走完发现漏了关键环节 | fullstack-intake 评估复杂度，选完整链 vs 轻量链 |

---

## 三、fullstack-intake 的四步流程

```
① 意图识别     → 用户在说什么？新功能？bug？重构？文档？
② 影响面评估   → 涉及哪些文件/模块/契约？（grep / GitNexus impact）
③ 流程选择     → 走哪条链路？（fullstack / ponytail / fullstack-debugger / fullstack-doc-updater）
④ 状态卡初始化 → 产出第一版状态卡 + 流程定位卡
```

### 3.1 意图识别

| 用户说什么 | 意图 | 走哪条链 |
|-----------|------|---------|
| "新功能""添加""实现""做一下" | 新功能开发 | fullstack 完整链 |
| "bug""报错""不工作""异常" | Bug 修复 | bug-batch 链（批量/单bug） |
| "重构""优化""清理" | 重构 | fullstack 简化链（无 proposal） |
| "文档""codemap""架构图" | 文档维护 | fullstack-doc-updater 链 |
| "改一行""小调整""修个值" | 小修改 | ponytail 链（不走流水线） |
| 含糊不清 / 多义 | 模糊需求 | AskUserQuestion 澄清后再分类 |

**铁律**：意图不明时不要猜，用 AskUserQuestion 澄清。30 秒澄清 > 30 分钟返工。

### 3.2 影响面评估

fullstack-intake 必须强制评估影响面，输出"影响面清单"：

```markdown
## 影响面清单

### 直接受影响
- 文件: [list，来自 grep / Glob]
- 模块: [list，来自 docs/modules/ 索引]
- 契约: [list，来自 contracts/api-contracts.md 检索]

### 间接受影响
- 调用方: [list，来自 GitNexus impact 或 grep]
- 测试: [list，来自 grep test 文件]
- 文档: [list，来自 docs/modules/ 索引]

### 风险点
- [高风险：如改了公共契约]
- [中风险：如改了内部接口]
- [低风险：如改了私有实现]
```

**工具优先级**：
1. **GitNexus impact**（如有 MCP）— 最准，能查跨模块调用图
2. **Grep + Glob**（基础）— 搜函数名/类型名/路由名
3. **SearchCodebase**（语义搜索）— 模糊意图搜代码

### 3.3 流程选择

fullstack-intake 输出"流程定位卡"：

```markdown
# 🎯 流程定位卡

## 意图
- 类型: {新功能 / bug修复 / 重构 / 文档 / 小修改}
- 复杂度: {简单 / 中等 / 复杂}

## 选定流程
- [x] fullstack 完整链（复杂新功能）
- [ ] fullstack 简化链（重构，无 proposal）
- [ ] bug-batch 链（bug 修复）
- [ ] fullstack-debugger 链（单 bug 诊断）
- [ ] ponytail 链（小修改）
- [ ] fullstack-doc-updater 链（纯文档）

## 链路（如选 fullstack）
fullstack-intake → proposal → spec → contract → design → dev → review → accept

## 跳过项（如有）
- [ ] 跳过 proposal（理由：重构，无新 Why）
- [ ] 跳过 contract（理由：单模块，无跨端契约）

## 进入下一阶段
→ 加载 fullstack-proposal-writer，输入本定位卡 + 影响面清单
```

**铁律**：跳过任何阶段必须有明确理由，记入流程定位卡。无理由跳过 = 违反铁律。

### 3.4 状态卡初始化

fullstack-intake 产出第一版状态卡（参考 [state-card.md](state-card.md)）：

```markdown
# 📍 当前状态卡

## 基本信息
- **变更**: {从用户需求提炼的 change-name}
- **当前阶段**: 1 / 8
- **阶段名**: fullstack-intake

## 工件进度
| 工件 | 状态 | 路径 |
|------|------|------|
| proposal.md | — | docs/specs/changes/{change}/proposal.md |
| spec.md | — | docs/specs/changes/{change}/specs/{cap}/spec.md |
| contracts/ | — | docs/specs/changes/{change}/contracts/ |
| design.md | — | docs/specs/changes/{change}/design.md |
| tasks.md | — | docs/specs/changes/{change}/tasks.md |
| 代码 | — | src/... |

## 健康度
- **Spec 漂移**: — （未开始）
- **契约漂移**: —
- **目标对齐度**: 100% 🟢（刚开始）
- **TDD 进度**: —

## 下一步
- 加载 fullstack-proposal-writer，输入流程定位卡 + 影响面清单

## 阻塞
- 无
```

---

## 四、fullstack-intake 的输出工件

fullstack-intake 完成后必须输出三个工件：

| 工件 | 路径 | 用途 |
|------|------|------|
| **流程定位卡** | 输出到对话（不持久化） | 告诉用户走哪条链 |
| **影响面清单** | 输出到对话（持久化到 proposal.md 的影响面段） | 后续 fullstack-proposal-writer / fullstack-implementer 共用 |
| **第一版状态卡** | `docs/specs/changes/{change}/.state-card.md` | 后续所有 Agent 读取定位 |

---

## 五、fullstack-intake 与其他阶段的关系

```
用户需求
    ↓
[fullstack-intake] ← 本方法论
    ├── 意图识别 → 选链
    ├── 影响面评估 → 输出影响面清单
    ├── 流程定位卡 → 告知用户
    └── 状态卡初始化 → 持久化
    ↓
[proposal] ← 加载 fullstack-proposal-writer
    输入: 流程定位卡 + 影响面清单
    输出: proposal.md（含影响面段）
```

**关键约束**：
- fullstack-intake 不写 proposal/specs/contract/design/tasks，只做定位
- fullstack-intake 不做技术决策，只做流程决策
- fullstack-intake 30 秒内完成（评估工具调用应并行）

---

## 六、fullstack-intake 的并行加速

fullstack-intake 的四步可以部分并行：

```
并行批 1: 意图识别 + 影响面评估（grep + GitNexus 并行调用）
    ↓
批 1 结果 → 流程选择
    ↓
并行批 2: 流程定位卡 + 状态卡初始化
```

**工具调用并行规则**：
- 影响面评估的多个 grep/Glob 调用应并行（最多 5 个并发）
- GitNexus impact 调用单独发（它是单次重型查询）
- SearchCodebase 调用单独发（避免与 grep 冲突）

---

## 七、检查清单

fullstack-intake 完成前自检：

- [ ] 意图已识别（新功能/bug/重构/文档/小修改）
- [ ] 影响面清单已输出（直接 + 间接 + 风险点）
- [ ] 影响面评估使用了工具（grep / GitNexus / SearchCodebase），不是凭空猜
- [ ] 流程定位卡已输出（选了哪条链 + 跳过项 + 理由）
- [ ] 第一版状态卡已持久化到 `.state-card.md`
- [ ] 跳过任何阶段都有明确理由
- [ ] 模糊需求已用 AskUserQuestion 澄清
- [ ] 下一步入口已明确（加载哪个 Agent）

---

## 八、反面范例

| 反面（禁止） | 正确（必须） |
|---|---|
| 跳过 fullstack-intake 直接 proposal | 30 秒 fullstack-intake 定位再进 proposal |
| 影响面评估凭空猜 | 必须用 grep / GitNexus 工具 |
| 模糊需求猜意图 | AskUserQuestion 澄清 |
| 不输出流程定位卡 | 必须输出，让用户知道走哪条链 |
| 不初始化状态卡 | 第一版状态卡必须持久化 |
| 简单 bug 走 fullstack 完整链 | 分类后走 bug-batch 链 |
| 大需求走 ponytail | 分类后走 fullstack 完整链 |
| fullstack-intake 做技术决策 | fullstack-intake 只做流程决策 |
| fullstack-intake 写 proposal/spec | fullstack-intake 只定位，不写工件 |
| fullstack-intake 串行调多次工具 | 并行调用加速 |

---

## 九、与其他方法论的关系

| 方法论 | 关系 |
|--------|------|
| [state-card.md](state-card.md) | fullstack-intake 产出第一版状态卡 |
| [contract-first.md](contract-first.md) | fullstack-intake 选 fullstack 链路才会进入 contract 阶段 |
| [feedback-loop.md](feedback-loop.md) | fullstack-intake 评估的影响面是后续漂移检测的基线 |
| [quantitative-acceptance.md](quantitative-acceptance.md) | fullstack-intake 的影响面清单是验收打分卡"影响面"维度的输入 |
| [planning.md](planning.md) | fullstack-intake 不做技术决策，技术决策交给 fullstack-planner |
