# Stage 3 Implement — 元信息

> **V11.7.0+ 设计入口**: [AC 核销门禁](../skills/09-review/SKILL.md) · [贾维斯门禁守护](../skills/00-boot/SKILL.md) · 评分制废除 → 门禁制 · 详见 [CHANGELOG.md V12.0.0](../CHANGELOG.md)


> 第一性原则：**TDD RED→GREEN，最简实现优先**。

## 第一性原则

1. **契约为唯一入口**: 不重新生成契约，直接消费 approved contracts/
2. **深度理解再编码**: GitNexus context() + modules/ → 输出"理解确认"
3. **TDD 三步循环**: RED → GREEN → REFACTOR → DRIFT CHECK
4. **量化汇报**: test/contract_tests/coverage 三个数字必填

## 完整骨架（4 步）

```
Step 1: 门禁（spec.md + contracts/ approved + state-card 存在）
Step 2: 深度理解（context + modules → 理解确认）
Step 3: TDD 循环（tasks.md 逐项）
Step 4: 模块接入文档（条件触发）+ 量化汇报
```

## 反例（4 条 + V10 蒸馏）

详见 [anti-patterns/](anti-patterns/)。

## 关联引用

[SKILL.md](SKILL.md) | [references/](references/) | [anti-patterns/](anti-patterns/)
