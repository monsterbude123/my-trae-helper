# 状态卡机制（State Card）

> **定位**：解决"全时间激活 fullstack 时 AI 不知道自己在哪步、用户问'进度'要重新推理"的导航问题。
>
> **触发**：任何 Agent 激活时先输出此卡再干活；用户说"状态"/"定位"/"进度"/"现在到哪了"时立即输出此卡。
>
> **模板**：[templates/state-card.md](../templates/state-card.md)

---

## 一、核心命题

**SDD 是长流程。状态卡是仪表盘。没有状态卡，AI 每次激活都要重新推理"我在哪个阶段"，用户也要重新问。**

```
无状态卡：  Agent 激活 → 凭上下文猜阶段 → 可能猜错 → 走错路 → 用户提醒 → 修正
有状态卡：  Agent 激活 → 先输出状态卡 → 明确阶段+下一步 → 直接干活
```

业界标准（SST3-AI-Harness、agent-rules-books）一致要求：Agent 在每个会话开始或阶段切换时必须输出"current state"。这不是装饰，是导航系统。

---

## 二、状态卡触发时机

| 时机 | 触发方式 | 输出形式 |
|------|---------|---------|
| **Agent 激活时** | 任何 Agent 被加载，第一件事先输出状态卡 | 完整状态卡 |
| **用户问"状态"** | 用户说"状态"/"定位"/"进度"/"现在到哪了"/"继续" | 完整状态卡 |
| **阶段切换时** | fullstack-intake → proposal → spec → contract → design → dev → review → accept | 状态卡 + 阶段切换说明 |
| **任务结束时** | Stop Hook 触发前 | 状态卡 + 下一步建议 |
| **漂移修复后** | feedback-loop 回流完成后 | 状态卡 + 漂移修复确认 |
| **会话开始时** | SessionStart Hook 注入 | 状态卡 + 待办恢复 |

