# Multi-Agent Matrix

> Detailed comparison of 4 agents' hook configs + activation costs + cross-machine
> strategy. Main entry: [SKILL.md §11](../SKILL.md#11-multi-agent-matrix).

| Agent | Hook config (personal) | Hook config (project) | Auto-detect | Reference |
|-------|------------------------|----------------------|-------------|-----------|
| Trae IDE | `~/.trae-cn/hooks.json` | `.trae/hooks.json` | yes | [trae-integration.md](trae-integration.md) |
| Claude Code | `~/.claude/settings.json` | `.claude/settings.json` | yes | [claude-code-integration.md](claude-code-integration.md) |
| Codex CLI | `~/.codex/settings.json` | `.codex/settings.json` | yes | [codex-integration.md](codex-integration.md) |
| GitHub Copilot | (no user-level config) | `.github/copilot-instructions.md` | **no** | [copilot-integration.md](copilot-integration.md) |

## Activation Decision Tree

```
Use user-self-improving for personal cross-project capture?
?
├── Yes — and I have a hook-supporting agent (Trae/Claude/Codex)
│         └── wire hook at user-level (`~/.<agent>/hooks.json`)
│             └── scripts/install-snippet.sh <agent>-user > ~/.config
?
└── No — I primarily use Copilot (no hooks)
          └── use project-self-improving instead (per-repo .learnings/)
              └── see ../project-self-improving/references/copilot-integration.md
```

## Cost Comparison

| Agent | Setup time | Runtime overhead | Activation reliability |
|-------|-----------|-----------------|------------------------|
| Trae | ~2 min | ~80 tokens/reminder | high (hook-native) |
| Claude Code | ~2 min | ~80 tokens/reminder | high |
| Codex | ~2 min | ~80 tokens/reminder | high |
| Copilot | N/A (no hooks) | 0 | low (manual review) |

## Cross-Machine Strategy

For users who work across many machines:

1. **Install globally** via `node bin/cli.mjs add user-self-improving -a trae-cn`.
2. The CLI puts scripts under `~/.trae-cn/skills/user-self-improving/scripts/`.
3. Reference scripts in `~/.trae-cn/hooks.json` using `${userHome}` or absolute paths.
4. Use `$HOME/.user-self-improving/.learnings/` (default) so logs survive machine
   migration.
5. Optionally sync `~/.user-self-improving/` via a private dotfiles repo.

## Coexistence with `project-self-improving`

Both skills can coexist, but you should choose the **default home** to avoid
double-logging:

| Scenario | Setup |
|----------|-------|
| Project-first (team-shared learnings) | `project-self-improving` ON, `user-self-improving` OFF |
| Personal-first (cross-project private) | `user-self-improving` ON, `project-self-improving` OFF |
| Both (use distinct homes) | `project-self-improving` → `<repo>/.learnings/`, `user-self-improving` → `$HOME/.user-self-improving/.learnings/` |

## See Also

- [SKILL.md §10 Relationship with project-self-improving](../SKILL.md#10-relationship-with-project-self-improving)
- [hook-self-check.md](hook-self-check.md) — self-check protocol
- [trae-integration.md](trae-integration.md) / [claude-code-integration.md](claude-code-integration.md) / [codex-integration.md](codex-integration.md) / [copilot-integration.md](copilot-integration.md)