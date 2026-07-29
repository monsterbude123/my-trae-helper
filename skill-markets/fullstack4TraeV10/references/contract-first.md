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

### 3. 事件契约 (events.md)
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

---

## 测试骨架目录约定

V10 contract 阶段后必须存在测试骨架目录，供后续 implement 阶段填充测试。两个合法路径（二选一）：

| 路径 | 适用场景 |
|------|----------|
| `docs/specs/{feature}/contracts/test-skeleton/` | V10 标准布局（spec-first 项目） |
| `__tests__/contracts/` | Vitest/Jest 项目惯例（front-end first） |

phase-gate.py `contract-to-implement` 会自动检测两者之一存在即通过。

---

## §5 契约扩展件（项目自定义）

V10 契约四件套（api-contracts / domain-models / events / validation-rules）是标准件。
复杂项目可能需要扩展件，建议命名规范如下（**必须**与 V10 标准件同目录 `contracts/` 下）：

| 文件 | 用途 | 典型场景 |
|------|------|---------|
| `component-props.md` | UI 组件 Props 契约 | 跨模块组件复用 |
| `interaction-states.md` | UI 交互状态机 | 多状态切换 |
| `store-contracts.md` | 状态管理契约 | Pinia/Redux 等 |
| `test-skeleton/` 或 `test-skeleton.md` | 测试骨架 | V10 目录或 V9 文档形态二选一 |

**机械校验**:
- acceptance-audit.py artifact_schema 维度查 V10 标准件
- 项目扩展件**不强制**，缺失不报错（仅 WARNING）
- 但**命名不规范**（如 `component_props.md` 下划线）→ 后续 doc-sync 会失联

**V9 → V10 迁移提示**:
- `acceptance-scorecard-{date}.md` → `docs/reports/review-latest.md`（phase-gate 自动 fallback 到 scorecard）
- `event-contracts.md` → `events.md`（audit/extract 自动兼容双名）
- `test-skeleton.md` → `test-skeleton/`（phase-gate 同时接受两者）
