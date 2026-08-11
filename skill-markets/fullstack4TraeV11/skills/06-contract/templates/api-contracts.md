# API Contracts: {change_id}

> 位置: `docs/specs/changes/{id}/contracts/api-contracts.md`

---

## API 1: [Name]

```yaml
- path: /api/v1/{resource}
  method: POST | GET | PUT | DELETE
  auth: required | optional | none
  request:
    headers: { Authorization: Bearer <token> }
    body: { ... }
  response:
    200: { ... }
    4xx: { error: string, code: int }
    5xx: { error: string, code: int }
  errors:
    - code: 130001
      message: "invalid credentials"
```

---

## 错误码规范

**6 位错误码**: `{module}{3 digits}{sub_code}`

| module | 范围 | 说明 |
|--------|------|------|
| 1xx | auth | 认证授权 |
| 2xx | user | 用户管理 |
| 3xx | data | 数据操作 |
| 4xx | integration | 集成层 |

## 关联引用

- [domain-models.md](domain-models.md)
- [validation-rules.md](validation-rules.md)
