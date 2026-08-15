# 反例 4：自动循环 Round 3+ 继续绕

> **V11.7.0+ 设计入口**: [AC 核销门禁](../skills/09-review/SKILL.md) · [贾维斯门禁守护](../skills/00-boot/SKILL.md) · 评分制废除 → 门禁制 · 详见 [CHANGELOG.md V11.7.0](../CHANGELOG.md)


**违反**: V10.12 Step 2.6 rescue hatch

**现象**: Round 3 失败 → 继续 Round 4 → ... → 5 轮小修小补。

**正确替代**: Round 3+ 自动触发 rescue hatch → 回退 Phase 0 重新审视需求。
