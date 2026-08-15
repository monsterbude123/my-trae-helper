# 反例 3：Spec 写实施（Spec Write Implementation）

> **V11.7.0+ 设计入口**: [AC 核销门禁](../skills/09-review/SKILL.md) · [贾维斯门禁守护](../skills/00-boot/SKILL.md) · 评分制废除 → 门禁制 · 详见 [CHANGELOG.md V11.7.0](../CHANGELOG.md)


> Spec 只写 What + Why，不写 How（代码 / 类名 / 函数签名 / 库名）。含代码 = Stage 2 Contract 矛盾 + Stage 3 实施者失去判断空间。

**违反**：铁律 7（NEVER 写实施）
**严重度**：P2（过程性缺陷，导致 Stage 2/3 边界模糊 + 实施者无判断空间）

---

## 现象

```markdown
# spec.md（反例版本）

## 登录功能

### 实现细节
```typescript
// ❌ 反例：spec.md 写了代码片段
function login(username: string, password: string): Promise<Token> {
    const user = await db.query('SELECT * FROM users WHERE username = $1', [username])
    if (!user) throw new Error('User not found')

    const valid = await bcrypt.compare(password, user.password_hash)
    if (!valid) throw new Error('Invalid password')

    const token = jwt.sign({ userId: user.id }, SECRET, { expiresIn: '7d' })
    return token
}
```

### 技术栈
- 数据库: PostgreSQL
- 密码哈希: bcrypt
- Token: JWT
- ORM: Prisma

# ❌ 反例 1: 代码片段（function / class / type）
# ❌ 反例 2: 具体技术栈绑定（Postgres / bcrypt / JWT）
# ❌ 反例 3: 字段名 / 表名硬编码（users.username / password_hash）
```

**识别信号**:
- spec.md 含 ``` 代码块（除"伪代码 / 数据结构示意"外）
- spec.md 含具体技术栈绑定（数据库 / 框架 / 库名）
- spec.md 含函数签名 / 类名 / 表名 / 字段名
- Stage 2 Contract 与 spec.md 代码段不一致时，边界模糊

---

## 根因

- **认知维度**：把"spec"当作"实施文档"，未区分 spec vs contract vs code
- **流程维度**：spec-writer 越过边界，写了 Stage 3 实施者的工作
- **责任维度**：spec-writer 替代实施者做技术决策（库/框架选择）

| 根因 | 占比 |
|------|:---:|
| 视 spec 为实施文档（边界错位）| 55% |
| spec-writer 越权（责任主体错位）| 30% |
| 缺乏 spec / contract / code 三层分离意识 | 15% |

---

## 教训

- **V11 实战**：spec-writer 写"用 bcrypt 哈希密码"。Stage 3 实施者评估"项目用 Argon2id 更安全（OWASP 推荐）" → 与 spec.md 矛盾 → 实施者改 spec → spec-writer 投诉越权 → 流程阻塞 2 天
- **真实场景**：spec.md 写 `function login() { ... }` → Stage 3 实施者以为这是实施约束 → 写代码时严格按 spec 函数签名 → 但 spec 函数签名有 bug（未考虑异常路径）→ 实施代码也带 bug
- **技术栈绑定反例**：spec.md 写"用 PostgreSQL" → 客户生产环境用 MySQL → 实施者强行迁移 → 性能下降 30% → 用户投诉

---

## 正确替代

```markdown
# spec.md（正确版本）

## 登录功能（What）

### 能力描述
- 用户输入凭据（用户名 + 密码）→ 系统验证 → 返回访问令牌
- 令牌用于后续 API 调用的身份认证

### 输入输出契约（Why + 接口语义）
- 输入: { username: string, password: string }
- 输出成功: { token: string, expiresAt: ISO8601 }
- 输出失败: { error: "InvalidCredentials" | "UserNotFound" | "RateLimited" }

### 业务规则
- BR-001: 密码必须以单向哈希存储（不可逆）
- BR-002: Token 必含过期时间
- BR-003: 失败次数过多必触发限流

### 验收 INV
- INV-001: 错误密码的响应时间与不存在用户的响应时间应一致（防时序攻击）
- INV-002: 失败 5 次后必锁定 30 分钟
- INV-003: Token 过期后必拒绝访问

# ✅ 正确：
#   - 无代码片段（除示意数据结构）
#   - 无具体技术栈绑定
#   - 无函数签名 / 类名
#   - 业务规则 + INV = 实施者可自由选择技术方案
```

```yaml
# ✅ 数据结构示意（允许的"代码"形式）

User:
  id: UUID
  username: string  # 登录标识
  password_hash: string  # 单向哈希
  created_at: timestamp
  last_login_at: timestamp | null

# 注：这是数据结构示意，不是数据库表定义
#     实施者可选择 Postgres / MySQL / MongoDB
#     字段名可调（user_id / userId / id）
```

---

## Spec / Contract / Code 三层分离

```yaml
# V11 Stage 1 / 2 / 3 边界
Stage 1 Spec:
  内容: What + Why（能力 + 业务规则 + INV）
  不写: 代码 / 技术栈 / 库名
  责任: spec-writer + 用户

Stage 2 Contract:
  内容: 接口语义（API / 事件 / 数据模型）
  可写: 数据结构 / 字段名 / 类型（接口级，非代码）
  不写: 函数实现 / 算法 / 业务逻辑
  责任: contract-writer

Stage 3 Implement:
  内容: How（代码 / 技术选型 / 实现）
  可写: 函数 / 类 / 库 / 框架
  责任: implementer
```

---

## Stage 4 Review 验证协议

```yaml
# reviewer 必走
1. spec.md 含 ``` 代码块（实现细节）→ 🛑 REJECT
2. spec.md 含具体技术栈（Postgres / bcrypt / JWT）→ 🛑 REJECT
3. spec.md 含函数签名 / 类名 / 表名 → 🛑 REJECT
4. spec.md 数据结构示意（仅字段名+类型）→ ✅ 允许
5. spec.md 含"我们建议用 X" → 🛑 REJECT（建议 = 越权）
6. Stage 3 实施者因 spec.md 技术栈绑定而无法选更优方案 → 🛑 REJECT spec.md
```

---

## 反模式识别（V11 实战踩雷）

| 反例类型 | 后果 |
|---------|------|
| spec.md 含代码片段 | 实施者失去判断空间 + spec/contract 边界模糊 |
| spec.md 绑死技术栈 | 客户环境不匹配 → 强行迁移 → 性能下降 |
| spec.md 含函数签名 | 实施者不敢优化 → bug 传递 |
| spec.md 含"我们建议用 X" | 🛑 越权（建议 = spec-writer 替实施者决策） |
| spec.md 数据结构示意 + 实施者误以为是 schema | 🛑 Stage 2/3 边界模糊 |

---

## 关联引用

- [SKILL.md §铁律 7](../SKILL.md) — NEVER 写实施
- 公共铁律 Article VII: [../../../references/common-iron-rules.md](../../../references/common-iron-rules.md) — Spec/Contract/Code 三层分离
- [acceptance-enhancement.md](../references/acceptance-enhancement.md) — What + Why 模板
