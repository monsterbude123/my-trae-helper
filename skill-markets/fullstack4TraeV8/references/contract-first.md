# 01-contract / 协议先行方法论（Contract-First）

> **定位**：在 spec 之后、design 之前的新增阶段。产出独立契约工件，作为前后端/多模块/团队协作的**一等公民事实来源**。
>
> **上游**：`00-product/spec-driven-development.md`（spec.md 行为契约）
> **下游**：`10-design/planning.md`（基于契约做设计决策）

---

## 一、核心命题

**协议先行 = 契约是一等公民，先于实现，先于设计模式决策。**

```
传统 SDD:  Spec → Design(含接口契约子章节) → Code
协议先行:  Spec → Contract(独立工件) → Design(基于契约) → Code(实现契约)
```

业界标准（CSDD / SST3 / specleap）一致认为：契约不是 design.md 的子章节，而是**独立的一等公民工件**。契约稳定 = 功能防腐层。

---

## 二、为什么需要协议先行

| 痛点 | 不做协议先行的后果 | 协议先行的解药 |
|------|------------------|--------------|
| AI 实现时"猜"接口 | 接口漂移、前后端不一致 | 契约即围栏，AI 实现契约不发明契约 |
| TDD 无从下手 | TDD 被静默跳过 | 契约直接生成 contract test 骨架 |
| 前后端分离协作乱 | 等待对方改代码 | 共享契约文件，并行开发 |
| 多模块领域切分模糊 | 模块边界争吵 | 按领域切契约，契约边界即模块边界 |
| 设计模式先于接口 | 模式驱动而非契约驱动 | 契约稳定后才选设计模式 |

**核心原则**（来自 CSDD）：
> AI 是执行者不是架构师。人类设计契约，AI 实现契约。
> 零幻觉：有显式契约，AI 不需要"猜"库或类型。

---

## 三、契约工件结构

```
docs/specs/changes/{change}/contracts/
├── domain-models.md      # 领域模型 + 公共变量/类型（必填）
├── api-contracts.md      # 接口契约（前后端共享，必填）
├── event-contracts.md    # 事件契约（如适用，可选）
└── validation-rules.md   # 验证规则（如适用，可选）
```

### 3.1 domain-models.md — 领域模型

定义跨模块共享的**领域语言**和**类型契约**：

```markdown
# 领域模型: {变更名称}

## 公共类型（不可变，变更走契约变更流程）
\`\`\`typescript
type UserId = string & { readonly __brand: 'UserId' };
type Email = string & { readonly __brand: 'Email' };

interface User {
  id: UserId;
  email: Email;
  status: 'active' | 'suspended' | 'deleted';
  createdAt: ISO8601String;
}
\`\`\`

## 枚举
| 枚举 | 值 | 说明 |
|------|----|------|
| UserStatus | active / suspended / deleted | 用户状态 |

## 不变量（Invariant）
- User.email 全局唯一
- User.status=deleted 时不可恢复
```

### 3.2 api-contracts.md — 接口契约

前后端共享的接口定义，**契约稳定 = 防腐层**：

```markdown
# 接口契约: {变更名称}

## POST /api/v1/users

### 请求
| 字段 | 类型 | 必填 | 约束 |
|------|------|------|------|
| email | Email | 是 | 合法邮箱格式 |
| password | string | 是 | 8-64 字符 |

### 响应（201）
\`\`\`typescript
interface CreateUserResponse {
  code: 201;
  data: { id: UserId; email: Email; status: 'active' };
}
\`\`\`

### 错误码（契约级，前后端共享）
| code | 场景 | errors[] 示例 |
|------|------|--------------|
| 40400 | 参数校验失败 | ["email: invalid format"] |
| 40911 | 邮箱冲突 | ["email: already exists"] |

### 契约测试映射
- Contract Test: `tests/contracts/create-user.contract.test.ts`
- Spec Scenario: `specs/user-registration/spec.md#happy-path`
```

### 3.3 event-contracts.md — 事件契约（如适用）

异步事件 / 消息队列的契约：

```markdown
# 事件契约: {变更名称}

