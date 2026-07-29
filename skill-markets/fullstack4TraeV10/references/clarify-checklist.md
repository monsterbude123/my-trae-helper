# Clarify 检查清单（借鉴 spec-kit /speckit.clarify）

> spec-enhancer 在追加 Enhanced Acceptance 前必跑此清单。
> 命中任意 1 项 = 必须 clarify，最多 5 个问题。

---

## 1. 模糊词检测（正则）

| 模式 | 含义 | 命中动作 |
|------|------|---------|
| `可能` | 不确定 | 必须 clarify |
| `大概` | 不确定 | 必须 clarify |
| `似乎` | 推测 | 必须 clarify |
| `用户觉得` | 用户视角模糊 | 必须 clarify |
| `一些` | 数量不清 | 必须 clarify |
| `适当的时候` | 时间不清 | 必须 clarify |
| `等等` | 列举不全 | 必须 clarify |
| `robust` | 缺度量 | 必须 clarify |
| `intuitive` | 缺度量 | 必须 clarify |
| `fast` | 缺数字 | 必须 clarify |
| `scalable` | 缺数字 | 必须 clarify |
| `secure` | 缺标准 | 必须 clarify |

→ 命中任意 1 个 = 必须 clarify

---

## 2. 占位符检测

| 模式 | 含义 |
|------|------|
| `TODO` | 未完成 |
| `TBD` | 待定 |
| `TKTK` | 待定 |
| `\?\?\?` | 不明 |
| `<placeholder>` | 占位符 |
| `{{...}}` | 模板未填 |

→ 命中任意 1 个 = 必须 clarify

---

## 3. BDD 完整性

- [ ] 每个 User Story 至少 1 个 Acceptance Scenario
- [ ] 每个 Scenario 都用 Given/When/Then
- [ ] Given 是状态描述（不是动作）
- [ ] When 是可执行动作
- [ ] Then 是可观察结果（含数字/状态/输出）

→ 任意未勾 = 必须 clarify

---

## 4. Edge Cases 数量

- [ ] ≥ 3 条 Edge Cases
- [ ] 至少 1 条错误场景
- [ ] 至少 1 条边界值场景
- [ ] 至少 1 条并发/竞态场景（如适用）

→ 数量 < 3 或缺错误场景 = 必须 clarify

---

## 5. Success Criteria 可量化

- [ ] 至少 1 个 Success Criteria 含具体数字（响应时间/吞吐量/错误率）
- [ ] 至少 1 个 Success Criteria 可观察（不是"系统好"）
- [ ] 至少 1 个 Success Criteria 可测试（不是"提升体验"）
- [ ] 所有 SC 都有 Given 触发条件

→ 不可量化 / 不可观察 / 不可测试 = 必须 clarify

---

## 6. Clarify 输出格式

clarify 步骤中，每条问题应包含：

```markdown
**Q{N}**: {问题描述}（≤ 80 字符）
**Recommended**: {推荐选项} - {1-2 句理由}

| Option | Description |
|--------|-------------|
| A | {选项 A} |
| B | {选项 B} |
| C | {选项 C} |
| Short | 自定义短答（≤ 5 词）|
```

用户回答后，spec.md 增量更新：

```markdown
## Clarifications
### Session {YYYY-MM-DD}
- Q: {问题} → A: {回答}
```

---

## 7. 跳过规则

- 情况 C（降级为 spec-writer）→ 跳过 Clarify
- 用户明确说"跳过澄清（探索性 spike）"→ 跳过，但 ⚠️ 标记"下游返工风险增加"
- 已完成 Clarify 段（当次会话内）→ 跳过，不重复问

---

## 关联

- 调用方：`agents/spec-enhancer.md` Step 0.5
- 借鉴源：GitHub spec-kit `/speckit.clarify` 命令
- 约束：单次会话 ≤ 5 个问题（重试不计数）
