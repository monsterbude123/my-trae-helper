# Errors

> Command / tool / API failures captured across sessions.

**Areas**: `frontend` | `backend` | `infra` | `tests` | `docs` | `config`
**Statuses**: `pending` | `in_progress` | `resolved` | `wont_fix`

## Status Definitions

| Status | Meaning |
|--------|---------|
| `pending` | Not yet addressed |
| `in_progress` | Actively being worked on |
| `resolved` | Issue fixed (add `### Resolution` with commit/PR ref) |
| `wont_fix` | Decided not to address (reason in `### Resolution`) |

## Example

```markdown
## [ERR-20260821-A3F] docker_build

**Logged**: 2026-08-21T09:15:00Z
**Priority**: high
**Status**: pending
**Area**: infra

### Summary
Docker build fails on Apple Silicon due to platform mismatch

### Error
```
error: failed to solve: python:3.11-slim: no match for platform linux/arm64
```

### Context
- Command: `docker build -t myapp .`
- Dockerfile uses `FROM python:3.11-slim`
- Running on Apple Silicon (M1/M2)

### Suggested Fix
Add platform flag: `docker build --platform linux/amd64 -t myapp .`
Or update Dockerfile: `FROM --platform=linux/amd64 python:3.11-slim`

### Metadata
- Reproducible: yes
- Related Files: Dockerfile

---
```

See [references/examples.md](../references/examples.md) for more.