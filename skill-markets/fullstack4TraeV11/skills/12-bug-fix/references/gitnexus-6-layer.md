# GitNexus 6 层排查 — Stage 6 Bug Fix

> **V11.7.0+ 设计入口**: [AC 核销门禁](../skills/09-review/SKILL.md) · [贾维斯门禁守护](../skills/00-boot/SKILL.md) · 评分制废除 → 门禁制 · 详见 [CHANGELOG.md V11.7.0](../CHANGELOG.md)


> Stage 6 Bug Fix Step 3 必走。用 GitNexus MCP 工具辅助 6 层根因排查。

---

## 6 层排查 + GitNexus 工具映射

| 层 | 排查内容 | GitNexus 工具 | 输出 |
|----|---------|-------------|------|
| 网络层 | curl / DNS / TLS | `query(query="network endpoint {symbol}")` | 端点清单 |
| 接入层 | API gateway / 路由 / 限流 | `impact(target="{gateway}", direction="upstream")` | 中间件依赖 |
| 应用层 | 业务逻辑 / 中间件 / 状态 | `context(name="{symbol}")` | 完整调用链 |
| 数据层 | DB schema / 索引 / 事务 | `query(query="database {entity}")` | 数据访问点 |
| 集成层 | 第三方服务 / SDK | `impact(target="{integration}")` | SDK 边界 |
| 客户端层 | UI / 缓存 / localStorage | `query(query="client cache {feature}")` | 前端依赖 |

---

## Stage 6 Step 3 必走的 5 个 GitNexus 调用

```
Step 1: bug 报入后 → impact(target=buggy_symbol) 找所有调用者
Step 2: → context(name=buggy_symbol) 看上下游完整链路
Step 3: → query(query="recent changes {buggy_symbol}") 找最近变更
Step 4: 6 层排查跨模块时 → impact(target=layer_name) 找跨层依赖
Step 5: 修复后 → detect_changes(scope=branch) 比 main 确认范围
```

---

## 真实案例（V10 + V11 蒸馏）

### 案例 1：登录接口返回 500

```python
# ❌ 错误路径
debugger: 读 error → 找 stack trace → 修代码  # 仅修表面

# ✅ 正确路径（GitNexus First）
mcp__gitnexus__impact(target="UserService.authenticate", direction="upstream")
# → 发现 28 处调用（含 indirect 16 处）
# → 评估修复一处影响全部

mcp__gitnexus__context(name="UserService.authenticate")
# → 找到 6 层链路：client → API → middleware → service → repository → DB
# → 根因：repository 层迁移时漏改 index → DB 超时 → service 抛异常 → 500
```

### 案例 2：UI 不显示

```python
# ✅ GitNexus 排查路径
mcp__gitnexus__query(query="dashboard widget {feature}")
# → 找到 3 个相关组件
mcp__gitnexus__impact(target="DashboardStore", direction="upstream")
# → 找到 8 个 UI 组件
# → 根因：DashboardStore 缺新加字段的 selector → UI 无值
```

---

## 反例（V11 Article V）

```python
# ❌ 反例 1: 跳过 GitNexus 用 grep
debugger: grep -r "authenticate" src/  # 仅找到 12 处直接调用
# 漏掉 16 处间接调用 → e2e 不全

# ❌ 反例 2: 不查跨层依赖
debugger: 修应用层 → 没 impact() 跨层检查 → 集成层兼容性破坏
```

详见 [../anti-patterns/](../anti-patterns/)

---

## 检测（bug 单 CLOSED 必含）

```yaml
bug_closed:
  root_cause: "{6 层排查结论}"
  gitnexus_calls:
    - impact({buggy_symbol})
    - context({buggy_symbol})
    - query("{layer}")
  closed_at: {ISO 8601}
```

任一缺失 → 🛑 REJECT

---

## 关联引用

- [six-layer-diagnosis.md](six-layer-diagnosis.md) — 6 层排查协议
- [cross-layer-fix.md](cross-layer-fix.md) — 跨层修复协议
- [Stage 7 impact-assessment.md](../../02-plan/references/impact-assessment.md) — 影响面评估基础
- [公共铁律 Article V](../../../references/common-iron-rules.md)
