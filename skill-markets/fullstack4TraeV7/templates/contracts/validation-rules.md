# 验证规则: {变更名称}

> 契约版本: 1.0.0
> 状态: draft → approved

## {字段名} 校验

- **规则**: {规则描述，如：RFC 5322 + 长度 ≤ 254}
- **实现**: `{path/to/validator.ts}`
- **契约测试**: `tests/contracts/{field}-validation.contract.test.ts`
- **错误码**: {code}（当校验失败时返回）

### 测试用例

| 输入 | 期望结果 | 说明 |
|------|---------|------|
| {valid input} | ✅ 通过 | 正常值 |
| {invalid input} | ❌ 失败 {code} | {原因} |
| {edge case} | {结果} | 边界值 |
