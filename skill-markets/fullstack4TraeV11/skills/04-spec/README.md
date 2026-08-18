# Stage 1 Spec — 元信息

> **V11.7.0+ 设计入口**: [AC 核销门禁](../skills/09-review/SKILL.md) · [贾维斯门禁守护](../skills/00-boot/SKILL.md) · 评分制废除 → 门禁制 · 详见 [CHANGELOG.md V12.0.0](../CHANGELOG.md)


> 第一性原则：**Spec 是真相源，验收维度决定交付质量**。

---

## 第一性原则

### 原则 1：Spec IS Truth

代码为规格服务。代码与 spec 冲突 → 改代码（除非 spec 错）。spec.md 必是项目最权威的真相源。

### 原则 2：Enhanced Acceptance + INV

每个 Capability ≥ 3 Acceptance Criteria + ≥ 1 E2E + ≥ 1 INV（整体）。INV 必基于业务规则。

### 原则 3：Clarify ≥ 2 轮

至少 2 轮澄清，防止单向理解（V10.16 禁止编造抽象理由）。

---

## 反例（3 条）

### 反例 1：INV 凭空臆造

**正确替代**: INV 必基于业务规则（如订单一致性 / 资金安全），不臆造。

### 反例 2：Clarify 跳过

**正确替代**: ≥ 2 轮澄清，每轮 < 4 题。

### 反例 3：Spec 写实施

**正确替代**: spec.md 只写规格（What + Why），不写代码（How）。

## 关联引用

[SKILL.md](SKILL.md) | [references/](references/) | [templates/](templates/) | [anti-patterns/](anti-patterns/)
