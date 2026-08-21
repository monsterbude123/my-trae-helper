# Claude Code Integration

Wire `user-self-improving` into Claude Code via the **native** hook config.
Default home: `$HOME/.user-self-improving/.learnings/`.

## Hook Config Location

| Path | Scope |
|------|-------|
| `~/.claude/settings.json` | **User-level (preferred for personal)** |
| `.claude/settings.json` | Project-level (committed, team-shared) |

For personal use, prefer **user-level** so the hook fires on every project.

## Recommended Configuration (User-Level)

```bash
mkdir -p ~/.claude
cat > ~/.claude/settings.json <<'JSON'
{
  "hooks": {
    "UserPromptSubmit": [
      {
        "matcher": "",
        "hooks": [
          { "type": "command",
            "command": "~/.claude/skills/user-self-improving/scripts/activator.sh" }
        ]
      }
    ],
    "PostToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          { "type": "command",
            "command": "~/.claude/skills/user-self-improving/scripts/error-detector.sh" }
        ]
      }
    ]
  }
}
JSON
```

## Install Snippet (One-Liner)

```bash
bash skill-markets/user-self-improving/scripts/install-snippet.sh claude-user \
  > ~/.claude/settings.json
```

## Verification

1. Restart Claude Code session.
2. Send any prompt.
3. Expect `<user-self-improving-reminder>` in context.
4. If absent, run `bash <skill-path>/scripts/hook-self-check.sh` to diagnose.

## Differences from Trae

| Aspect | Trae | Claude Code |
|--------|------|-------------|
| Config file | `.trae/hooks.json` | `.claude/settings.json` |
| Top-level wrapper | `{"version": 1, "hooks": {...}}` | `{"hooks": {...}}` |
| Path variable | `${workspaceFolder}` / `${userHome}` | absolute or `~`-prefixed |
| Event `SessionStart` | yes | no (use `UserPromptSubmit`) |
| Timeout field | optional | n/a |

## See Also

- [SKILL.md §3](../SKILL.md#3-hook-protocol-agent-native-not-invented)
- [trae-integration.md](trae-integration.md)
- [codex-integration.md](codex-integration.md) — same schema