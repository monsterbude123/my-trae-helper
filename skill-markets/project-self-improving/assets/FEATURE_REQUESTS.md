# Feature Requests

> User-stated capability gaps. Each entry = one concrete missing capability.

**Areas**: `frontend` | `backend` | `infra` | `tests` | `docs` | `config`
**Statuses**: `pending` | `in_progress` | `resolved` | `wont_fix`
**Complexity**: `simple` | `medium` | `complex`

## Status Definitions

| Status | Meaning |
|--------|---------|
| `pending` | Not yet addressed |
| `in_progress` | Actively being worked on |
| `resolved` | Capability shipped (add `### Resolution` with commit/PR ref) |
| `wont_fix` | Decided not to address (reason in `### Resolution`) |

## Example

```markdown
## [FEAT-20260821-001] export_to_csv

**Logged**: 2026-08-21T16:45:00Z
**Priority**: medium
**Status**: pending
**Area**: backend

### Requested Capability
Export analysis results to CSV format

### User Context
User runs weekly reports and needs to share results with non-technical
stakeholders in Excel. Currently copies output manually.

### Complexity Estimate
simple

### Suggested Implementation
Add `--output csv` flag to the analyze command. Use standard csv module.
Could extend existing `--output json` pattern.

### Metadata
- Frequency: recurring
- Related Features: analyze command, json output

---
```

See [references/examples.md](../references/examples.md) for more.