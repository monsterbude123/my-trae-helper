# Domain-Driven Design — Stage 2 Contract

> Stage 2 Contract 必走。DDD 领域模型设计协议。

---

## DDD 4 步

```
Step 1: 提取 Aggregate（聚合根）
  └─ 一致性边界内的实体集合

Step 2: 定义 Entity vs Value Object
  └─ Entity: 有 ID + 可变
  └─ Value Object: 无 ID + 不可变

Step 3: 提取 INV（不变量）
  └─ 跨实体约束

Step 4: 状态机（如有）
  └─ 实体状态转换规则
```

---

## Entity vs Value Object

```yaml
Entity:
  id_required: true
  mutable: true
  example: "User(id, name, email)"

Value Object:
  id_required: false
  mutable: false  # 任何修改 = 创建新对象
  example: "Email(value='user@example.com')  # 验证后构造"
  example: "Money(amount, currency)"
```

---

## Aggregate 提取算法

```python
def extract_aggregates(entities: list) -> list:
    aggregates = []
    visited = set()

    for entity in entities:
        if entity in visited:
            continue
        cluster = {entity}
        # 找强关联实体（同事务访问）
        for other in entities:
            if other == entity or other in visited:
                continue
            if has_strong_association(entity, other):
                cluster.add(other)
        aggregates.append({
            "root": entity,
            "entities": cluster,
            "invariant_count": count_invariants(cluster),
        })
        visited.update(cluster)

    return aggregates
```

---

## INV 提取规则（V10 spec.md 蒸馏）

| 类型 | 规则 |
|------|------|
| **数据一致性** | 事务原子性 / 字段依赖 |
| **安全约束** | 认证必在授权前 / 不可越权 |
| **业务规则** | 订单总额 = 单价 × 数量 |
| **状态机** | 必走合法状态转换 |

---

## 输出: domain-models.md

```yaml
# Domain Models: {change-id}

## Entities

### User
  - id: UUID
  - name: string
  - email: Email (VO)
  - status: UserStatus (enum)
  state_machine:
    - DRAFT → ACTIVE (event: email_verified)
    - ACTIVE → SUSPENDED (event: violation)
    - SUSPENDED → ACTIVE (event: appeal_approved)

## Value Objects

### Email
  - value: string
  - validator: "regex RFC 5322"
  - immutable: true

## Aggregates

### User Aggregate
  - root: User
  - includes: [User, Email, UserStatus]
  - invariants: [INV-1, INV-2]

## Invariants

### INV-1: 认证必在授权前
  rule: "任何 API 必先 authenticate 再 authorize"
  enforcement: "middleware/auth_required"

### INV-2: email 不可重复
  rule: "User.email 全局唯一"
  enforcement: "DB unique constraint"
```

---

## 反例

### 反例 A：跳 Aggregate 直接写 Entity

```
domain-models.md: 只列 Entity  # ❌
正确: Aggregate 必含 + INV 必含
```

### 反例 B：可变 VO

```python
class Email:
    def __init__(self, value):
        self.value = value
    def set_value(self, new):
        self.value = new  # ❌ VO 不可变
```

正确: 不可变 + 修改 = 创建新 VO。

---

## 关联引用

- [SKILL.md](../SKILL.md)
- [contract-four-suite.md](../references/contract-four-suite.md)
- [Stage 1 Spec](../../04-spec/SKILL.md)