# Best Practices

> Main entry: [SKILL.md §12](../SKILL.md#12-best-practices).
> 10 operating disciplines for personal, machine-scoped experience capture.

---

## §1 Writing Discipline

1. **Log immediately** — context is freshest right after the issue.
2. **Be specific** — future you (or another agent) must understand without
   original chat.
3. **Include reproduction steps** — especially for ERR entries.
4. **Link related files** — makes fixes easier.
5. **Suggest concrete fixes** — not just "investigate".
6. **Use consistent categories** — enables filtering.

## §2 Promotion Discipline

7. **Promote to the right place:**
   - Cross-machine personal pattern → `~/.user-self-improving/SOUL.md` /
     `TOOLS.md` / `MEMORY.md`
   - Project-shared pattern → `AGENTS.md` / `CLAUDE.md` /
     `copilot-instructions.md` (via `project-self-improving`)
   - Generic best practice → extract as new skill (see
     [`assets/SKILL-TEMPLATE.md`](../assets/SKILL-TEMPLATE.md))
8. **Don't bind to a single agent** — `.learnings/` is portable. Only the
   hook snippet is agent-specific.

## §3 Operational Discipline

9. **Self-check before complaining** — if a hook didn't fire, run
   `scripts/hook-self-check.sh` before assuming the skill is broken.
10. **Review monthly** — stale entries lose value.

## §4 Anti-Patterns (10 + 1)

| # | Anti-pattern | Consequence |
|---|--------------|-------------|
| 1 | Don't write `.learnings/` and just edit `AGENTS.md` to dump experience | `AGENTS.md` bloat + context overflow |
| 2 | Promote entries to `SOUL.md` that are actually team conventions | Knowledge pollution (project rules belong in `AGENTS.md`) |
| 3 | Install the skill but skip `hook-self-check.sh` | Hook misconfig silently fails — user never knows |
| 4 | Push `~/.user-self-improving/` to a public repo | Personal data leaks |
| 5 | 3+ `See Also` links without promoting to rule/skill | Same mistake keeps recurring |
| 6 | Install both `project-self-improving` AND `user-self-improving` with overlapping homes | Double-logging; entries appear in both files |
| 7 | `**Status**: promoted` without `**Promoted**: <file>` | Cannot trace promotion target |
| 8 | Mark `**Status**: resolved` without writing reproduction | Next time can't repro the fix |
| 9 | Let `add-all` install both skills without warning the user | User may not realize both are writing to `.learnings/` |
| 10 | Copy someone else's `.learnings/` into your home without scrubbing | Their private data in your files |
| 11 | Use `SOUL.md` to dump project-specific decisions | Belongs in `AGENTS.md` / `.trae/rules/<topic>.md`, not personal style |

## §5 See Also

- [SKILL.md §12 Best Practices](../SKILL.md#12-best-practices)
- [SKILL.md §6 Personal Workspace Files](../SKILL.md#6-personal-workspace-files-opt-in)
- [references/periodic-review.md](periodic-review.md)
- [skill-markets/agent-dev-control-kit/references/traps.md](../../agent-dev-control-kit/references/traps.md) — `self-improvement` section deep anti-patterns