# 验收门禁

> Review 和 Accept 阶段的硬性检查点。

---

## Review 门禁（硬门禁，任一项 FAIL → 🛑 REJECT）

### 代码质量
- [ ] 测试 100% 通过
- [ ] lint 0 错误
- [ ] 覆盖率 > 80%

### 契约一致性
- [ ] 接口签名与 API 契约一致
- [ ] 数据模型与领域模型一致
- [ ] 错误码与契约定义一致

### 5 维度量化打分

| # | 维度 | 权重 | 一票否决 |
|---|------|:---:|---------|
| 1 | Spec 对齐 | 25% | 单维度 < 3.0 |
| 2 | 契约一致 | 25% | 严重漂移 → REJECT |
| 3 | 测试质量 | 20% | 闭环 FAIL → 总分封顶 3.0 |
| 4 | 代码质量 | 15% | 文件 > 1000 行 / 无文档 |
| 5 | 安全性 | 15% | < 4.0 → 一票否决 |

```
维度得分 = (PASS / 可适用项数) × 5.0
总分     = Σ(维度得分 × 权重)
门禁: 总分 ≥ 4.0 + 单维度 ≥ 3.0 + 安全 ≥ 4.0
```

### Visual Gate（涉及 UI 时强制）

```
判定: 变更包含 .tsx/.jsx/.vue → 执行；否则 N/A

两阶段:
  Phase A — 视觉一致性（100% 对齐）:
    基准: Trae Work 按 design-prompt.md 生成的原型截图
    验证: vision-audit 逐像素比对（布局/间距/颜色/字体/组件位置）
    任一差异 → 🛑 FAIL
  
  Phase B — 交互逻辑:
    基准: prototypes/ui-ux-logic.md
    验证: 逐条行为规格比对（触发→前置→步骤→后置→异常）
    任一不符 → 🛑 FAIL

降级: vision-audit 不可用 → ⚠️ "降级验收"，维度 1 封顶 3.0
跳过: 涉及 UI 但未执行 → 🛑 总分封顶 3.0
```

### DOC SYNC
- [ ] 模块文档已更新（P0 接口/模型/职责）
- [ ] 架构文档已更新（如涉及变更）
- [ ] 一致性自检通过（接口/模型/依赖 三项）

### 归档门禁（3 项）
- [1] define.md tasks 全 [x] → 否则 🛑
- [2] git diff 含 src/ 变更 → 纯文档提交 🛑
- [3] 无 TODO/FIXME/HACK → 存在 🛑（或写 ponytail 标记）

---

## Accept 门禁

> **只审当前原则（铁律 11 延伸）**: 验收只对比当前 define.md 的 Acceptance 清单 + 当前 Spec。禁止因为"历史验收通过"跳过任何项目。_invalidated/ 中的旧验收状态视为不存在。

### UI/UX 验收（两阶段）

```
Phase A — 视觉一致性（100% 像素级对齐）:
  基准: Trae Work 按 prototypes/design-prompt.md 生成的视觉原型
  [ ] 实现截图逐像素比对原型 — 布局/间距/颜色/字体/组件位置 完全一致
  [ ] 5 状态全部覆盖（加载中/空数据/正常/错误/边界）
  [ ] 响应式 ≥ 2 断点对齐
  任一差异 → 🛑 FAIL "视觉偏差: {具体差异}"

Phase B — 交互逻辑:
  基准: prototypes/ui-ux-logic.md 的行为规格
  [ ] 所有交互流路径验证通过（触发→前置→步骤→后置→异常）
  [ ] 所有状态变化验证通过（状态表逐条）
  [ ] 所有错误边界处理验证通过
  任一不符 → 🛑 FAIL "行为偏差: {差异描述}"
```

### 后端验收（API 层面，非单元测试）

```
后端功能通过 API 契约测试验收，不依赖内部单元测试覆盖:

[ ] 契约测试打真实端点（HTTP 请求 → 响应）
[ ] 接口签名 vs api-contracts.md 完全一致（路径/方法/参数/响应码）
[ ] 数据模型 vs domain-models.md 完全一致（字段/类型/约束）
[ ] 错误码 vs validation-rules.md 完全一致
[ ] 事件 vs events.md 完全一致（发送时机/字段）
[ ] 性能: P0 接口响应 < 500ms
```

### 安全

- [ ] 无 SQL 注入风险
- [ ] 无 XSS 风险
- [ ] 无敏感信息泄露

---

## 门禁失败处理

```
门禁 FAIL
    ├── UI 视觉不对齐 → 退回 Implementer（UI 重写 → Visual Gate 重跑 Phase A+B）
    ├── UI 交互不符   → 退回 Implementer（修正行为 → Visual Gate 重跑 Phase B）
    ├── API 契约不对齐 → 退回 Implementer（修正接口 → API 契约测试重跑）
    ├── Spec 不对齐  → 退回 Spec-Writer
    ├── 契约漂移     → 退回 Contract-Writer
    └── 文档缺失     → 退回 Reviewer（补充 DOC SYNC）

同一 change Review FAIL 3 次 → 🛑 标记 🔴 高风险，汇报用户
```
