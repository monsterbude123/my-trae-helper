# Learnings

> Personal, machine-scoped cross-session experience ledger — corrections,
> knowledge gaps, best practices. Survives repo clones / branch switches.

**Categories**: `correction` | `insight` | `knowledge_gap` | `best_practice`
**Areas**: `frontend` | `backend` | `infra` | `tests` | `docs` | `config`
**Statuses**: `pending` | `in_progress` | `resolved` | `wont_fix` | `promoted`

## Status Definitions

| Status | Meaning |
|--------|---------|
| `pending` | Not yet addressed |
| `in_progress` | Actively being worked on |
| `resolved` | Issue fixed or knowledge integrated |
| `wont_fix` | Decided not to address (reason in `### Resolution` notes) |
| `promoted` | Elevated to `SOUL.md` / `TOOLS.md` / `MEMORY.md` (personal) — or to a project-level rule via `project-self-improving` |

## Promotion Fields

When a learning is promoted, add a `**Promoted**` line:

```markdown
**Status**: promoted
**Promoted**: SOUL.md  (or TOOLS.md / MEMORY.md / AGENTS.md / CLAUDE.md)
```

## Example

```markdown
## [LRN-20260821-001] best_practice

**Logged**: 2026-08-21T10:30:00Z
**Priority**: high
**Status**: pending
**Area**: config

### Summary
Always use `pnpm` not `npm` for this user's projects

### Details
This user has pnpm-lock.yaml on disk and refuses to use npm install.
Switching to pnpm reduced install time by 40%.

### Suggested Action
Before any package install, check for pnpm-lock.yaml. Use pnpm install.

### Metadata
- Source: user_feedback
- Related Files: pnpm-lock.yaml
- Tags: package-manager, pnpm, personal-pref

---
```

See [references/examples.md](../references/examples.md) for the full set.