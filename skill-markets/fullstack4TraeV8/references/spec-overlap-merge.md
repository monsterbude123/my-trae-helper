# 30% 需求原子化去重（V7 NEW）

> 防止"用户在不同会话提类似需求 → 不同 Agent 建重复 change → spec 爆炸"。

---

## 设计动机

来自实战教训：

用户在多个会话中讨论同一功能的不同方面，每次都可能触发 Agent 创建新 change。结果是一个功能有 3-4 个重叠的 change，各自的 spec 互相矛盾，验收时发现重复建设。

30% 规则通过**原子化 + 量化重叠 + 强制合并**解决这个问题。

---

## 原子化方法

把用户需求拆成**不可再分的独立功能点**：

```
用户需求："我要一个用户系统，能注册登录，能重置密码，还能绑定 Google 账号"

原子化：
  1. 邮箱注册
  2. 邮箱+密码登录
  3. 密码重置
  4. Google OAuth 绑定
```

**原子化粒度参考**：
- 细了（"输入邮箱校验格式"）：太碎，导致误判重叠
- 粗了（"用户系统"）：太粗，无法做重叠比较
- 合适：一个用户可以独立验证的、有明确边界的完整功能点

**原则**：如果用户能看到和验证这个功能点，它就是一个原子。如果只是实现细节，它不是原子。

---

## 去重流程

```
新需求进来
  ↓
intake 原子化用户需求（拆成独立功能点，记为 A1...An）
  ↓
并行搜索已有 change：
  - Glob docs/specs/changes/*/proposal.md
    → 读每个 proposal 的 Capabilities 段
  - Grep 每个原子点关键词在 docs/specs/changes/*/specs/
  - Grep 每个原子点关键词在 docs/specs/changes/*/proposal.md
  ↓
对每个已有 change 计算重叠度：
  匹配的原子点数 / 新需求总原子点数 = 重叠度%
  ↓
对重叠度最高的 change 做判定
```

### 判定矩阵

| 重叠度 | 判定 | 操作 |
|--------|------|------|
| ≥ 70% | 完全覆盖 | 🛑 不创建新 change，告知用户已有 change |
| 30%-70% | 合并候选 | ⚠️ 根据已有 change 当前阶段决定 |
| < 30% | 无实质重叠 | ✅ 创建新 change |

### 合并候选的子判定

| 已有 change 阶段 | 操作 |
|-----------------|------|
| intake / proposal / spec | **自动合并**：扩展已有 change 的 specs/，被合并的 change 归档到 archive/out/ |
| contract / design | **警告用户**：合并可能推翻已审批的 contracts，用户决定 |
| dev / review / accept | **不合并**：创建新 change，proposal 中标记交叉引用到已有 change |

---

## 合并执行步骤

由主 Agent 执行：

```
1. 用户确认合并
2. 读取被合并 change 的所有工件
3. 已完成且有效的内容 → docs/archive/done/{change-name}/
4. 被淘汰的工件 → docs/archive/out/{change-name}/
5. 未完成的 spec → 合并入目标 change 的 specs/
6. 更新目标 change 的 proposal.md（扩展 Capabilities 段）
7. 更新目标 change 的 .state-card.md（标记覆盖范围扩展）
8. 更新项目级 Cockpit（移除被合并 change 行）
9. 通知用户合并完成
```

---

## 输出：去重报告

intake 在步骤 1.5 输出去重报告：

```markdown
## 🔍 去重报告

### 原子化结果
- [原子点1], [原子点2], [原子点3], [原子点4]

### 重叠分析
| 已有 change | 匹配原子点 | 重叠度 | 阶段 | 判定 |
|-------------|-----------|--------|------|------|
| 01-auth | [原子点1, 原子点2] | 50% | spec | ⚠️ 合并候选 |
| 02-profile | [原子点3] | 25% | design | ✅ 无重叠 |

### 最终决定
- **合并到 01-auth**（50% 重叠，proposal 阶段，自动合并）
- 01-auth 的 proposal.md 将扩展以下 Capabilities: [原子点3, 原子点4]
```

---

## 特殊情况处理

### 多个 change 都有中等重叠

如果新需求与 change-A 重叠 40%，与 change-B 重叠 35%：
- 按重叠度最高优先 → 合并到 change-A
- 如果 change-A 和 change-B 内容交叉 → 考虑先合并 change-A 和 change-B

### 用户坚持不合并

用户说"这是两个不同的需求，不要合并"：
- 尊重用户决定
- 但记入去重报告，标记"用户选择不合并"
- 在 Cockpit 中标记两个 change 有交叉引用
- 验收时 reviewer 检查两个 change 是否有冲突

### 需求原子化本身有分歧

用户说"你这原子化的不对，这不是一个功能"：
- 回退到 AskUserQuestion，让用户确认原子化结果
- 重新计算重叠度

---

## 与 SKILL.md 的集成

SKILL.md 中的铁律 11：

```
11. SPEC OVERLAP MUST MERGE  需求原子化重叠 > 30% 必须合并，禁止重复建设
```

执行原则 5：

```
5. 去重必执行：intake 必须执行 30% 重叠检查
```

参考路由：`[references/spec-overlap-merge.md](references/spec-overlap-merge.md)`
