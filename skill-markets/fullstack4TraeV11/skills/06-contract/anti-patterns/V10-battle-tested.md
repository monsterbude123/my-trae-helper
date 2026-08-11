# V10 实战蒸馏（Battle-Tested Patterns）

> Stage 2 Contract 从 V10 agents/contract-writer.md + contract-first.md + 配置治理 D-009 蒸馏。

---

## V10 实战反例（4 条）

### 蒸馏 1：D-009 前后端 config key 大小写不一致（V10 配置治理）

**实战场景**（V10 配置治理 D-009，2026-08-08 实战）:
- 前端 config key: `apiKey`（camelCase）
- 后端 regex: `[a-z0-9._]+`（严格小写）
- 前端请求被后端拒绝 → bug

**根因**: 契约修改只改代码，未同步改契约文档 + 测试。

**V11 改进**: 铁律 9（THREE-WAY SYNC — 契约修改必同步改 3 处：代码 + 契约文档 + 测试代码）+ D-009 实战案例写入反例 3。

**V10 源**: .trae/rules/配置治理.md §5 契约修改三方同步。

---

### 蒸馏 2：删 API 未删测试（V10 rot #12）

**实战场景**（V10 腐烂点 12）:
- 删 `/api/v1/old_login` → 旧测试 `__tests__/contracts/test_old_login.test.ts` 保留
- Stage 4 Review 时测试失败但查不出原因（接口已删）

**根因**: 删 API 时未删测试。

**V11 改进**: 铁律 3（ORPHAN TEST SWEEP）+ orphan-test-sweep.md + orphan-detector.py + 反例 2。

**V10 源**: process-rot-analysis.md rot #12。

---

### 蒸馏 3：契约包含"未来接口"（V10 contract-writer 反例）

**实战场景**（V10 蒸馏）:
- 契约写了 5 个 API，实际只实现 2 个
- Stage 4 Review 时"未实现的 API 是否计入验收"分歧

**根因**: DELTA ONLY 原则被忽略，写了"将来可能用"的接口。

**V11 改进**: 铁律 5（DELTA ONLY）+ contract-writer 四件套只写当前 change 必需的。

**V10 源**: agents/contract-writer.md 铁律 4 DELTA ONLY。

---

### 蒸馏 4：契约类型与实现不一致（V10 frontend-backend-contract-alignment 实战）

**实战场景**（V10 蒸馏）:
- 契约写 `created_at: ISO8601`
- 前端实现：`new Date()` 字符串（"2026-08-11"）
- 后端解析失败

**根因**: 契约格式与代码实现不匹配。

**V11 改进**: depends_on.skills 含 `frontend-backend-contract-alignment` + V10 frontend-backend-contract-alignment skill 蒸馏到 V11 公共 references。

**V10 源**: frontend-backend-contract-alignment skill。

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
