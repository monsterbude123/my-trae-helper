# Enhanced Acceptance 规则

> Stage 1 Spec Step 2 必走。每个 Capability 拆 ≥ 3 Acceptance Criteria + ≥ 1 E2E。

---

## Acceptance Criteria 类型

| 类型 | 含义 | 示例 |
|------|------|------|
| **功能正确性** | happy path | 正确凭据 → 登录成功 |
| **边界条件** | 极端值 | 用户名长度 1/255 |
| **异常处理** | 错误路径 | 错误密码 → 拒绝 |

---

## 拆分规则

| 规则 | 含义 |
|------|------|
| **AC ≥ 3** | 每个 Capability 至少 3 个 Acceptance Criteria |
| **E2E ≥ 2** | 整体至少 2 个 E2E 场景 |
| **INV ≥ 1** | 整体至少 1 个不变量 |
| **可测试** | 每个 AC 必可被一条测试覆盖 |

---

## AC 模板

```yaml
acceptance_criteria:
  - id: AC-001
    description: "用户使用正确用户名和密码可登录"
    type: functional
    test_layer: UNIT | E2E | INV
    test_id: TC-001
  - id: AC-002
    description: "用户使用错误密码被拒绝（401）"
    type: error_handling
    test_layer: UNIT
    test_id: TC-002
  - id: AC-003
    description: "并发登录不冲突（独立 token）"
    type: boundary
    test_layer: E2E
    test_id: TC-010
```

---

## E2E 场景设计

E2E 跨多个模块/服务：

| E2E | 跨模块 |
|-----|--------|
| 用户登录流程 | AuthController → UserService → TokenService → JwtMiddleware |
| 支付流程 | PaymentController → OrderService → PaymentGateway → Notification |

**关键路径 100% E2E 覆盖**（认证 / 支付 / 数据完整性）。

---

## 反例

### 反例 A：AC 只有 1 个

```
AC-001: "用户能登录"
# ❌ 1 个 AC = 没拆维度
正确: AC-001 正确路径 + AC-002 错误路径 + AC-003 并发路径
```

### 反例 B：AC 不可测试

```
AC-001: "系统应该安全"  # ❌ 模糊不可测
正确: AC-001 错误密码 3 次后账号锁定 5 分钟
```

### 反例 C：AC 写实施

```
AC-001: "用 bcrypt 哈希密码"  # ❌ 写实施
正确: AC-001 密码以不可逆哈希存储
```

## 关联引用

- [SKILL.md §铁律 2-4](../SKILL.md)
- [clarify-checklist.md](clarify-checklist.md) — Clarify 检查清单
- [spec-template.md](../templates/spec-template.md)
