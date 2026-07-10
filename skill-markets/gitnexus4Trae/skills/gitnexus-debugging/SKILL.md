---
name: gitnexus-debugging
description: "用于调试时追踪 bug、定位错误来源。当用户问\"为什么 X 失败了\"、\"这个错误从哪来\"、\"追踪这个 bug\"、\"这个接口返回 500\"等调试问题时主动加载。即使不直接说 debug，只要在排查报错或异常行为都应加载。"
---

# GitNexus 调试追踪

## 使用场景

- "这个函数为什么失败了？"
- "追踪这个错误从哪来的"
- "谁调用了这个方法？"
- "这个接口返回 500"
- 排查 bug、错误或异常行为

## 工作流

```
1. query      → 根据错误/症状找到相关执行流
2. context    → 查看疑点的调用者/被调用者/所在流程
3. 读流程追踪 → 跟随完整执行流
4. cypher     → 需要时自定义调用链追踪
```

## 检查清单

- [ ] 理解症状（报错信息、异常行为）
- [ ] `query` 搜索报错文本或相关代码
- [ ] 从返回的执行流中定位嫌疑函数
- [ ] `context` 查看调用者和被调用者
- [ ] 如有需要，跟踪完整执行流
- [ ] 需要时用 `cypher` 自定义调用链追踪
- [ ] 读源码确认根因

## 调试模式

| 症状 | GitNexus 方法 |
|------|--------------|
| 报错信息 | `query` 搜报错文本 → `context` 查看异常抛出点 |
| 返回值错误 | `context` 查函数 → 追踪被调用者的数据流 |
| 偶发失败 | `context` → 找外部调用、异步依赖 |
| 性能问题 | `context` → 找调用者多的符号（热点路径）|
| 近期回归 | `detect_changes` 查看改动影响范围 |

## TRAE MCP 调用参考

**query** — 根据错误找到相关代码：

```
run_mcp({server_name: "gitnexus", tool_name: "query", args: {query: "支付验证错误"}})
→ 执行流: CheckoutFlow, ErrorHandling
→ 符号: validatePayment, handlePaymentError, PaymentException
```

**context** — 嫌疑函数的完整上下文：

```
run_mcp({server_name: "gitnexus", tool_name: "context", args: {name: "validatePayment"}})
→ 入向调用: processCheckout, webhookHandler
→ 出向调用: verifyCard, fetchRates (外部 API!)
→ 所属流程: CheckoutFlow (第 3/7 步)
```

**cypher** — 自定义调用链追踪：

```
run_mcp({server_name: "gitnexus", tool_name: "cypher", args: {query: "MATCH path = (a)-[:CodeRelation {type: 'CALLS'}*1..2]->(b:Function {name: 'validatePayment'}) RETURN [n IN nodes(path) | n.name] AS chain"}})
```

**detect_changes** — 查看近期改动影响：

```
run_mcp({server_name: "gitnexus", tool_name: "detect_changes", args: {}})
```

## 示例："支付接口偶发 500"

```
1. run_mcp({server_name: "gitnexus", tool_name: "query", args: {query: "支付 错误处理"}})
   → 执行流: CheckoutFlow, ErrorHandling
   → 符号: validatePayment, handlePaymentError

2. run_mcp({server_name: "gitnexus", tool_name: "context", args: {name: "validatePayment"}})
   → 出向调用: verifyCard, fetchRates (外部 API!)

3. 查看 CheckoutFlow 执行流追踪
   → 第3步: validatePayment → 调用 fetchRates (外部请求)

4. 根因: fetchRates 调用外部 API 没有设置超时
```

> 如果索引过时，先在终端运行 `npx gitnexus analyze`。
