# Validation Rules Template — Stage 2 Contract

> **V12.0.0+ 设计入口**: [AC 核销门禁](../skills/09-review/SKILL.md) · [贾维斯门禁守护](../skills/00-boot/SKILL.md) · 评分制废除 → 门禁制 · 详见 [CHANGELOG.md V12.0.0](../CHANGELOG.md)


> 位置: `docs/specs/changes/{id}/fact/contracts/validation-rules.md` (V12 物理布局,fact/contracts/ 子目录)

---

```yaml
# Validation Rules: {change-id}

## Parameter Validation

| 字段 | 类型 | 校验 | 错误码 |
|------|------|------|--------|
| email | string | 长度 1-255, regex RFC 5322 | 130002 |
| password | string | 长度 ≥ 8, 含大小写 + 数字 | 130003 |
| username | string | 长度 3-20, regex `^[a-zA-Z0-9_]+$` | 130004 |

## Business Rules

- BR-1: 用户名全局唯一
- BR-2: 同一邮箱 24h 内最多 3 次注册尝试
- BR-3: 密码 90 天强制更换
- BR-4: 登录失败 5 次后账号锁定 30 分钟

## Error Messages

| 错误码 | 用户提示 | 内部提示 |
|--------|---------|---------|
| 130001 | "用户名或密码错误" | "Invalid credentials for user X" |
| 130002 | "邮箱格式不正确" | "Email regex mismatch" |
| 130003 | "密码强度不足" | "Password must contain uppercase + lowercase + digit" |
| 130010 | "请求过于频繁，请稍后再试" | "Rate limit exceeded: 5/min" |

## Validation Pipeline

```
[Request] → [Schema Validation] → [Business Rules] → [Response]
              ↓                       ↓
            400 (格式错)            401/422 (业务错)
```

## 关联引用

- [Stage 2 Contract](../../skills/06-contract/SKILL.md)
- [api-contracts-template.md](api-contracts-template.md)
