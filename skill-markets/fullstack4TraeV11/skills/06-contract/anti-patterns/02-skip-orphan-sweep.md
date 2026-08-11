# 反例 2：跳过孤儿契约测试清理

**违反**: 铁律 3 ORPHAN TEST SWEEP（V10 腐烂点 12）

**现象**: 写新契约前未跑 orphan-detector.py。

**根因**: 不知道 V10 rot #12 修复协议。

**教训**: 旧孤儿测试仍在，新契约测试 + 旧孤儿 → Stage 4 Review 失败。

**正确替代**: Step 4 必跑 orphan-detector.py → 清理 → 再写新契约。

## 关联引用

- [SKILL.md §铁律 3](../SKILL.md)
- [orphan-test-sweep.md](../references/orphan-test-sweep.md)
- V10 rot #12: `V10 来源` (已蒸馏到本文档)
