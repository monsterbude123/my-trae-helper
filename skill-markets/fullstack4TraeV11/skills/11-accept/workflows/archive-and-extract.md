# Archive and Extract — Stage 5 Accept

> Stage 5 Accept 必走。归档 + 知识沉淀协议。

---

## 5 步流程

```
Step 1: 归档前检查
  └─ spec.md + contracts/ + review-report.md + rot-scan PASS

Step 2: spec-knowledge-extract.py
  └─ docs/api-endpoints/ + domain-models/ + events/

Step 3: spec-purge.py
  └─ _invalidated/ 隔离 → archive/done/

Step 4: docs/INDEX.md + CHANGELOG.md 更新

Step 5: 状态卡 stage_status = archived + health = 🟢
```

---

## Step 1: 归档前检查

```yaml
required_artifacts:
  - docs/specs/changes/{id}/spec.md
  - docs/specs/changes/{id}/plan.md
  - docs/specs/changes/{id}/contracts/domain-models.md
  - docs/specs/changes/{id}/contracts/api-contracts.md
  - docs/specs/changes/{id}/contracts/events.md
  - docs/specs/changes/{id}/contracts/validation-rules.md
  - docs/specs/changes/{id}/review-report.md
  - docs/reports/rot-scan-{date}.md
  - docs/reports/verify-report.md
```

任一缺失 → 5 字段阻塞报告 + 状态卡 blocked。

---

## Step 2: 知识沉淀

```bash
# 提取 API 契约
python ../../scripts/spec-knowledge-extract.py --change-id {id} --type api

# 提取领域模型
python ../../scripts/spec-knowledge-extract.py --change-id {id} --type domain

# 提取事件
python ../../scripts/spec-knowledge-extract.py --change-id {id} --type events
```

输出:
- `docs/api-endpoints/{endpoint}.md`
- `docs/domain-models/{entity}.md`
- `docs/events/{event-name}.md`

---

## Step 3: 归档隔离（spec-purge.py）

```bash
# Dry-run 验证
python ../../scripts/spec-purge.py --change-id {id} --dry-run

# 实际归档
python ../../scripts/spec-purge.py --change-id {id}
```

操作:
1. 隔离原 change → `_invalidated/{timestamp}-{id}/`
2. 归档到 `archive/done/{id}/`

---

## Step 4: INDEX 更新

`docs/INDEX.md` 增量：

```markdown
## API Endpoints

- [auth-login](docs/api-endpoints/auth-login.md) — 用户登录
- [user-create](docs/api-endpoints/user-create.md) — 用户创建（新增 2026-08-11）

## Domain Models

- [User](docs/domain-models/User.md) — 用户实体（新增 2026-08-11）

## Events

- [UserRegistered](docs/events/UserRegistered.md) — 用户注册事件（新增 2026-08-11）
```

`docs/CHANGELOG.md` 追加：

```markdown
## [2026-08-11] change-001-add-user-auth
- Added: UserService + TokenService
- Added: POST /api/v1/auth/login
- Modified: User entity (新增 email_verified 字段)
```

---

## Step 5: 状态卡归档

```yaml
current_stage: 5/accept
stage_status: completed
health: "🟢 on-track"
updated_at: {ISO 8601}
artifacts:
  - path: docs/archive/done/{id}/
    type: directory
    exists: true
```

---

## 反例

### 反例 A：跳过知识沉淀直接归档

```
spec-purge → archive/  # ❌ INDEX 未更新
正确: knowledge-extract → INDEX → CHANGELOG → archive
```

### 反例 B：归档后修改归档

```
CLOSE 归档 → 用户反馈 → 直接 Edit archive/done/{id}/  # ❌ Article VIII
正确: 新建 change 重新走流程
```

---

## 关联引用

- [SKILL.md](../SKILL.md)
- [archive-protocol.md](../references/archive-protocol.md)
- [knowledge-extract.md](../references/knowledge-extract.md)