## Event: user.registered
- Producer: UserService.register()
- Consumers: EmailService, AnalyticsService
- Payload Schema:
  \`\`\`typescript
  interface UserRegisteredEvent {
    eventId: string;
    userId: UserId;
    email: Email;
    timestamp: ISO8601String;
  }
  \`\`\`
- Delivery: at-least-once
- Idempotency Key: eventId
```

### 3.4 validation-rules.md — 验证规则

跨模块共享的校验规则，避免重复实现：

```markdown
# 验证规则: {变更名称}

## Email 校验
- 规则: RFC 5322 + 长度 ≤ 254
- 实现: shared/validators/email.ts
- 契约测试: tests/contracts/email-validation.contract.test.ts

## Password 强度
- 规则: 8-64 字符，至少 1 字母 + 1 数字
- 实现: shared/validators/password.ts
```

---

## 四、契约不变量（Iron Rules）

```
┌─────────────────────────────────────────────────────────────┐
│  1. CONTRACT BEFORE DESIGN   契约稳定后才选设计模式           │
│  2. CONTRACT IS IMMUTABLE    契约不可变，变更走契约变更流程    │
│  3. CONTRACT IS SHARED       契约前后端/多模块共享            │
│  4. CONTRACT DRIVES TEST     契约直接生成 contract test 骨架  │
│  5. NO CODE WITHOUT CONTRACT 编码前契约必须 approved          │
│  6. DRIFT DETECTION MANDATORY 契约 vs 代码漂移必须检测        │
└─────────────────────────────────────────────────────────────┘
```

---

## 五、契约与其他工件的关系

```
proposal.md (Why/What)
    ↓
spec.md (BDD 行为契约 — 系统 SHALL 做什么)
    ↓
contracts/ (协议契约 — 接口/类型/事件的精确形态)  ← NEW
    ↓
design.md (技术决策 — 基于契约选设计模式)
    ↓
tasks.md (任务清单 — 实现契约)
    ↓
代码 (契约的实现)
```

