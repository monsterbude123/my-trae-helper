# Changelog

本文件记录 `my-trae-helper` 的所有显著变更。格式基于 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/)。
版本号遵循 [语义化版本](https://semver.org/lang/zh-CN/)。

## [Unreleased]

### Added

- **Catalog 主动指引机制**(agent-dev-control-kit 子套件)
  - `tests/catalogs/skill-catalog.yaml` 声明 SKILL 应包含什么(文档/章节/schema 字段/脚本)
  - `tests/catalogs/test_catalog_coverage.py` 15 用例守门,缺什么 fail + emit_hint
  - `tests/_helpers/agent_hint.py` 主动指引:trap fail 时给 agent 看 `🛠 next: Skill(name=...)`
  - `references/trap-instructions.yaml` 6 条结构化反例(AP-2 / AP-3 / AP-CAT-*)
  - `scripts/catalog-guard.py` commit-time gate,缺失阻断 + banner
  - `scripts/agent-hint-emit.py` 按 trap 聚合 hint 给人类/agent 看

- **CI 接入**
  - `scripts/run-agent-dev-control-kit-tests.py` 跨平台 wrapper(纯 Python,Windows/macOS/Linux)
  - `tests/unit/test_agent_dev_control_kit_wrapper.py` 8 个 wrapper 自验收
  - `tests/unit/test_main_pytest_rootdir_isolation.py` 6 个跨包隔离验证
  - `tests/conftest.py` + `pytest.ini` 主仓 pytest rootdir 隔离(防止吸入子包 conftest)
  - `.github/workflows/agent-dev-control-kit-ci.yml` 子 skill CI(改了它必跑,~30s 反馈)
  - `.github/workflows/skill-market-gate.yml` L3 + L4 各加 catalog-guard step
  - `.husky/pre-commit` 第 5 步:catalog-guard(改了 agent-dev-control-kit 才跑)
  - `.husky/pre-push` 第 5 步:同上,但全量留给 L3 CI
  - `package.json` `lint` / `test:unit` / 新增 `test:agent-dev-control-kit`

- **文档**
  - `docs/CI.md` 完整 CI 矩阵(L1~L4 + 子 skill CI),含步骤/阻塞条件/反例固化索引
  - `.github/PULL_REQUEST_TEMPLATE.md` PR 自检清单(L1/L2/反例四块勾选项)

### Changed

- `.husky/pre-push`:新增第 5 步 catalog-guard(按变更触发),原有 lint / structure / build 不动

### Removed

(无)

---

## 历史记录

仓库之前未维护 CHANGELOG,本次为首次建立。如需追溯更早的提交,使用 `git log --oneline`。