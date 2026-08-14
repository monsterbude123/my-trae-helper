# Goal Mode — 原理说明

> 本文件解释 goal-mode 技能的**工作原理**：它如何把"用户的目标"变成"Agent 无法绕过的机械门禁"，以及各组件如何协作。
>
> 版本：v2.0（强门禁模式）

---

## 一句话原理

**goal-mode 把"目标"拆成可验证的验收项，然后用"执行与审计分离 + 外部机械验证器"保证 Agent 只有在产出真实满足验收清单时，才被允许声明完成。**

核心思想来自开源项目 [agent-completion-gate](https://github.com/zhjai/agent-completion-gate)：

```
A rule is advisory — a goal rationalizes past it.
A skill can be skipped — the agent chooses not to invoke it.
Only a gate the agent can't edit, on a path it can't skip,
reading artifacts it can't fake — reliably stops "looks done but isn't."
```

翻译：**规则是建议（可被绕过），技能可被跳过（Agent 选择不调用），只有"Agent 改不了的门禁 + 跳不过的路径 + 读它伪造不了的真实产物"才能真正阻止"看起来完成但其实没完成"。**

---

## 核心问题：为什么要"机械门禁"？

Agent 有天然动机"声称完成"——它无法感知自己是否真的完成任务，只会根据上下文推断"该做完了"。

普通 skill 或 prompt 约束的弱点：

| 约束方式 | 弱点 | 能否绕过 |
|---------|------|---------|
| Prompt 规则（"必须审计"） | Agent 可跳过，直接说"完成" | ✅ 能 |
| 子代理审计（"委托 auditor"） | Agent 可不委派，自己声称 | ✅ 能 |
| 记忆 / 历史对话 | 记录的是"信念"，不是"验证过的真值" | ✅ 能 |

goal-mode v2.0 的解法：在所有这些 **advisory（指导性）** 层下面，加一层 **mechanical（机械性）** 层——**外部脚本读真实产物，只有它才能写 `complete`**。

---

## 架构总览

```
┌─────────────────────────────────────────────────────────────┐
│  Layer 1-2  advisory 层（指导 Agent 行为，可被跳过）          │
│   ├─ SKILL.md 六步审计协议 + 三大铁律                        │
│   └─ goal-auditor 子代理（执行审计）                         │
├─────────────────────────────────────────────────────────────┤
│  Layer 3-5  mechanical 层（机械执行，无法绕过）⭐             │
│   ├─ gate/verify-goal.py        外部验证器（唯一可写 complete）│
│   ├─ gate/acceptance_manifest.yaml 验收清单（人类冻结）        │
│   └─ state/completion_candidate.yaml 运行时状态               │
├─────────────────────────────────────────────────────────────┤
│  Layer 6  Gate 接线（项目级门禁）                             │
│   └─ scripts/goal-mode-guard.py → .husky/pre-commit          │
└─────────────────────────────────────────────────────────────┘
```

- **advisory 层**：指导 Agent"该怎么工作、怎么审计"，优化行为质量。
- **mechanical 层**：强制执行"是否真的完成"，Agent 物理上无法绕过。
- **Gate 接线**：把机械层接入 git 提交门禁，篡改状态/产物在提交时被阻断。

---

## 状态机（四种状态）

goal-mode 用明确的**状态机**表示目标完成进度，核心是：**Agent 只能"提议完成"，不能"判定完成"**。

```
in_progress ──► candidate_complete ──► [外部验证器] ──► complete
     ▲                                        │
     └────────────── blocked ◄────────────────┘
```

| 状态 | 含义 | 谁可以写入 |
|------|------|-----------|
| `in_progress` | Agent 正在工作 | Agent |
| `candidate_complete` | Agent 提议完成，等待验证 | Agent（只能提议） |
| `complete` | 验证通过，目标达成 | **仅外部验证器** |
| `blocked` | 验证失败，需要返工 | 外部验证器 |

**关键安全不变量**：Agent 写不了 `complete`。如果 Agent 试图直接把状态写成 `complete`，`goal-mode-guard.py` 会发现"state 为 complete 但验证器未运行"，在 git 提交时被 BLOCK。

---

## 数据流（一次完整目标执行）

下面以"让测试通过"为目标，走一遍完整流程：

```
1. 目标登记
   goal-mode 拆解目标 → 提炼验收项 → 写入 gate/acceptance_manifest.yaml
   （例如: checks = [command_exit_zero: "pytest tests/ -v"]）
   请求用户确认后冻结 → 状态置 in_progress

2. 执行工作
   委派执行子 Agent 修代码 / 写产物
   完成后把 state/completion_candidate.yaml 的 status 写为 candidate_complete
   （Agent 只能写到这里，到此为止）

3. 机械验证
   委托 goal-auditor 子代理 → 调用外部验证器:
     python gate/verify-goal.py --manifest gate/acceptance_manifest.yaml \
                                --candidate state/completion_candidate.yaml

4. 验证器判定
   verify-goal.py 只读真实产物（跑 pytest / 查文件 / 查内容），
   不读 Agent 的任何"声明"。
   - 全部通过 → 把 state 写为 complete → "COMPLETE-OK"
   - 有失败   → state 置 blocked → 报告失败项 → 返回工作
```

**重点**：验证器读的是**真实产物**（文件内容、命令退出码），不是 Agent 的自述。Agent 说"我做完了"不会改变验证结果——**只有产物真的满足验收清单，`complete` 才会被写入**。

---

## 组件职责

| 组件 | 路径 | 职责 | 谁可改 |
|------|------|------|--------|
| 状态契约 | `gate/STATE_MACHINE.md` | 定义 4 态状态机 + 安全不变量 | 人类 |
| 外部验证器 | `gate/verify-goal.py` | 读真实产物，唯一可写 `complete` | 人类 |
| 验收清单 | `gate/acceptance_manifest.yaml` | 从目标提炼的验收项，validation 的依据 | 人类冻结 |
| 运行时状态 | `state/completion_candidate.yaml` | Agent 工作进度 + 提议完成 | Agent + 验证器 |
| 审计子代理 | `agents/auditor.md` | 存在 gate 时调验证器；否则手动六步审计 | - |
| 监工子代理 | `agents/goal-mode.md` | 拆解目标、委派执行/审计/规划、管进度 | - |
| 规划子代理 | `agents/planner.md` | 遇到挑战时调整计划 | - |
| 项目忠实 | `scripts/goal-mode-guard.py`（项目侧） | git 提交门禁，检测状态篡改 | guard-smith |

---

## 验收清单（acceptance_manifest.yaml）

验收清单是"机械验证的依据"，由目标拆解而来，**Agent 草拟、人类确认后冻结**。支持以下检查类型：

```yaml
goal: "让测试套件通过"
checks:
  - id: file_exists         # 产物文件是否存在
    type: file_exists
    path: "artifacts/report.json"
  - id: content_contains    # 文件是否包含目标内容
    type: file_contains
    path: "src/config.ts"
    substring: "production-api.example.com"
  - id: test_pass           # 命令退出码是否为 0
    type: command_exit_zero
    command: "pytest tests/ -v"
  - id: data_points         # 数据点数是否达标
    type: min_series_points
    path: "artifacts/report.json"
    series: "series_a"
    min_points: 3
```

**原则**：每一项都必须是**机器可判定的**（文件在不在 / 命令成不成功 / 内容含不含 / 数量够不够），不允许"看起来没问题"这类模糊项。

---

## 安全不变量（为什么 Agent 绕不过）

| # | 不变量 | 实现 | 若违反 |
|---|--------|------|--------|
| 1 | gate/ 目录受保护 | project 侧 CODEOWNERS / guard 校验 | Agent 改验收清单=作弊 |
| 2 | 验证器只读真实产物 | `verify-goal.py` 不读 state 的 claim | Agent 自述可伪造结果 |
| 3 | 未知项 fail-closed | 无对应 check 的项 = blocked | Agent 可漏检 |
| 4 | 唯一完成信号 | 只有验证器能写 `complete` | Agent 可自判完成 |
| 5 | 产物是敌对数据 | 验证器用确定性检查，不把产物当指令执行 | 产物内容可注入 |
| 6 | 禁止环境注入 | `python3 -E` 执行验证器 | 环境变量可污染验证 |

---

## 两种工作模式

| 模式 | 触发条件 | 完成验证方式 |
|------|---------|-------------|
| **强门禁** | 存在 `gate/verify-goal.py` | 外部验证器机械判定 |
| **手动审计** | gate 不存在 | goal-auditor 六步门禁（DERIVE→PRESERVE→IDENTIFY→INSPECT→JUDGE→PROVE） |

强门禁是"硬兜底"，手动审计是"无 gate 时的降级"。两者都保证：**未通过审计 = 未完成**。

---

## Gate 门禁（git 层）

`scripts/goal-mode-guard.py`（项目侧，由 guard-smith 维护）在 `.husky/pre-commit` 阶段对 goal-mode 做检查：

- **state 状态合法性**：`complete/candidate_complete/in_progress/blocked` 之外的状态 → 警告
- **非法写 complete**：state 为 `complete` 但验证器不存在 / 缺 verdict → **BLOCK**（阻断提交）
- **gate 完整性**：`verify-goal.py` 缺 `sys.exit`、验收清单缺 `goal`/`checks` → 警告

这样，即使 Agent 在执行期试图"跳过验证直接写 complete"，也会在 git 提交时被机械阻断。

---

## 与普通"目标管理"工具的区别

| 能力 | 普通待办/目标 | goal-mode |
|------|--------------|-----------|
| 追踪进度 | ✅ | ✅ |
| 拆解子任务 | ✅ | ✅ |
| 阻塞检测 | 部分 | ✅（连续 3 turn 才标记） |
| **完成是否被验证** | ❌ 靠自觉 | ✅ 靠外部验证器 |
| **能否绕过完成判定** | ✅ 能 | ❌ 不能（机械层） |
| 门禁接入 git | ❌ | ✅（pre-commit 阻断） |

---

## 相关文件导航

- 完整协议与铁律：[SKILL.md](SKILL.md)
- 状态机契约：[gate/STATE_MACHINE.md](gate/STATE_MACHINE.md)
- 外部验证器实现：[gate/verify-goal.py](gate/verify-goal.py)
- 验收清单模板：[gate/acceptance_manifest.yaml](gate/acceptance_manifest.yaml)
- 联网调研结论：[report-20260814.md](report-20260814.md)
- 子代理定义：[agents/](agents/)

---

## 参考来源

- [agent-completion-gate](https://github.com/zhjai/agent-completion-gate) — 状态机 + 外部验证器设计蓝本
- [make-no-mistakes](https://github.com/momomuchu/make-no-mistakes) — 三铁律 + 篡改检测
- [ProtocolForge](https://github.com/gitstq/protocolforge) — Hook 门控范式