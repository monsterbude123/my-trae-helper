# Codex CLI Integration

Wire `user-self-improving` into Codex CLI. Codex uses the **same hook
schema as Claude Code** (`.codex/settings.json`).

## Hook Config Location

| Path | Scope |
|------|-------|
| `~/.codex/settings.json` | **User-level (preferred for personal)** |
| `.codex/settings.json` | Project-level (committed) |

## Recommended Configuration (User-Level)

```bash
mkdir -p ~/.codex
cat > ~/.codex/settings.json <<'JSON'
{
  "hooks": {
    "UserPromptSubmit": [
      {
        "matcher": "",
        "hooks": [
          { "type": "command",
            "command": "~/.codex/skills/user-self-improving/scripts/activator.sh" }
        ]
      }
    ],
    "PostToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          { "type": "command",
            "command": "~/.codex/skills/user-self-improving/scripts/error-detector.sh" }
        ]
      }
    ]
  }
}
JSON
```

## Install Snippet (One-Liner)

```bash
bash skill-markets/user-self-improving/scripts/install-snippet.sh codex-user \
  > ~/.codex/settings.json
```

## See Also

- [claude-code-integration.md](claude-code-integration.md) — same schema
- [SKILL.md §3](../SKILL.md#3-hook-protocol-agent-native-not-invented)