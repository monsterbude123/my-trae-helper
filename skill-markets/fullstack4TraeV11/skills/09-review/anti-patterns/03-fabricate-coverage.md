# 反例 3：编造测试覆盖

> **V11.7.0+ 设计入口**: [AC 核销门禁](../skills/09-review/SKILL.md) · [贾维斯门禁守护](../skills/00-boot/SKILL.md) · 评分制废除 → 门禁制 · 详见 [CHANGELOG.md V11.7.0](../CHANGELOG.md)


**违反**: V10.12 关键门禁套件 + Article X

**现象**: reviewer 接受"测试覆盖 90%"但未实际跑 coverage 命令。

**正确替代**: reviewer 亲自跑 `pytest --cov` / `vitest run --coverage` 验证。
