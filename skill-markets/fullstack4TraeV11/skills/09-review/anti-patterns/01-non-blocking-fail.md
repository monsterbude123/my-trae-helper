# 反例 1："非阻塞 FAIL" 放水

> **V11.7.0+ 设计入口**: [AC 核销门禁](../skills/09-review/SKILL.md) · [贾维斯门禁守护](../skills/00-boot/SKILL.md) · 评分制废除 → 门禁制 · 详见 [CHANGELOG.md V11.7.0](../CHANGELOG.md)


**违反**: reviewer 铁律 1 FAIL IS FAIL

**现象**: reviewer 发现问题但标"非阻塞"放行。

**正确替代**: 任一 FAIL = REJECT + 失败标签。
