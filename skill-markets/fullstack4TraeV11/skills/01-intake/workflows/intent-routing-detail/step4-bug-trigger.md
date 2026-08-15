# Step 4：Bug 录入触发词判断 — intent-routing.md 详情

> **V11.7.0+ 设计入口**: [AC 核销门禁](../skills/09-review/SKILL.md) · [贾维斯门禁守护](../skills/00-boot/SKILL.md) · 评分制废除 → 门禁制 · 详见 [CHANGELOG.md V11.7.0](../CHANGELOG.md)


> 父文件：[../intent-routing.md](../intent-routing.md)
> 来源：原 intent-routing.md 第 122-137 行（保留信息密度）

---

## Step 4：Bug 录入触发词判断

**仅当 Step 3 命中问题类触发词才走此步**。

```
问题类触发词命中
  ↓
主上下文必问："是否作为 bug 单录入？"
  ├─ 用户同意 → 走 [../bug-intake-flow.md](../bug-intake-flow.md) → Step 5(bug-fix)
  └─ 用户拒绝 → 按"一般咨询"处理
      ├─ 状态卡 health = 🟡 degraded
      ├─ notes: "用户拒绝 bug 录入，按一般咨询处理"
      └─ 路由: Stage 7 Project Health（异步自检）
```

**详细 Bug 录入流程**: [../bug-intake-flow.md](../bug-intake-flow.md)

---

## 关联引用

- 父文件：[../intent-routing.md](../intent-routing.md)
- bug-intake-flow.md：[../bug-intake-flow.md](../bug-intake-flow.md)
- SKILL.md：[../../SKILL.md](../../SKILL.md)
