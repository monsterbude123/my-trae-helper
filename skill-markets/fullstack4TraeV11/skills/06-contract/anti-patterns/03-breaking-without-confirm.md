# 反例 3：BREAKING 变更不走用户确认（Breaking Without Confirm）

> BREAKING 变更（删除字段 / 改类型 / 改路径）必走用户确认 + major 版本号 + 三方同步。跳过 = 客户端崩溃 + 6h 排错（V10 D-009 实战）。

**违反**：铁律 4（ADDITIVE OVER BREAKING）
**严重度**：P0（直接生产事故 + 客户端崩溃）

---

## 现象

```yaml
# Stage 2 反例（V10 D-009 实战）

# 旧契约
config:
  api_key: "sk-xxx"           # 全小写
  api_url: "https://api.example.com"

# 新契约（反例：BREAKING 变更未通知）
config:
  API_KEY: "sk-xxx"           # 改为大写 ← BREAKING
  apiUrl: "https://api.example.com"   # 改驼峰 ← BREAKING

# ❌ 反例：未走用户确认 + 未走 major 版本号
#          后端改了大小写 → 前端读取失败 → 6 小时排错
```

**识别信号**:
- 契约变更含 BREAKING（删除字段 / 改类型 / 改路径 / 改大小写）
- 提交时未走 AskUserQuestion 用户确认
- 版本号未升 major
- 客户端在不知情下崩溃

---

## 根因

- **认知维度**：觉得"反正有版本号"，不区分 major/minor/patch
- **流程维度**：跳过 BREAKING 变更用户确认 Step
- **责任维度**：contract-writer 越权做 BREAKING 决策

| 根因 | 占比 |
|------|:---:|
| 视版本号为万能（不区分 major/minor/patch）| 50% |
| 跳过 BREAKING 用户确认 Step | 30% |
| contract-writer 越权做 BREAKING 决策 | 20% |

---

## 教训

- **V10 D-009 实战**：后端把 config key 从 `api_key` 改为 `API_KEY`（大小写变化），前端用 `process.env.api_key` 读取 → undefined → 整个功能崩溃 → 6 小时排错才发现是大小写问题
- **真实场景**：删除 `user.phone` 字段（"反正用户不用"）。生产环境老客户端调用 `/api/users/{id}` 仍读 phone → undefined → 前端白屏 → 用户投诉爆表
- **类型变更反例**：`age: number` 改为 `age: string`（"为了支持 '18岁' 这种表述"）。前端 `parseInt(user.age)` → NaN → 表单提交失败 → 数据丢失

---

## 正确替代

```yaml
# ✅ 正确：BREAKING 变更必走 4 步流程

## Step 1: 识别 BREAKING（contract-writer 自检）

BREAKING 类型清单:
  - 删除字段（API response 减少字段）
  - 改类型（string → number / number → string / int → long）
  - 改路径（/api/v1/users → /api/v2/users）
  - 改大小写（api_key → API_KEY）← V10 D-009 反例
  - 改枚举值（role: 'admin' → 'super_admin'，旧值删除）
  - 必填字段新增（旧客户端未传 → 服务端拒绝）

识别到任一 → 触发 BREAKING 流程（不可跳过）
```

```yaml
## Step 2: AskUserQuestion 用户确认

Q: 检测到 BREAKING 变更（删除 user.phone 字段）。
   是否确认升级到 major 版本（v1 → v2）？

选项:
  A: 确认升级 major + 通知所有客户端迁移
  B: 改为 ADDITIVE（保留旧字段 + 新字段，标 deprecated）
  C: 暂缓变更（保留旧契约）

用户答 A → 进入 Step 3
用户答 B → 改写契作为 ADDITIVE
用户答 C → 撤销变更
```

```yaml
## Step 3: 版本号升 major

package.json: "1.x.x" → "2.0.0"
api-contracts.md: 顶部版本号同步
CHANGELOG.md: 必含 BREAKING CHANGES 章节
通知所有下游: 邮件 / Slack / 客户公告
```

```yaml
## Step 4: 三方同步（V10 D-009 修复协议）

# 必改 3 处
1. 代码: 实现新契约
2. 契约文档: api-contracts.md 更新（标注 BREAKING + 迁移指南）
3. 测试: tests/contracts/ 新增 v2 测试 + 保留 v1 测试（迁移期）

# drift-detect 验证三方一致
python scripts/drift-detect.py
# 输出: code ↔ contract ↔ test 一致性 100%
```

```yaml
# ✅ ADDITIVE 替代方案（推荐）

# 不删除旧字段，而是 deprecated
config:
  api_key: "sk-xxx"           # 保留（deprecated: true）
  API_KEY: "sk-xxx"           # 新字段（推荐使用）
  apiUrl: "https://api.example.com"   # 新字段

deprecation_policy:
  api_key:
    deprecated_since: "2.0.0"
    remove_in: "3.0.0"（给客户端 1 年迁移期）
    migration_guide: "改用 API_KEY（驼峰）"
```

---

## BREAKING 决策矩阵

| 变更类型 | 是否 BREAKING | 推荐做法 |
|---------|:------------:|---------|
| 新增字段 | � 否 | 直接 ADDITIVE |
| 新增可选字段 | ❌ 否 | 直接 ADDITIVE |
| 改字段类型 | ✅ 是 | 必走 major + 通知 |
| 删除字段 | ✅ 是 | 必走 major 或 deprecated 标记 |
| 改路径 | ✅ 是 | 保留旧路径 + 新路径（迁移期）|
| 改大小写 | ✅ 是 | V10 D-009 反例，必走确认 |
| 改枚举值 | ✅ 是 | 保留旧值 + 新值（迁移期）|
| 新增必填 | ✅ 是 | 客户端必传 → 必走 major |

---

## Stage 4 Review 验证协议

```yaml
# reviewer 必走
1. 检测 BREAKING 类型清单（contract-writer 自检表）
2. BREAKING 变更无用户确认记录 → 🛑 REJECT
3. 版本号未升 major → 🛑 REJECT
4. CHANGELOG.md 无 BREAKING CHANGES 章节 → 🛑 REJECT
5. 代码 / 契约 / 测试三方不同步 → 🛑 REJECT
6. 优先建议 ADDITIVE 方案（除非用户明确选 major）
```

---

## 反模式识别（V11 实战踩雷）

| 反例类型 | 后果 |
|---------|------|
| 大小写变化未通知 | 🛑 6h 排错（V10 D-009） |
| 删除字段未通知 | 客户端白屏 → 用户投诉 |
| 类型变更未通知 | parseInt NaN → 数据丢失 |
| major 版本未升 | 下游不知情 → 全部崩溃 |
| 无 CHANGELOG | 后续维护者不知历史 |
| 不走用户确认直接改 | 🛑 越权（contract-writer 无权 BREAKING） |

---

## 关联引用

- [SKILL.md §铁律 4](../SKILL.md) — ADDITIVE OVER BREAKING
- V10 配置治理 §5 D-009: [../../../.trae/rules/配置治理.md](../../../.trae/rules/配置治理.md) — 大小写不一致 6h 排错实战
- 公共铁律 Article VIII: [../../../references/common-iron-rules.md](../../../references/common-iron-rules.md)