**关键区分**：
- **spec.md** 回答"系统 SHALL 做什么"（行为层）
- **contracts/** 回答"接口精确长什么样"（契约层）
- **design.md** 回答"用什么模式实现契约"（实现层）

---

## 六、契约变更流程

契约是**不可变**的（Immutable Contracts，来自 specleap）。变更必须走流程：

```
发现需要改契约
    ↓
1. 评估变更影响面（grep / gitnexus impact）
    ↓
2. 输出契约变更提案
   ├── 变更类型: ADDITIVE / BREAKING
   ├── 影响范围: 前端 / 后端 / 模块X / 模块Y
   └── 迁移成本: 估计
    ↓
3. BREAKING 变更需用户确认
    ↓
4. 更新 contracts/ 文件 + 版本号
    ↓
5. 触发漂移检测：对比契约 vs 代码 vs spec
    ↓
6. 同步更新受影响的 spec.md / design.md / 代码
```

**版本号规则**：
- ADDITIVE 变更（新增字段/接口）→ 次版本 +1（1.0.0 → 1.1.0）
- BREAKING 变更（删除/改类型）→ 主版本 +1（1.0.0 → 2.0.0）

---

## 七、契约与 TDD 的绑定

协议先行对 TDD 友好的根本原因：**契约直接生成测试骨架**。

```
contracts/api-contracts.md
    ↓ （自动映射）
tests/contracts/*.contract.test.ts
    ↓ （fullstack-implementer 进来时已就绪）
🔴 RED: 填入断言 → 失败
🟢 GREEN: 实现契约 → 通过
```

**契约测试模板**：
```typescript
// tests/contracts/create-user.contract.test.ts
import { describe, it, expect } from 'vitest';
import { contract } from './contracts/create-user';

describe('Contract: POST /api/v1/users', () => {
  it('201 - 创建成功', async () => {
    const res = await fetch('/api/v1/users', {
      method: 'POST',
      body: JSON.stringify(contract.fixtures.validRequest)
    });
    expect(res.status).toBe(201);
    expect(await res.json()).toMatchObject(contract.schemas.response);
  });

  it('40400 - 参数校验失败', async () => {
    // 基于 contract.fixtures.invalidEmail
  });

  it('40911 - 邮箱冲突', async () => {
    // 基于 contract.fixtures.duplicateEmail
  });
});
```

fullstack-implementer 进来时，测试骨架已就绪，TDD 心理成本骤降。

---

## 八、契约漂移检测

参考 SST3 的 MIRROR-CONTRACT 机制：

```
契约文件 (contracts/api-contracts.md)
    ↕ 漂移检测
代码实现 (src/api/users.ts)
    ↕ 漂移检测
spec 行为 (specs/user-registration/spec.md)
```

**检测时机**：
- 编码后（Hook: `drift-detect.ps1`）
- 阶段切换时（fullstack-reviewer 强制检查）
- 提交前（pre-commit）

**漂移等级**：
| 等级 | 条件 | 行动 |
|------|------|------|
| 🟢 无漂移 | 契约 = 代码 = spec | 通过 |
| 🟡 轻微漂移 | 命名/注释不一致 | 警告但通过 |
| 🔴 严重漂移 | 类型/字段/接口签名不一致 | 🛑 强制回流改 specs/契约 |

详见 `references/feedback-loop.md`。

---

## 九、检查清单

写完契约后自检：

- [ ] domain-models.md 定义了所有跨模块共享的类型
- [ ] api-contracts.md 每个接口有请求/响应/错误码
- [ ] 每个契约项标注了对应的 contract test 路径
- [ ] 每个契约项可追溯到 spec.md 的某个 Scenario
- [ ] 契约文件版本号已标注
- [ ] BREAKING 变更已获用户确认
- [ ] 契约已 approved（门禁）

---

## 十、反面范例

| 反面（禁止） | 正确（必须） |
|---|---|
| 接口契约写在 design.md §4.3 | 独立 contracts/api-contracts.md |
| 契约写"返回用户对象" | 契约写明 TypeScript interface + 错误码 |
| 先写 design 再补契约 | 契约 approved 才能进 design |
| 契约改了不通知下游 | 契约变更走流程 + 漂移检测 |
| 契约无版本号 | 每次变更递增版本号 |
| 契约无测试映射 | 每个契约项标注 contract test 路径 |

---

## 十一、契约格式附录

> 来源：contract-writer Agent 步骤内联模板，并入供完整参考。

---

### A. 领域模型定义（domain-models.md）

```markdown
# Domain Models

## 公共类型

### UserID
- 类型: string (UUID v4)
- 格式: `^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$`
- 示例: "550e8400-e29b-41d4-a716-446655440000"

### Email
- 类型: string
- 格式: RFC 5322
- 示例: "user@example.com"

## 领域模型

### User
| 字段 | 类型 | 必填 | 约束 | 描述 |
|------|------|------|------|------|
| id | UserID | ✅ | UUID v4 | 用户唯一标识 |
| email | Email | ✅ | RFC 5322 | 邮箱 |
| name | string | ✅ | 1-100 字符 | 显示名 |
| createdAt | ISO8601 | ✅ | 时间戳 | 创建时间 |
| updatedAt | ISO8601 | ✅ | 时间戳 | 更新时间 |

### UserStatus（枚举）
- `active` — 活跃
- `inactive` — 停用
- `pending` — 待激活

## 不变量（Invariants）
- INV-001: User.email 全局唯一
- INV-002: User.updatedAt ≥ User.createdAt
- INV-003: User.status = "pending" 时 email 未验证
```

> 铁律：领域模型必须包含不变量（Invariants）。不变量是契约的护栏。

---

### B. 接口契约定义（api-contracts.md）

```markdown
# API Contracts

## 版本: v1.0.0
> Approved: YYYY-MM-DD
> Author: {fullstack-contract-writer}

---

## POST /api/v1/users

### 描述
创建新用户

### 请求

#### Headers
| 名 | 类型 | 必填 | 描述 |
|----|------|------|------|
| Content-Type | string | ✅ | `application/json` |
| Authorization | string | ✅ | `Bearer {token}` |

#### Body (application/json)
| 字段 | 类型 | 必填 | 约束 | 描述 |
|------|------|------|------|------|
| email | Email | ✅ | RFC 5322 | 邮箱 |
| name | string | ✅ | 1-100 字符 | 显示名 |

#### 示例
```json
{
  "email": "user@example.com",
  "name": "张三"
}
```

### 响应

#### 201 Created
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "user@example.com",
  "name": "张三",
  "status": "pending",
  "createdAt": "2026-06-28T10:00:00Z",
  "updatedAt": "2026-06-28T10:00:00Z"
}
```

#### 400 Bad Request
| code | 描述 |
|------|------|
| 40001 | 邮箱格式无效 |
| 40002 | 名字长度越界 |

#### 409 Conflict
| code | 描述 |
|------|------|
| 40901 | 邮箱已存在 |

### 关联 Spec
- spec.md#Scenario: Happy path — 创建用户成功
- spec.md#Scenario: Email conflict — 邮箱已存在
```

> 铁律：
> - 每个接口必须关联 spec 场景（可追溯）
> - 每个错误码必须显式定义（不靠猜）
> - 请求/响应示例必须可执行（不是占位符）

---

### C. 事件契约定义（event-contracts.md，如适用）

```markdown
# Event Contracts

## 版本: v1.0.0

---

## Event: user.created

### 描述
用户创建成功后发布

### Producer
- Service: user-service
- Trigger: POST /api/v1/users 成功创建后

### Consumers
- email-service — 发送激活邮件
- audit-service — 记录审计日志

### Payload Schema
```json
{
  "eventId": "UUID v4",
  "eventType": "user.created",
  "eventVersion": "1.0.0",
  "occurredAt": "ISO8601",
  "data": {
    "userId": "UUID v4",
    "email": "Email",
    "name": "string"
  }
}
```

### 语义保证
- 至少一次投递
- 消费者必须幂等
```

---

### D. 验证规则定义（validation-rules.md，如适用）

```markdown
# Validation Rules

## VR-001: Email 校验
- 格式: RFC 5322
- 长度: ≤ 254 字符
- 实现: `^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$`

## VR-002: Password 强度
- 长度: 8-128 字符
- 至少: 1 大写 + 1 小写 + 1 数字 + 1 特殊字符
- 黑名单: 常见弱密码（password、123456 等）

## VR-003: Pagination 参数
- page: ≥ 1
- pageSize: 1-100
- 默认: page=1, pageSize=20
```

---

### E. Contract Test 骨架

```markdown
## Contract Tests 骨架

### POST /api/v1/users
- [ ] test_create_user_happy_path
  - 请求: { email: "user@example.com", name: "张三" }
  - 期望: 201 + User 对象（status=pending）
- [ ] test_create_user_invalid_email
  - 请求: { email: "invalid", name: "张三" }
  - 期望: 400 + code=40001
- [ ] test_create_user_duplicate_email
  - 请求: { email: "existing@example.com", name: "张三" }
  - 期望: 409 + code=40901
```

> 铁律：契约 approved 后，contract test 骨架移交给 fullstack-implementer 作为 TDD 起点。

---

### F. BREAKING 变更记录格式

```markdown
## BREAKING CHANGES (v2.0.0)
- [2026-06-28] 删除 User.middleName 字段（用户确认：业务不再需要）
- [2026-06-28] 修改 POST /api/v1/users 响应 code=40001 语义（用户确认）
```

---

### G. AOP POST Q 典型问题

```
Q: [POST][P-01][domain-models.md 是否包含本次变更涉及的所有实体][全部包含/部分包含]
Q: [POST][P-02][api-contracts.md 中每个 endpoint 是否声明了所有可能的错误码][完整/缺失/未声明]
Q: [POST][P-03][每个 API 是否关联到 spec 场景][全部关联/部分关联]
Q: [POST][P-04][contract test 骨架是否存在且每个 API 至少 1 个测试][存在/缺失]
Q: [POST][P-05][contracts/ 中的领域模型/接口定义是否与 modules/*.md 中的已有定义全文重复（V8 NEW）][无重复/有疑似重复段]
Q: [POST][P-06][contracts/ 中是否有接口被标记为 published（其他模块必须遵循的公共契约）|有—已标注 / 无 / 不确定—标无]
```

---

### H. `@published` 注释块标注规则

被其他模块依赖的公共接口/事件/模型，需在接口注释中标注：
```
# @published — 被 {模块X, 模块Y} 依赖
```
- 标注位置：接口标题下方
- 标注条件：接口被 ≥1 个其他模块引用
- 标注后冻结修改（BREAKING 变更需用户确认）
