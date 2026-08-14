# GitNexus 影响面评估（Impact Assessment）

> Stage 0 Plan Step 3 子代理 B 必走。使用 GitNexus MCP 工具评估代码影响面。

---

## 核心理念

```
改 symbol 前必跑 impact()  # Article V GitNexus First
探索代码用 query() / context()，不用 grep
```

---

## GitNexus 工具使用

### impact({target})

**用途**: 评估修改某 symbol 的影响面。

**调用**:
```python
mcp__gitnexus__impact(target="UserService.authenticate", direction="upstream")
# 返回: 直接调用者 + 受影响 processes + 风险等级
```

**输出解读**:
| 字段 | 含义 | 处置 |
|------|------|------|
| direct_callers | 直接调用此 symbol 的代码 | 必读 + 改 caller 测试 |
| indirect_callers | 间接调用（callers of callers）| 抽样 + 关注高风险路径 |
| affected_processes | 受影响的执行流 | 走完整 e2e 测试 |
| risk_level | LOW/MEDIUM/HIGH/CRITICAL | 影响 plan.md 的 Impact 段 |

### context({name})

**用途**: 查 symbol 的完整上下文（调用链 + 上下游）。

**调用**:
```python
mcp__gitnexus__context(name="authenticate")
# 返回: 完整调用图 + 文件位置 + 代码片段
```

### query({query})

**用途**: 概念相关代码搜索（语义搜索，非精确匹配）。

**调用**:
```python
mcp__gitnexus__query(query="user authentication flow")
# 返回: 相关代码片段 + 文件路径
```

### detect_changes({scope})

**用途**: 检测近期变更（避免冲突 + 重复实施）。

**调用**:
```python
mcp__gitnexus__detect_changes(scope="compare", base_ref="main")
# 返回: 变更 symbols + 影响的 execution flows
```

---

## 影响面评估流程

```
Step 1: 识别 target symbol
  ├─ 从意图推断（"用户登录" → UserService.authenticate）
  ├─ 从现有 Capabilities 推断
  └─ 从 docs/constitution.md 推断（架构关键 symbol）

Step 2: impact({target}) → 风险等级
  ├─ LOW: ≤ 5 direct_callers，无 critical path
  ├─ MEDIUM: 5-20 direct_callers 或 1 个 critical path
  ├─ HIGH: > 20 direct_callers 或多个 critical path
  └─ CRITICAL: 涉及安全 / 资金 / 数据完整性

Step 3: context({name}) → 调用链
  ├─ 画调用图（文字描述）
  ├─ 标注 critical path
  └─ 标注下游副作用

Step 4: query({concept}) → 相关代码
  ├─ 搜索类似功能（避免重复实现）
  └─ 搜索已弃用但仍使用的（避免依赖）

Step 5: detect_changes({scope="compare"}) → 冲突检测
  ├─ 是否有未合并的冲突？
  ├─ 是否有相关 PR？
  └─ 输出 recent_changes 列表
```

---

## 风险等级判定矩阵

| 影响符号数 | Critical Path | 风险等级 | 处置 |
|:---:|:---:|:---:|------|
| ≤ 5 | 无 | LOW | 标准 Plan |
| 5-20 | 1 个 | MEDIUM | Plan + 额外测试 |
| > 20 | 多个 | HIGH | Plan + 分阶段实施 |
| 任意 | 安全/资金/数据 | CRITICAL | Plan + 用户决策 + 额外评审 |

---

## 影响面报告模板

```json
{
  "explored_at": "2026-08-11T14:30:00",
  "target_symbol": "UserService.authenticate",
  "gitnexus_calls": [
    {"tool": "impact", "target": "UserService.authenticate", "result_count": 12},
    {"tool": "context", "name": "UserService.authenticate", "result_count": 8},
    {"tool": "query", "query": "user authentication", "result_count": 5},
    {"tool": "detect_changes", "scope": "compare", "result_count": 3}
  ],
  "affected_symbols": [
    {"name": "UserService.authenticate", "file": "src/auth/user_service.py", "line": 42, "impact_level": "self"},
    {"name": "AuthController.login", "file": "src/auth/auth_controller.py", "line": 18, "impact_level": "direct"},
    {"name": "OAuthCallbackHandler", "file": "src/auth/oauth_handler.py", "line": 56, "impact_level": "direct"}
  ],
  "call_graph": "AuthController.login → UserService.authenticate → TokenService.sign → JwtMiddleware.verify",
  "critical_paths": ["TokenService.sign（涉及 Token 签发）"],
  "risk_level": "MEDIUM",
  "recent_changes": ["PR #123 重构 TokenService（避免冲突）"]
}
```

---

## 反模式

> 完整反例见 [anti-patterns/02-grep-instead-of-gitnexus.md](../anti-patterns/02-grep-instead-of-gitnexus.md),本节不再展开(防冗余)。

---

## 关联引用

- [SKILL.md §铁律 3](../SKILL.md) — IMPACT BY TOOL
- [README.md §完整骨架 Step 3](../README.md) — 3 路并行探索
- [three-path-exploration.md](../workflows/three-path-exploration.md) — 3 路探索工作流
- 公共铁律 Article V: [../../../references/common-iron-rules.md](../../../references/common-iron-rules.md)
- 公共反例 §23: [../../../references/common-anti-patterns.md](../../../references/common-anti-patterns.md)
- GitNexus MCP 资源: `gitnexus://repo/my-trae-helper`（V11 已用 MCP 资源取代 V10 残留路径 `.claude/skills/gitnexus-guide`）
