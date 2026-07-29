# TDD 工作流

> Test-Driven Development — 先写失败测试，再写实现。

---

## 三步循环

### Step 1: 🔴 RED
- 编写失败的测试用例
- 测试必须明确失败（不是编译错误）

### Step 2: 🟢 GREEN
- 编写最简实现代码
- 只让当前测试通过，不多写

### Step 3: ♻️ REFACTOR
- 优化代码质量
- 保持所有测试通过

---

## 测试层级

```
E2E 测试（端到端，模拟用户操作）
    ↓
Integration 测试（模块间协作）
    ↓
Contract 测试（接口契约验证）
    ↓
Unit 测试（单个函数/类）
```

---

## 测试命名规范

```
test_{行为}_{条件}_{预期}

示例：
test_create_user_happy_path_returns_user
test_create_user_duplicate_email_returns_error
test_payment_insufficient_balance_returns_400
```

---

## 覆盖率目标

| 层级 | 目标 |
|------|------|
| Unit | ≥ 80% |
| Contract | 100%（每个接口至少 1 个测试） |
| Integration | 关键路径覆盖 |
| E2E | 核心用户流程 |

---

## 禁止项

- ❌ 跳过测试直接写实现
- ❌ 修改测试让用例通过
- ❌ 测试只写 Happy Path
- ❌ 测试断言不明确（如 `expect(result).toBeTruthy()`）
