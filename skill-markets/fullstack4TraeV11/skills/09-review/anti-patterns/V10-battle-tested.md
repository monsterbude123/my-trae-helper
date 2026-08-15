# V10 实战蒸馏（Battle-Tested Patterns）

> **V11.7.0+ 设计入口**: [AC 核销门禁](../skills/09-review/SKILL.md) · [贾维斯门禁守护](../skills/00-boot/SKILL.md) · 评分制废除 → 门禁制 · 详见 [CHANGELOG.md V11.7.0](../CHANGELOG.md)


> Stage 4 Review 从 V10 agents/reviewer.md + reviewer-templates.md + acceptance-gates-v10.md + multi-round-revision-protocol.md + skeptical-validation-protocol.md 蒸馏。

---

## V10 实战反例（5 条：1 独有 + 2 部分 + 2 完全重叠）

### 蒸馏 1：盖章者思维（部分重叠）

**独特差异**: 不同于 01-non-blocking-fail.md 聚焦"不拦截 FAIL"，本条聚焦 reviewer 默认立场——"默认已完成 → 找证据确认 → 找不到放过"，V11 改进为立场反转：质疑式验收官（默认未完成/有隐瞒 → 索要证据 → 不全拦截）。

→ 关联 [01-non-blocking-fail.md](01-non-blocking-fail.md)（reviewer.md §立场 + 铁律 9 ZERO TRUST）。

### 蒸馏 2：自评=self_attested 失真（部分重叠）

**独特差异**: 不同于 02-reviewer-fix-code.md 聚焦"reviewer 亲自改代码"，本条聚焦 sub-agent 自评"已通过全部测试" → 主上下文未二次抽检 → 实际有测试 skip 标记未发现。V11 改进为铁律 8 CROSS-SESSION VERIFY + acceptance-audit.py。

→ 关联 [02-reviewer-fix-code.md](02-reviewer-fix-code.md)。

### 蒸馏 3：编造测试覆盖（完全重叠）

→ 见 [03-fabricate-coverage.md](03-fabricate-coverage.md)（reviewer 亲自跑 coverage 命令 + 关键门禁套件铁律 10）。

### 蒸馏 4：反复反馈升级（完全重叠）

→ 见 [04-round-keep-trying.md](04-round-keep-trying.md)（Round 3+ rescue hatch 自动触发 → 回退 Phase 0）。

### 蒸馏 5：抽象理由放水（独有蒸馏，无对应反例文件）

**实战场景**（V10.10 蒸馏）: reviewer 接受 "基本通过" / "大致完成" 灰色术语 → 实际未达满分硬门禁。

**V11 改进**: 铁律 2 SCORING IS DERIVED + 四维度 4 反例 A（凑分）+ 四维度反例 B（N/A 充数）。

**V10 源**: reviewer.md 铁律 2-4 + acceptance-gates-v10.md。

---

## V10 实战蒸馏经验（5 条）

| 经验 | V10 来源 | V11 落地位置 |
|------|---------|------------|
| 立场反转（盖章者→质疑式）| reviewer.md §立场 | SKILL.md §立场 |
| 自评=self_attested 必抽检 | reviewer.md 铁律 8 | 铁律 8 + acceptance-audit.py |
| reviewer 必亲自跑覆盖 | reviewer-templates.md §2.4 | 铁律 10 + 反例 3 |
| Round 3+ rescue hatch | reviewer.md Step 2.6 | references/multi-round-revision.md |
| 拒绝灰色术语 | reviewer.md 铁律 2-4 | 四维度反例 A/B |

---

## V10 来源溯源（开发期，部署前可删）

> ⚠️ 本节记录 V10 来源，仅供 V11 维护者追溯。**V11 部署时不依赖 V10**——V10 内容已蒸馏进 V11 references/anti-patterns。

| V10 来源 | 蒸馏到 V11 位置 |
|---------|---------------|
| V10 reviewer.md | → `../../09-review/SKILL.md` 铁律 1-10 + `references/skeptical-acceptance.md` + `multi-round-revision.md` |
| V10 reviewer-templates.md | → `../../09-review/references/...` + `templates/review-report-template.md` |
| V10 acceptance-gates-v10.md | → `../../09-review/references/four-dimension-scoring.md` + `evidence-3-layer.md` |
| V10 multi-round-revision-protocol.md | → `../../09-review/references/multi-round-revision.md` |
| V10 skeptical-validation-protocol.md | → `../../09-review/SKILL.md` 铁律 9-10 + `references/skeptical-acceptance.md` |
| V10 scenarios.md §6 §8 | → 本文档蒸馏 1+4 |

---

## 关联引用

- [SKILL.md](../SKILL.md) | [README.md](../README.md)
- [four-dimension-scoring.md](../references/four-dimension-scoring.md) | [evidence-3-layer.md](../references/evidence-3-layer.md) | [skeptical-acceptance.md](../references/skeptical-acceptance.md) | [multi-round-revision.md](../references/multi-round-revision.md)
- 其他反例: [01-non-blocking-fail.md](01-non-blocking-fail.md) / [02-reviewer-fix-code.md](02-reviewer-fix-code.md) / [03-fabricate-coverage.md](03-fabricate-coverage.md) / [04-round-keep-trying.md](04-round-keep-trying.md)
