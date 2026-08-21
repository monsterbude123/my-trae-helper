# Changelog — quality-documentation-manager

All notable changes to this skill are documented here.
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [1.0.0] - 2026-08-21

### Added

- **Initial release** — Professional Documentation Steward methodology
- **§0 Positioning** — Boundaries vs existing skills (doc-map-manager / vibe-coding-standards / skill-acceptance / common-project-coding-conf / fullstack4TraeV11 / meeting-minutes-taker / docsify-doc-builder)
- **§1 Diátaxis 4-quadrant protocol** — Tutorial / How-to / Reference / Explanation with quadrant frontmatter schema
- **§2 SSOT 6 iron rules** — Code as SSOT / One definition / Relative reference / Backlink graph / 4 truth elements / Byte-consistent replicas
- **§3 Docs-as-Code 5 principles + toolchain** — lychee v0.20+ / Vale v3+ / markdownlint-cli2 v0.13+ / pre-commit v3+ / GitHub Actions
- **§4 Reverse citation graph** — Delegated to doc-map-manager (--context-mode / --impact / --detect-changes) + lychee link health
- **§5 Document state machine + timeliness red lines** — Draft / Stable / Outdated / Deprecated 4 states, P0 ≤24h / P1 ≤7d / P2 ≤30d
- **§6 4-layer enforcement chain** — L1 editor / L2 pre-commit / L3 CI / L4 monitoring
- **§7 Relationships** — Explicit non-overlap with existing skills
- **§8 Trigger words** — ≥6 keywords: documentation / doc governance / diataxis / SSOT / ROT / lychee / markdownlint / vale
- **§9 Anti-patterns** — 10 traps synced with `references/trap-instructions.yaml`
- **References (6 files)** — diataxis-quadrants.md / ssot-protocol.md / docs-as-code-toolchain.md / freshness-state-machine.md / ci-gate-stack.md / trap-instructions.yaml

### Notes

- Source report: `d:\workplace\code\ai-dev\new-api-monster\docs\research\professional-documentation-management-20260821.md` (22+ sources)
- This is a **methodology distillation**, not a project-specific refactor
- **Abbreviation conflicts** (declared in §0):
  - ROT: this skill = Redundant/Outdated/Trivial (docs audit) vs fullstack4TraeV11/skills/10-rot-scan = 腐化扫描 (10 rot indicators)
  - SSOT: this skill = Single Source of Truth (docs governance protocol) — same as industry-wide meaning
- **Soft dependencies** (declared in frontmatter `requires`): doc-map-manager / vibe-coding-standards / skill-acceptance / common-project-coding-conf
- **No hard dependencies** — installable independently
- **Field naming**: Uses local schema (`severity` / `what_is_wrong` / `detect_signal` / `see_also`) per .agents/rules/learning.md §3 — no global self-improving-agent field collision
- **Out of scope** (per [GUARD-SMITH-DELEGATION]):
  - No new scripts in `scripts/` (project-side reserved for guard-smith per AGENTS.md §1.11)
  - No registration in `registry/skills.yaml` (guard-smith write domain)
  - No `.husky/<name>-gate` (guard-smith write domain)
  - No `CAPABILITY-MAP.md` update (user-assigned separate task)
