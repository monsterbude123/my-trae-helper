# Hook Self-Check Protocol

Every agent that loads `project-self-improving` **must** verify its hook
is installed. This document explains why and how.

## Why a Self-Check?

The legacy `self-improving-agent` skill suffered from three recurring
issues (see `skill-markets/agent-dev-control-kit/references/traps.md`,
"self-improvement" section):

1. **Silent failure** — hooks installed but pointing at the wrong path;
   no reminder ever fires; user assumes the skill is broken.
2. **Wrong config file** — Trae expects `.trae/hooks.json`, Claude Code
   expects `.claude/settings.json`; users paste the wrong one and nothing
   happens.
3. **No remediation message** — when the hook doesn't fire, the user has
   no idea whether the script is broken, the path is wrong, or the event
   is not supported.

The self-check is the **mandatory, session-start probe** that reports
one of three outcomes and prints a single-line remediation block.

## Protocol

```
On session start:
  1. Run scripts/hook-self-check.sh
  2. Read its stdout (single-line result)
  3. Surface result to user if not INSTALLED
```

The script probes in this fixed order:

1. `.trae/hooks.json` — Trae IDE (highest priority in this market)
2. `.claude/settings.json` — Claude Code
3. `.codex/settings.json` — Codex CLI
4. `.github/copilot-instructions.md` — Copilot (manual; expected MISSING_CONFIG_FILE)

For each file, it greps for either:
- The literal path of any script in `scripts/` (e.g. `scripts/activator.sh`)
- The literal string `project-self-improving`

If **any** match is found, the script reports `INSTALLED` and exits 0.

If **no** config file exists, it reports `MISSING_CONFIG_FILE` (exit 1)
and prints the install-snippet command for the most likely agent.

If a config file exists but contains no reference, it reports
`MISSING_HOOK_ENTRY` (exit 1) and points the user to the relevant
`references/<agent>-integration.md` section.

## Self-Check Output Format

```
<self-improving-hook-state>STATE</self-improving-hook-state>
```

States:
- `INSTALLED` — green path; no action needed.
- `MISSING_CONFIG_FILE` — no config file; run `install-snippet.sh`.
- `MISSING_HOOK_ENTRY` — config exists but no hook; merge snippet manually.

When state is not `INSTALLED`, the script also prints a remediation
block to stderr:

```
[self-improving] hook not installed
  remediation:
    bash skill-markets/project-self-improving/scripts/install-snippet.sh <agent>
  agents: trae (default), claude-code, codex, copilot
```

Agents must surface this block in chat (not silently suppress).

## Cross-Platform

`hook-self-check.sh` uses only POSIX sh + `grep` + `sed`. It is
cross-platform (Linux / macOS / Git Bash on Windows). It does NOT
require Python or Node.

## Script Source

See `scripts/hook-self-check.sh` for the implementation. It is ~50
lines, single file, no dependencies.

## When to Re-Run

| Trigger | Action |
|---------|--------|
| Session start | Run once |
| User reports reminder didn't fire | Run on demand |
| Config file edited by hand | Run to verify |
| New agent installed alongside | Run to verify cross-detection |
| `install-snippet.sh` invoked | Re-run after to verify |

## See Also

- [SKILL.md §4](../SKILL.md#4-mandatory-hook-self-check-new-in-v10)
- [trae-integration.md](trae-integration.md) — Trae-specific setup
- [claude-code-integration.md](claude-code-integration.md) — Claude Code setup
- [codex-integration.md](codex-integration.md) — Codex setup
- [copilot-integration.md](copilot-integration.md) — Copilot setup (expected MISSING)