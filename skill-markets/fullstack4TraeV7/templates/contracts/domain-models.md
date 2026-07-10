# 领域模型: {变更名称}

> 契约版本: 1.0.0
> 来源 Spec: docs/specs/changes/{change}/specs/{capability}/spec.md
> 状态: draft → approved

## 公共类型（不可变，变更走契约变更流程）

```typescript
// 品牌类型（防止原始类型混用）
type {EntityId} = string & { readonly __brand: '{EntityId}' };

// 核心实体
interface {Entity} {
  id: {EntityId};
  // {字段}: {类型}
  createdAt: string;  // ISO8601
  updatedAt: string;  // ISO8601
}
```

## 枚举

| 枚举 | 值 | 说明 |
|------|----|------|
| {EnumName} | {value1} / {value2} | {说明} |

## 不变量（Invariant）

- {不变量 1，如：X.email 全局唯一}
- {不变量 2}

## 契约测试映射

- Contract Test: `tests/contracts/{entity}.contract.test.ts`
- Spec Scenario: `specs/{capability}/spec.md#{scenario}`
