# Learnings

> Cross-session experience ledger — corrections, knowledge gaps, best practices.

**Categories**: `correction` | `insight` | `knowledge_gap` | `best_practice`
**Areas**: `frontend` | `backend` | `infra` | `tests` | `docs` | `config`
**Statuses**: `pending` | `in_progress` | `resolved` | `wont_fix` | `promoted` | `promoted_to_skill`

## Status Definitions

| Status | Meaning |
|--------|---------|
| `pending` | Not yet addressed |
| `in_progress` | Actively being worked on |
| `resolved` | Issue fixed or knowledge integrated |
| `wont_fix` | Decided not to address (reason in `### Resolution` notes) |
| `promoted` | Elevated to `AGENTS.md`, `CLAUDE.md`, `.github/copilot-instructions.md`, or `.trae/rules/*.md` |
| `promoted_to_skill` | Extracted as a reusable skill (add `**Skill-Path**`) |

## Promotion Fields

When a learning is promoted, add a `**Promoted**` line to the header:

```markdown
**Status**: promoted
**Promoted**: AGENTS.md  (or CLAUDE.md / .github/copilot-instructions.md / .trae/rules/<topic>.md)
```

When extracted as a skill:

```markdown
**Status**: promoted_to_skill
**Skill-Path**: skill-markets/<skill-name>
```

## Example

```markdown
## [LRN-20260821-001] best_practice

**Logged**: 2026-08-21T10:30:00Z
**Priority**: high
**Status**: pending
**Area**: config

### Summary
Project uses pnpm not npm for package management

### Details
Attempted to run `npm install` but project uses pnpm workspaces. Lock file is
`pnpm-lock.yaml`, not `package-lock.json`.

### Suggested Action
Check for `pnpm-lock.yaml` or `pnpm-workspace.yaml` before assuming npm.
Use `pnpm install` for this project.

### Metadata
- Source: error
- Related Files: pnpm-lock.yaml, pnpm-workspace.yaml
- Tags: package-manager, pnpm, setup

---
```

See [references/examples.md](../references/examples.md) for the full set
(correction, knowledge gap, promoted-to-rule, promoted-to-skill).