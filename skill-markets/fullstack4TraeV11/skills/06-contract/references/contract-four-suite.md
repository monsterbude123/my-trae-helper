# 契约四件套详细规则（Contract Four-Suite）

> Stage 2 Contract Step 2-3 必走。V10 contract-writer.md + contract-first.md 蒸馏。

---

## 四件套结构

### 1. domain-models.md（先于接口）

**位置**: `docs/specs/changes/{id}/contracts/domain-models.md`

**内容**:
- 领域实体（Entities）
- 值对象（Value Objects）
- 聚合根（Aggregate Roots）
- 不变量（INV）
- 状态机（如有）

**INV 定义规则**（V10 spec.md INV 蒸馏）:
- 数据一致性（事务原子性）
- 安全约束（认证必在授权前）
- 业务规则（订单总额 = 单价 × 数量）

### 2. api-contracts.md

**位置**: `docs/specs/changes/{id}/contracts/api-contracts.md`

**内容**:
- API 路径 + HTTP method
- 请求/响应 schema（type + format）
- 错误码 + 错误响应
- 鉴权要求

**示例**:
```yaml
- path: /api/v1/auth/login
  method: POST
  request:
    body: { username: string, password: string }
  response:
    200: { token: string, expires_at: ISO8601 }
    401: { error: "invalid_credentials", code: 130001 }
  auth: required (none for login)
```

### 3. events.md（如适用）

**位置**: `docs/specs/changes/{id}/contracts/events.md`

**内容**:
- 事件名 + schema
- 发布者 / 订阅者
- 触发条件

### 4. validation-rules.md

**位置**: `docs/specs/changes/{id}/contracts/validation-rules.md`

**内容**:
- 参数校验（regex / 长度 / 范围）
- 业务规则校验
- 错误信息模板

---

## DOMAIN FIRST 顺序

```
domain-models.md (INV 先定)
  ↓
api-contracts.md (基于实体 + INV)
  ↓
events.md (基于 API + 业务事件)
  ↓
validation-rules.md (基于 API 参数)
```

**反模式**: 直接写 API → 后期补 domain → 大量返工。

---

## 错误码规范（V10 实战）

**6 位错误码**: `{module}{3 digits}{sub_code}`

示例:
- `130001` = auth 模块 001 号错误 = invalid_credentials
- `auth-003` = auth 模块 003 = token_refresh_failed

**V10 D-009 实战**: 错误码必须前后端一致 + 文档同步。

---

## 关联引用

- [SKILL.md §铁律 2](../SKILL.md) — DOMAIN FIRST
- [orphan-test-sweep.md](orphan-test-sweep.md) — 孤儿测试扫描
- V10 contract-writer.md: `V10 来源` (已蒸馏到本文档)
- V10 contract-first.md: `V10 来源` (已蒸馏到本文档)
