# 最小业务闭环 — {change-name}

> 由 planner agent 从 Spec BDD Scenarios 提取，从**用户视角**定义核心路径的连通步骤。
> 用于 implementer CLOSURE GATE 优先实现 + reviewer 业务闭环验证。

---

## 闭环定义

用户完成一次完整操作的**最小步骤链**——每条来自 Spec BDD Scenario：

```
S1: {用户操作} → {预期结果}
S2: {用户操作} → {预期结果}
S3: {用户操作} → {预期结果}
...
```

---

## 不可降级的 P0 项（闭环阻断）

任一未实现则闭环 FAIL：

- [ ] {P0-1 描述}（{Spec 引用}）
- [ ] {P0-2 描述}（{Spec 引用}）
- [ ] ...

## 可降级的 P1 项（不阻断闭环）

闭环外，可后续实现：

- [ ] {P1-1 描述}（{Spec 引用}）
- [ ] ...

---

## 验收标准

- 闭环中每个步骤在浏览器中**可达且可操作**
- P0 项全部实现 → 闭环 PASS；任一 P0 FAIL → 闭环 FAIL → 总分封顶 3.0
- 截图存放: `docs/reports/screenshots/{change}/`

---

> 模板说明：`{...}` 占位符由 planner 在 Phase 5.6 时用实际 Spec 内容填充。
> **禁止直接使用此模板默认值**——planner 必须从 spec.md BDD Scenarios 提取实际闭环步骤。
