# templates/ — 单源原则

> V11 模板遵循 **single source of truth**（单源原则）。

---

## 三类位置（不重复）

### 1. 顶层 `templates/`（项目级 + 通用）

路径：`skill-markets/fullstack4TraeV11/templates/`

| 模板 | 用途 |
|------|------|
| `constitution-template.md` | 项目级宪法（17 Articles）|
| `checklist-template.md` | Stage 1 Spec 完整性验证 |
| `state-card.md` | 13 stage 通用状态卡 |
| `bug-template.md`（注：已迁） | **已迁到 skills/01-intake/templates/** |
| `project-rules-example/` | 项目级 rules 范例 |
| `project-agents-example.md` | 项目级 agents 范例 |
| `hooks/` | TRAE IDE 13 hooks |

### 2. `references/templates/`（共享 contracts）

路径：`skill-markets/fullstack4TraeV11/references/templates/`

仅存**跨 stage 共享的契约模板**：
- `api-contracts-template.md`
- `domain-models-template.md`
- `events-template.md`
- `validation-rules-template.md`
- `test-plan-template.md`
- `rot-scan-template.md`

> 注意：**plan / spec / bug 模板已迁到 skills/<stage>/templates/**（避免重复）。

### 3. `skills/<stage>/templates/`（stage 私有）

路径：`skill-markets/fullstack4TraeV11/skills/NN-{name}/templates/`

每个 stage 的**私有模板**（仅该 stage 使用）：
- 01-intake: `bug-template.md` + `state-card-init.md`
- 02-plan: `plan-template.md`
- 03-test-plan: `test-plan.md`
- 04-spec: `spec-template.md`
- 05-prototype: `prototype-template.md`
- 06-contract: `api-contracts.md` + `domain-models.md` + `events.md` + `validation-rules.md`
- 09-review: `review-report-template.md`

---

## 单源原则（必走）

```
1. 一个模板只存在一个权威位置
2. 其他位置用相对路径引用，不复制
3. 模板修改必同步所有引用方
4. 部署前必跑 scan-templates.py --strict 检查无重复
```

---

## 检测（scan-templates.py）

```bash
# 检查项目 + V11 模板可解析性
python scripts/scan-templates.py --project-root . --strict

# 输出 5 项：
# - spec-template
# - constitution-template
# - checklist-template
# - state-card
# - bug-template
```

任一 FAIL → 🛑 REJECT。

---

## 关联引用

- [scan-templates.py](../../scripts/scan-templates.py) — 模板路径解析检测
- [references/templates/](../templates/) — 跨 stage 共享契约模板
- [skills/*/templates/](../../skills/) — stage 私有模板
- [templates/](../../templates/) — 项目级 + 通用模板
- V10 来源（开发期）: `../../../fullstack4TraeV10/scripts/scan-templates.py`