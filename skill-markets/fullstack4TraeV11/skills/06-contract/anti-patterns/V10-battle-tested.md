# V10 实战蒸馏（Battle-Tested Patterns）

> **V11.7.0+ 设计入口**: [AC 核销门禁](../skills/09-review/SKILL.md) · [贾维斯门禁守护](../skills/00-boot/SKILL.md) · 评分制废除 → 门禁制 · 详见 [CHANGELOG.md V11.7.0](../CHANGELOG.md)


> Stage 2 Contract 从 V10 agents/contract-writer.md + contract-first.md + 配置治理 D-009 蒸馏。

---

## V10 实战反例（4 条：2 部分 + 2 完全重叠）

### 蒸馏 1：D-009 前后端 config key 大小写不一致（部分重叠）

**独特差异**: 不同于 03-breaking-without-confirm.md 聚焦"破坏性变更未确认"，本条聚焦 D-009 实战——前端 config key `apiKey`（camelCase）vs 后端 regex `[a-z0-9._]+`（严格小写）→ 前端请求被后端拒绝。V11 改进为铁律 9 THREE-WAY SYNC（契约修改必同步改 3 处：代码 + 契约文档 + 测试代码）。

→ 关联 [03-breaking-without-confirm.md](03-breaking-without-confirm.md)。

### 蒸馏 2：删 API 未删测试（完全重叠）

→ 见 [02-skip-orphan-sweep.md](02-skip-orphan-sweep.md)（V10 rot #12，铁律 3 ORPHAN TEST SWEEP + orphan-detector.py）。

### 蒸馏 3：契约包含"未来接口"（部分重叠）

**独特差异**: 不同于 01-skip-domain.md 聚焦"跳过领域驱动设计"，本条聚焦 DELTA ONLY 原则被忽略——契约写 5 个 API 实际只实现 2 个 → Stage 4 Review "未实现 API 是否计入验收"分歧。V11 改进为铁律 5 DELTA ONLY（contract-writer 四件套只写当前 change 必需的）。

→ 关联 [01-skip-domain.md](01-skip-domain.md)。

### 蒸馏 4：契约类型与实现不一致（完全重叠）

→ 见 [04-contract-drift.md](04-contract-drift.md)（铁律 datetime 等格式对齐 + depends_on.skills 含 frontend-backend-contract-alignment）。

---

## V10 实战蒸馏经验（4 条）

| 经验 | V10 来源 | V11 落地位置 |
|------|---------|------------|
| 契约修改三方同步（代码+文档+测试）| 配置治理 D-009 | 铁律 9 + 反例 3 |
| 孤儿契约测试必清理（rot #12）| process-rot-analysis.md | 铁律 3 + orphan-test-sweep.md |
| DELTA ONLY（不写未来接口）| contract-writer.md 铁律 4 | 铁律 5 |
| 契约类型与代码对齐（datetime 等）| frontend-backend-contract-alignment | depends_on.skills |

---

## V10 来源溯源（开发期，部署前可删）

> ⚠️ 本节记录 V10 来源，仅供 V11 维护者追溯。**V11 部署时不依赖 V10**——V10 内容已蒸馏进 V11 references/anti-patterns。

| V10 来源 | 蒸馏到 V11 位置 |
|---------|---------------|
| V10 contract-writer.md | → `../../06-contract/SKILL.md` 铁律 + `references/contract-four-suite.md` |
| V10 contract-first.md | → `../../06-contract/references/contract-four-suite.md` |
| V10 配置治理 D-009 | → 本文档蒸馏 1 + `anti-patterns/03-breaking-without-confirm.md` |
| V10 process-rot-analysis.md rot #12 | → `../../06-contract/references/orphan-test-sweep.md` |
| V10 drift-detect.md | → `../../07-implement/references/drift-detect.md` |

---

## 关联引用

- [SKILL.md](../SKILL.md) | [README.md](../README.md)
- [contract-four-suite.md](../references/contract-four-suite.md) | [orphan-test-sweep.md](../references/orphan-test-sweep.md)
- 其他反例: [01-skip-domain.md](01-skip-domain.md) / [02-skip-orphan-sweep.md](02-skip-orphan-sweep.md) / [03-breaking-without-confirm.md](03-breaking-without-confirm.md) / [04-contract-drift.md](04-contract-drift.md)
