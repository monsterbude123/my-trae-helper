# Clarify 检查清单

> **V11.7.0+ 设计入口**: [AC 核销门禁](../skills/09-review/SKILL.md) · [贾维斯门禁守护](../skills/00-boot/SKILL.md) · 评分制废除 → 门禁制 · 详见 [CHANGELOG.md V11.7.0](../CHANGELOG.md)


> Stage 1 Spec Step 4 必走。Clarify ≥ 2 轮，每轮 < 4 题。

---

## Clarify 协议

```
Round 1: 列出 ≥ 3 模糊点 → AskUserQuestion → 用户答
  ↓
基于 Round 1 回答追问更深层
  ↓
Round 2: ≥ 2 模糊点 → AskUserQuestion → 用户答
  ↓
（可选 Round 3）若仍有歧义
  ↓
产出 spec.md（含 Clarify History 段）
```

---

## 模糊点类型

| 类型 | 示例 |
|------|------|
| 需求歧义 | "重构 X" → X 的边界？ |
| 业务规则不清 | "退款" → 30 天内 vs 7 天内？ |
| 异常处理策略 | "支付失败" → 重试 vs 直接拒绝？ |
| Non-Goals 边界 | 是否包含 X 子功能？ |

---

## ≥ 2 轮返工根因诊断

若用户对 spec 提出 ≥ 2 轮修改，触发**根因诊断**：

```
第 2 轮用户修改
  ↓
主上下文诊断:
  ├─ 是 Acceptance 模糊？→ 拆 AC + 补 E2E
  ├─ 是 INV 缺漏？→ 补 INV（基于业务规则）
  ├─ 是 Non-Goals 边界？→ 标注 explicit non-goals
  ├─ 是用户场景不清？→ 加 user persona 段
  └─ 是技术决策混入？→ 移除技术细节
  ↓
更新 spec.md + Clarify History 追加
```

---

## Clarify History 模板

```markdown
## Clarify History

### Round 1 (2026-08-11)
- Q: 退款周期？A: 7 天内自动，> 7 天人工审核
- Q: 退款金额限制？A: 单笔 ≤ 1000 美元
- Q: 部分退款？A: 支持

### Round 2 (2026-08-11)
- Q: 退款到原支付渠道还是余额？A: 原渠道
- Q: 退款失败重试？A: 3 次，间隔 1h
```

---

## 反模式

### 反例 A：单轮 Clarify

```
主上下文: Round 1 → 用户答 → 立即写 spec  # ❌ 单轮
正确: ≥ 2 轮
```

### 反例 B：一次问 10 题

```
主上下文: AskUserQuestion 10 题  # ❌ 用户疲劳
正确: 每轮 < 4 题
```

### 反例 C：用经验主义臆断歧义

```
用户: "退款支持部分"
主上下文: "我理解您的意思" → 直接写 spec  # ❌ V10.16
正确: AskUserQuestion 澄清边界
```

## 关联引用

- [SKILL.md §铁律 5](../SKILL.md)
- [acceptance-enhancement.md](acceptance-enhancement.md)
- 公共铁律 Article XVI: [../../../references/common-iron-rules.md](../../../references/common-iron-rules.md)
