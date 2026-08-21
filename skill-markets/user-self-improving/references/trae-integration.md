# Trae IDE Integration

Wire `user-self-improving` into Trae IDE via the **native** Trae hook
mechanism. Default home: `$HOME/.user-self-improving/.learnings/`. Override
with `--home <path>` on the script command line.

## Hook Config Location

Trae reads hooks from:

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
          { "type": "command", "command": "<path>", "timeout": 5000 }
        ]
      }
    ]
  }
}
```

Supported events: `SessionStart`, `UserPromptSubmit`, `PostToolUse`, `Stop`.

## Recommended Configuration (User-Level Hook)

For personal hook behavior, prefer **user-level** (`~/.trae-cn/hooks.json`) so
the hook fires regardless of repo:

```bash
mkdir -p ~/.trae-cn
cat > ~/.trae-cn/hooks.json <<'JSON'
{
  "version": 1,
  "hooks": {
    "SessionStart": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "${userHome}/.trae-cn/skills/user-self-improving/scripts/hook-self-check.sh",
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
            "command": "${userHome}/.trae-cn/skills/user-self-improving/scripts/activator.sh",
            "timeout": 5000
          }
        ]
      }
    ],
    "PostToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "${userHome}/.trae-cn/skills/user-self-improving/scripts/error-detector.sh",
            "timeout": 5000
          }
        ]
      }
    ]
  }
}
JSON
```

> Use `${userHome}` (Trae user-home variable), not `${workspaceFolder}` — the
> skill is personal and lives outside any repo.

## Install Snippet (One-Liner)

```bash
bash skill-markets/user-self-improving/scripts/install-snippet.sh trae-user \
  > ~/.trae-cn/hooks.json
```

(or for project-level: `> .trae/hooks.json`)

## Verification

1. Restart Trae IDE.
2. Open chat, send any message.
3. Expect `<user-self-improving-reminder>` block in context.
4. If absent, run `bash <skill-path>/scripts/hook-self-check.sh` to diagnose.

## Troubleshooting

| Symptom | Cause | Fix |
|---------|-------|-----|
| No reminder fires | Hook not registered | Run `hook-self-check.sh` — reports MISSING_* state |
| `${userHome}` not resolved | Trae version older than 3.5.66 | Upgrade Trae or use absolute path |
| Script not found | Path mismatch | Verify `~/.trae-cn/skills/user-self-improving/scripts/` exists |
| Permission denied | Scripts not executable | `chmod +x scripts/*.sh` |

## See Also

- [SKILL.md §3 Hook Protocol](../SKILL.md#3-hook-protocol-agent-native-not-invented)
- [hook-self-check.md](hook-self-check.md) — self-check protocol
- [multi-agent-matrix.md](multi-agent-matrix.md) — 4 agent 接入成本对比