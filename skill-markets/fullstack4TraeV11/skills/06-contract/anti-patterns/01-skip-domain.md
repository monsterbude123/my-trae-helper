# 反例 1：跳过 DOMAIN FIRST 直接写 API（Skip Domain First）

> 契约必须先写 domain-models.md（含 INV），后写 api-contracts.md。先 API 后 domain = INV 字段缺失 + Stage 3 实施返工。

**违反**：铁律 2（DOMAIN FIRST）
**严重度**：P1（直接导致 INV 与 API 矛盾 + Stage 3 实施返工）

---

## 现象

```yaml
# Stage 2 流程（反例顺序）

Step 1: 先写 api-contracts.md
  POST /api/users
  request: { username, password, email }
  response: { id, username, email, created_at }

Step 2: 后补 domain-models.md
  User: { id, username, password_hash, email, role, created_at }

# ❌ 反例：API 不含 role 字段
#          但 domain Model 含 role 字段（INV: 必填 role）
#          矛盾点：API 调用者无法设置 role → 用户全部 default = "user"
#          后期补 domain 时发现 INV 与 API 矛盾 → 返工
```

**识别信号**:
- Stage 2 文档生成顺序错误：先 api-contracts.md 后 domain-models.md
- api-contracts.md 字段 < domain-models.md 字段
- INV 在 domain-models.md 定义但 API 无对应字段
- Stage 3 实施时发现 API 缺字段 → 重新改 API（破坏下游）

---

## 根因

- **认知维度**：觉得"API 是用户视角，先写 API"
- **流程维度**：跳过 contract-four-suite.md §DOMAIN FIRST 顺序
- **责任维度**：contract-writer 把 API 当作契约的唯一形态

| 根因 | 占比 |
|------|:---:|
| 视 API 为契约唯一形态 | 50% |
| 跳过 contract-four-suite §DOMAIN FIRST | 35% |
| 不理解 domain 是 API 的真子集 | 15% |

---

## 教训

- **V11 实战**：先写 api-contracts.md（含 5 个字段），后补 domain-models.md（含 8 个字段，含 INV: 必填 role）→ API 调用者无法设 role → 全部 default → 权限系统失效 → 紧急改 API（破坏 3 个下游调用方）→ 2 周修复期
- **真实场景**：domain 含 `password_hash` 但 API 含 `password`（明文）。API → domain 转换缺哈希逻辑 → 实施时临时补 → 安全漏洞
- **INV 矛盾反例**：domain INV "用户必填 role"，但 API 无 role 字段 → 实施时强制 default = "user" → 所有新用户无管理员权限 → 业务方无法初始化 admin

---

## 正确替代

```yaml
# ✅ 正确顺序（contract-four-suite.md §DOMAIN FIRST）

## Stage 2 强制顺序

Step 1: domain-models.md（含 INV）
  User: {
    id: UUID,
    username: string,           # INV: 3-30 字符（基于业务规则 BR-001）
    password_hash: string,      # INV: 单向哈希（基于业务规则 BR-002）
    email: string,              # INV: RFC-5322 邮箱格式
    role: enum['user','admin'], # INV: 必填，默认 user（基于业务规则 BR-007）
    created_at: timestamp,
    last_login_at: timestamp | null
  }

  INV 推导:
    - INV-001: role 必填（基于 BR-007 权限规则）
    - INV-002: username 不可重复（基于 BR-001 唯一性）
    - INV-003: email 不可重复（基于 BR-005 唯一性）

Step 2: api-contracts.md（API 字段 ⊇ Domain 字段）
  POST /api/users
  request: {
    username: string,       # → domain.username
    password: string,       # → 转换为 domain.password_hash（API 不暴露明文）
    email: string,          # → domain.email
    role: enum              # → domain.role（API 必含，否则 INV-001 失败）
  }
  response: {
    id, username, email, role, created_at
    # password_hash 不暴露（安全）
  }

Step 3: events.md（领域事件）
  UserCreated: { user_id, username, role, timestamp }
  UserLoggedIn: { user_id, timestamp, ip }

Step 4: validation-rules.md
  username: 长度 3-30，字符集 [a-zA-Z0-9_]
  password: 长度 ≥ 12，强度 NIST 推荐
  email: RFC-5322 + DNS MX 记录校验
  role: enum 校验
```

```yaml
# ✅ 字段覆盖断言

# api-contracts.md 字段 ⊇ domain-models.md 字段
# 但 domain 含 password_hash，API 不暴露 password_hash（安全映射）

字段映射断言:
  api.username → domain.username           # ✅ 直映射
  api.password → domain.password_hash       # ✅ 转换映射（API 不暴露）
  api.email → domain.email                  # ✅ 直映射
  api.role → domain.role                    # ✅ 直映射（API 必含）
  api.* → domain.*                          # ✅ 全部覆盖

API 不暴露:
  - password_hash                            # 安全
  - internal_flags                           # 内部字段
```

---

## contract-four-suite.md 强制顺序

```yaml
# V11 Stage 2 四件套生成顺序
顺序（不可逆）:
  1. domain-models.md      # 必先：定义领域 + INV
  2. api-contracts.md      # 次之：API 是 domain 的视图
  3. events.md             # 再次：领域事件
  4. validation-rules.md   # 最后：字段级校验

# 字段覆盖断言（自动检查）
- api.* ⊇ domain.* (除 security 字段)
- events.* ⊇ domain.* state transitions
- validation.* ⊇ domain.* INV 字段约束
```

---

## Stage 4 Review 验证协议

```yaml
# reviewer 必走
1. Stage 2 文档生成顺序（git log）检查
   - domain-models.md commit 时间 < api-contracts.md commit 时间
2. api-contracts.md 字段 ⊇ domain-models.md 字段
3. domain INV 字段必在 API 体现（如 role）
4. API 不暴露 domain security 字段（如 password_hash）
5. 顺序错误或字段缺失 → 🛑 REJECT
```

---

## 反模式识别（V11 实战踩雷）

| 反例类型 | 后果 |
|---------|------|
| 先 API 后 domain | INV 与 API 矛盾 → 返工 |
| domain 字段 > API 字段 | 实施时强制 default → 业务失效 |
| API 含明文 password | 🛑 安全漏洞（应转换为 password_hash） |
| domain INV 字段 API 无 | INV-001 失败 → 权限/数据问题 |
| 字段映射无断言 | Stage 4 Review 无法自动化检查 |

---

## 关联引用

- [SKILL.md §铁律 2](../SKILL.md) — DOMAIN FIRST
- [contract-four-suite.md §DOMAIN FIRST 顺序](../references/contract-four-suite.md) — 四件套强制顺序
- [domain-driven-design.md](../workflows/domain-driven-design.md) — Domain 建模 Step
- 公共铁律 Article VIII: [../../../references/common-iron-rules.md](../../../references/common-iron-rules.md)
