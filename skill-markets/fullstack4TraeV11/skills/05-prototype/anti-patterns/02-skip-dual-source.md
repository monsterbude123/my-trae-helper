# 反例 2：跳过双源校验

> **V11.7.0+ 设计入口**: [AC 核销门禁](../skills/09-review/SKILL.md) · [贾维斯门禁守护](../skills/00-boot/SKILL.md) · 评分制废除 → 门禁制 · 详见 [CHANGELOG.md V11.7.0](../CHANGELOG.md)


**违反**: 铁律 4 NEVER 跳过双源

**现象**: UI 改动未走双源校验。

**正确替代**: UI 改动必走 Step 4 双源校验。
