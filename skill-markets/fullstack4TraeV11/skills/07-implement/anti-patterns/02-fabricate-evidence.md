# 反例 2：编造测试证据

> **V11.7.0+ 设计入口**: [AC 核销门禁](../skills/09-review/SKILL.md) · [贾维斯门禁守护](../skills/00-boot/SKILL.md) · 评分制废除 → 门禁制 · 详见 [CHANGELOG.md V11.7.0](../CHANGELOG.md)


**违反**: V10.12 ANTI-反模式 1+2

**现象**:
- 假报 `tests/foo.test.ts:999`（实际不存在）
- 用 `grep 关键字` 充当测试覆盖
- 用 `console.log("test passed")` 充当 GREEN

**根因**: 想快点"完成"。

**教训**: reviewer 抽检发现 → 流程违规 REJECT。

**正确替代**: 真实 test/contract_tests/coverage 三个数字必填 + 真实 file:line 证据。
