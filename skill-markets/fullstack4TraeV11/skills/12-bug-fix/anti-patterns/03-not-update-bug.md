# 反例 3：修复未回写 bug 单（Stage 6 Bug Fix）

> Stage 6 Bug Fix Step 5 必走：**bug 单状态 OPEN → CLOSED**。来源：V10 agents/debugger.md 铁律 7 + bug-workflow.md §Bug 状态机。

## 现象

```
debugger: 修完代码 → 测试 PASS → 没回写 bug 单  # ❌ bug 单仍 OPEN
```

## 根因

| 根因 | 占比 |
|------|:---:|
| 觉得修了就 OK | 50% |
| 不知道 bug 单模板在哪 | 30% |
| 忘记状态机 | 20% |

## 教训

**bug 单状态机**（V10 bug-workflow.md）：

```
OPEN → IN_PROGRESS → FIXED → CLOSED
                  ↘ WONT_FIX → 显式说明
```

**必须**：
- 修完填 CLOSED 时间 + 修复 commit hash
- 填 root cause 6 层排查结论
- 填 gitnexus_calls 清单（impact / context / query 调用记录）

## 正确替代

```yaml
# docs/bugs/{bug-id}.md 必填字段
bug_id: auth-001-login-500
status: CLOSED  # ← 必改
closed_at: 2026-08-11T15:30:00Z
closed_by: debugger
fix_commit: "abc1234"
gitnexus_calls:
  - impact(target="UserService.authenticate")
  - context(name="UserService.authenticate")
  - query("recent changes UserService")
root_cause: "DB 索引缺失 → service 抛异常 → 500"
preventive_measures:
  - 加 DB 索引（已加）
  - 加 e2e 回归测试（已加）
```

## 关联引用

- [bug-state-machine.md](../references/bug-state-machine.md) — 状态机
- [SKILL.md §铁律 7](../SKILL.md) — 修复回写 bug 单
- V10 来源: `../../../../fullstack4TraeV10/references/bug-workflow.md`