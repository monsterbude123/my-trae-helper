# V10 实战蒸馏（Battle-Tested Patterns）

> Stage 5 Accept 从 V10 artifact-lifecycle.md + prd-integration-workflow.md + spec-purge.py + spec-knowledge-extract.py 蒸馏。

## V10 实战反例（3 条：1 部分 + 2 完全重叠）

### 蒸馏 1：归档前未沉淀知识（完全重叠）

→ 见 [01-skip-knowledge-extract.md](01-skip-knowledge-extract.md)（rot #12 文档腐烂，铁律 2 知识沉淀先于归档 + knowledge-extract.md）。

### 蒸馏 2：归档目录被改（完全重叠）

→ 见 [02-modify-archive.md](02-modify-archive.md)（Article VIII 违规，铁律 1 归档不可变 + archive-protocol.md 反例 B）。

### 蒸馏 3：spec-purge 误删有效 change（部分重叠）

**独特差异**: 不同于 03-delete-archive.md 聚焦"删除归档"，本条聚焦 spec-purge.py 误把**活跃 change** 归档 → 状态卡 current_stage 指向已归档目录。V11 改进为 spec-purge.py 必先 dry-run 验证 + 状态卡 validator。

→ 关联 [03-delete-archive.md](03-delete-archive.md)。

## V10 来源溯源（开发期，部署前可删）

> ⚠️ 本节记录 V10 来源，仅供 V11 维护者追溯。**V11 部署时不依赖 V10**——V10 内容已蒸馏进 V11 references/anti-patterns。

| V10 来源 | 蒸馏到 V11 位置 |
|---------|---------------|
| V10 artifact-lifecycle.md | → `../../11-accept/references/archive-protocol.md` |
| V10 prd-integration-workflow.md | → `../../11-accept/references/knowledge-extract.md` |
| V10 spec-purge.py | → V11 `scripts/spec-purge.py`（重写） |
| V10 spec-knowledge-extract.py | → V11 `scripts/spec-knowledge-extract.py`（重写） |

## 关联引用

[SKILL.md](../SKILL.md) | [archive-protocol.md](../references/archive-protocol.md) | [knowledge-extract.md](../references/knowledge-extract.md)
