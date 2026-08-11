# GitNexus 影响面追踪 — Stage 3 Implement

> Stage 3 实施前必走。改 symbol 前必跑 `gitnexus impact()`（Article V GitNexus First）。

---

## 核心铁律

```
改 symbol 前必跑 impact()
探索代码用 query() / context()，不用 grep
```

**违反 = 🛑 REJECT**（Article V 不可降级）

---

## 4 个 GitNexus MCP 工具

### impact({target, direction})

```python
mcp__gitnexus__impact(target="UserService.authenticate", direction="upstream")
```

| 字段 | 含义 | 处置 |
|------|------|------|
| `direct_callers` | 直接调用此 symbol 的代码 | 必读 + 改 caller 测试 |
| `indirect_callers` | 间接调用 | 抽样 + 关注高风险路径 |
| `affected_processes` | 受影响的执行流 | 走完整 e2e 测试 |
| `risk_level` | LOW/MEDIUM/HIGH/CRITICAL | 影响 plan.md 的 Impact 段 |

### context({name})

```python
mcp__gitnexus__context(name="authenticate")
# 返回: 完整调用图 + 文件位置 + 代码片段
```

### query({query})

```python
mcp__gitnexus__query(query="user authentication flow")
# 返回: 相关代码片段 + 文件路径
```

### detect_changes({scope, base_ref})

```python
mcp__gitnexus__detect_changes(scope="compare", base_ref="main")
# 返回: 与 main 的 diff + 冲突风险
```

---

## Stage 3 必走的 4 个调用点

```
Step 1: 实施第一个 symbol 前 → impact() 确认影响面
Step 2: 实现跨模块接口前 → context() 查上下游
Step 3: TDD RED 阶段用 query() 找相似测试用例参考
Step 4: 实施完成用 detect_changes() 比 main 确认无冲突
```

---

## 反例（V11 Article V 必走）

```python
# ❌ 违反
subagent: grep -r "authenticate" src/  # 找到 12 处
# 影响范围被低估 60%

# ✅ 正确
mcp__gitnexus__impact(target="UserService.authenticate", direction="upstream")
# 找到 28 处（含间接调用）
```

详见 [../anti-patterns/02-grep-instead-of-gitnexus.md](../anti-patterns/02-grep-instead-of-gitnexus.md)

---

## 检测（commit 前必走）

```yaml
code_summary.json:
  gitnexus_calls:
    - mcp__gitnexus__impact
    - mcp__gitnexus__context
    - mcp__gitnexus__query
    - mcp__gitnexus__detect_changes
  no_grep: true
```

任一缺失 → 🛑 REJECT（V11 Article V）

---

## 关联引用

- [Stage 2 Contract impact-assessment.md](../../02-plan/references/impact-assessment.md) — 影响面评估基础
- [../anti-patterns/02-grep-instead-of-gitnexus.md](../anti-patterns/02-grep-instead-of-gitnexus.md) — 反例
- [公共铁律 Article V](../../references/common-iron-rules.md)