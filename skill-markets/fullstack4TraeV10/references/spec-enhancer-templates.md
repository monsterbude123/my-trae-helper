# Spec-Enhancer 模板库

> 调用方：`agents/spec-enhancer.md` Step 2 Enhanced Acceptance
> 用途：spec-enhancer 在 spec.md 末尾追加 Enhanced Acceptance 段时使用的格式模板。
> 原则：ENHANCE, NOT REWRITE — 仅追加段，不修改上游产出的核心结构。

---

## §1. Enhanced Acceptance 模板

在 spec.md 末尾以 `## Enhanced Acceptance` 附加段写入：

```markdown
## Enhanced Acceptance

### E2E Scenarios
- **E2E-1**: {用户操作路径} → {预期结果}
- **E2E-2**: {用户操作路径} → {预期结果}

### Invariants
- {INV-1}: {不变的业务规则}

### Acceptance Criteria
- [ ] {AC-1}: {可验证的验收项}
- [ ] {AC-2}: {可验证的验收项}
- [ ] {AC-3}: {可验证的验收项}
```

---

## §2. 字段填写规范

| 字段 | 数量下限 | 填写要求 |
|------|---------|---------|
| E2E Scenarios | ≥ 2 | 用户操作路径 + 预期结果，端到端可验证 |
| Invariants | ≥ 1 | 不变的业务规则（无论何种输入都成立） |
| Acceptance Criteria | ≥ 3 | 可验证的验收项，含具体数字/状态/输出 |

---

## §3. 禁止项

**禁止**: 修改 spec.md 中上游产出的 `## Requirements`、`## Scenarios`、`## Tasks` 等核心段落。

Enhanced Acceptance 是**追加段**，位于 spec.md 末尾，与上游核心结构并存，互不冲突。

---

## 关联

- 调用方：`agents/spec-enhancer.md` Step 2
- 关联铁律：spec-enhancer §铁律 1-5（ENHANCE, NOT REWRITE / E2E MIN 2 / INVARIANTS MIN 1 / ACCEPTANCE MIN 3）
- 兄弟文档：[clarify-checklist.md](clarify-checklist.md)（Step 0.5 澄清检查）
