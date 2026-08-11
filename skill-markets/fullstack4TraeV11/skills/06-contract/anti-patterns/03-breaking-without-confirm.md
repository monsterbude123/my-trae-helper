# 反例 3：BREAKING 变更不用户确认

**违反**: 铁律 4 ADDITIVE OVER BREAKING

**现象**: 删除字段 / 改类型 / 改路径 未走用户确认。

**根因**: 觉得"反正有版本号"。

**教训**: 破坏性变更影响下游所有调用者 → 客户端崩溃。

**正确替代**: BREAKING 变更必用户确认 + 走 major 版本号 + V10 D-009 三方同步（代码 + 契约文档 + 测试）。

## 关联引用

- [SKILL.md §铁律 4](../SKILL.md) — ADDITIVE OVER BREAKING
- V10 配置治理 §5 D-009: [../../../.trae/rules/配置治理.md](../../../.trae/rules/配置治理.md)
