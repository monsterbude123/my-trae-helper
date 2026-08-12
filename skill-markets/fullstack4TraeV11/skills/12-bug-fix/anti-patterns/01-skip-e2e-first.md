# 反例 1：跳过 e2e 先行直接修（Stage 6 Bug Fix）

> Stage 6 Bug Fix Step 2 必走：**e2e 先行 → 初始 FAIL → 证明 bug 真实存在 → 才修**。
> 来源：V10 references/debugger-methodology.md §Step 2 + agents/debugger.md 铁律 2。

## 现象

```
debugger: 用户报 bug → 读错误日志 → 修代码 → 测试 PASS  # ❌ 跳了 e2e 先行
```

## 根因

| 根因 | 占比 |
|------|:---:|
| 觉得 bug 显然不用 e2e | 40% |
| e2e 写起来费时 | 30% |
| 不懂 e2e 先行意义 | 30% |

## 教训

**e2e 先行的核心 = 证明 bug 真实存在**。

- e2e 写完跑 → **初始 FAIL** → 证明 bug 存在 → 修代码 → e2e GREEN
- e2e 写完跑 → **初始 PASS** → bug 不存在 → 回退 OPEN 状态
- 跳过 e2e → 改完后"测试 PASS"不能证明"bug 已修"

## 正确替代

```python
# ✅ 流程（V10 debugger-methodology.md §Step 2）
Step 1: 写 e2e 测试（模拟用户操作触发 bug）
Step 2: 跑 e2e → 必初始 FAIL（"TimeoutError: login takes 30s"）
Step 3: 才进 Step 4 TDD 修复（RED → GREEN → REFACTOR）
Step 4: 跑全量回归（确认没破坏其他）
```

## 反模式警告

```
❌ 不写 e2e 直接修代码
❌ e2e 初始 PASS → 仍然改代码（说明不是 bug）
❌ 只跑单元测试不跑 e2e
```

## 关联引用

- [five-step-flow.md](../references/five-step-flow.md) — 5 步精简流程
- [SKILL.md §铁律 2](../SKILL.md) — e2e 先行
- V10 来源: `../../../../fullstack4TraeV10/references/debugger-methodology.md`