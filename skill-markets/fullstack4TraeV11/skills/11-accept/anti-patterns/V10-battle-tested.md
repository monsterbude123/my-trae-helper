# V10 实战蒸馏（Battle-Tested Patterns）

> Stage 5 Accept 从 V10 artifact-lifecycle.md + prd-integration-workflow.md + spec-purge.py + spec-knowledge-extract.py 蒸馏。

## V10 实战反例（3 条）

### 蒸馏 1：归档前未沉淀知识（rot #12 文档腐烂）

**实战场景**（V10 实战）:
- change Accept → spec-purge 归档
- API/Domain/Event 未提取到 docs/ → 后续项目无法引用

**V11 改进**: 铁律 2（知识沉淀先于归档）+ knowledge-extract.md。

### 蒸馏 2：归档目录被改（Article VIII 违规）

**实战场景**（V10 实战）:
- 用户："归档里的 spec 有错" → 主上下文直接 Edit archive/

**V11 改进**: 铁律 1（归档不可变）+ archive-protocol.md 反例 B（修改归档）。

### 蒸馏 3：spec-purge 误删有效 change

**实战场景**（V10 实战）:
- spec-purge.py 误把活跃 change 归档
- 状态卡 current_stage 指向已归档

**V11 改进**: spec-purge.py 必先 dry-run 验证 + 状态卡 validator。

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
