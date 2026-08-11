# 反例 1：跳过 RED 直接 GREEN

**违反**: V10 铁律 8 禁止虚假绿灯

**现象**: implementer 直接写实现 → 测试通过 → 但实际是 GREEN-only。

**根因**: 觉得 RED 步骤浪费时间。

**教训**: 测试可能永远 GREEN（未真正验证逻辑）→ 上线后 bug。

**正确替代**: TDD 三步循环必走（RED → GREEN → REFACTOR）。
