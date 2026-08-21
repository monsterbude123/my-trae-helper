# Hook Self-Check Protocol

> Same protocol as `project-self-improving`. Documented separately so this
> skill is self-contained.

## Why a Self-Check?

Without a self-check, three failure modes are silent:

1. **Hook installed but pointing at the wrong path** — no reminder ever
   fires; user assumes the skill is broken.
2. **Wrong config file** — Trae expects `.trae/hooks.json`, Claude Code
   expects `.claude/settings.json`; users paste the wrong one and nothing
   happens.
3. **No remediation message** — when the hook doesn't fire, the user has
   no idea whether the script is broken, the path is wrong, or the event
   is not supported.

The self-check is the **mandatory session-start probe** that reports one of
three outcomes and prints a single-line remediation block.

## Protocol

```
On session start:
  1. Run scripts/hook-self-check.sh
  2. Read its stdout (single-line result)
  3. Surface result to user if not INSTALLED
```

The script probes in this fixed order:

1. `~/.trae-cn/hooks.json` — Trae user-level (highest priority for personal use)
2. `.trae/hooks.json` — Trae project-level
3. `~/.claude/settings.json` — Claude Code user-level
4. `.claude/settings.json` — Claude Code project-level
5. `~/.codex/settings.json` — Codex user-level
6. `.codex/settings.json` — Codex project-level
7. `~/.user-self-improving/SOUL.md` — fallback "is installed at all" probe
   (if any of the SOUL/TOOLS/MEMORY workspace files exist, the user has
   intentionally set up the skill)

For each file, it greps for either:
- The literal path of any script in `scripts/` (e.g. `scripts/activator.sh`)
- The literal string `user-self-improving`

If **any** match is found, the script reports `INSTALLED` and exits 0.

## Self-Check Output Format

```
<user-self-improving-hook-state>STATE</user-self-improving-hook-state>
```

States:
- `INSTALLED` — green path; no action needed.
- `MISSING_CONFIG_FILE` — no config file; run `install-snippet.sh <agent>`.
- `MISSING_HOOK_ENTRY` — config exists but no hook; merge snippet manually.

When state is not `INSTALLED`, the script also prints a remediation block
to stderr:

```
[user-self-improving] hook not installed
  remediation:
    bash skill-markets/user-self-improving/scripts/install-snippet.sh <agent>
  agents: trae-user (default) | trae-project | claude-user | claude-project | codex-user | codex-project | copilot (manual)
```

Agents must surface this block in chat.

## Cross-Platform

`hook-self-check.sh` uses only POSIX sh + `grep` + `sed`. Cross-platform
(Linux / macOS / Git Bash on Windows). Does NOT require Python or Node.

## When to Re-Run

| Trigger | Action |
|---------|--------|
| Session start | Run once |
| User reports reminder didn't fire | Run on demand |
| Config file edited by hand | Run to verify |
| New agent installed alongside | Run to verify cross-detection |
| `install-snippet.sh` invoked | Re-run after to verify |

## See Also

- [SKILL.md §4](../SKILL.md#4-mandatory-hook-self-check)
- [trae-integration.md](trae-integration.md)
- [claude-code-integration.md](claude-code-integration.md)
- [codex-integration.md](codex-integration.md)
- [copilot-integration.md](copilot-integration.md)