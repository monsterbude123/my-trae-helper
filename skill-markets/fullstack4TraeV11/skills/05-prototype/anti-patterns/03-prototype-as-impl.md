# 反例 3：prototype 写实现

> **V11.7.0+ 设计入口**: [AC 核销门禁](../skills/09-review/SKILL.md) · [贾维斯门禁守护](../skills/00-boot/SKILL.md) · 评分制废除 → 门禁制 · 详见 [CHANGELOG.md V11.7.0](../CHANGELOG.md)


**违反**: prototype 阶段定位（spec 视觉表达，不是 implementation）

**现象**: prototype 含完整业务逻辑代码。

**正确替代**: prototype 是最小可运行 demo，业务逻辑留给 Stage 3 Implement。
