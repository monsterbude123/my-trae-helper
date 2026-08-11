# V10 实战蒸馏（Battle-Tested Patterns）

> Stage 1.5 Prototype 从 V10 agents/spec-prototype-enhancer.md + references/prototype*.md + designer-handoff.md 蒸馏。

---

## V10 实战反例（4 条）

### 蒸馏 1：设计稿与代码无关联（V10 prototype-reverse-spec 实战）

**实战场景**（V10 蒸馏）:
- 设计师出 Figma 设计稿
- 工程师独立写代码原型
- Stage 4 Review 发现 UI 与设计稿不一致（颜色、间距、交互）→ 大返工

**根因**: 双源未建立反向追溯（prototype-reverse-spec）。

**V11 改进**: 铁律 1（双源一致）+ 铁律 2（prototype-reverse-spec）+ 反例 1（设计稿与代码脱节）+ dual-source-protocol.md。

**V10 源**: agents/spec-prototype-enhancer.md + references/prototype-reverse-spec.md + references/prototype.md。

---

### 蒸馏 2：designer-handoff 缺关键信息（V10 designer-handoff.md 实战）

**实战场景**（V10 蒸馏）:
- 设计师只移交 Figma 链接
- 工程师实现时：hover 状态未定义 / loading 状态缺失 / 错误状态空白
- Stage 4 Review 大量"边缘状态缺失"问题

**根因**: designer-handoff 清单不全。

**V11 改进**: 铁律 3（designer-handoff）+ prototype-code-gap.md "designer-handoff 必含"段（设计稿 + 交互说明 + token + 边缘情况）。

**V10 源**: references/designer-handoff.md。

---

### 蒸馏 3：原型代码混入业务逻辑（V10 prototype-code-gap-analysis.md 实战）

**实战场景**（V10 蒸馏）:
- 工程师 prototype 阶段直接写完整 UserService（含 DB / Auth / Token 签发）
- Stage 3 Implement 时无 prototype 与实施边界 → 重复实施

**根因**: Prototype 阶段越界到 Implementation。

**V11 改进**: 铁律 4（NEVER 跳过双源）+ 反例 3（prototype 写实现）+ prototype-template.md "最小可运行 demo"段。

**V10 源**: references/prototype-code-gap-analysis.md。

---

### 蒸馏 4：prototype-linkage 缺失（V10 实战）

**实战场景**（V10 蒸馏）:
- Stage 1.5 完成 prototype.md，但未建立与 Stage 1 spec.md / Stage 3 Implement 的链接
- Stage 4 Review 时无法定位"设计依据"

**根因**: prototype-linkage 未维护。

**V11 改进**: prototype-template.md 必含 "spec.md AC 映射" 表 + "GAP 列表"。

**V10 源**: references/prototype-linkage.md。

---

## V10 实战蒸馏经验（4 条）

| 经验 | V10 来源 | V11 落地位置 |
|------|---------|------------|
| 双源反向追溯 | prototype-reverse-spec.md | 铁律 2 + dual-source-protocol.md |
| designer-handoff 必含边缘 | designer-handoff.md | 铁律 3 + prototype-code-gap.md |
| Prototype ≠ Implementation | prototype-code-gap-analysis.md | 反例 3 |
| prototype-linkage 必维护 | prototype-linkage.md | prototype-template.md AC 映射表 |

---

## V10 来源溯源（开发期，部署前可删）

> ⚠️ 本节记录 V10 来源，仅供 V11 维护者追溯。**V11 部署时不依赖 V10**——V10 内容已蒸馏进 V11 references/anti-patterns。

| V10 来源 | 蒸馏到 V11 位置 |
|---------|---------------|
| V10 spec-prototype-enhancer.md | → `../../05-prototype/SKILL.md` + `README.md` |
| V10 prototype.md | → `../../05-prototype/references/dual-source-protocol.md` |
| V10 prototype-reverse-spec.md | → `../../05-prototype/references/dual-source-protocol.md` §prototype-reverse-spec |
| V10 prototype-linkage.md | → `../../05-prototype/templates/prototype-template.md` AC 映射表 |
| V10 prototype-code-gap-analysis.md | → `../../05-prototype/references/prototype-code-gap.md` |
| V10 designer-handoff.md | → `../../05-prototype/references/prototype-code-gap.md` §designer-handoff |

---

## 关联引用

- [SKILL.md](../SKILL.md) | [README.md](../README.md) | [dual-source-protocol.md](../references/dual-source-protocol.md) | [prototype-code-gap.md](../references/prototype-code-gap.md)
- 其他反例: [01-design-code-mismatch.md](01-design-code-mismatch.md) / [02-skip-dual-source.md](02-skip-dual-source.md) / [03-prototype-as-impl.md](03-prototype-as-impl.md)
