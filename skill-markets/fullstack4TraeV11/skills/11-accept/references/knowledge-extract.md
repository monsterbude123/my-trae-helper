# 知识沉淀协议（Knowledge Extract）

> **V11.7.0+ 设计入口**: [AC 核销门禁](../skills/09-review/SKILL.md) · [贾维斯门禁守护](../skills/00-boot/SKILL.md) · 评分制废除 → 门禁制 · 详见 [CHANGELOG.md V11.7.0](../CHANGELOG.md)


> Stage 5 Accept Step 2 必走。V10 prd-integration-workflow.md + spec-knowledge-extract.py 蒸馏。

---

## spec-knowledge-extract.py 流程

```bash
# 提取 API 契约 → docs/api-endpoints/
python ../../scripts/spec-knowledge-extract.py --change-id {id} --type api

# 提取领域模型 → docs/domain-models/
python ../../scripts/spec-knowledge-extract.py --change-id {id} --type domain

# 提取事件 → docs/events/
python ../../scripts/spec-knowledge-extract.py --change-id {id} --type events
```

## 沉淀内容

| 类型 | 来源 | 输出 |
|------|------|------|
| API | contracts/api-contracts.md | docs/api-endpoints/{endpoint}.md |
| Domain | contracts/domain-models.md | docs/domain-models/{entity}.md |
| Events | contracts/events.md | docs/events/{event-name}.md |

## INDEX 更新

```markdown
# docs/INDEX.md 增量更新

## API Endpoints

- `auth-login` (docs/api-endpoints/auth-login.md) — 用户登录
- `user-create` (docs/api-endpoints/user-create.md) — 用户创建（新增 2026-08-11）

## Domain Models

- `User` (docs/domain-models/User.md) — 用户实体（新增 2026-08-11）

## Events

- `UserRegistered` (docs/events/UserRegistered.md) — 用户注册事件（新增 2026-08-11）
```

## CHANGELOG 追加

```markdown
# docs/CHANGELOG.md

## [2026-08-11] change-001-add-user-auth
- Added: UserService + TokenService
- Added: POST /api/v1/auth/login
- Modified: User entity (新增 email_verified 字段)
```

## 反例

### 反例 A：跳过知识沉淀直接归档

```
主上下文: spec-purge → archive  # ❌ INDEX 未更新
正确: knowledge-extract → INDEX 更新 → CHANGELOG → archive
```

### 反例 B：INDEX 与归档不一致

```
归档目录有 user-create.md → INDEX 没列  # ❌ 文档腐烂
正确: 归档必含 INDEX 更新 + CHANGELOG
```

---

## 关联引用

- [SKILL.md §铁律 2](../SKILL.md)
- [archive-protocol.md](archive-protocol.md)
- V10 prd-integration-workflow.md: `V10 来源` (已蒸馏到本文档)
