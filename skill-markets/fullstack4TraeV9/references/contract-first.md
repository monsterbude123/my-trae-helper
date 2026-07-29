# 契约先行（Contract-First）

> 契约是开发的唯一入口，代码必须实现契约。

---

## 契约四件套

### 1. API 契约 (api-contracts.md)
```markdown
## {接口名}
- **路径**: {URL}
- **方法**: GET/POST/PUT/DELETE
- **请求**: {参数表}
- **响应**: {返回结构}
- **错误码**: {错误码列表}
```

### 2. 领域模型 (domain-models.md)
```markdown
## {实体名}
| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| id | string | 是 | 唯一标识 |
```

### 3. 事件契约 (event-contracts.md)
```markdown
## {事件名}
- **发布者**: {模块}
- **订阅者**: [{模块1}, {模块2}]
- **负载**: {数据结构}
```

### 4. 校验规则 (validation-rules.md)
```markdown
## {接口名} 校验规则
- {字段}: {规则}
```

---

## 契约变更流程

```
现有契约 → 变更评估
              │
    ├── ADDITIVE（兼容）→ 更新契约 → 实现 → Review
    │
    └── BREAKING（不兼容）→ 用户确认 → 更新契约 → 实现 → Review
```

---

## 契约测试骨架

每个接口生成 contract test：
```typescript
describe('{接口名}', () => {
  it('{场景}', async () => {
    const result = await client.{接口名}(params)
    expect(result).toMatchSnapshot()
  })
})
```
