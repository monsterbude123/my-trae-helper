# Domain Models Template — Stage 2 Contract

> **V11.7.0+ 设计入口**: [AC 核销门禁](../skills/09-review/SKILL.md) · [贾维斯门禁守护](../skills/00-boot/SKILL.md) · 评分制废除 → 门禁制 · 详见 [CHANGELOG.md V11.7.0](../CHANGELOG.md)


> 位置: `docs/specs/changes/{id}/contracts/domain-models.md`

---

```yaml
# Domain Models: {change-id}

## Entities

### User
  description: "用户实体"
  fields:
    - id: UUID (PK)
    - name: string
    - email: Email (VO)
    - status: UserStatus (enum)
    - created_at: ISO8601
  state_machine:
    - DRAFT → ACTIVE (event: email_verified)
    - ACTIVE → SUSPENDED (event: violation)
    - SUSPENDED → ACTIVE (event: appeal_approved)

## Value Objects

### Email
  description: "邮箱值对象"
  fields:
    - value: string
  validation:
    - regex: RFC 5322
  immutable: true

### Money
  description: "金额值对象"
  fields:
    - amount: decimal
    - currency: string (ISO 4217)
  immutable: true

## Aggregates

### User Aggregate
  description: "用户聚合"
  root: User
  includes: [User, Email, UserStatus]
  invariants: [INV-1, INV-2]

## Invariants

### INV-1: 认证必在授权前
  rule: "任何 API 必先 authenticate 再 authorize"
  enforcement: "middleware/auth_required"
  category: 安全

### INV-2: email 全局唯一
  rule: "User.email 不可重复"
  enforcement: "DB unique constraint"
  category: 数据一致性

### INV-3: 订单总额 = 单价 × 数量
  rule: "Order.total == Order.unit_price * Order.quantity"
  enforcement: "service 层校验"
  category: 业务规则
```

---

## 关联引用

- [Stage 2 Contract](../../skills/06-contract/SKILL.md)
- [domain-driven-design.md](../../skills/06-contract/workflows/domain-driven-design.md)
- [contract-four-suite.md](../../skills/06-contract/references/contract-four-suite.md)
