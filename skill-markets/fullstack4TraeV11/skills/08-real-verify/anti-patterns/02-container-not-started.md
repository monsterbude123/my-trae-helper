# 反例 2：容器未启声称迁移成功

> **V11.7.0+ 设计入口**: [AC 核销门禁](../skills/09-review/SKILL.md) · [贾维斯门禁守护](../skills/00-boot/SKILL.md) · 评分制废除 → 门禁制 · 详见 [CHANGELOG.md V11.7.0](../CHANGELOG.md)


**违反**: V10 Article XV 障碍诚实

**现象**: postgres 容器未启 → 迁移脚本报 success（实际跳过）→ 主上下文声称 PASS。

**正确替代**: Real Verify 必先 `docker compose ps postgres | grep Up` → 容器运行后才迁移。
