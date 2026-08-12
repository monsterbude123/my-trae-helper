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

> **位数说明**: `{module}` = 1 位分类 + `{3 digits}` = 3 位 sub_code + `{sub_code}` 末尾 = 3 位细化 = 共 6 位(如 `130001` = auth / login 类 / 001 号)
> 例:validation-rules.md 的 `130001 / 130002 / 130003 / 130004` = auth 模块的 login sub_code 1-4 号

| module | 范围(6 位完整) | 说明 |
|--------|---------------|------|
| 1xxxxx | auth | 认证授权(如 `100001 = token 缺失`、`130001 = login 失败`) |
| 2xxxxx | user | 用户管理 |
| 3xxxxx | data | 数据操作 |
| 4xxxxx | integration | 集成层 |

## 关联引用

- [domain-models.md](domain-models.md)
- [validation-rules.md](validation-rules.md)
