# API Contracts Template — Stage 2 Contract

> 位置: `docs/specs/changes/{id}/contracts/api-contracts.md`

---

```yaml
# API Contracts: {change-id}

## POST /api/v1/auth/login

- path: /api/v1/auth/login
  method: POST
  auth: none (login endpoint)
  request:
    headers: { Content-Type: application/json }
    body:
      email: string (required, RFC 5322)
      password: string (required, ≥ 8 chars)
  response:
    200:
      body:
        token: string (JWT)
        expires_at: ISO 8601
        user_id: UUID
    400:
      body: { error: string, code: int }
    401:
      body: { error: "invalid_credentials", code: 130001 }
    429:
      body: { error: "rate_limited", code: 130010 }
  errors:
    - code: 130001
      message: "用户名或密码错误"
      http_status: 401
    - code: 130002
      message: "邮箱格式不正确"
      http_status: 400

## POST /api/v1/auth/logout

- path: /api/v1/auth/logout
  method: POST
  auth: required (Bearer token)
  request: {}
  response:
    204: {}
    401: { error: "invalid_token", code: 130003 }
```

---

## 错误码规范

| module | 范围 | 说明 |
|--------|------|------|
| 1xx | auth | 认证授权 |
| 2xx | user | 用户管理 |
| 3xx | data | 数据操作 |
| 4xx | integration | 集成层 |

## 关联引用

- [Stage 2 Contract](../skills/06-contract/SKILL.md)
- [domain-models-template.md](domain-models-template.md)
- [validation-rules-template.md](validation-rules-template.md)