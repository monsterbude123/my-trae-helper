---
name: goal-mode
version: "2.0.0"
description: "目标追逐模式 — 绝对严格的任务执行协议。当用户有明确目标、需要严格追踪和逐项验证时使用。激活后 Agent 不得声称任何形式的\"完成\"、\"好了\"、\"搞定\"、\"done\"，除非通过完整审计门禁。支持强门禁模式：Agent 只能提议 candidate_complete，外部验证器决定是否 complete。触发词: /goal、目标追逐、严格验收、不准偷懒、goal mode、进入目标模式。未通过审计 = 未完成。"
triggers: [/goal, /goal-mode, 目标追逐, 进入目标模式, 激活goal]
related: [coding-xinfa, ponytail4Trae, agent-completion-gate]
intent: 目标追逐模式 — 绝对严格的任务执行协议
category: gate
audience: [agent]
---
# Goal Mode — 目标追逐协议 v2.0

> **激活后，Agent 不得以任何形式声称完成，除非通过六步审计门禁。没有例外。**
>
> **v2.0 新增强门禁模式**：Agent 只能 *提议* `candidate_complete`，外部验证器决定是否写入 `complete`。

---

## 版本变更

| 版本 | 变更 |
|------|------|
| v2.0 | 新增强门禁模式（gate/verify-goal.py）、状态机（四态）、验收清单（acceptance_manifest.yaml） |
| v1.0 | 初始版本：六步门禁、三大铁律、Agent 编排 |

---

## 三角心法互引

| 关注维度 | 推荐加载 | 本 skill 覆盖 |
|---------|---------|---------------|
| **通用编码心法 + 完成审计精简版 + 表达风格** | [`coding-xinfa`](../coding-xinfa/SKILL.md) | 不重复 |
| **目标追逐完整协议 + Agent 编排 + 强门禁** | **本 skill** | 全文 |
| **懒人开发模式 / 过度工程审查** | [`ponytail4Trae`](../ponytail4Trae/AGENTS.md) | 不重复 |

---

## 强门禁模式（v2.0 新增）

### 触发条件

- 项目存在 `gate/verify-goal.py`
- 或用户明确要求"用强门禁"

### 状态机

```
in_progress → candidate_complete → [外部验证器] → complete / blocked
     └────────→ blocked (needs-review / missing evidence)
```

| 状态 | 含义 | 谁可以写入 |
|------|------|-----------|
| `in_progress` | Agent 正在工作 | Agent |
| `candidate_complete` | Agent 提议完成 | Agent（只能提议） |
| `complete` | 验证通过 | **仅外部验证器** |
| `blocked` | 验证失败 | 外部验证器 |

### 核心文件

| 文件 | 职责 | 谁可以编辑 |
|------|------|-----------|
| `gate/verify-goal.py` | 外部验证器 | 仅人类（CODEOWNERS） |
| `gate/acceptance_manifest.yaml` | 验收清单 | 仅人类（CODEOWNERS） |
| `state/completion_candidate.yaml` | 运行时状态 | Agent + 验证器 |

### 与六步门禁的关系

| 模式 | 触发 | 流程 |
|------|------|------|
| **强门禁** | gate 存在 | Step 0: 调用 verify-goal.py → 机械验证 |
| **手动审计** | gate 不存在 | Step 1-6: 六步门禁手动审计 |

详细说明见 [gate/STATE_MACHINE.md](gate/STATE_MACHINE.md) 和 [agents/auditor.md](agents/auditor.md)。

---

## 三大铁律

```
1. NO "DONE" WITHOUT AUDIT — 声称完成前必须跑完成审计。任何形式的"好了/搞定/done/finished/完成"都视为声称。
2. NO BLOCKED BEFORE 3 — 同一障碍连续 3 turn 才标记阻塞。不得提前放弃。
3. EVIDENCE > MEMORY — 当前 worktree 状态和命令输出是唯一权威来源。历史对话不是证据。
```

---

## 绝对禁止（违反即违规）

以下行为在 goal-mode 下**绝对禁止**：

```
❌ 01. 声称"应该可以了"、"看起来没问题"、"应该完成了"——没有"应该"，只有"已验证"
❌ 02. 声称"done"、"完成"、"搞定"、"好了"、"works"，且未附审计报告链接
❌ 03. 以"改动很小"为由跳过验证——小改动 = 大盲区
❌ 04. 运行了验证命令但未阅读输出——未读输出 = 未运行
❌ 05. 缩小目标范围以适应"已完成的部分"——不允许重新定义成功
❌ 06. 用更简单/兼容的替代方案偷换原始目标
❌ 07. 跳过审计中的任一步骤
❌ 08. 在目标含多个子任务时，只完成部分就声称"完成"
❌ 09. 用历史对话/记忆替代当前状态检查
❌ 10. 因"太慢/太麻烦"而使用缓存结果替代新鲜运行
❌ 11. 强门禁模式下绕过外部验证器
❌ 12. Agent 自己写入 complete 状态（只有验证器可以）
```

---

## 完成审计协议

### 强门禁模式流程

```
Step 0 - GATE CHECK: 检查 gate/verify-goal.py 是否存在
  存在 → 执行机械验证流程
  不存在 → 执行六步门禁手动审计
```

### 六步门禁（手动审计）

触发条件：Agent 或子 Agent 说出任何完成含义的词语时，**立即触发**。

```
Step 1 - DERIVE:   从目标中提取所有具体需求
Step 2 - PRESERVE: 保持原始范围，不以"已有工作"重新定义成功
Step 3 - IDENTIFY: 对每项需求，确定权威证据类型
Step 4 - INSPECT:  逐项运行验证命令（新鲜运行）
Step 5 - JUDGE:    逐项判定 ✅/❌/⚠️/❓/🚫
Step 6 - PROVE:    汇总结果
```

---

## Agent 架构

| Agent | 角色 | 用途 |
|-------|------|------|
| `goal-mode` | 监工 | 拆解目标、委派执行/审计/规划、管理进度/阻塞/升级、组装验收清单 |
| `goal-auditor` | 审计官 | 独立执行六步门禁审计、优先调用外部验证器、一票否决 |
| `goal-planner` | 规划师 | 应对挑战时多方向分析、生成备选方案 |

**工作流水线：**
```
用户目标 → goal-mode 拆解需求 → [组装验收清单] → 执行子 Agent 工作
    → goal-auditor 审计 [gate/verify-goal.py] → goal-mode 报告进度
```

---

## 文件结构

```
skill-markets/goal-mode/
├── SKILL.md                      # 本文件
├── agents/
│   ├── goal-mode.md              # 监工 Agent
│   ├── auditor.md                # 审计官 Agent
│   └── planner.md                # 规划师 Agent
├── gate/                         # 强门禁层
│   ├── verify-goal.py            # 外部验证器
│   ├── acceptance_manifest.yaml  # 验收清单模板
│   └── STATE_MACHINE.md          # 状态契约
├── state/                        # 运行时状态
│   └── completion_candidate.yaml
├── evals/
│   └── evals.json
└── report-20260814.md            # 研究报告
```

---

## 引用

- [agent-completion-gate](https://github.com/zhjai/agent-completion-gate) — 状态机 + 外部验证器设计参考
- [make-no-mistakes](https://github.com/momomuchu/make-no-mistakes) — 三铁律 + 篡改检测参考
- [ProtocolForge](https://github.com/gitstq/protocolforge) — Hook 门控参考