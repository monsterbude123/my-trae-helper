# Skill Template

> Copy this file to `skill-markets/<skill-name>/SKILL.md` and fill in the
> sections marked `[FILL]`. Designed for the Agent Skills spec
> (https://agentskills.io/specification).

---

## SKILL.md Template

```markdown
---
name: [FILL-skill-name-lowercase-hyphens]
description: "[FILL-action verb]. Use when [FILL-trigger conditions]."
---

# [FILL-Skill Name]

[FILL-brief intro — problem this skill solves and origin]

## Quick Reference

| Situation | Action |
|-----------|--------|
| [FILL-trigger 1] | [FILL-action 1] |
| [FILL-trigger 2] | [FILL-action 2] |

## Background

[FILL-why this knowledge matters. What problems it prevents. Context from the original learning.]

## Solution

### Step-by-Step

1. [FILL-step 1]
2. [FILL-step 2]
3. [FILL-verification step]

### Code Example

\`\`\`[FILL-language]
[FILL-example code]
\`\`\`

## Common Variations

- **[FILL-variation A]**: [FILL-description + handling]
- **[FILL-variation B]**: [FILL-description + handling]

## Gotchas

- [FILL-warning / common mistake 1]
- [FILL-warning / common mistake 2]

## Related

- [FILL-link to related doc]
- [FILL-link to related skill]

## Source

Extracted from learning entry.

- **Learning ID**: [FILL-LRN-YYYYMMDD-XXX]
- **Original Category**: [FILL-correction | insight | knowledge_gap | best_practice]
- **Extraction Date**: [FILL-YYYY-MM-DD]
```

---

## Minimal Template

For skills that don't need all sections:

```markdown
---
name: [FILL-skill-name]
description: "[FILL-what + when]"
---

# [FILL-Skill Name]

[FILL-problem statement in one sentence]

## Solution

[FILL-direct solution with code/commands]

## Source

- Learning ID: [FILL-LRN-YYYYMMDD-XXX]
```

---

## Template with Scripts

For skills that ship executable helpers:

```markdown
---
name: [FILL-skill-name]
description: "[FILL-what + when]"
---

# [FILL-Skill Name]

[FILL-introduction]

## Quick Reference

| Command | Purpose |
|---------|---------|
| `./scripts/[FILL-helper].sh` | [FILL-what it does] |
| `./scripts/[FILL-validate].sh` | [FILL-what it does] |

## Usage

### Automated (Recommended)

\`\`\`bash
./scripts/[FILL-helper].sh [FILL-args]
\`\`\`

### Manual Steps

1. [FILL-step 1]
2. [FILL-step 2]

## Scripts

| Script | Description |
|--------|-------------|
| `scripts/[FILL-helper].sh` | [FILL-main utility] |
| `scripts/[FILL-validate].sh` | [FILL-validation checker] |

## Source

- Learning ID: [FILL-LRN-YYYYMMDD-XXX]
```

---

## Naming Conventions

- **Skill name**: lowercase, hyphens for spaces
  - Good: `docker-m1-fixes`, `api-timeout-patterns`
  - Bad:  `Docker_M1_Fixes`, `APITimeoutPatterns`
- **Description**: action verb + trigger
  - Good: "Handles Docker build failures on Apple Silicon. Use when builds fail with platform mismatch."
  - Bad:  "Docker stuff"

## Required Files

| File | Required | Notes |
|------|----------|-------|
| `SKILL.md` | yes | YAML frontmatter (name + description) + body |
| `scripts/` | no | Executable helpers, **cross-platform bash** preferred |
| `references/` | no | Detailed docs (split when SKILL.md > 350 lines) |
| `assets/` | no | Templates + boilerplate users copy |
| `agents/` | no | Sub-agents (multi-role pipelines only) |
| `README.md` | **NO** | Spec forbids README inside skill folder |

## Extraction Checklist

Before extraction:
- [ ] Learning is verified (`**Status**: resolved`)
- [ ] Solution is broadly applicable (not one-off)
- [ ] Content is complete (all needed context)
- [ ] Name follows kebab-case convention
- [ ] Description is concise but informative
- [ ] Quick Reference table is actionable
- [ ] Code examples are tested
- [ ] Source learning ID recorded

After extraction:
- [ ] Update original learning: `**Status**: promoted_to_skill` + `**Skill-Path**`
- [ ] Test skill by reading in a fresh session
- [ ] Run `scripts/hook-self-check.sh` to verify integration with active agent