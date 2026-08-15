# 反例 1：把 project-health 当必走流程

> **V11.7.0+ 设计入口**: [AC 核销门禁](../skills/09-review/SKILL.md) · [贾维斯门禁守护](../skills/00-boot/SKILL.md) · 评分制废除 → 门禁制 · 详见 [CHANGELOG.md V11.7.0](../CHANGELOG.md)


**违反**: 铁律 1 异步非阻塞

**现象**: project-health 阻塞主流程。

**正确替代**: project-health 是异步支线，可与任一 stage 并行；不阻塞主流程。
