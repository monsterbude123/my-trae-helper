# 反例 4：跳过 E2E / INV（Skip E2E & INV）

> E2E ≥ 2 + INV ≥ 1 + UNIT ≥ 5 是 V11 最低组合。只写 UNIT = 端到端流程无保障 + 数据一致性裸奔。

**违反**：铁律 3（E2E ≥ 2 / INV ≥ 1 / UNIT ≥ 5）
**严重度**：P1（直接导致 Stage 3.5 Real Verify 返工 + 生产事故）

---

## 现象

```yaml
# test-plan.md（反例版本）

## 测试清单
- tests/unit/test_login.py::test_login_success
- tests/unit/test_login.py::test_login_fail
- tests/unit/test_logout.py::test_logout
- tests/unit/test_order.py::test_create_order
- tests/unit/test_order.py::test_query_order
- tests/unit/test_payment.py::test_payment
- ...（100 个 UNIT 测试）

## ❌ 反例特征
- E2E 测试: 0  ← 🛑 违反铁律 3
- INV 测试: 0  ← 🛑 违反铁律 3
- UNIT 测试: 100（远超 5，但不够）

# 实施结果
pnpm test
# ✓ 100/100 pass（UNIT 全过）
# ✗ 端到端流程未验证
# ✗ 数据一致性未验证
```

**识别信号**:
- test-plan.md §Tests 只有 `tests/unit/` 无 `tests/e2e/` / `tests/integration/`
- INV（数据一致性 / 安全约束）测试缺失
- 端到端流程（用户登录 → 下单 → 支付 → 收货）从未实测
- Stage 3.5 Real Verify 启动验证时第一次发现端到端失败

---

## 根因

- **认知维度**：把"测试"等同于"单元测试"，不区分 E2E / INV / UNIT 层级
- **成本维度**：觉得"E2E 太慢 / INV 不知道测什么"
- **工具维度**：缺 Playwright（E2E）/ 数据库事务测试框架（INV）配置

| 根因 | 占比 |
|------|:---:|
| 把测试等同于单元测试（缺层级意识）| 50% |
| 觉得 E2E 太慢 / INV 复杂（成本/认知）| 35% |
| 缺 E2E / INV 工具配置 | 15% |

---

## 教训

- **V11 实战**：项目交付时 vitest 100/100 pass。Stage 3.5 Real Verify 启动完整应用 → 用户登录 → 下单 → 支付 → 页面崩溃（前后端字段不一致）→ 返工 2 天
- **真实场景**：单元测试覆盖了 `login()` 函数内部逻辑，但没测过"前端表单提交 → 后端 API → DB 写入 → 返回前端"的端到端链路。生产环境首单 = 崩溃
- **INV 反例**：支付金额 = 商品价格 × 数量这条 INV 无测试。生产环境出现 `total = price + 1`（浮点错误）→ 资损 → 用户投诉 → 紧急回滚

---

## 正确替代

```yaml
# ✅ 正确：3 层级组合（V11 铁律 3 强制）

## 测试层级（V11 最低组合）
- UNIT:  ≥ 5  ← 单函数 / 单类内部逻辑
- E2E:   ≥ 2  ← 端到端用户流程（Playwright/Cypress）
- INV:   ≥ 1  ← 数据一致性 / 安全不变量

## UNIT 示例（≥ 5）
- tests/unit/test_login.py::test_login_success
- tests/unit/test_login.py::test_login_wrong_password
- tests/unit/test_login.py::test_login_empty_fields
- tests/unit/test_order.py::test_create_order
- tests/unit/test_payment.py::test_calculate_total

## E2E 示例（≥ 2，覆盖关键流程）
- tests/e2e/test_purchase_flow.spec.ts
    - 用户登录 → 浏览商品 → 加购物车 → 下单 → 支付 → 订单详情
- tests/e2e/test_user_profile.spec.ts
    - 用户登录 → 编辑资料 → 上传头像 → 保存 → 验证显示

## INV 示例（≥ 1，覆盖数据一致性 + 安全）
- tests/inv/test_invariants.py::test_payment_total_invariant
    - INV: total = price × quantity（精确小数计算）
- tests/inv/test_invariants.py::test_auth_required
    - INV: 所有 mutation API 必须带有效 token
- tests/inv/test_invariants.py::test_order_state_consistency
    - INV: 订单状态机转换合法（created → paid → shipped，不可逆）
```

```python
# ✅ INV 测试示例（数据一致性）

def test_payment_total_invariant():
    """
    INV: 订单总额 = 单价 × 数量（精确小数运算）
    """
    price = Decimal("99.99")
    quantity = 3
    total = calculate_order_total(price, quantity)
    assert total == Decimal("299.97")  # � 浮点错误 = 0.01 偏差

def test_payment_total_invariant_decimal():
    """用 Decimal 而非 float"""
    total = calculate_order_total_safe(Decimal("99.99"), 3)
    assert total == Decimal("299.97")  # ✅ 精确
```

```typescript
// ✅ E2E 测试示例（Playwright）
// tests/e2e/test_purchase_flow.spec.ts
test('user can complete purchase', async ({ page }) => {
    await page.goto('/login')
    await page.fill('[name=username]', 'alice')
    await page.fill('[name=password]', 'pass123')
    await page.click('[type=submit]')

    await page.goto('/products/123')
    await page.click('[data-test=add-to-cart]')

    await page.goto('/checkout')
    await page.click('[data-test=pay]')

    await expect(page.locator('[data-test=order-success]')).toBeVisible()
    // ✅ 端到端流程验证
})
```

---

## Stage 4 Review 验证协议

```yaml
# reviewer 必走 3 层级核验
1. UNIT 测试数 ≥ 5
2. E2E 测试数 ≥ 2（关键流程）
3. INV 测试数 ≥ 1（数据一致性 / 安全约束）
4. 缺任一层级 → 🛑 REJECT + 要求补
5. E2E 跑通必含 playwright trace + screenshot（V11 视觉证据）
6. INV 测试必含精确小数 / 状态机 / 认证前置
```

---

## 反模式识别（V11 实战踩雷）

| 反例类型 | 后果 |
|---------|------|
| 只有 UNIT，无 E2E | 端到端崩溃 → Stage 3.5 返工 |
| 只有 UNIT，无 INV | 数据不一致 → 资损/数据污染 |
| E2E 写但不跑（"以后跑"）| 🛑 REJECT（未实测） |
| INV 写抽象数字断言（`assert x > 0`）| 🛑 REJECT（必含精确数学） |
| UNIT 100 个但 E2E 0 个 | Stage 4 维度评分"端到端"维度 = 0 |

---

## 关联引用

- [SKILL.md §铁律 3](../SKILL.md) — E2E ≥ 2 / INV ≥ 1 / UNIT ≥ 5
- [coverage-mapping.md §最低组合](../workflows/coverage-mapping.md) — 3 层级映射
- 公共铁律 Article I.2(测试覆盖 ≥ 90%) + Article XIII(可见产物是唯一信任基础): [../../../references/common-iron-rules.md](../../../references/common-iron-rules.md)
