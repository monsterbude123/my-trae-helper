# Domain Models: {change_id}

> 位置: `docs/specs/changes/{id}/contracts/domain-models.md`
> 优先于 API 契约 / 事件 / 校验规则（DOMAIN FIRST）

---

## Entities（领域实体）

### Entity 1: [Name]

| 字段 | 类型 | 必填 | 说明 |
|------|------|:---:|------|
| id | UUID | ✅ | 主键 |
| name | string | ✅ | 名称 |
| created_at | ISO8601 | ✅ | 创建时间 |

**状态机**（如有）:
```
[State A] → trigger → [State B]
```

---

## Value Objects（值对象）

### VO 1: [Name]

| 字段 | 类型 | 约束 |
|------|------|------|
| ... | ... | ... |

---

## Aggregate Roots（聚合根）

### AR 1: [Name]

- 包含: Entity 1 + Entity 2
- 根实体: Entity 1
- 跨实体不变量: [INV]

---

## Invariants（不变量）

### INV-1: [数据一致性 / 安全 / 业务规则]

```python
def check_inv(entity):
    assert entity.total == entity.unit_price * entity.quantity
```

### INV-2: [业务规则]

...

---

## 关联引用

- spec.md: [../spec.md](../spec.md)
- api-contracts.md: [api-contracts.md](api-contracts.md)
- V10 contract-writer: `V10 来源` (已蒸馏到本文档)
