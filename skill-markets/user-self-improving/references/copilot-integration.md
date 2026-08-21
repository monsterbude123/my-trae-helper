# GitHub Copilot Integration

GitHub Copilot **does not support hooks**. Activation is **manual** via
`.github/copilot-instructions.md` (per-repo) — note this is per-repo, NOT
truly user-scoped, which makes `user-self-improving` an awkward fit for
Copilot. If you use Copilot primarily, prefer `project-self-improving`.

## Setup (per-repo)

Create or update `.github/copilot-instructions.md`:

```markdown
# Project Instructions

## User Self-Improving (personal experience ledger)

After completing tasks that involved:
- Debugging non-obvious issues
- Discovering workarounds
- Learning project-specific patterns
- Resolving unexpected errors

Consider logging the learning to `~/.user-self-improving/.learnings/` (or
`$HOME/.user-self-improving/.learnings/` if global home is set) using
the format from the user-self-improving skill.

For high-value personal learnings, write to `~/.user-self-improving/SOUL.md`
(style) / `TOOLS.md` (machine gotchas) / `MEMORY.md` (long-term reflection).

Also review `~/.user-self-improving/.learnings/` for related entries
before starting a major task.
```

## Why Not a Better Fit?

| Aspect | Other agents | Copilot |
|--------|-------------|---------|
| Hook support | yes | **no** |
| Activation | event-driven | manual |
| User-level config | yes (`~/.trae-cn/`, `~/.claude/`) | **no** (per-repo only) |
| `hook-self-check.sh` result | INSTALLED | expected MISSING_CONFIG_FILE |

If you rely on Copilot for a workflow, you may want to use
`project-self-improving` inside the repo instead.

## Verification

`hook-self-check.sh` will return `MISSING_CONFIG_FILE` for Copilot. **This is
expected** — not a misconfiguration. Wrap the script if you want to suppress
non-zero exits when Copilot is the active agent.

## See Also

- [SKILL.md §13 Multi-Agent Matrix](../SKILL.md#13-multi-agent-matrix)
- [hook-self-check.md](hook-self-check.md) — why MISSING_CONFIG_FILE is
  expected for Copilot
- [../project-self-improving/](../project-self-improving/SKILL.md) — better
  fit for Copilot (per-repo `.learnings/`)