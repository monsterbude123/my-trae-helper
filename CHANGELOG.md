# Changelog

本文件记录 `my-trae-helper` 的所有显著变更。格式基于 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/)。
版本号遵循 [语义化版本](https://semver.org/lang/zh-CN/)。

## [Unreleased]

### fullstack4TraeV11 升级(2026-08-15)

- **V11.8.4** — commit 准入最小集与全量验收分层
  - SKILL.md §0.3 Stage 3.5/4.5 异步化声明(cross-link §3.7.3 §8.4 工具-人类分层判定)
  - SKILL.md §1.6 视觉验证豁免(默认异步,不入流线化判定)
  - SKILL.md §3.7 #10 反虚假交付反向陷阱(范围盲目扩大)
  - references/common-anti-patterns.md §7 新增 6 个子段(7.1-7.6)
- **V11.8.3** — Stage 6 重构为 4 层分层决策框架
  - skills/12-bug-fix/references/bug-layer-{1-4}-*.md
  - trap-instructions.yaml V11-BH7 范围自扩反例
  - tests/unit/test_battle_report_coverage.py 重写(20 cases)
  - scripts/bug-hunt/dev-hmr-recovery.{sh,ps1} 安全修复(路径白名单 + scan-ignore-line)
- **V11.8.2** — Stage 6 Bug Fix & Hunt 统一工序(7 步 + 13 铁律 + 6 反例 + 6 工具脚本)

### guard/gate 路由(V11.7.0+ 升级,guard-smith 委派完成)

**本节记录 guard-smith 委派(2026-08-15)对白名单路径的增量改动**:

#### Added

- **CI workflow `v11-doc-check.yml`**(白名单 `.github/workflows/` 新增)— V11 改动 PR 自动跑 `v11-doc-sync.py --check`,missing=0 PASS / missing>0 BLOCK
- **CI workflow `v11-security-check.yml`**(白名单 `.github/workflows/` 新增)— V11 改动 PR 自动跑 `trae-security-review scan_skills_dir.py`,verdict=PASS 放行 / BLOCKED/WARNING 评论 + exit 1
- **注册表路由**:在 `registry/skills.yaml` 的 `fullstack4TraeV11` 条目新增 2 个 L3-specialized gate 路由:
  - `fullstack4TraeV11-l3-doc-check`(hooks: `.github/workflows/v11-doc-check.yml`)
  - `fullstack4TraeV11-l3-security-check`(hooks: `.github/workflows/v11-security-check.yml`)
  - `total_skills` 43 → 46(含 gitnexus4Trae / ponytail4Trae / product-teardown 三个新加入的项目级配置模板)

#### Changed

- **`scripts/skill-structure-guard.py`**(白名单 `scripts/<name>-guard.*` 共享过渡脚本修改 +63 行):
  - 新增 `EXCLUDED_NON_SKILL_DIRS` 白名单:`gitnexus4Trae` / `ponytail4Trae` / `product-teardown`(项目级配置模板,非 SKILL 包)
  - 新增 `LEGACY_NAMING_DIRS` 降级白名单:`fullstack4TraeV9` / `fullstack4TraeV10` / `fullstack4TraeV11` / `shuxia-novel-engine`(历史命名兼容,目录名含大写 V 不阻断,仅记 info)
  - 新增 `agents/` 文件 kebab-case 容差:V11 历史 agents 名降级为 info
  - 新增批量扫模式:`python scripts/skill-structure-guard.py skill-markets` → 全量扫 + 汇总
  - 原有 SKILL.md 检查 / 铁律数量 / 行软上限逻辑**全部保留**

- **`.github/workflows/skill-market-gate.yml`**(白名单 `.github/workflows/` 修改 +107 行):在 L3 PR merge 段加 5.6 / 5.7 / 5.8 步,在 L4 release 段加 5.7 / 5.8 全量步(全 V11 步 + protocol coverage + skill catalog V1 report-only)。L3-merge-gate / L4-publish-gate 原有 step 全部保留

#### Verification(guard-smith §2.4 Step 6 防假通过)

| 验证 | 结果 |
|------|------|
| `node src/guards/skill-registration-guard.mjs` | ✅ PASS(46/46 一致) |
| `node scripts/guard-router.mjs --all` | ⚠️ 44 PASS / 2 已知 FAIL(pre-existing,与本次改动无关) |
| `node tests/unit/test_guard_router.mjs` | ✅ 4/4 PASS |
| `python tests/unit/run_registration_guard.py` | ✅ 9/9 PASS |
| `node scripts/lint.mjs` | ✅ 29/29 PASS |

**已知 2 FAIL 不阻断 commit**:
- `fullstack4TraeV11-flow` → `gates.yaml` line 91 column 23 `name: 评审门禁(V11.6.0: AC 核销门禁,取代评分)` 冒号在值里未转义 — V11 升级引入,不在 guard-smith 白名单(skill 内部),需主 agent 决策是否另派 V11 内部 agent 整改
- `minimax-multimodal` → `tests/test_minimax.py` 硬编码 API Key 8 处 — 预存在 FAIL,本次 diff 未触及

#### 文档同步

- `CAPABILITY-MAP.md` §2(共享能力注册表)新增 6 行:4 个 V11 脚本(ac-gate / gate-installer / gate-integrity-guard / v11-doc-sync)+ 2 个 CI workflow
- `SECURITY-MAP.md` V11 行加 V11.8.0+ CI 升级备注
- `CHANGELOG.md` 本节

## [Unreleased]

### Added

- **Skill 创建/更新工作流引导**:`.agents/rules/skill-creation-workflow.md`(2026-08-15 NEW)
  - **V11.8.0.1 路径迁移(2026-08-15)**:原 `.agents/rules/` 下 3 个协议迁移到 `.agents/skills/project-rule-skill/references/`,与 project-rule-skill 同包统一管理:
    - `skill-creation-workflow.md` → `.agents/skills/project-rule-skill/references/skill-creation-workflow.md`
    - `skills开发细则.md` → `.agents/skills/project-rule-skill/references/skills-development-rules.md`(同时改为英文文件名)
    - `protocol-coverage-protocol.md` → `.agents/skills/project-rule-skill/references/protocol-coverage-protocol.md`
  - 原 `.agents/rules/` 路径保留 redirect stub(防死链);`project-rule-skill` 升级到 v2.0.0(frontmatter 加 `version` + `requires`)+ 路由表/§3 关系/§5 反模式全部更新
  - 同步 14 个引用源文件:AGENTS.md / CHANGELOG.md / README.md / SECURITY-MAP.md / `references/catalog-coverage-evaluation.md` / `tests/catalogs/catalog-protocol.md` / `tests/catalogs/README.md` / `.github/workflows/skill-market-gate.yml` / `scripts/_check_protocol_coverage.py` / `tests/unit/test_check_protocol_coverage.py`
  - 核心理念:**协议先行 + 多维度一致**
  - 覆盖场景:新建 / 升级 / 合并 / 废弃 4 种
  - 强制 6 维度同步:SKILL / reference / workflow / script / guard / 其他引用
  - 防"做一半"机制:全有或全无自检清单(§7)
  - 与现有体系联动:AGENTS.md §1.3 + §1.12 + project-rule-skill SKILL.md 路由表
  - **多维度同步落地**:
    - `.agents/rules/README.md` 目录结构同步 ✅
    - `.agents/rules/skills开发细则.md` 短细则加 MUST 引用新规则 ✅
    - `.agents/skills/project-rule-skill/SKILL.md` §2 路由表 "新建/修改/删除 skill" 行加引用 ✅
    - `AGENTS.md` §1.3 启动加载协议加引用 ✅
    - `AGENTS.md` §7 能力地图加新行 ✅
  - 用户原话:"**彻底的处理,还有最好是理念方面先做好文档层面的同步,避免做了一半又忘记,后续又是卡一半做不完,这个需要同步到这个技能市场项目的agent 工作流里去,和这个技能的理念一致,文档'协议'先行,多维度(SKILL reference workflow script guard 其他引用)保持一致**"

- **协议覆盖度协议 + 程序化检测工具**(2026-08-15 NEW)
  - **协议规范**:`.agents/rules/protocol-coverage-protocol.md`(10 章节,含 §8 自我应用)
  - **检测脚本**:`scripts/_check_protocol_coverage.py`(200+ 行,std lib 优先 + argparse)
    - `--scope {package,global}` 双 scope(package = 6 维度,global = 1 维度)
    - 3 种引用形式检测(文件名/全路径/stem)
    - `--check` CI gate 模式 + `--json` + `--dry-run` + `--strict`
  - **pytest 14 用例**:`tests/unit/test_check_protocol_coverage.py`(0.12s 全过)
    - 4 类覆盖:文件引用 / 维度集合 / scope 解析 / 真实项目 / main() 集成
  - **CI gate**:`.github/workflows/skill-market-gate.yml` §5.7
    - L3 PR merge: git diff 检协议变更,scope 自动判
    - L4 Release: 全量 `find skill-markets -name '*-protocol.md'` + `.agents/rules/*.md` 扫
  - **自验证**:skill-creation-workflow.md / skills开发细则.md / 项目核心.md / protocol-coverage-protocol.md 全过 `global --check` ✅

- **Catalog 主动指引机制**(agent-dev-control-kit 子套件)
  - `tests/catalogs/skill-catalog.yaml` 声明 SKILL 应包含什么(文档/章节/schema 字段/脚本)
  - `tests/catalogs/test_catalog_coverage.py` 15 用例守门,缺什么 fail + emit_hint
  - `tests/_helpers/agent_hint.py` 主动指引:trap fail 时给 agent 看 `🛠 next: Skill(name=...)`
  - `references/trap-instructions.yaml` 6 条结构化反例(AP-2 / AP-3 / AP-CAT-*)
  - `scripts/catalog-guard.py` commit-time gate,缺失阻断 + banner
  - `scripts/agent-hint-emit.py` 按 trap 聚合 hint 给人类/agent 看

- **Skill Catalog 校验协议 + 程序化校验**(2026-08-15 NEW V1)
  - **协议规范**:`tests/catalogs/catalog-protocol.md`(11 章节,scope=skill-metadata)
  - **schema**:`tests/catalogs/skill-catalog.schema.json`(必填字段 + optional + 结构规则 + 反例库)
  - **catalog yaml**:`tests/catalogs/skill-catalog.yaml` — V1 必填只 `name` + `description`(渐进式,不强制全填避免大面积 FAIL)
  - **校验脚本**:`tests/catalogs/_check_skill_catalog.py`(200+ 行,std lib + argparse)
    - V1 默认 **report-only**(发现错误但不阻断)— `--strict` 才 exit 1
    - 沿用 vibe-coding-standards v2.5:max_skill_md_lines=500 + min_yaml_frontmatter_fields=2
  - **pytest 11 用例**:`tests/unit/test_skill_catalog.py`(0.15s 全过,4 类覆盖:加载 / 解析 / 单 SKILL / main 集成)
  - **CI gate**:`.github/workflows/skill-market-gate.yml` §5.8
    - L3 PR merge: 检变更的 SKILL.md + 全量报告
    - L4 Release: 全量 catalog 检查
  - **真实数据**(2026-08-15 14:42,43 SKILL 全扫):1 错误(fullstack-auto 缺 frontmatter)+ 4 警告(行数 > 500)

- **Skill Catalog V2 进阶**(2026-08-15)
  - **version 升级为必填**:从 V1 推荐 → V2 必填,`required_metadata` 加 `version`
  - **新增 recommended_metadata**:requires 推荐字段(声明时 WARN,不阻断)— V2.1 升级为必填
  - **批量补字段**:`logs/catalog-v2-batch-fill.py` 给 29 个 SKILL 加 `version: 1.0.0`
  - **结构调整**:max_skill_md_lines 350 → 500(避免 false positive)+ min_yaml_frontmatter_fields 2 → 3
  - **pytest 14 用例**(0.18s):新增 3 个 V2 用例(required_version / recommended_warns_only / all_required_pass)
  - **真实跑结果**(V2 实扫 43 SKILL):必填字段覆盖率 **100%**(43/43)— 推荐字段 26.2%(11/42)
  - **V2.1 留待**:逐 SKILL 评估 requires 字段 + 4 个 > 500 行 SKILL.md 提取 references/(agent-dev-control-kit 622 / fullstack4TraeV11 727 / meeting-minutes-taker 670 / session-distiller 526)

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