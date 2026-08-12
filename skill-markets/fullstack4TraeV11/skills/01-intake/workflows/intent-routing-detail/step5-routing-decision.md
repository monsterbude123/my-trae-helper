# Step 5：路由决策 — intent-routing.md 详情

> 父文件：[../intent-routing.md](../intent-routing.md)
> 来源：原 intent-routing.md 第 141-152 行（保留信息密度）

---

## Step 5：路由决策

| 意图类型 | 路由目标 | 状态卡类型 | next_stage |
|---------|---------|-----------|-----------|
| **project-init** | Stage 0 Plan → Stage 5 Accept | project | `0/plan` |
| **change-start (feature/refactor)** | Stage 0 Plan → Stage 5 Accept | change | `0/plan` |
| **change-start (doc-sync)** | Stage 1 Spec → Stage 5 Accept (lite) | change | `1/spec` |
| **bug-fix** | Stage 6 Bug Fix（独立支线）| bug | `6/bug-fix` |
| **project-health** | Stage 7 Project Health（异步自检）| project | `7/project-health` |

**详细路由决策树**: [../../references/routing-decision-tree.md](../../references/routing-decision-tree.md)

---

## 关联引用

- 父文件：[../intent-routing.md](../intent-routing.md)
- routing-decision-tree.md：[../../references/routing-decision-tree.md](../../references/routing-decision-tree.md)
- SKILL.md：[../../SKILL.md](../../SKILL.md)
