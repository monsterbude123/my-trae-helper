# Changelog

All notable changes to the agent-dev-control-kit skill package will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Reserved for future features

## [1.1.0] - 2026-08-13

### Added
- **Three-Layer Control System**
  - Execution Layer: Atomic skill-level operations
  - Guard Layer: Pre/post-conditions validation hooks
  - Gate Layer: Process-level quality gates (4-tier)

- **Execution Skills (5 skills)**
  - `config-sync-control`: Configuration file synchronization
  - `data-change-control`: Data model change management
  - `doc-sync-control`: Documentation synchronization control
  - `asset-management-control`: Asset (files/images/binary) lifecycle management
  - `release-process-control`: Standardized release/deployment workflow

- **Guard Skills (5 guards)**
  - API contract validation guard
  - Test coverage threshold guard
  - Code quality metrics guard
  - Security policy compliance guard
  - Performance regression guard

- **Gate Mechanism (4 tiers)**
  - Tier 1: Pre-commit gate (local validation)
  - Tier 2: Pre-push gate (integration checks)
  - Tier 3: Pre-merge gate (team review gates)
  - Tier 4: Pre-release gate (production readiness)

- **Template Project Scaffold**
  - Complete `.agents/` structure with skill templates
  - Pre-configured guards directory with validation scripts
  - Gate configuration files with tier definitions
  - Hook installation scripts for Git integration
  - Test directories structure (unit/integration/e2e)

- **Standard Templates**
  - Execution skill template with YAML frontmatter
  - Guard skill template with validation logic
  - Gate skill template with tier configuration

- **Comprehensive Guides**
  - Execution skills implementation guide
  - Guard skills development guide
  - Gate skills configuration guide
  - Full implementation roadmap

### Changed
- Bumped from 1.0.0 to 1.1.0 to reflect Execution Skills expansion (from 3 → 5 skills)
- README simplified to remove redundant capability descriptions (now points to SKILL.md)
- `.env.example` cleaned to only include variables actually consumed by scripts
- Hooks install script now accepts `--project-root` and `--hooks-source` parameters

### Fixed
- Filled missing Execution Skills: added `asset-management-control` and `release-process-control` (previously reserved slots)
- Removed hardcoded paths in `hooks/install-hooks.sh` (now parameterizable)
- Removed unused environment variables from `.env.example` (e.g. `GUARD_TIMEOUT`, `CONTROL_TIMEOUT`, `LOG_*` etc.)
- Aligned test coverage threshold description across README, gate-skills-guide.md, and gate-control SKILL.md (all ≥ 80%)

---

## [2.0.0] - Future Vision

### Added
- AI-powered guard suggestions (anomaly detection)
- Predictive gate failures prevention
- Execution skill auto-generation from templates
- Multi-language support for guard definitions
- Cloud-based gate orchestration

### Changed
- Complete architecture redesign for distributed systems
- Migration to event-driven guard execution model
- Gate tier definitions will support custom tiers

### Deprecated
- Legacy hook scripts (migrate to new hook system)
- Old guard configuration format (use YAML instead)

### Security
- Zero-trust execution environment
- Encrypted guard communication channels
- Signed gate policies for tamper-proof validation

---

## Version Naming Convention

This skill package follows semantic versioning:

- **MAJOR (X.0.0)**: Breaking changes to skill structure, guard protocols, or gate tiers
- **MINOR (x.Y.0)**: New execution skills, guards, or backward-compatible enhancements
- **PATCH (x.y.Z)**: Bug fixes, documentation updates, minor improvements

## Migration Guide

### Upgrading from 1.0.x to 1.1.0

No breaking changes expected. To upgrade:

```bash
# Update skill package
node bin/cli.mjs update agent-dev-control-kit -a trae-cn -y

# Re-install hooks (optional)
cd your-project
./scripts/install-hooks.sh
```

### Upgrading to 2.0.0

Migration guide will be provided before 2.0.0 release.

---

[Unreleased]: https://github.com/your-org/agent-dev-control-kit/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/your-org/agent-dev-control-kit/releases/tag/v1.0.0
[1.1.0]: https://github.com/your-org/agent-dev-control-kit/milestone/1
[2.0.0]: https://github.com/your-org/agent-dev-control-kit/milestone/2