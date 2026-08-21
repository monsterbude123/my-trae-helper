# TOOLS.md (personal)

> **Personal tool / environment gotchas** — opt-in. Captures quirks specific
> to this machine + workflow that don't belong in any project's `AGENTS.md`.
>
> See [SKILL.md §6](../SKILL.md#6-personal-workspace-files-opt-in) for the
> distinction.

## Usage

- **Write here:** machine-specific quirks ("WSL2 DNS takes 5s to resolve on
  this laptop", "this user's Python is at `/opt/homebrew/bin/python3`"),
  tool-specific workarounds ("always pass `--no-cache` to docker on this box").
- **Don't write here:** generic tool knowledge ("docker needs auth" — that's
  in `CLAUDE.md`), project-specific build steps (those go in `AGENTS.md`).

## Sections (suggested)

### Machine Quirks
<!-- This specific box's oddities -->

### Local Tool Paths
<!-- Where things actually live on this machine -->

### Recurring Workarounds
<!-- Patterns that work but shouldn't have to -->

### Tool-Specific Flags
<!-- Defaults you always set -->

---

> **Note:** This file is **not shared** via git. Keep it in
> `~/.user-self-improving/TOOLS.md` only.