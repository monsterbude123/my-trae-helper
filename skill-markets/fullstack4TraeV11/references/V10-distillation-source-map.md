# V10 → V11 蒸馏溯源（开发期参考）

> ⚠️ **本文档是开发期 reference，不属于 V11 运行时依赖**。
>
> V11 是独立 skill 版本，部署到 `~/.trae-cn/skills/fullstack4TraeV11/` 时**不依赖** `fullstack4TraeV10/` 目录存活。
>
> 本文档记录 V10 哪些内容被蒸馏到 V11 哪些位置，供 V11 维护者追溯。**部署前可删除本文档**。

---

## 蒸馏原则

```
V10 (来源)  ──── 蒸馏吸收 ────>  V11 (运行时)
                              │
                              ├─ V11 references/  (运行时引用)
                              ├─ V11 anti-patterns/ (运行时引用)
                              └─ V10 实战案例内化进 V11 反例
```

**禁止**: V11 运行时文档含 `../../fullstack4TraeV10/...` 路径（部署即断裂）。

---

## 蒸馏映射表

### Stage -1 Intake

| V10 来源 | V11 蒸馏位置 |
|---------|------------|
| `references/bug-workflow.md` | `skills/01-intake/workflows/bug-intake-flow.md` + `anti-patterns/V10-battle-tested.md` 蒸馏 1 |
| SKILL.md §1.6 + §7.5 | `skills/01-intake/anti-patterns/V10-battle-tested.md` 蒸馏 1+4 |
| scenarios.md §1+§2+§5 | `anti-patterns/V10-battle-tested.md` 蒸馏 2 |

### Stage 0 Plan

| V10 来源 | V11 蒸馏位置 |
|---------|------------|
| `agents/planner.md` | `skills/02-plan/SKILL.md` 铁律 + `workflows/three-path-exploration.md` |
| `references/sub-agent-rules.md` | `skills/02-plan/references/...` |
| `references/skeptical-validation-protocol.md` | `references/skeptical-validation-protocol.md`（V11 完整继承 240 行 + 新增反例 6/7）+ 7 stage 铁律永久引用 |
| `references/glossary.md` | `references/glossary.md`（V11 完整继承 64 行 V10 术语 + 新增 5 大类 V11 术语 100+）|
| `scenarios.md §3` | `anti-patterns/V10-battle-tested.md` |

### Stage 0.5 Test Plan

| V10 来源 | V11 蒸馏位置 |
|---------|------------|
| `references/acceptance-gates-v10.md` | `skills/03-test-plan/references/coverage-rules.md` + `anti-patterns/V10-battle-tested.md` |

### Stage 1 Spec

| V10 来源 | V11 蒸馏位置 |
|---------|------------|
| `agents/spec-enhancer.md` | `skills/04-spec/SKILL.md` 铁律 |
| `references/spec-enhancer-templates.md` | `skills/04-spec/references/acceptance-enhancement.md` |
| `references/clarify-checklist.md` | `skills/04-spec/references/clarify-checklist.md` |
| `scenarios.md §8` | `skills/04-spec/anti-patterns/V10-battle-tested.md` 蒸馏 1 |

### Stage 1.5 Prototype

| V10 来源 | V11 蒸馏位置 |
|---------|------------|
| `agents/spec-prototype-enhancer.md` | `skills/05-prototype/...` |
| `references/prototype.md` + `prototype-reverse-spec.md` + `prototype-linkage.md` + `prototype-code-gap-analysis.md` + `designer-handoff.md` | `skills/05-prototype/references/dual-source-protocol.md` + `prototype-code-gap.md` |

### Stage 2 Contract

| V10 来源 | V11 蒸馏位置 |
|---------|------------|
| `agents/contract-writer.md` | `skills/06-contract/SKILL.md` 铁律 |
| `references/contract-first.md` | `skills/06-contract/references/contract-four-suite.md` |
| `references/process-rot-analysis.md` rot #12 | `skills/06-contract/references/orphan-test-sweep.md` |
| `.trae/rules/配置治理.md` D-009 | `skills/06-contract/anti-patterns/V10-battle-tested.md` 蒸馏 1 |

