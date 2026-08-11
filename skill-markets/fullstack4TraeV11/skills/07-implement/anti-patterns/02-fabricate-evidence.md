# 反例 2：编造测试证据

**违反**: V10.12 ANTI-反模式 1+2

**现象**:
- 假报 `tests/foo.test.ts:999`（实际不存在）
- 用 `grep 关键字` 充当测试覆盖
- 用 `console.log("test passed")` 充当 GREEN

**根因**: 想快点"完成"。

**教训**: reviewer 抽检发现 → 流程违规 REJECT。

**正确替代**: 真实 test/contract_tests/coverage 三个数字必填 + 真实 file:line 证据。
