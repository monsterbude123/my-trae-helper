# 5 步精简流程（Five-Step Flow）

> Stage 6 Bug Fix 必走。V10 debugger-methodology.md 蒸馏。

---

## Step 1：理解期望

```
读 bug 单 6 字段:
  ├─ 症状: [期望 vs 实际]
  ├─ 期望: [正确行为]
  ├─ 复现步骤: [操作序列]
  ├─ 影响范围: [P0/P1/P2 + 用户/功能]
  ├─ 环境信息: [OS/浏览器/版本]
  └─ 触发词: [用于追溯]

读 spec.md INV + AC:
  ├─ 哪些 INV 被违反？
  └─ 哪些 AC 失败？
```

## Step 2：e2e 先行（必初始 FAIL）

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

## Step 3：数据分析

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

## Step 4：TDD 修复

```
🔴 RED: 已有 e2e 失败 → 加更细粒度单元测试（必 FAIL）
🟢 GREEN: 最简实现（让 e2e + 单元测试都通过）
♻️ REFACTOR: 优化质量
🔍 DRIFT CHECK: 对照 contracts/
```

## Step 5：验收

```
全量回归测试 PASS
bug 单回写 CLOSED + 根因记录
用户确认
```

---

## 反例

### 反例 A：跳过 Step 2 e2e 先行

```
debugger: 直接读代码猜原因 → 改代码 → 修复  # ❌
正确: 先写 e2e 测试证明 bug 真实存在 → 修复
```

### 反例 B：INITIAL PASS 不回退

```
debugger: e2e 写完 → 跑 → PASS → "哦，没事" → 关闭  # ❌
正确: INITIAL PASS = 不是 bug → 回退 OPEN + 用户确认
```

### 反例 C：跨层过度修复

```
debugger: 修了应用层 + 数据层 + 集成层（共 5 文件）  # ❌ 跨层过度
正确: 找最小修复点（通常 1-2 文件）
```

---

## 关联引用

- [SKILL.md §铁律 1-2](../SKILL.md)
- [six-layer-diagnosis.md](six-layer-diagnosis.md)
- [cross-layer-fix.md](cross-layer-fix.md)
- V10 debugger-methodology.md: `V10 来源` (已蒸馏到本文档)
