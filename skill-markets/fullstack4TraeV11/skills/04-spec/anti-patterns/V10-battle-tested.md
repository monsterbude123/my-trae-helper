# V10 实战蒸馏（Battle-Tested Patterns）

> Stage 1 Spec 从 V10 agents/spec-enhancer.md + references/spec-enhancer-templates.md + clarify-checklist.md + scenarios.md §8 蒸馏。

---

## V10 实战反例（4 条）

### 蒸馏 1：Clarify 单轮返工 ≥ 2 轮根因未诊断（V10.8 §8 真实场景）

**实战场景**（V10.8 scenarios.md §8 实战）:
- 用户对 spec 提出 ≥ 2 轮修改
- 主上下文继续修补命名/编号细节，不分析根因
- 第 5 轮用户："这个丝滑技能没有引导清楚吗？？？这个很重要"

**根因**: 未识别"用户连续 N 轮返工 = 流程问题，不是细节问题"。

**V11 改进**: clarify-checklist.md "≥ 2 轮返工根因诊断"段 + 反例 2（Clarify 跳过）+ 5 类根因诊断表。

**V10 源**: scenarios.md §8 反复反馈升级 + references/clarify-checklist.md §7。

---

### 蒸馏 2：Enhanced Acceptance 未增强（V10 acceptance-gates-v10.md 实战）

**实战场景**（V10 蒸馏）:
- spec.md Capabilities 3 项，但 Acceptance Criteria 只列 1-2 个
- Stage 4 Review 时 reviewer 标"AC 不全" → 返工补 AC → 又返工（因 spec 已基于原 AC 实施）

**根因**: AC 拆分粒度不够，未按 acceptance-enhancement.md 的 3 类（functional / error_handling / boundary）拆。

**V11 改进**: acceptance-enhancement.md 3 类型 AC + 铁律 4（ACCEPTANCE ≥ 3）+ Spec 模板 AC 强制拆分。

**V10 源**: acceptance-gates-v10.md §验收维度 + references/spec-enhancer-templates.md。

---

### 蒸馏 3：INV 凭空臆造（V10 spec-enhancer 失误）

**实战场景**（V10 蒸馏）:
- spec.md INV-1: "系统应该稳定"
- 不可测、不可证伪

**根因**: INV 不是基于业务规则，是主上下文臆造。

**V11 改进**: 铁律 6（NEVER 凭空 INV）+ 反例 1（INV 凭空臆造）+ acceptance-enhancement.md "INV 基于业务规则"。

**V10 源**: agents/spec-enhancer.md + scenarios.md §3 §8。

---

### 蒸馏 4：spec.md 写实施细节（V10 §7 实战）

**实战场景**（V10 蒸馏）:
- spec.md 含 "使用 bcrypt 算法哈希密码" / "UserService 类有 login 方法"
- Stage 3 Implement 严格按 spec 实现 → 用了 bcrypt → 性能问题 → 需改 → 但 spec 不允许改（已批准）

**根因**: Spec 混淆 "What" 与 "How"。

**V11 改进**: 铁律 7（NEVER 写实施）+ 反例 3（Spec 写实施）+ spec-template.md 只含规格段。

**V10 源**: SKILL.md §7 文档时铁律 DOC FIRST / references/spec-enhancer-templates.md。

---

## V10 实战蒸馏经验（4 条）

| 经验 | V10 来源 | V11 落地位置 |
|------|---------|------------|
| Clarify ≥ 2 轮 + 根因诊断 | scenarios.md §8 + clarify-checklist.md | 铁律 5 + clarify-checklist.md |
| AC ≥ 3 拆分 3 类型 | acceptance-gates-v10.md + spec-enhancer-templates.md | acceptance-enhancement.md + 铁律 4 |
| INV 基于业务规则 | spec-enhancer.md | 铁律 6 + 反例 1 |
| Spec 不写 How | references/doc-sync.md | 铁律 7 + 反例 3 |

---

## V10 来源溯源（开发期，部署前可删）

> ⚠️ 本节记录 V10 来源，仅供 V11 维护者追溯。**V11 部署时不依赖 V10**——V10 内容已蒸馏进 V11 references/anti-patterns。

| V10 来源 | 蒸馏到 V11 位置 |
|---------|---------------|
| V10 spec-enhancer.md | → `../../04-spec/SKILL.md` 铁律 + `README.md` |
| V10 spec-enhancer-templates.md | → `../../04-spec/references/acceptance-enhancement.md` + `templates/spec-template.md` |
| V10 clarify-checklist.md | → `../../04-spec/references/clarify-checklist.md` |
| V10 scenarios.md §8 反复反馈升级 | → 本文档蒸馏 1 |
| V10 acceptance-gates-v10.md §验收维度 | → `../../04-spec/references/acceptance-enhancement.md` |

---

## 关联引用

- [SKILL.md](../SKILL.md) | [README.md](../README.md) | [acceptance-enhancement.md](../references/acceptance-enhancement.md) | [clarify-checklist.md](../references/clarify-checklist.md)
- 其他反例: [01-inv-fabrication.md](01-inv-fabrication.md) / [02-skip-clarify.md](02-skip-clarify.md) / [03-spec-write-impl.md](03-spec-write-impl.md)
