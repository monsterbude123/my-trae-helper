# Validation Rules: {change_id}

> 位置: `docs/specs/changes/{id}/contracts/validation-rules.md`

---

## Parameter Validation

| 字段 | 类型 | 校验 | 错误码 |
|------|------|------|--------|
| username | string | 长度 1-255, regex `^[a-zA-Z0-9_]+$` | 130002 |
| password | string | 长度 ≥ 8, 含大小写+数字 | 130003 |
| email | string | regex RFC 5322 | 130004 |

## Business Rules

- BR-1: 用户名唯一
- BR-2: 同一邮箱 24h 内最多 3 次注册尝试
- BR-3: 密码 90 天强制更换

## Error Messages

| 错误码 | 用户提示 | 内部提示 |
|--------|---------|---------|
| 130001 | "用户名或密码错误" | "Invalid credentials for user X" |
| 130002 | "用户名格式不正确" | "Username regex mismatch" |

## 关联引用

- [api-contracts.md](api-contracts.md)
- [domain-models.md](domain-models.md)
- V10 配置治理 D-009: 项目级 `.trae/rules/配置治理.md §5`（已蒸馏到本文档）
