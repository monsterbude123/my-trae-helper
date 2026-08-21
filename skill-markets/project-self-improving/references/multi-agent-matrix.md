# Multi-Agent Matrix

> 详细对比 4 个 agent 的 hook 配置格式 + 自动检测能力 + 接入成本。
> 主入口见 [SKILL.md §13](../SKILL.md)。

| Agent | Activation method | Auto-detect | Reference |
|-------|-------------------|-------------|-----------|
| Trae IDE | `.trae/hooks.json` (`SessionStart` + `UserPromptSubmit` + `PostToolUse`) | yes (`hook-self-check.sh`) | [trae-integration.md](trae-integration.md) |
| Claude Code | `.claude/settings.json` (`UserPromptSubmit` + `PostToolUse`) | yes | [claude-code-integration.md](claude-code-integration.md) |
| Codex CLI | `.codex/settings.json` (same as Claude Code) | yes | [codex-integration.md](codex-integration.md) |
| GitHub Copilot | `.github/copilot-instructions.md` (no hook runtime) | **no** (manual review) | [copilot-integration.md](copilot-integration.md) |

## Activation Decision Tree

```
Does the agent support event-driven hooks?
├── Yes → wire hook config (Trae / Claude / Codex)
│         └── run scripts/install-snippet.sh <agent> > <config-file>
└── No  → use instructions file only (Copilot)
          └── append snippet from scripts/install-snippet.sh copilot
              to .github/copilot-instructions.md

After installation:
  1. Restart the agent
  2. Run scripts/hook-self-check.sh
  3. Expect: <self-improving-hook-state>INSTALLED</self-improving-hook-state>
```

## Cost Comparison

| Agent | Setup time | Runtime overhead | Activation reliability |
|-------|-----------|-----------------|------------------------|
| Trae | ~2 min | ~80 tokens/reminder | high (hook-native) |
| Claude Code | ~2 min | ~80 tokens/reminder | high |
| Codex | ~2 min | ~80 tokens/reminder | high |
| Copilot | ~30 sec (instructions edit only) | 0 (no runtime hook) | low (manual review) |

## Cross-Project Strategy

For developers who work across many projects:

1. **Install globally** via `node bin/cli.mjs add project-self-improving -a trae-cn`.
2. The CLI puts scripts under `~/.trae-cn/skills/project-self-improving/scripts/`.
3. Reference scripts in your **project-level** `.trae/hooks.json` using absolute paths.
4. Use `$HOME/.self-improving-agent/.learnings/` (global mode) so logs survive
   project switches.

For project-specific teams:

1. Commit `.trae/hooks.json` to repo (after running `install-snippet.sh`).
2. Use `.learnings/` inside the repo (commit + team-shared).
3. Add `.learnings/*.md` to `.gitignore` if personal-noise only.

## See Also

- [SKILL.md §3 Hook Protocol](../SKILL.md#3-hook-protocol-agent-native-not-invented)
- [SKILL.md §13 Multi-Agent Matrix (entry point)](../SKILL.md#13-multi-agent-matrix)
- [hook-self-check.md](hook-self-check.md) — the mandatory self-check protocol
- [trae-integration.md](trae-integration.md) — Trae setup
- [claude-code-integration.md](claude-code-integration.md) — Claude Code setup
- [codex-integration.md](codex-integration.md) — Codex setup
- [copilot-integration.md](copilot-integration.md) — Copilot setup