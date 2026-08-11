# V10 实战蒸馏（Battle-Tested Patterns）

> Stage 4 Review 从 V10 agents/reviewer.md + reviewer-templates.md + acceptance-gates-v10.md + multi-round-revision-protocol.md + skeptical-validation-protocol.md 蒸馏。

---

## V10 实战反例（5 条）

### 蒸馏 1：盖章者思维（V10.8 反思）

**实战场景**（V10.8 蒸馏）:
- reviewer 默认"已完成" → 找证据确认 → 找不到放过
- 实际有 3 处关键 FAIL 未检出

**V11 改进**: 立场反转 — 质疑式验收官（默认未完成/有隐瞒 → 索要证据 → 不全拦截）。

**V10 源**: reviewer.md §立场 + 铁律 9 ZERO TRUST。

---

### 蒸馏 2：自评=self_attested 失真（V10.4 修复）

**实战场景**（V10.4 蒸馏）:
- sub-agent "已通过全部测试" → 主上下文未二次抽检
- 实际有测试 skip 标记未发现

**V11 改进**: 铁律 8 CROSS-SESSION VERIFY + acceptance-audit.py。

**V10 源**: reviewer.md 铁律 8 + acceptance-gates-v10.md。

---

### 蒸馏 3：编造测试覆盖（V10.12 关键门禁套件）

**实战场景**: 见 anti-patterns/03-fabricate-coverage.md。

**V11 改进**: reviewer 亲自跑 coverage 命令 + 关键门禁套件（铁律 10）。

**V10 源**: reviewer-templates.md §Step 2.4 Test Plan 前置门禁。

---

### 蒸馏 4：反复反馈升级（V10.8 §6 实战）

**实战场景**: 见 references/multi-round-revision.md。

**V11 改进**: Round 3+ rescue hatch 自动触发 → 回退 Phase 0。

**V10 源**: scenarios.md §6 审核不通过返工 + reviewer.md Step 2.6。

---

### 蒸馏 5：抽象理由放水（V10.10 Article XVI）

**实战场景**（V10.10 蒸馏）:
- reviewer 接受 "基本通过" / "大致完成" 灰色术语
- 实际未达满分硬门禁

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
