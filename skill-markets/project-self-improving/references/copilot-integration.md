# GitHub Copilot Integration

GitHub Copilot **does not support hooks**. Activation is **manual** via
`.github/copilot-instructions.md`. The `hook-self-check.sh` script will
report `MISSING_CONFIG_FILE` for Copilot, which is expected — Copilot
agents should perform the review manually at session end (or use a
session-start reminder via instructions file).

## Setup

Create or update `.github/copilot-instructions.md`:

```markdown
# Project Instructions

## Self-Improvement (project-self-improving skill)

After completing tasks that involved:
- Debugging non-obvious issues
- Discovering workarounds
- Learning project-specific patterns
- Resolving unexpected errors

Consider logging the learning to `.learnings/` (or
`$HOME/.self-improving-agent/.learnings/` if global mode is active) using
the format from the project-self-improving skill.

For high-value learnings that would benefit other sessions, consider
**skill extraction** (see
`skill-markets/project-self-improving/assets/SKILL-TEMPLATE.md`).

Also review `.learnings/` for related issues before starting a major task.
```

## Optional: Use Copilot Chat Trigger Phrases

In Copilot Chat, prompt explicitly:

- "Log this to .learnings/"
- "Create a skill from this solution"
- "Check .learnings/ for related issues"

## Verification

Because Copilot has no hook runtime, `hook-self-check.sh` will return
`MISSING_CONFIG_FILE`. This is the **expected** state for Copilot and
should not be treated as a misconfiguration. The script's exit code is
non-zero in this state, so guard scripts that wrap it must check the
copilot-specific override (see `hook-self-check.sh` source).

## Differences from Trae / Claude Code / Codex

| Aspect | Trae / Claude / Codex | Copilot |
|--------|----------------------|---------|
| Hook support | yes | **no** |
| Activation | event-driven | **manual** |
| Self-check script | reports `INSTALLED` | reports `MISSING_CONFIG_FILE` (expected) |
| Reminder mechanism | event injection | instructions file only |

## See Also

- [SKILL.md §13 Multi-Agent Matrix](../SKILL.md#13-multi-agent-matrix)
- [hook-self-check.md](hook-self-check.md) — why `MISSING_CONFIG_FILE` is
  expected for Copilot