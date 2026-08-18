# GitNexus 失败处理协议（3 次重试 — V11 NEW 蒸馏自 V10 debugger-methodology.md §1.6）

> **V12.0.0+ 设计入口**: [AC 核销门禁](../skills/09-review/SKILL.md) · [贾维斯门禁守护](../skills/00-boot/SKILL.md) · 评分制废除 → 门禁制 · 详见 [CHANGELOG.md V12.0.0](../CHANGELOG.md)


> **V11 缺失的关键思想**。V10 debugger-methodology.md §1.6 明确规定：
> "失败时执行 3 次重试协议（修参数 → 换工具 → list_repos），仍失败 → 停下汇报用户。"
> V11 GitNexus 文档缺乏此协议 = 表达失真。

---

## 核心铁律

```
MUST: GitNexus 调用失败时必走 3 次重试协议
NEVER: 直接降级为 grep/glob（违反 Article V.5 不可降级）
NEVER: 跳过重试直接静默继续
```

---

## 3 次重试协议

### 第 1 次重试：修参数

**触发**: 调用 `impact / context / query / detect_changes` 返回参数错误或空结果。

**动作**:
```
1. 检视调用参数
   - impact({target}) → target 拼写？是否含 class.method 格式？
   - context({name}) → name 是否为单个 symbol？
   - query({query}) → query 是否为自然语言短语？
   - detect_changes({scope, base_ref}) → scope 是 "compare" 或 "branch"？base_ref 存在？
2. 修正参数后重新调用
3. 失败 → 进入第 2 次重试
```

### 第 2 次重试：换工具

**触发**: 第 1 次重试仍失败。

**动作**:
```
1. 换 GitNexus 同目标工具：
   - impact({target}) 失败 → 换 context({name}) 或 query({query})
   - context({name}) 失败 → 换 impact({target}) 或 query({query})
2. 用 query 找相似 symbols → 找到候选 → 重新调 impact
3. 失败 → 进入第 3 次重试
```

### 第 3 次重试：list_repos

**触发**: 第 2 次重试仍失败（GitNexus 可能索引过期）。

**动作**:
```
1. 调用 mcp__gitnexus__list_repos() 看索引状态
2. 如索引不存在/过期 → 等待后台 analyze 完成（gitnexus-session-check.py 已在跑）
3. 重新调原工具
4. 仍失败 → 停下汇报用户
```

---

## 停下汇报用户（仍失败）

**触发**: 3 次重试后仍失败。

**必走 Article XV 5 字段阻塞报告**:

```yaml
blocker_report:
  type: "gitnexus_call_failed_after_3_retries"
  description: "GitNexus impact({target}) 连续 3 次失败：1 次修参数、2 次换工具、3 次 list_repos"
  attempted_solution:
    - "修参数: target=UserService.authenticate → UserService_authenticate"
    - "换工具: impact → context → query 仍失败"
    - "list_repos: 索引存在但 impact() 返回空"
  time_consumed_minutes: 8
  attempt_count: 3
  risk_level: HIGH
  recommendation: "用户决策：a) 重新跑 gitnexus analyze  b) 标注 L4 异常 + 降级  c) 跳过此 change"
```

---

## 反模式（V11 禁止）

### 反例 A：直接降级为 grep

```
GitNexus impact() 失败 → 主上下文 grep -r "authenticate"  # ❌ 违反 Article V.5
正确: 走 3 次重试协议 → 仍失败 → 5 字段阻塞报告
```

### 反例 B：跳过重试直接继续

```
GitNexus 失败 → "算了，不重要" → 直接改代码  # ❌ 风险评估不完整
正确: 必走 3 次重试协议 → 仍失败 → 汇报用户
```

### 反例 C：3 次重试后未停下

```
GitNexus 失败 3 次 → 重复 3 次同样的调用 → 仍失败  # ❌ 浪费时间
正确: 3 次重试用不同方法 → 仍失败 → 立刻停下汇报
```

---

## 检测（commit/CI 必走）

```yaml
gitnexus_retry_compliance:
  attempt_count_tracked: true  # 必含 attempt_count 字段
  retry_methods_used:
    - "修参数"
    - "换工具"
    - "list_repos"
  grep_in_commit_diff: false  # 不能含 grep -r "symbol"
  blocker_report_present: true  # 失败时必有 5 字段报告
```

任一缺失 → 🛑 REJECT

---

## 关联引用

- [gitnexus-tools.md](gitnexus-tools.md) — 4 工具使用
- [Article V](common-iron-rules.md) — GitNexus First 不可降级
- 反例 23（见 references/common-anti-patterns.md）
- V10 来源（开发期，已蒸馏）：见 V11 references 与 anti-patterns §1.6
