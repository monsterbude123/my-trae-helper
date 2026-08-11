# Events Template — Stage 2 Contract

> 位置: `docs/specs/changes/{id}/contracts/events.md`

---

```yaml
# Events: {change-id}

## Event 1: UserRegistered

- event: auth.user.registered
  publisher: auth-service
  subscribers: [email-service, audit-service]
  trigger: "用户注册成功（email_verified）"
  schema:
    user_id: UUID
    email: string
    registered_at: ISO 8601
  when: "publish on success"
  delivery: "at-least-once"

## Event 2: UserLoggedIn

- event: auth.user.logged_in
  publisher: auth-service
  subscribers: [audit-service, analytics-service]
  trigger: "用户登录成功"
  schema:
    user_id: UUID
    ip_address: string
    logged_in_at: ISO 8601
  when: "publish on success"

## Event 3: TokenRefreshed

- event: auth.token.refreshed
  publisher: auth-service
  subscribers: [audit-service]
  trigger: "token 续签成功"
  schema:
    user_id: UUID
    old_token_hash: string
    new_token_hash: string
    refreshed_at: ISO 8601
```

---

## 关联引用

- [Stage 2 Contract](../skills/06-contract/SKILL.md)
- [api-contracts-template.md](api-contracts-template.md)