# 反例 1："启动 = 完成"软指标

> **V11.7.0+ 设计入口**: [AC 核销门禁](../skills/09-review/SKILL.md) · [贾维斯门禁守护](../skills/00-boot/SKILL.md) · 评分制废除 → 门禁制 · 详见 [CHANGELOG.md V11.7.0](../CHANGELOG.md)


**违反**: V10 §0.10 强约束

**现象**: 未验证的启动断言(如"vite 启动了应该没问题"/"服务起来了视为通过") → 声称 Real Verify PASS。

**正确替代**: 必须有可见产物（截图 ≥5KB / curl 200 / 输出 ≥10 行）+ file:line 证据。
