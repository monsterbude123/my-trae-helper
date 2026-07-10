---
name: gitnexus-impact-analysis
description: "用于修改代码前的安全分析——爆炸半径、依赖影响评估。当用户问\"改 X 安全吗\"、\"改这个会破坏什么\"、\"爆炸半径多大\"、\"谁依赖这个\"、\"提交前检查影响\"时加载。修改任何函数/类/方法前必须加载此技能做影响分析。"
---

# GitNexus 影响分析

## 使用场景

- "改这个函数安全吗？"
- "改了 X 会破坏什么？"
- "显示爆炸半径"
- "谁在用这段代码？"
- 做任何非平凡代码修改之前
- 提交之前 — 了解改动影响范围

**强制规则：修改任何函数、类或方法之前必须先做影响分析。**

## 工作流

```
1. impact({target: "X", direction: "upstream"})  → 什么依赖这个
2. 查看执行流                                    → 检查受影响流程
3. detect_changes()                              → 映射当前 git 改动到受影响流程
4. 评估风险并汇报用户
```

## 检查清单

- [ ] `impact({target, direction: "upstream"})` 查找所有依赖者
- [ ] 优先审查 d=1 项（这些**必定破坏**）
- [ ] 检查高置信度 (>0.8) 依赖
- [ ] 查看受影响的执行流
- [ ] `detect_changes()` 提交前检查
- [ ] 评估风险等级并汇报用户
- [ ] **HIGH 或 CRITICAL 风险时必须警告用户**才能继续

## 输出解读

| 深度 | 风险等级 | 含义 |
|------|---------|------|
| d=1 | **必定破坏** | 直接调用者/导入者 |
| d=2 | 可能影响 | 间接依赖 |
| d=3 | 需要测试 | 传递性影响 |

## 风险评估

| 影响范围 | 风险 |
|---------|------|
| <5 符号、少量流程 | LOW |
| 5-15 符号、2-5 流程 | MEDIUM |
| >15 符号，或众多流程 | HIGH |
| 关键路径（认证、支付） | CRITICAL |

## TRAE MCP 调用参考

**impact** — 符号爆炸半径的主工具：

```
run_mcp({server_name: "gitnexus", tool_name: "impact", args: {
  target: "validateUser",
  direction: "upstream",
  minConfidence: 0.8,
  maxDepth: 3
}})

→ d=1 (必定破坏):
  - loginHandler (src/auth/login.ts:42) [CALLS, 100%]
  - apiMiddleware (src/api/middleware.ts:15) [CALLS, 100%]

→ d=2 (可能影响):
  - authRouter (src/routes/auth.ts:22) [CALLS, 95%]
```

**detect_changes** — 基于 git diff 的影响分析：

```
run_mcp({server_name: "gitnexus", tool_name: "detect_changes", args: {scope: "staged"}})

→ 变更: 5 符号, 3 文件
→ 受影响: LoginFlow, TokenRefresh, APIMiddlewarePipeline
→ 风险: MEDIUM
```

## 示例："改 validateUser 安全吗？"

```
1. run_mcp({server_name: "gitnexus", tool_name: "impact", args: {target: "validateUser", direction: "upstream"}})
   → d=1: loginHandler, apiMiddleware (必定破坏)
   → d=2: authRouter, sessionManager (可能影响)

2. 检查受影响执行流
   → LoginFlow 和 TokenRefresh 涉及 validateUser

3. 风险: 2 个直接调用者, 2 个执行流 = MEDIUM
   → 告知用户: "MEDIUM 风险——2 个直接调用者会被破坏，2 个执行流受影响"
```

## 绝对禁止

- 绝对不要不先运行 `impact` 就编辑任何函数、类或方法
- 绝对不要忽略 HIGH 或 CRITICAL 风险警告
- 绝对不要不运行 `detect_changes()` 就提交改动

> 如果索引过时，先在终端运行 `npx gitnexus analyze`。
