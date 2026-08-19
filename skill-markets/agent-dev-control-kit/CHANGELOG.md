# Changelog

All notable changes to the agent-dev-control-kit skill package will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Changed
- **SKILL.md 体积瘦身(482 → 244 行,vibe-coding-standards v2.5 弹性范围 100~350 内)**:按 §1.5 地图 vs 规范判定,把已存在于 references/ 的内容改为指针引用
  - §1.2 / §2-§4:5 Execution / 5 Guard / 4 Gate 详细流程 → `references/{execution,guard,gate}-skills-guide.md`
  - §5 使用方式长 bash 脚本列表(10+ 行)→ `scenarios/01-05.md` + `scripts/README.md`
  - §6 目录结构二级展开 → `§0.2 一级 tree`
  - §7.3 状态机 ASCII → `references/implementation-roadmap.md`
  - §9 完整指标表(质量/效率/风险 11 行) → 3 行摘要 + 指针
  - §11 Gate 自验收**保留内联**(会话蒸馏硬约束,必须可见)
  - 章节编号保留:`required_sections` 契约要求 §11,瘦身时未改章节顺序,直接复用原编号
  - §0 标题保留原貌"定位":`MANIFEST.yaml` must_contain 硬约束
- **version: 1.2.0 → 1.2.1**(PATCH — 纯文档瘦身,无 API/契约变更)

### Tests
- `pytest -m trap` 31 passed
- `pytest tests/unit/` 118 passed

### Source
- 由 my-trae-helper 2026-08-19 vibe-coding-standards v2.5 行数守卫触发,源头是 AGENTS.md §1.11 + §7 路径治理 + 此次会话 "处理 agent-dev-control-kit/SKILL.md 超限问题" 指令

## [1.2.0] - 2026-08-14

### Changed
- **README.md / SKILL.md / CHANGELOG.md 数字对齐**:移除"30+ 契约检查脚本 / 6 Agent Skills"夸大口径,改为真实"10 业务脚本 + 5 Execution Skill + 3 控制核心 Skill"
- **references/implementation-roadmap.md**:删除 P0/P1/P2/P3 backlog 优先级与时间估算,只保留"必要性"三档(必须/推荐/可选)
- **SKILL.md §5.1 / README.md 方式一**:删除不存在的 `template-project/` / `init-project.sh` / `hooks/install-hooks.sh` 路径,改为真实 `scripts/init-control-kit.py` + `validate-gate-integrity.py` + `install-husky.py`
- **SKILL.md §6 目录结构**:删除不存在的 `rust-react/nextjs-fullstack/cli-only` scaffold,改为实际四个内置 + 用户自定义优先级说明
- **README.md 文件结构树**:补充真实存在的 `tests/catalogs/` `registry/` `presets/` 与 10 个业务脚本

### Added
- **references/trap-instructions.yaml** 新增 `AP-CAT-DOCS-LANG`(缺中英双写文档)反例 — 对应 ai-short-studio-monster AGENTS.md §2
- **references/trap-instructions.yaml** 新增 `AP-CAT-META-REGISTER`(缺 _meta.ts 导航注册)反例 — 对应 ai-short-studio-monster AGENTS.md §2
- **references/execution-skills-guide.md §4 CP-5**:补"快照导出 / 回灌"控制点 — 对应 ai-short-studio-monster `npm run project:init:export` + `:init` 联动
- **registry/guards.yaml** `security-scan`:加 `requires_scripts: trae-security-review/scripts/scan_skills_dir.py`,显式声明依赖
- **references/traps.md §0 反例索引**:加 AP-CAT-DOCS-LANG / AP-CAT-META-REGISTER 两条

### Tests
- **tests/unit/test_trap_instructions.py** REQUIRED_TRAP_IDS 加入两条新 AP-* — 全套 153 用例通过(原 102,新增 51 主要来自 trap 参数化与 catalog 覆盖)
- `pytest -m trap` 77 passed
- `pytest tests` 153 passed

### Source
- 本轮修订由 my-trae-helper 2026-08-14 第三轮蒸馏触发,源头是 ai-short-studio-monster AGENTS.md 的双写铁律与本 skill 自身的目录漂移

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

> 注:本节"30+ 契约检查脚本 / 6 Agent Skills"等数字源于 1.0 早期口径,与 1.1.0 实际产物不符(实测 10 业务脚本 + 5 Execution Skill + 3 控制核心 Skill),以修正后的 README §来源为准。

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