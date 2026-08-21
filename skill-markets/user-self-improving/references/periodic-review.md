# Periodic Review

> Main entry: [SKILL.md §12](../SKILL.md#12-best-practices).
> Monthly review of `~/.user-self-improving/.learnings/` + personal workspace files.

---

## When to Review

- **Weekly** (active dev): catch recurring patterns (See Also link density)
- **Monthly**: promote stale entries, prune noise
- **Before major task**: check for relevant prior learnings
- **Quarterly**: review `SOUL.md` / `TOOLS.md` / `MEMORY.md` size — keep small

## Quick Status Check Commands

```bash
# Count pending items
grep -h "Status\*\*: pending" ~/.user-self-improving/.learnings/*.md | wc -l

# List pending high-priority items
grep -B5 "Priority\*\*: high" ~/.user-self-improving/.learnings/*.md | grep "^## \["

# Find recurring issues (3+ See Also links)
for f in ~/.user-self-improving/.learnings/*.md; do
  n=$(grep -c "See Also:" "$f")
  [ "$n" -ge 3 ] && echo "$f: $n See Also"
done

# Find learnings not promoted after 30 days
find ~/.user-self-improving/.learnings -name "*.md" -mtime +30 -exec grep -l "Status\*\*: pending" {} \;

# Size check on personal workspace files
wc -l ~/.user-self-improving/{SOUL,TOOLS,MEMORY}.md
```

## Review Actions

| Action | When | Example |
|--------|------|---------|
| **Resolve** | Issue is fixed | `**Status**: pending` → `**Status**: resolved`, add `### Resolution` |
| **Promote to SOUL.md** | Personal style preference | Move from `LEARNINGS.md` to `~/.user-self-improving/SOUL.md` |
| **Promote to TOOLS.md** | Machine-specific quirk | Move from `ERRORS.md` to `~/.user-self-improving/TOOLS.md` |
| **Promote to MEMORY.md** | Long-term reflection | Move to `~/.user-self-improving/MEMORY.md` |
| **Link** | Similar entry exists | Add `**See Also**: LRN-YYYYMMDD-XXX` |
| **Escalate** | 3+ `See Also` links | Pattern is recurring — promote to rule or extract as skill |
| **Extract to skill** | Recurring + verified + broadly applicable | See [`assets/SKILL-TEMPLATE.md`](../assets/SKILL-TEMPLATE.md) |
| **Drop** | Won't fix / out of scope | `**Status**: wont_fix`, add reason in `### Resolution` |

## Review Cadence

| Cadence | Use case |
|---------|----------|
| Per-session (before major task) | Avoid re-solving known problems |
| Weekly (active dev) | Catch recurring patterns (See Also link density) |
| Monthly | Promote stale entries to personal workspace files |
| Quarterly | Prune `SOUL.md` / `TOOLS.md` / `MEMORY.md` to essentials |

## See Also

- [SKILL.md §12 Best Practices](../SKILL.md#12-best-practices)
- [SKILL.md §6 Personal Workspace Files](../SKILL.md#6-personal-workspace-files-opt-in)