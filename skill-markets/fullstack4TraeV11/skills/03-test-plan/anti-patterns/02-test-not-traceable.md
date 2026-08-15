# 反例 2：测试不可追溯（Test Not Traceable）

> 测试与 Capability 必须双向追溯。缺映射 = Stage 4 Review 失败定位 + 实施阶段变更追踪不可逆。

**违反**：铁律 4（测试用例可追溯）
**严重度**：P2（过程性缺陷，导致 Stage 4 Review 返工 + Stage 7 项目健康度评估失真）

---

## 现象

```markdown
# test-plan.md（反例版本）

## Capabilities
- C1: 用户登录
- C2: 订单查询
- C3: 支付回调

## Tests
- tests/unit/test_user.py::test_login
- tests/unit/test_user.py::test_logout
- tests/integration/test_order_query.py::test_query
- tests/integration/test_payment.py::test_callback

# ❌ 反例：5 个 Capability 列在 §顶部
#          100 个 test 列在 §Tests
#          但 test_to_capability 映射表完全缺失
```

**识别信号**:
- test-plan.md 只列"测试名称"，不标注对应 Capability
- 实施阶段改 Capability 时，无法定位"哪些测试需要改"
- Stage 4 Review 失败 case，无法定位"哪个 Capability 受影响"
- Stage 7 项目健康度评估无法回答"Capability X 的测试覆盖率"

---

## 根因

- **认知维度**：把"测试"当作独立产物，不视为"Capability 的验证实例"
- **流程维度**：跳过 coverage-matrix-build.md §Step 3 矩阵构建
- **工具维度**：没有强制 test docstring/注解标注 capability ID

| 根因 | 占比 |
|------|:---:|
| 视测试为独立产物（非 Capability 实例）| 50% |
| 跳过 coverage-matrix-build §Step 3 | 35% |
| 无强制 capability 注解工具 | 15% |

---

## 教训

- **V11 实战**：Stage 3 实施期间改了 Capability C2 的字段，但 test-plan.md 无映射表 → 实施者不知道要同步修改 12 个相关测试 → 留下 12 个悬挂测试 → Stage 4 Review 才发现 → 返工 6h
- **真实场景**：变更追踪失败。`test_order_query` 失败时，reviewer 写"哪个 Capability 出问题"必须人工逐个对照，5 个 Capability × 100 测试 = 500 次人工核对
- **Stage 7 阻塞**：项目健康度评估无法回答"Capability X 当前测试覆盖率是否达标"，需重建映射 → 浪费 1 天

---

## 正确替代

```yaml
# ✅ 正确流程（coverage-matrix-build.md §Step 3 强制）

Step 1: 列 Capability
  - C1: 用户登录
  - C2: 订单查询
  - C3: 支付回调

Step 2: 列所有测试（按文件分组）
  - tests/unit/test_user.py::test_login
  - tests/unit/test_user.py::test_logout
  - tests/integration/test_order_query.py::test_query
  - tests/integration/test_payment.py::test_callback
  - ...

Step 3: 构建 test_to_capability 矩阵（双向）
  | test_id                          | capability_id | dimension  |
  |----------------------------------|---------------|------------|
  | test_user.py::test_login         | C1            | 功能       |
  | test_user.py::test_logout        | C1            | 功能       |
  | test_order_query.py::test_query  | C2            | 功能       |
  | test_payment.py::test_callback   | C3            | 异常       |

Step 4: 构建 capability_to_test 反向索引
  - C1 → [test_login, test_logout, ...]
  - C2 → [test_query, ...]
  - C3 → [test_callback, ...]

Step 5: 实施阶段改 Capability 时
  - 查反向索引 → 列出受影响测试
  - 同步修改测试 → drift-detect 验证
```

```python
# ✅ 强制 capability 注解（test docstring 标准）

def test_login_success():
    """
    Capability: C1
    Dimension: 功能
    INV: 用户名 + 密码正确 → 返回 200 + token
    """
    response = login("alice", "pass123")
    assert response.status_code == 200

def test_login_sql_injection():
    """
    Capability: C1
    Dimension: 安全
    INV: SQL 注入尝试 → 返回 401（拒绝）
    """
    response = login("alice' OR '1'='1", "pass123")
    assert response.status_code == 401
```

---

## Stage 4 Review 验证协议

```yaml
# reviewer 必走
1. 读 test-plan.md §test_to_capability
2. 对每个 Capability: 至少 1 个测试映射
3. 对每个测试: capability 注解必含
4. 缺失任一映射 → 🛑 REJECT + 要求补矩阵
```

---

## 关联引用

- [SKILL.md §铁律 4](../SKILL.md) — 测试可追溯
- [coverage-matrix-build.md](../workflows/coverage-matrix-build.md) — §Step 3 矩阵构建
- [coverage-mapping.md §Step 3](../workflows/coverage-mapping.md) — 矩阵合并
- 公共铁律 Article XII.1(workflow discipline — 流程纪律不可跳过): [../../../references/common-iron-rules.md](../../../references/common-iron-rules.md)
