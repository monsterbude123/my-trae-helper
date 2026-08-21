# Entry Examples

> Concrete examples for `LEARNINGS.md` / `ERRORS.md` / `FEATURE_REQUESTS.md`
> / `SOUL.md` / `TOOLS.md` / `MEMORY.md`.

---

## LRN: Correction (Personal Style)

```markdown
## [LRN-20260821-001] correction

**Logged**: 2026-08-21T10:30:00Z
**Priority**: high
**Status**: pending
**Area**: docs

### Summary
I (the user) hate the agent hedging with "I think" / "perhaps" — be direct

### Details
After several rounds, the user explicitly said: "Stop saying 'I think',
just tell me what you found. If unsure, say 'unsure' once and move on."

### Suggested Action
In all responses, remove hedging qualifiers. Use direct statements.
If truly uncertain, mark it explicitly but don't repeat.

### Metadata
- Source: user_feedback
- Tags: style, communication, personal-pref
- See Also: LRN-20260815-002 (similar style correction)
```

---

## LRN: Knowledge Gap (Promoted to SOUL.md)

```markdown
## [LRN-20260821-002] insight

**Logged**: 2026-08-21T14:22:00Z
**Priority**: medium
**Status**: promoted
**Promoted**: SOUL.md
**Area**: docs

### Summary
User prefers terse responses (≤5 paragraphs unless asked)

### Details
After 3 long replies in a row, the user asked: "Why so verbose? Just
give me the answer." Promoted to SOUL.md for cross-project continuity.

### Suggested Action
Default response length: ≤5 short paragraphs. Long form only when
explicitly asked.

### Metadata
- Source: user_feedback
- Tags: style, verbosity, personal-pref
```

---

## LRN: Knowledge Gap (Promoted to TOOLS.md)

```markdown
## [LRN-20260821-003] knowledge_gap

**Logged**: 2026-08-21T16:00:00Z
**Priority**: high
**Status**: promoted
**Promoted**: TOOLS.md
**Area**: config

### Summary
This user's WSL2 DNS takes 5s to resolve — add retry to all curl

### Details
Reproducible on this machine: `curl https://api.example.com` often
takes 5+ seconds to start. Standard practice is to add `--retry 3
--retry-delay 2` to all curl invocations.

### Suggested Action
When invoking curl on this machine, default to `--retry 3 --retry-delay 2`.
For long-running scripts, consider `--retry-connrefused` too.

### Metadata
- Source: error
- Tags: wsl2, dns, machine-specific
- See Also: ERR-20260821-A3F (related DNS failure)
```

---

## LRN: Best Practice (Promoted to MEMORY.md)

```markdown
## [LRN-20260821-004] best_practice

**Logged**: 2026-08-21T18:00:00Z
**Priority**: high
**Status**: promoted
**Promoted**: MEMORY.md
**Area**: docs

### Summary
User is colorblind — always pair color with shape in diagrams

### Details
Mentioned in passing during a UI review: "I can't tell which line is
which in your diagram because they're both red." User has red-green
colorblindness.

### Suggested Action
For any diagram (mermaid, ASCII art, etc.), also include:
- Shape (circle vs square vs diamond)
- Label (next to each element)
- Pattern (solid vs dashed vs dotted)
Never rely on color alone.

### Metadata
- Source: user_feedback
- Tags: accessibility, colorblind, personal-style
```

---

## ERR: Machine-Specific Failure

```markdown
## [ERR-20260821-A3F] wsl_dns

**Logged**: 2026-08-21T09:15:00Z
**Priority**: high
**Status**: pending
**Area**: infra

### Summary
DNS resolution stalls in WSL2 on this machine

### Error
```
$ curl -v https://api.github.com 2>&1 | head -10
* Trying 140.82.121.6:443...
* connect to 140.82.121.6 port 443 failed: Connection timed out
*   Trying ...
* Connection #0 to host api.github.com left intact
```

### Context
- Machine: Windows 11 + WSL2 (Ubuntu 22.04)
- DNS resolver: default systemd-resolved
- First seen: 2026-08-21
- Pattern: every curl takes 5s to start

### Suggested Fix
1. Add `--retry 3 --retry-delay 2` to curl calls
2. Or set `RES_OPTIONS="timeout:2 attempts:3"` in ~/.bashrc

### Metadata
- Reproducible: yes (this machine)
- Tags: wsl2, dns, machine-specific
- See Also: LRN-20260821-003 (promoted to TOOLS.md)
```

---

## FEAT: Personal Capability Gap

```markdown
## [FEAT-20260821-001] auto_commit_msg

**Logged**: 2026-08-21T16:45:00Z
**Priority**: medium
**Status**: pending
**Area**: config

### Requested Capability
Generate commit messages from staged diff that follow this user's
style (terse, lowercase, no period at end)

### User Context
User has run `git commit` ~50 times this month and manually writes
every message. Their style: "feat(api): add user lookup endpoint"
(Conventional Commits, lowercase, no period).

### Complexity Estimate
medium

### Suggested Implementation
Wrap git commit with a helper script that:
1. Runs `git diff --staged`
2. Sends to LLM with style examples
3. Returns suggested message
4. User can accept / edit / regenerate

### Metadata
- Frequency: recurring (~50/month)
- Related Features: git, conventional commits
```

---

## SOUL.md Style Example

```markdown
# SOUL.md

## Communication Style
- Be direct, no hedging
- ≤5 paragraphs unless asked for detail
- Skip disclaimers ("I should note that...")
- End with action items or "next step" pointer

## Response Shape
- Quick answer first (1-2 sentences)
- Then reasoning if non-obvious
- Code/commands with comments only where the why isn't obvious

## Things to Avoid
- Emoji in technical responses
- "I think" / "perhaps" / "it seems"
- Repeating the question back to me
- "Let me know if..." (just do it or stop)

## Things You Always Want
- File paths as clickable links
- Code blocks with syntax highlighting
- Test results inline, not as a separate doc
```

---

## TOOLS.md Style Example

```markdown
# TOOLS.md

## Machine Quirks
- WSL2 DNS takes 5s to resolve — always `--retry 3` for curl
- Docker on this box needs `--platform linux/amd64` (M2 Mac)
- Python is at `/opt/homebrew/bin/python3`, not `/usr/bin/python3`

## Local Tool Paths
- node: /opt/homebrew/bin/node (v22.x)
- python3: /opt/homebrew/bin/python3 (3.12.x)
- pnpm: /opt/homebrew/bin/pnpm (9.x)

## Recurring Workarounds
- git push → always `git push -u origin HEAD` (no upstream defaults)
- pytest → always `pytest -x` (stop on first failure)

## Tool-Specific Flags
- rg: default to `--hidden --glob '!.git/'`
- fd: default to `--hidden --exclude .git`
```

---

## MEMORY.md Style Example

```markdown
# MEMORY.md

## Standing Preferences
- I prefer TDD for new features
- I read code top-to-bottom; flag any deviation
- I work in 25-min pomodoros; respect task boundaries

## Values / Style Anchors
- Optimize for "boring tech that works" over "new and shiny"
- I value explicit > clever
- I'd rather wait 1 day for a stable API than ship today

## Recurring Frustrations
- Agent re-explaining what I just asked (read the chat)
- Agent inventing facts when uncertain
- Agent skipping steps in multi-step tasks

## Goals
- Maintain 95% test coverage on personal projects
- Keep weekly tech reading to ≤2 hours (not 10)
- Build at least one "ship-it" product this quarter
```