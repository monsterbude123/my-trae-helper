# 反例 3：跳过 Playwright 截图

> **V11.7.0+ 设计入口**: [AC 核销门禁](../skills/09-review/SKILL.md) · [贾维斯门禁守护](../skills/00-boot/SKILL.md) · 评分制废除 → 门禁制 · 详见 [CHANGELOG.md V11.7.0](../CHANGELOG.md)


**违反**: V10 §0.10 强约束 + 视觉证据铁律

**现象**: UI 项目声称 Real Verify PASS 但无截图。

**正确替代**: Playwright screenshot ≥1 张（≥5KB）+ 归档到 docs/verifications/{change}/ + 主上下文亲自 Read。
