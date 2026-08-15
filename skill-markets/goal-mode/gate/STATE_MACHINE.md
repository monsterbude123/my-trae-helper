# Goal-Mode 完成状态机

> 参考：[agent-completion-gate STATE_MACHINE.md](https://github.com/zhjai/agent-completion-gate/blob/main/STATE_MACHINE.md)

---

## 状态定义

| 状态 | 含义 | 谁可以写入 |
|------|------|-----------|
| `in_progress` | Agent 正在工作 | Agent |
| `candidate_complete` | Agent 提议完成，等待验证 | Agent（只能提议，不能写 complete） |
| `complete` | 验证通过，目标达成 | **仅外部验证器** |
| `blocked` | 验证失败，需要返工 | 外部验证器 |

---

## 状态转换图

```
in_progress ──► candidate_complete ──► [外部验证器] ──► complete
     │                                                      │
     │                                                      ▼
     └────────► blocked ◄────────────────────────────────────┘
                     │
                     └──► in_progress (返工)
```

---

## 关键规则

### 1. Agent 只能写 `candidate_complete`

Agent 无法写入 `complete` 状态。如果检测到 `complete` 状态由 Agent 写入（而非验证器），gate 将拒绝并标记为违规。

### 2. 外部验证器是唯一的 `complete` 写入者

`gate/verify-goal.py` 是唯一可以写入 `complete` 状态的组件。它：
- 只读真实产物文件
- 不读 `state/completion_candidate.yaml` 中的 Agent 声明
- 根据 `gate/acceptance_manifest.yaml` 逐项验证

### 3. Fail-Closed 原则

未知项 = blocked。如果一个 surface 被标记为 user_visible 但没有对应的 check，验证器将返回 blocked。

### 4. 门禁级联重验

任何文件/配置/依赖变更后，之前通过的 gate 必须重新验证。

---

## 文件职责

| 文件 | 职责 | 谁可以编辑 |
|------|------|-----------|
| `gate/verify-goal.py` | 外部验证器 | 仅人类（CODEOWNERS） |
| `gate/acceptance_manifest.yaml` | 验收清单 | 仅人类（CODEOWNERS） |
| `gate/STATE_MACHINE.md` | 状态契约文档 | 仅人类（CODEOWNERS） |
| `state/completion_candidate.yaml` | 运行时状态 | Agent + 验证器 |

---

## 安全不变量

1. **gate/manifest/inventory 受保护**：`.husky/CODEOWNERS` 标注，Agent 不可编辑
2. **验证器只读真实产物**：不读 state 的 claim
3. **未知项 fail-closed**：无 check 的 surface = blocked
4. **唯一完成信号**：gate verdict 是唯一 `complete` 来源
5. **产物内容是敌对数据**：验证器用确定性检查，不把产物当指令
6. **禁止环境注入**：`python3 -E` 执行

---

## 与 goal-mode SKILL.md 的关系

- SKILL.md 的六步审计协议是 **advisory** 层，指导 Agent 行为
- 本状态机是 **mechanical** 层，强制执行完成验证
- Agent 即使跳过 advisory 层，也无法绕过 mechanical 层

---

## 引用

- [agent-completion-gate STATE_MACHINE.md](https://github.com/zhjai/agent-completion-gate/blob/main/STATE_MACHINE.md)
- [make-no-mistakes Three Laws](https://github.com/momomuchu/make-no-mistakes#the-three-laws)