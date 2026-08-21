# Errors

> Personal log of tool / API / command failures. Captures quirks specific to
> this user's machine + workflow (see also `TOOLS.md` for long-term tool gotchas).

**Statuses**: `pending` | `in_progress` | `resolved` | `wont_fix`

## Example

```markdown
## [ERR-20260821-A3F] docker_build

**Logged**: 2026-08-21T09:15:00Z
**Priority**: high
**Status**: pending
**Area**: infra

### Summary
Docker build fails on this M2 MacBook

### Error
```
error: failed to solve: python:3.11-slim: no match for platform linux/arm64
```

### Context
- Command: `docker build -t myapp .`
- Machine: MacBook Air M2 (ARM64)
- First seen: 2026-08-21

### Suggested Fix
Add platform flag: `docker build --platform linux/amd64 -t myapp .`
Or use ARM-compatible base image.

### Metadata
- Reproducible: yes (this machine)
- Related Files: Dockerfile
- Tags: docker, arm64, machine-specific

---
```

See [references/examples.md](../references/examples.md) for more.