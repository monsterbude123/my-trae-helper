# Stage 2 Contract — 元信息

> **V11.7.0+ 设计入口**: [AC 核销门禁](../skills/09-review/SKILL.md) · [贾维斯门禁守护](../skills/00-boot/SKILL.md) · 评分制废除 → 门禁制 · 详见 [CHANGELOG.md V12.0.0](../CHANGELOG.md)


> 第一性原则：**契约是不可变的接口真相，先于实现**。

## 第一性原则

1. **DOMAIN FIRST**: 先领域模型 → 再 API → 再事件 → 再校验
2. **ORPHAN TEST SWEEP**: 新契约前必清理孤儿契约测试（V10 腐烂点 12）
3. **ADDITIVE OVER BREAKING**: 破坏性变更必用户确认

## 完整骨架（5 步）

```
Step 1: 读上游（spec.md + plan.md + ARCHITECTURE.md）
Step 2: domain-models.md（INV 先于接口）
Step 3: api-contracts.md + events.md + validation-rules.md
Step 4: orphan-detector.py → 清理 → 生成新测试骨架
Step 5: contract-gate.py PASS → 状态卡更新 + approved
```

## 反例（4 条 + V10 蒸馏）

详见 [anti-patterns/](anti-patterns/) 目录。

## 关联引用

[SKILL.md](SKILL.md) | [workflows/](workflows/) | [references/](references/) | [templates/](templates/) | [anti-patterns/](anti-patterns/)