### Stage 3 Implement

| V10 来源 | V11 蒸馏位置 |
|---------|------------|
| `agents/implementer.md` | `skills/07-implement/SKILL.md` 铁律 1-10 |
| `references/tdd-workflow.md` | `skills/07-implement/references/tdd-workflow.md` |
| `references/drift-detect.md` | `skills/07-implement/references/drift-detect.md` |
| `.trae/rules/硬编码治理.md` | `skills/07-implement/references/code-hygiene.md` |

### Stage 3.5 Real Verify

| V10 来源 | V11 蒸馏位置 |
|---------|------------|
| SKILL.md §0.10 | `skills/08-real-verify/SKILL.md` 铁律 1-6 |
| `.trae/rules/视觉证据铁律.md` | `skills/08-real-verify/references/visual-evidence.md` |
| `scripts/visual-content-check.py` | V11 由 `scripts/visual-content-check.py` 重写 |
| `scripts/dist-hash-check.py` | V11 由 `scripts/dist-hash-check.py` 重写 |

### Stage 4 Review

| V10 来源 | V11 蒸馏位置 |
|---------|------------|
| `agents/reviewer.md` (V10.8 + V10.12) | `skills/09-review/SKILL.md` 铁律 + `references/skeptical-acceptance.md` + `multi-round-revision.md` |
| `references/reviewer-templates.md` | `skills/09-review/references/...` + `templates/review-report-template.md` |
| `references/acceptance-gates-v10.md` | `skills/09-review/references/four-dimension-scoring.md` + `evidence-3-layer.md` |
| `references/multi-round-revision-protocol.md` | `skills/09-review/references/multi-round-revision.md` |

### Stage 4.5 Rot Scan

| V10 来源 | V11 蒸馏位置 |
|---------|------------|
| `agents/rot-detector.md` | `skills/10-rot-scan/SKILL.md` 铁律 1-6 |
| `references/process-rot-analysis.md` | `skills/10-rot-scan/references/rot-classification.md` |
| `scripts/proactive-scan.py` | V11 由 `scripts/proactive-scan.py` 重写 |
| `scripts/self-diagnose.py` | V11 由 `scripts/self-diagnose.py` 重写 |

### Stage 5 Accept

| V10 来源 | V11 蒸馏位置 |
|---------|------------|
| `references/artifact-lifecycle.md` | `skills/11-accept/references/archive-protocol.md` |
| `references/prd-integration-workflow.md` | `skills/11-accept/references/knowledge-extract.md` |
| `scripts/spec-purge.py` | V11 由 `scripts/spec-purge.py` 重写 |
| `scripts/spec-knowledge-extract.py` | V11 由 `scripts/spec-knowledge-extract.py` 重写 |

### Stage 6 Bug Fix

| V10 来源 | V11 蒸馏位置 |
|---------|------------|
| `agents/debugger.md` | `skills/12-bug-fix/SKILL.md` 铁律 1-8 |
| `references/debugger-methodology.md` | `skills/12-bug-fix/references/five-step-flow.md` + `six-layer-diagnosis.md` + `cross-layer-fix.md` |
| `references/bug-workflow.md` | `skills/12-bug-fix/references/bug-state-machine.md` |

### Stage 7 Project Health

| V10 来源 | V11 蒸馏位置 |
|---------|------------|
| `agents/project-health-auditor.md` | `skills/13-project-health/...` |
| `references/project-health-checklist.md` | `skills/13-project-health/references/four-dimension-check.md` |

---

## 部署动作

V11 部署前可删除：

- 本文件 `references/V10-distillation-source-map.md`（开发期 reference）
- 所有 `skills/*/anti-patterns/V10-battle-tested.md`（开发期反例吸收来源记录）

V11 部署后保留：

- `skills/*/references/*.md`（V10 内容已蒸馏进去，独立可用）
- `skills/*/anti-patterns/[01-09]-*.md`（V10 反例已蒸馏为 V11 反例，独立可用）

---

## 关联引用

- [SKILL.md](../../SKILL.md) — V11 总编排器
- V10 来源参考（开发期）: `../../fullstack4TraeV10/`（不部署）