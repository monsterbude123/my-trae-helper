# Codex CLI Integration

Wire `project-self-improving` into Codex CLI. Codex uses the **same hook
schema as Claude Code** (`.codex/settings.json`), so this is intentionally
short — see [claude-code-integration.md](claude-code-integration.md) for the
detailed schema.

## Hook Config Location

| Path | Scope |
|------|-------|
| `.codex/settings.json` (in project root) | Project-level (committed) |
| `~/.codex/settings.json` | User-level (private) |

## Recommended Configuration

```bash
mkdir -p .codex
cat > .codex/settings.json <<'JSON'
{
  "hooks": {
    "UserPromptSubmit": [
      {
        "matcher": "",
        "hooks": [
          { "type": "command",
            "command": "${workspaceFolder}/skill-markets/project-self-improving/scripts/activator.sh" }
        ]
      }
    ],
    "PostToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          { "type": "command",
            "command": "${workspaceFolder}/skill-markets/project-self-improving/scripts/error-detector.sh" }
        ]
      }
    ]
  }
}
JSON
```

## Install Snippet (One-Liner)

```bash
node skill-markets/project-self-improving/scripts/install-snippet.sh codex \
  > .codex/settings.json
```

## Verification

1. Restart Codex session.
2. Send any prompt.
3. Look for `<self-improving-reminder>` in the context.

## See Also

- [claude-code-integration.md](claude-code-integration.md) — same schema
- [SKILL.md §3](../SKILL.md#3-hook-protocol-agent-native-not-invented)