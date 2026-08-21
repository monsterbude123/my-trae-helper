# Periodic Review

> 主入口: [SKILL.md §12](../SKILL.md#12-periodic-review)。
> 定期审查 `.learnings/` 时使用的命令清单 + 操作清单。

---

## When to Review

- Before starting a new major task
- After completing a feature
- When working in an area with past learnings
- Weekly during active development

## Quick Status Check Commands

```bash
# Count pending items
grep -h "Status\*\*: pending" .learnings/*.md | wc -l

# List pending high-priority items
grep -B5 "Priority\*\*: high" .learnings/*.md | grep "^## \["

# Find learnings for a specific area
grep -l "Area\*\*: backend" .learnings/*.md

# Find recurring issues (3+ See Also links)
for f in .learnings/*.md; do
  n=$(grep -c "See Also:" "$f")
  [ "$n" -ge 3 ] && echo "$f: $n See Also"
done

# Find learnings not promoted after 30 days
find .learnings -name "*.md" -mtime +30 -exec grep -l "Status\*\*: pending" {} \;
```

## Review Actions

After running the commands above, take these actions:

| Action | When | Example |
|--------|------|---------|
| **Resolve** | Issue is fixed in code | `**Status**: pending` → `**Status**: resolved`, add `### Resolution` block |
| **Promote** | Learning is broadly applicable | Move to `AGENTS.md` / `CLAUDE.md` / `copilot-instructions.md` / `.trae/rules/<topic>.md` (see [SKILL.md §6](../SKILL.md#6-promotion-targets)) |
| **Link** | Similar entry exists | Add `**See Also**: LRN-YYYYMMDD-XXX` |
| **Escalate** | 3+ `See Also` links | Likely a missing rule — create a rule, not a learning |
| **Extract to skill** | Recurring + verified + broadly applicable | See [assets/SKILL-TEMPLATE.md](../assets/SKILL-TEMPLATE.md) |
| **Drop** | Won't fix / out of scope | `**Status**: wont_fix`, add reason in `### Resolution` |

## Review Cadence

| Cadence | Use case |
|---------|----------|
| Per-session (before major task) | Avoid re-solving known problems |
| Per-feature (after ship) | Capture learnings while context is fresh |
| Weekly | Catch recurring patterns (See Also link density) |
| Monthly | Promote stale learnings to rules or skills |

## See Also

- [SKILL.md §12 Periodic Review](../SKILL.md#12-periodic-review)
- [SKILL.md §6 Promotion Targets](../SKILL.md#6-promotion-targets)
- [assets/SKILL-TEMPLATE.md](../assets/SKILL-TEMPLATE.md) §"Extraction Checklist"