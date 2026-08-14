# Test Plan: {change_id}

> 位置: `docs/specs/changes/{change_id}/test-plan.md`
> 编制依据: plan.md Capabilities + 验收维度拆解 + 覆盖率门槛

---

## Capabilities（来自 plan.md）

1. [Capability 1]
2. [Capability 2]
3. [Capability 3]
4. [Capability 4]
5. [Capability 5]

## 验收维度 + 测试用例映射

### Capability 1: [名称]

| 验收维度 | 类型 | 测试用例 | 文件 | 层级 |
|---------|------|---------|------|------|
| [维度 1] | functional | test_xxx_1 | tests/... | UNIT |
| [维度 2] | error_handling | test_xxx_2 | tests/... | UNIT |
| [维度 3] | boundary | test_xxx_3 | tests/... | E2E |

### Capability 2: [名称]

...

## 测试层级最低组合

- **E2E**: [N 个（≥ 2）]
- **INV**: [N 个（≥ 1）]
- **UNIT**: [N 个（≥ 5）]
- **总计**: [N 个（≥ 8）]

## 覆盖率门槛

```yaml
coverage_thresholds:
  line: 0.90       # 行 ≥ 90%
  branch: 0.85     # 分支 ≥ 85%
  function: 0.95   # 函数 ≥ 95%
  critical_path: 1.00  # 关键路径 100%
```

## 关键路径

| 路径 | 涉及 | E2E 覆盖 |
|------|------|---------|
| [路径 1] | 认证 | ✓ |
| [路径 2] | 支付 | ✓ |

## 测试命名规范

```
test_{module}_{scenario}_{expected}
```

示例:
- `test_user_service_login_with_valid_credentials_returns_token`
- `test_payment_process_with_insufficient_balance_raises_error`

## 覆盖率不足（如有）

- [未覆盖行/分支清单]
- [Stage 3 必补]

## 关联引用

- plan.md: `../plan.md`（项目级路径，本模板运行时由项目生成）
- 覆盖率规则: [../references/coverage-rules.md](../references/coverage-rules.md)
- 验收维度工作流: [../workflows/coverage-mapping.md](../workflows/coverage-mapping.md)
