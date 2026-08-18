# Events Template — Stage 2 Contract

> **V12.0.0+ 设计入口**: [AC 核销门禁](../skills/09-review/SKILL.md) · [贾维斯门禁守护](../skills/00-boot/SKILL.md) · 评分制废除 → 门禁制 · 详见 [CHANGELOG.md V12.0.0](../CHANGELOG.md)


> 位置: `docs/specs/changes/{id}/fact/contracts/events.md` (V12 物理布局,fact/contracts/ 子目录)

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

- [Stage 2 Contract](../../skills/06-contract/SKILL.md)
- [api-contracts-template.md](api-contracts-template.md)
