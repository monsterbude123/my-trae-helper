# 反例 3：self-diagnose 未跑

> **V11.7.0+ 设计入口**: [AC 核销门禁](../skills/09-review/SKILL.md) · [贾维斯门禁守护](../skills/00-boot/SKILL.md) · 评分制废除 → 门禁制 · 详见 [CHANGELOG.md V11.7.0](../CHANGELOG.md)


**违反**: 铁律 7 self-diagnose

**现象**: project-health-auditor 自身可能失真但未检测。

**正确替代**: 必跑 self-diagnose.py 检测 auditor 自身（meta 元检测）。