**铁律**：状态卡上限参考 [thresholds.md §累积型工件硬上限](thresholds.md#累积型工件硬上限) per-change 状态卡默认值，不能写成长报告。状态卡是仪表盘，不是日志。

> 阈值配置 → [thresholds.md](thresholds.md)

**检测流程**（不依赖记忆）:
  1. 先检测 REFACTOR_MODE → 存在则自动重置（[§6.4](#64-refactor_mode-自动检测)）
  2. 再 `wc -l` → > 80 → 🛑 不追加，执行重置（[artifact-lifecycle.md §3](artifact-lifecycle.md#3-状态卡四态生命周期)）

---

## 三、状态卡格式

详见 [templates/state-card.md](../templates/state-card.md)。核心五段：

```
1. 基本信息       — 变更名 + 当前阶段 + 阶段名
2. 工件进度       — proposal/specs/contracts/design/tasks/代码 的状态表
3. 健康度         — Spec漂移 / 契约漂移 / 目标对齐度 / TDD 进度
4. 下一步         — 明确的下一个动作
5. 阻塞           — 当前阻塞项（无则填"无"）
```

### 状态符号统一

| 符号 | 含义 |
|------|------|
| ✅ | 已完成且通过验证 |
| ⏳ | 进行中 |
| ❌ | 未开始或存在问题 |
| — | 不适用本变更 |
| 🚫 | 阻塞 |
| 🟢 | 健康度优（≥90%） |
| 🟡 | 健康度中（70-89%） |
| 🔴 | 健康度差（<70%） |

---

## 四、状态卡与各工件的关系

```
状态卡是"派生视图"，不是"原始数据"。
状态卡的字段都来自其他工件，状态卡本身不存储信息。

变更名          ← docs/specs/changes/{change}/ 目录名
当前阶段        ← 最近一次阶段切换的记录
工件进度        ← 各工件文件是否存在 + approved 状态
健康度-Spec漂移 ← 最近一次 Spec Drift Report
健康度-契约漂移 ← 最近一次契约漂移检测
健康度-目标对齐 ← 最近一次目标对齐检查
TDD 进度        ← tasks.md 中 [x]/[ ] 计数 + 测试运行结果
下一步          ← 当前阶段未完成项 / 下一阶段入口
阻塞            ← 当前阻塞清单（来自反馈回流报告）
```

**铁律**：状态卡的字段必须可在工件中追溯。不可凭空写。

---

## 五、状态卡更新规则

### 5.1 阶段切换时更新

```
fullstack-intake → proposal     : 状态卡更新为"00-proposal"，工件进度标 proposal ⏳
proposal → spec       : 状态卡更新为"00-product"，工件进度标 proposal ✅、spec ⏳
spec → contract       : 状态卡更新为"01-contract"，工件进度标 spec ✅、contracts ⏳
contract → design     : 状态卡更新为"10-design"，工件进度标 contracts ✅、design ⏳
design → dev          : 状态卡更新为"20-dev"，工件进度标 design ✅、tasks ✅、代码 ⏳
dev → review          : 状态卡更新为"40-review"，工件进度标代码 ✅（待审）
review → accept       : 状态卡更新为"40-accept"，进入验收
accept → done         : 状态卡标"已完成"，变更移入 archive/
```

### 5.2 工件完成时更新

每完成一个工件，立刻更新该工件在状态卡中的状态：
- 文件创建但未 approved → ⏳
- 文件创建且 approved → ✅
- 文件存在问题 → ❌

### 5.3 健康度更新

- **漂移检测后**：更新 Spec漂移 / 契约漂移 字段
- **目标对齐检查后**：更新 目标对齐度 字段
- **测试运行后**：更新 TDD 进度 字段

### 5.4 阻塞更新

发现阻塞立即登记到状态卡"阻塞"段；阻塞解除立即从状态卡移除。

---

## 六、状态卡持久化

状态卡是派生视图，但需要轻量持久化以便会话恢复。

### 6.1 推荐持久化路径

```
docs/specs/changes/{change}/.state-card.md   ← 隐藏文件，避免污染变更目录
```

### 6.2 SessionStart Hook 注入

SessionStart Hook 读取 `.state-card.md`，注入到 AI 上下文，让新会话立即"知道自己在哪"。

### 6.3 Stop Hook 检查

Stop Hook 检查 `.state-card.md` 是否与最新工件状态一致；不一致则提示 AI 更新。

详见 [templates/hooks/session-start.ps1](../templates/hooks/session-start.ps1) 和 [templates/hooks/tasks-integrity.ps1](../templates/hooks/tasks-integrity.ps1)。

### 6.4 REFACTOR_MODE 自动检测

> 🛑 不依赖记忆 — 机械检测，自动触发。Agent 不需要"记得"回流时要重置状态卡。

每次状态卡更新前（阶段切换 / SessionStart / Stop Hook），必须执行：

```
检测: docs/changes/{id}/REFACTOR_MODE.md 是否存在
  ├── 存在 → 🛑 不追加，执行重置:
  │     1. 旧卡 mv → _invalidated/v{N}/.state-card.md
  │     2. 从模板生成新卡（阶段 = Intake，工件全 ❌）
  │     3. 输出: "检测到 REFACTOR_MODE，状态卡已自动重置 (v{N+1})"
  └── 不存在 → 正常追加
```

此检测在超限检测（`wc -l > 80`）之前执行。存在 REFACTOR_MODE 时不检查行数。

---

## 七、状态卡速查口诀

```
进入新阶段 → 先看卡 → 卡说下一步 → 干下一步 → 干完更新卡
用户问进度 → 立刻看卡 → 输出卡
漂移修复后 → 更新卡 → 卡说继续 → 继续
会话开始 → Hook 注入卡 → AI 知道在哪
```

---

## 八、检查清单

Agent 输出状态卡前自检：

- [ ] 状态卡行数 ≤ thresholds.md 配置值
- [ ] 基本信息：变更名 + 当前阶段（含阶段编号 /8）
- [ ] 工件进度：6 个工件全部列出（无则 — ）
- [ ] 健康度：4 项全部填写（无漂移则 ✅ 无）
- [ ] 下一步：明确动作，不模糊
- [ ] 阻塞：有则列，无则填"无"
- [ ] 所有字段可在工件中追溯（不凭空写）

---

## 九、反面范例

| 反面（禁止） | 正确（必须） |
|---|---|
| Agent 激活直接干活不输出状态卡 | 先输出状态卡再干活 |
| 状态卡写成长报告 | thresholds.md 配置值内的仪表盘 |
| 状态卡字段凭空写 | 所有字段可在工件中追溯 |
| 阶段切换不更新状态卡 | 立即更新阶段编号 |
| 用户问进度时重新推理阶段 | 直接读 `.state-card.md` 输出 |
| 漂移修复后不更新健康度 | 立即更新漂移字段 |
| 阻塞解除仍保留在状态卡 | 立即移除 |
| 回流时不重置状态卡 | 旧卡归档 _invalidated/，新卡从模板重置 |
| 状态卡超过 30 行继续追加 | 🛑 执行重置（artifact-lifecycle.md §3） |

---

## 十、与其他方法论的关系

| 方法论 | 关系 |
|--------|------|
| [fullstack-intake.md](fullstack-intake.md) | fullstack-intake 阶段产出第一版状态卡 |
| [feedback-loop.md](feedback-loop.md) | 漂移修复后更新状态卡健康度 |
| [contract-first.md](contract-first.md) | 契约阶段切换时更新状态卡 |
| [quantitative-acceptance.md](quantitative-acceptance.md) | 验收打分卡作为状态卡的"验收扩展" |
| [tdd-workflow.md](tdd-workflow.md) | TDD 进度作为状态卡的健康度字段 |
| [artifact-lifecycle.md](artifact-lifecycle.md) | 状态卡四态生命周期 + 体积硬上限 + 回流重置 |
| [refactor-protocol.md](refactor-protocol.md) | §3 L1 物理隔离中重置状态卡 |
