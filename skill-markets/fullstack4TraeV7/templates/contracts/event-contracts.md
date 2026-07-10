# 事件契约: {变更名称}

> 契约版本: 1.0.0
> 状态: draft → approved

## Event: {event.name}

- **Producer**: {ProducerModule}.{method}()
- **Consumers**: {ConsumerModule1}, {ConsumerModule2}
- **Delivery**: at-least-once / exactly-once
- **Idempotency Key**: {field}

### Payload Schema

```typescript
interface {EventName} {
  eventId: string;
  // {字段}: {类型}
  timestamp: string;  // ISO8601
}
```

### 触发条件

- {条件 1，如：用户注册成功后}
- {条件 2}

### 消费者契约

| 消费者 | 行为 | 幂等性 |
|--------|------|--------|
| {ConsumerModule} | {行为描述} | {如何幂等} |

### 契约测试映射

- Contract Test: `tests/contracts/{event}.contract.test.ts`
