# V10 实战蒸馏（Battle-Tested Patterns）

> Stage 3 Implement 从 V10 agents/implementer.md + tdd-workflow.md + drift-detect.md + scenarios.md §3-9 蒸馏。

---

## V10 实战反例（5 条：1 独有 + 1 部分 + 3 完全重叠）

### 蒸馏 1：rot #13 Bundle Staleness（独有蒸馏，无对应反例文件）

**实战场景**（V10.4 蒸馏）: 改 `src/auth/login.ts` → `dist/auth/login.js` 未重生成 → 部署后用户跑旧 bundle → bug。

**V11 改进**: 铁律 5（Bundle Staleness）+ depends_on.scripts 含 `dist-hash-check.py`。

**V10 源**: implementer.md 铁律 5（V10.4 4.5 升级命名）。

### 蒸馏 2：改实现不改测试（完全重叠）

→ 见 [03-impl-without-test-sync.md](03-impl-without-test-sync.md)（V10 rot #12，铁律 2 TDD 即时 + orphan-detector.py）。

### 蒸馏 3：DRIFT 静默回流（完全重叠）

→ 见 [04-drift-silent.md](04-drift-silent.md)（铁律 3 漂移必报告 + drift-detect.md）。

### 蒸馏 4：模块文档缺失（部分重叠）

**独特差异**: 不同于 01-skip-red.md 聚焦"跳过 TDD RED 阶段"，本条聚焦"基础模块（如 `src/auth/token.ts`）创建后未写 `docs/modules/auth/token.md`"→ 后续 Stage 3 增量任务不知道如何复用 → 重新实现。

→ 关联 [01-skip-red.md](01-skip-red.md)（铁律 4 基础模块留文档 + 模块文档模板条件触发）。

### 蒸馏 5：编造测试证据（完全重叠）

→ 见 [02-fabricate-evidence.md](02-fabricate-evidence.md)（V10.12 ANTI-反模式 1+2，铁律 10 禁止编造测试证据）。

---

## V10 实战蒸馏经验（5 条）

| 经验 | V10 来源 | V11 落地位置 |
|------|---------|------------|
| Bundle Staleness 检测 | implementer 铁律 5（rot #13）| 铁律 5 + dist-hash-check.py |
| TDD 即时（rot #12）| implementer 铁律 2 | 铁律 2 + 反例 3 |
| 漂移必报告 | implementer 铁律 3 + drift-detect.md | 铁律 3 + drift-detect.md |
| 基础模块留文档 | implementer 铁律 4 | 铁律 4 + 模块文档模板 |
| 禁止编造测试证据 | V10.12 ANTI-反模式 | 铁律 10 + 反例 2 |

---

## V10 来源溯源（开发期，部署前可删）

> ⚠️ 本节记录 V10 来源，仅供 V11 维护者追溯。**V11 部署时不依赖 V10**——V10 内容已蒸馏进 V11 references/anti-patterns。

| V10 来源 | 蒸馏到 V11 位置 |
|---------|---------------|
| V10 implementer.md | → `../../07-implement/SKILL.md` 铁律 1-10 + `README.md` |
| V10 tdd-workflow.md | → `../../07-implement/references/tdd-workflow.md` |
| V10 drift-detect.md | → `../../07-implement/references/drift-detect.md` |
| V10 scenarios.md §3-9 | → 本文档蒸馏 1-5 |
| V10 doc-sync.md | → Stage 4 Review DOC SYNC |
| V10 .trae/rules/硬编码治理.md | → `../../07-implement/references/code-hygiene.md` L0-L4 |

---

## 关联引用

- [SKILL.md](../SKILL.md) | [README.md](../README.md)
- [tdd-workflow.md](../references/tdd-workflow.md) | [code-hygiene.md](../references/code-hygiene.md) | [drift-detect.md](../references/drift-detect.md)
- 其他反例: [01-skip-red.md](01-skip-red.md) / [02-fabricate-evidence.md](02-fabricate-evidence.md) / [03-impl-without-test-sync.md](03-impl-without-test-sync.md) / [04-drift-silent.md](04-drift-silent.md)
