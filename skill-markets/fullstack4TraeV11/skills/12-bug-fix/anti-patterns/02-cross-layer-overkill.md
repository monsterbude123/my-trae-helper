# 反例 2：跨层过度修复（Stage 6 Bug Fix）

> Stage 6 Bug Fix 跨层修复最小化。来源：V10 debugger-methodology.md §跨层修复 + agents/debugger.md 铁律 6。

## 现象

```
debugger: 网络 500 → 改了 DB 连接池 + 中间件 + 缓存策略 + 路由  # ❌ 跨层过度
```

## 根因

| 根因 | 占比 |
|------|:---:|
| 6 层排查未做 | 40% |
| 跨层依赖未用 GitNexus impact() | 30% |
| Ponytail First 违反 | 30% |

## 教训

**Ponytail bug 修复决策阶梯**（V10 agents/debugger.md 铁律 6）：

```
Level 1: 改当前层（首选）
Level 2: 改直接上游/下游（如 API → 改 service）
Level 3: 改跨层（如改 DB schema）
Level 4: 重构（最后）
```

**禁止**：
- 不做 6 层排查就改跨层
- 用 grep 找跨层依赖（违反 Article V.5）
- 一次修跨 3+ 层

## 正确替代

```python
# ✅ 6 层排查 + GitNexus 决策
Step 1: 网络层检查（curl / DNS / TLS）
Step 2: 接入层（API gateway / 路由 / 限流）
Step 3: 应用层（业务逻辑 / 中间件 / 状态）  ← 通常 bug 在这层
Step 4: 数据层（DB schema / 索引 / 事务）  ← 如查 root cause 在这层
Step 5: 集成层（第三方 / SDK）
Step 6: 客户端层（UI / 缓存）

# 用 GitNexus 找跨层影响
mcp__gitnexus__impact(target="BuggyClass", direction="upstream")
mcp__gitnexus__impact(target="BuggyClass", direction="downstream")
```

## 关联引用

- [cross-layer-fix.md](../references/cross-layer-fix.md) — 跨层修复协议
- [gitnexus-6-layer.md](../references/gitnexus-6-layer.md) — 6 层 + GitNexus 工具
- [SKILL.md §铁律 6](../SKILL.md) — 跨层修复最小化
- V10 来源: `../../../../fullstack4TraeV10/references/debugger-methodology.md`