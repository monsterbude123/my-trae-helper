# V10 实战蒸馏（Battle-Tested Patterns）

> Stage 6 Bug Fix 从 V10 `agents/debugger.md` + `references/debugger-methodology.md` + `references/bug-workflow.md` 蒸馏实战智慧。

---

## V10 实战反例（4 条，均完全重叠于独立反例文件）

| # | 蒸馏主题 | 反例文件指针 |
|---|---------|------------|
| 蒸馏 1 | 跳过 e2e 先行直接修（V10 debugger.md 铁律"e2e 必初始 FAIL"） | → 见 [01-skip-e2e-first.md](01-skip-e2e-first.md) |
| 蒸馏 2 | 跨层过度修复（违反 Ponytail 最小修复面决策阶梯） | → 见 [02-cross-layer-overkill.md](02-cross-layer-overkill.md) |
| 蒸馏 3 | 修复不回写 bug 单（bug-workflow 状态机闭环未走） | → 见 [03-not-update-bug.md](03-not-update-bug.md) |
| 蒸馏 4 | 大小写不敏感比较违规（rot #11 hash/ID/token 比较铁律） | → 见 [04-case-insensitive-bug.md](04-case-insensitive-bug.md) |

---

## V10 → V11 蒸馏映射

| V10 来源 | V11 蒸馏位置 |
|---------|------------|
| agents/debugger.md 8 铁律 | skills/12-bug-fix/SKILL.md 铁律 1-8 |
| references/debugger-methodology.md | references/five-step-flow.md + six-layer-diagnosis.md + cross-layer-fix.md |
| references/bug-workflow.md | references/bug-state-machine.md |
| rot #11 字符串比较 | anti-patterns/04 + sub-agent-rules §11 |

---

## 关联引用

- [skills/12-bug-fix/SKILL.md](../SKILL.md) — Stage 6 主入口
- [references/agent-error-diagnosis.md](../../references/agent-error-diagnosis.md) — agent 5 模式根因诊断
- [references/common-iron-rules.md](../../references/common-iron-rules.md) — Article XVII Secret Redaction（V11 NEW）
