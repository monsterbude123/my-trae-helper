# Product Teardown — Agent Ecosystem

> A 3-agent orchestrated pipeline for competitive product analysis and PRD generation.

---

## Agents

| Agent | Directory | Role | Trigger |
|-------|-----------|------|---------|
| **product-teardown** | [SKILL.md](file:///d:/workspace/my-trae-helper/product-teardown/skills/product-teardown/SKILL.md) | Orchestrator. Collects requirements, presents feature menu, confirms selections, delegates heavy work. | User says "analyze product X", "replicate Y", "competitive analysis" |
| **product-teardown-analyze** | [SKILL.md](file:///d:/workspace/my-trae-helper/product-teardown/skills/product-teardown-analyze/SKILL.md) | Deep analyzer. Receives product context, outputs 6-dimension structured analysis. | Called by orchestrator via `Task` tool |
| **product-teardown-prd** | [SKILL.md](file:///d:/workspace/my-trae-helper/product-teardown/skills/product-teardown-prd/SKILL.md) | PRD writer. Receives selected features + analysis, generates structured PRD. | Called by orchestrator via `Task` tool |

---

## Workflow

```
Phase 1: Info Collection ──→ Orchestrator (self)
Phase 2: Product Analysis  ──→ Task → product-teardown-analyze
Phase 3: Feature Menu       ──→ Orchestrator (self, stops for user)
Phase 4: User Confirmation  ──→ Orchestrator (self)
Phase 5: PRD Generation     ──→ Task → product-teardown-prd
```

---

## 6 Analysis Dimensions

| # | Dimension | What It Covers |
|---|-----------|----------------|
| 1 | Core Business Flow | User journey, key nodes, branch logic, exception handling |
| 2 | Feature Module Breakdown | By user role, by business domain, core/important/enhancement classification |
| 3 | UX & Interaction Design | Page architecture, interaction patterns, highlights & improvement points |
| 4 | Tech Architecture | Inferred tech stack, third-party dependencies, core technical challenges |
| 5 | Business Model & Growth | Monetization, growth mechanisms, conversion funnel |
| 6 | Differentiation & Moat | Core competitiveness, MVP must-haves, deferrable features |

---

## PRD Output

| Scope | Chapters | Use Case |
|-------|----------|----------|
| **Lite** | 1. Overview, 2. Feature Architecture, 3. Detailed Requirements | Quick dev handoff |
| **Full** | Lite + 4. Non-functional, 5. Tech Architecture, 6. Ops & Growth, 7. Iteration Plan | Complete project planning |

---

## Templates

| Template | Used By | Content |
|----------|---------|---------|
| `templates/menu.md` | [menu.md](file:///d:/workspace/my-trae-helper/product-teardown/skills/product-teardown/templates/menu.md) | Orchestrator (Phase 3) | Feature menu with checkboxes, complexity labels, version recommendations |
| `templates/prd-lite.md` | [prd-lite.md](file:///d:/workspace/my-trae-helper/product-teardown/skills/product-teardown/templates/prd-lite.md) | prd Agent | Chapters 1-3: overview, architecture, detailed requirements |
| `templates/prd-full.md` | [prd-full.md](file:///d:/workspace/my-trae-helper/product-teardown/skills/product-teardown/templates/prd-full.md) | prd Agent | Chapters 4-7: non-functional, tech, ops, iteration plan |

---

## Invocation

```
User: "Analyze Notion, I want to build a similar note-taking tool"
→ product-teardown skill auto-loads
```

Or explicit:
```
User: "Load product-teardown skill and analyze [Product]"
```

---

## Key Rules

1. Never skip the feature menu — wait for user selection before generating PRD
2. Heavy work always delegated — orchestrator never writes analysis or PRD itself
3. One phase per response — no cross-phase merging
4. Never fabricate data — mark uncertain items as `[待确认]` or `[TBD]`
5. Only write selected features into PRD Chapter 3
