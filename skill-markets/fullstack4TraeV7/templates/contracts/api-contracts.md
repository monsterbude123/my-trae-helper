# 接口契约: {变更名称}

> 契约版本: 1.0.0
> 来源 Spec: docs/specs/changes/{change}/specs/{capability}/spec.md
> 状态: draft → approved

## {METHOD} {PATH}

### 请求

#### Headers
| Header | 必填 | 说明 |
|--------|------|------|
| Content-Type | 是 | application/json |
| Authorization | {是/否} | Bearer {token} |

#### Body / Query
| 字段 | 类型 | 必填 | 约束 | 说明 |
|------|------|------|------|------|
| {field} | {type} | {是/否} | {约束} | {说明} |

### 响应（{status}）

```typescript
interface {ResponseName} {
  code: {status};
  data: {
    // {字段}: {类型}
  };
  errors?: Array<{ field: string; message: string }>;
}
```

### 错误码（契约级，前后端共享）

| code | HTTP | 场景 | errors[] 示例 |
|------|------|------|--------------|
| {code} | {http} | {场景} | ["{field}: {reason}"] |

### 契约测试映射

- Contract Test: `tests/contracts/{endpoint}.contract.test.ts`
- Spec Scenario: `specs/{capability}/spec.md#{scenario}`
- Fixtures: `tests/fixtures/{endpoint}.json`

---

## 契约变更记录

| 版本 | 日期 | 变更类型 | 描述 |
|------|------|---------|------|
| 1.0.0 | {date} | ADDITIVE | 初始契约 |
