# Trae IDE Integration

Wire `project-self-improving` into Trae IDE via the **native** Trae hook
mechanism (no custom protocol, no bootstrap injection).

## Hook Config Location

Trae reads hooks from **either** of these locations (project-level preferred):

| Path | Scope |
|------|-------|
| `.trae/hooks.json` | Project-level (committed, team-shared) |
| `~/.trae-cn/hooks.json` | User-level (private, all projects) |

Schema (Trae v3.5.66+):

```json
{
  "version": 1,
  "hooks": {
    "<EventName>": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "<absolute-or-workspaceRelative-path>",
            "timeout": 5000
          }
        ]
      }
    ]
  }
}
```

Supported `EventName`s for this skill: `SessionStart`, `UserPromptSubmit`,
`PostToolUse`, `Stop`.

## Recommended Configuration

Minimal (reminder only — recommended starting point):

```bash
mkdir -p .trae
cat > .trae/hooks.json <<'JSON'
{
  "version": 1,
  "hooks": {
    "SessionStart": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "${workspaceFolder}/skill-markets/project-self-improving/scripts/hook-self-check.sh",
            "timeout": 5000
          }
        ]
      }
    ],
    "UserPromptSubmit": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "${workspaceFolder}/skill-markets/project-self-improving/scripts/activator.sh",
            "timeout": 5000
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
cat > .trae/hooks.json <<'JSON'
{
  "version": 1,
  "hooks": {
    "SessionStart": [
      {
        "matcher": "",
        "hooks": [
          { "type": "command",
            "command": "${workspaceFolder}/skill-markets/project-self-improving/scripts/hook-self-check.sh",
            "timeout": 5000 }
        ]
      }
    ],
    "UserPromptSubmit": [
      {
        "matcher": "",
        "hooks": [
          { "type": "command",
            "command": "${workspaceFolder}/skill-markets/project-self-improving/scripts/activator.sh",
            "timeout": 5000 }
        ]
      }
    ],
    "PostToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          { "type": "command",
            "command": "${workspaceFolder}/skill-markets/project-self-improving/scripts/error-detector.sh",
            "timeout": 5000 }
        ]
      }
    ]
  }
}
JSON
```

> The `${workspaceFolder}` token is replaced by Trae at runtime with the
> absolute path of the workspace root. Relative paths are also accepted but
> less portable across projects.

## Install Snippet (One-Liner)

If you have the skill installed via the local package manager, run:

```bash
node skill-markets/project-self-improving/scripts/install-snippet.sh trae \
  > .trae/hooks.json
```

Otherwise copy the snippet above verbatim.

## Verification

1. Restart Trae IDE (or `/reload` if available).
2. Open a chat and send any message.
3. You should see a brief `<self-improving-reminder>` block injected into the
   context. If not, run `bash scripts/hook-self-check.sh` to diagnose.

## Troubleshooting

| Symptom | Cause | Fix |
|---------|-------|-----|
| No reminder fires | Hook not registered | Run `hook-self-check.sh` — should report `MISSING_CONFIG_FILE` or `MISSING_HOOK_ENTRY` |
| Reminder fires but content is empty | `activator.sh` not executable | `chmod +x scripts/activator.sh` |
| `command not found: detect-python.sh` | Scripts not on PATH | Scripts in `scripts/` use **relative** paths to `detect-python.sh` — keep them co-located |
| Hook fails on Windows | Path separator or shell issue | Trae translates paths; `bash` is required for these scripts — verify the IDE's shell setting |

## See Also

- [SKILL.md §3 Hook Protocol](../SKILL.md#3-hook-protocol-agent-native-not-invented)
- [hook-self-check.md](hook-self-check.md) — the mandatory self-check protocol
- [claude-code-integration.md](claude-code-integration.md) — equivalent for
  Claude Code (different config location, similar shape)