# 反例 1：跳过 DOMAIN FIRST 直接写 API

**违反**: 铁律 2 DOMAIN FIRST

**现象**: 立即写 API endpoint，跳过领域模型。

**根因**: 觉得"API 是用户视角，先写 API"。

**教训**: 后期补 domain 时发现 INV 与 API 矛盾 → 大量返工。

**正确替代**: Step 2 先写 domain-models.md（含 INV）→ Step 3 才写 api-contracts.md。

## 关联引用

- [SKILL.md §铁律 2](../SKILL.md)
- [contract-four-suite.md §DOMAIN FIRST 顺序](../references/contract-four-suite.md)
