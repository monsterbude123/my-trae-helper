# E2E-First Fix — Stage 6 Bug Fix

> Stage 6 Bug Fix 必走。e2e 先行 + 5 步修复协议。

---

## 5 步流程

```
Step 1: 理解期望（读 bug 单 + spec.md INV）
Step 2: e2e 先行（必初始 FAIL → 证明 bug 真实存在）
Step 3: 数据分析（GitNexus impact + 6 层排查）
Step 4: TDD 修复（RED → GREEN → REFACTOR）
Step 5: 验收（回归测试 + bug 单 CLOSED）
```

---

## Step 1: 理解期望

```yaml
bug_id: {module}-{NNN}-{slug}
expected: "{正确行为}"
actual: "{实际行为}"
INV_violated: [INV-1, INV-2]
AC_failed: [AC-3]
```

---

## Step 2: e2e 先行（必 INITIAL FAIL）

```python
# tests/e2e/test_bug_xxx.py
def test_bug_xxx_reproduction():
    """必初始 FAIL — 证明 bug 真实存在"""
    result = reproduce_bug_steps()
    assert result == expected, f"实际: {result}, 期望: {expected}"

# 跑测试 → 必 FAIL
pytest tests/e2e/test_bug_xxx.py -v
```

**关键**: INITIAL PASS = 不是 bug → 回退 OPEN（V10 反模式 3）。

---

## Step 3: 数据分析

```
GitNexus impact({target}) → 受影响符号
GitNexus context({target}) → 调用链

6 层排查:
  ├─ 网络层: curl / DNS / TLS
  ├─ 接入层: API gateway / 路由 / 限流
  ├─ 应用层: 业务逻辑 / 中间件 / 状态
  ├─ 数据层: DB schema / 索引 / 事务
  ├─ 集成层: 第三方服务 / SDK
  └─ 客户端层: UI / 缓存 / localStorage
```

**根因不明不修复**：6 层排查超 5 轮仍未找到 → 用户决策。

---

## Step 4: TDD 修复

```
🔴 RED: 加更细粒度单元测试（必 FAIL）
🟢 GREEN: 最简实现（让 e2e + 单元测试都通过）
♻️ REFACTOR: 优化质量
🔍 DRIFT CHECK: 对照 contracts/
```

---

## Step 5: 验收

```yaml
regression_test:
  e2e_test: PASS
  unit_test: PASS
  contract_test: PASS

bug_closed:
  status: CLOSED
  root_cause: "{6 层排查结论}"
  fix_files: [file:line list]
  closed_at: {ISO 8601}
  user_signed: true
```

---

## 跨层修复最小化（Ponytail）

```
Step 1: 根因在 1 层 → 改该层（最优）
Step 2: 根因跨 2 层 → 改源头层 + 1 处防御层
Step 3: 根因跨 3+ 层 → 用户决策（这是设计问题，非 bug）
```

---

## 反例

### 反例 A：跳过 e2e 先行

```
debugger: 立即读代码猜原因 → 修代码  # ❌
正确: 先写 e2e 测试证明 bug 真实存在
```

### 反例 B：INITIAL PASS 不回退

```
e2e 写完 → 跑 → PASS → "哦，没事" → 关闭  # ❌
正确: INITIAL PASS = 不是 bug → 回退 OPEN + 用户确认
```

### 反例 C：跨层过度修复

```
debugger: 改应用层 + 数据层 + 集成层（共 5 文件）  # ❌
正确: 找最小修复点（通常 1-2 文件）
```

---

## 关联引用

- [SKILL.md](../SKILL.md)
- [five-step-flow.md](../references/five-step-flow.md)
- [six-layer-diagnosis.md](../references/six-layer-diagnosis.md)
- [cross-layer-fix.md](../references/cross-layer-fix.md)
- [bug-state-machine.md](../references/bug-state-machine.md)