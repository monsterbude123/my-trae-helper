# Claude Code Integration

Wire `project-self-improving` into Claude Code via the **native** Claude Code
hook config (`.claude/settings.json`).

## Hook Config Location

| Path | Scope |
|------|-------|
| `.claude/settings.json` (in project root) | Project-level (committed, team-shared) |
| `~/.claude/settings.json` | User-level (private, all projects) |

Schema:

```json
{
  "hooks": {
    "UserPromptSubmit": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "<absolute-or-relative-path>"
          }
        ]
      }
    ]
  }
}
```

Supported events for this skill: `UserPromptSubmit`, `PostToolUse`, `Stop`.

## Recommended Configuration

Minimal:

```bash
mkdir -p .claude
cat > .claude/settings.json <<'JSON'
{
  "hooks": {
    "UserPromptSubmit": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "${workspaceFolder}/skill-markets/project-self-improving/scripts/activator.sh"
          }
        ]
      }
    ]
  }
}
JSON
```

Full (with error capture):

```bash
cat > .claude/settings.json <<'JSON'
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
node skill-markets/project-self-improving/scripts/install-snippet.sh claude-code \
  > .claude/settings.json
```

## Verification

1. Restart Claude Code session.
2. Send any prompt.
3. Look for `<self-improving-reminder>` in the context. If absent, run
   `bash scripts/hook-self-check.sh` to diagnose.

## Differences from Trae

| Aspect | Trae | Claude Code |
|--------|------|-------------|
| Config file | `.trae/hooks.json` | `.claude/settings.json` |
| Top-level wrapper | `{"version": 1, "hooks": {...}}` | `{"hooks": {...}}` |
| Path variable | `${workspaceFolder}` | `${workspaceFolder}` (or relative) |
| Event `SessionStart` | ✅ | ❌ (use `UserPromptSubmit`) |
| Timeout field | optional | n/a |

## See Also

- [SKILL.md §3](../SKILL.md#3-hook-protocol-agent-native-not-invented)
- [trae-integration.md](trae-integration.md)
- [codex-integration.md](codex-integration.md) — Codex CLI uses the same schema