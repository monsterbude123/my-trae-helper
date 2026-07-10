---
name: gitnexus-exploring
description: "用于理解代码架构、探索不熟悉的代码、追踪执行流。当用户问\"X 怎么工作\"、\"谁调用了这个函数\"、\"认证流程是什么样的\"、\"项目结构\"、\"数据库逻辑在哪\"等探索性问题时加载。优先用此技能替代 grep 搜索。"
---

# GitNexus 代码探索

## 使用场景

- "认证是怎么工作的？"
- "项目结构是什么？"
- "主要组件有哪些？"
- "数据库逻辑在哪？"
- 理解没见过的代码

## 工作流

```
1. list_repos  → 发现已索引仓库
2. 读 context  → 代码库概览 + 新鲜度检查
3. query       → 找到相关执行流
4. context     → 深入特定符号
5. 读流程追踪  → 完整执行流
```

## 检查清单

- [ ] 检查代码库概览和索引新鲜度
- [ ] `query` 搜索你想理解的概念
- [ ] 审查返回的执行流
- [ ] `context` 深入关键符号的调用者和被调用者
- [ ] 如需完整执行流，读流程追踪资源
- [ ] 读源文件获取实现细节

## TRAE MCP 调用参考

**query** — 找到概念相关的执行流：

```
run_mcp({server_name: "gitnexus", tool_name: "query", args: {query: "支付处理"}})
→ 执行流: CheckoutFlow, RefundFlow, WebhookHandler
→ 符号按流程分组，附带文件位置
```

**context** — 符号的 360 度视图：

```
run_mcp({server_name: "gitnexus", tool_name: "context", args: {name: "validateUser"}})
→ 入向调用: loginHandler, apiMiddleware
→ 出向调用: checkToken, getUserById
→ 所属流程: LoginFlow (第 2/5 步), TokenRefresh (第 1/3 步)
```

**list_repos** — 发现已索引仓库：

```
run_mcp({server_name: "gitnexus", tool_name: "list_repos", args: {}})
```

## 示例："支付处理是怎么工作的？"

```
1. run_mcp({server_name: "gitnexus", tool_name: "list_repos", args: {}})
   → my-app (918 符号, 45 流程)

2. run_mcp({server_name: "gitnexus", tool_name: "query", args: {query: "支付处理"}})
   → CheckoutFlow: processPayment → validateCard → chargeStripe
   → RefundFlow: initiateRefund → calculateRefund → processRefund

3. run_mcp({server_name: "gitnexus", tool_name: "context", args: {name: "processPayment"}})
   → 入向: checkoutHandler, webhookHandler
   → 出向: validateCard, chargeStripe, saveTransaction

4. 读 src/payments/processor.ts 了解实现细节
```

> 如果索引过时，先在终端运行 `npx gitnexus analyze`。
