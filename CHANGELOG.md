# Changelog

本文件记录 `my-trae-helper` 的所有显著变更。格式基于 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/)。
版本号遵循 [语义化版本](https://semver.org/lang/zh-CN/)。

## [Unreleased]

### agent-dev-control-kit SKILL.md 瘦身 482 → 244 行(2026-08-19)

- **触发**:vibe-coding-standards v2.5 弹性阈值(100~350)超限治理
- **§1.5 地图 vs 规范判定**:内联保留 三层架构 ASCII / 整体流程 mermaid / 摘要表 / 联动 mermaid + 失败矩阵 / 5 条设计原则 / 目录结构一级 tree / §11 Gate 自验收;指针化已存在 references/ 内容 + scenarios/01-05 + 完整指标表 → 摘要 + 指针
- **两道契约守卫生效**(不退让):
  - `tests/catalogs/skill-catalog.yaml` required_sections 硬要求 §11 → 主标题 §10 → §11 + 子章节编号对齐
  - `skill-markets/MANIFEST.yaml` must_contain 硬要求 `## §0 定位` → 标题保留原貌
- **版本**:1.2.0 → 1.2.1(PATCH — 纯文档瘦身)
- **验证**:`pytest -m trap` 31 passed + `pytest tests/unit/` 118 passed + `python scripts/catalog-guard.py` ✅
- 参考 [skill-markets/agent-dev-control-kit/SKILL.md](skill-markets/agent-dev-control-kit/SKILL.md) + [skill-markets/agent-dev-control-kit/CHANGELOG.md §1.2.1](skill-markets/agent-dev-control-kit/CHANGELOG.md)

### vibe-coding-standards v2.5 落地 + fullstack4TraeV11 SKILL.md 瘦身(2026-08-19)

- **vibe-coding-standards 注册 + 挂载 pre-commit gate**(guard-smith 委派)
  - 新建 `scripts/vibe-coding-standards-line-guard.py`(封装 SKILL.md 行数 100~350 弹性检查 + 5 Pillar 联动)
  - 新建 `.husky/vibe-coding-standards-gate`(跨平台 husky 文件,detect-python.sh 探测)
  - `.husky/pre-commit` 追加 step 9 调用新 gate
  - `registry/skills.yaml` 新增 vibe-coding-standards-line guard + gate
- **fullstack4TraeV11 SKILL.md 拆分**(vibe-coding-standards v2.5 阈值 350 行)
  - 644 → 349 行(100~350 弹性范围内 ✅)
  - 5 段抽到 `references/v11-*.md`(three-layer-control / fidelity-protocol / load-protocol / project-ecosystem / paths-config)
  - 详见 `skill-markets/fullstack4TraeV11/CHANGELOG.md V12.0.0.P4`
- **注册表 pre-existing 错误修复**(guard-smith 委派)
  - 删除注册表中残留的 `- skill: project-rules-gate` 条目
  - 新增 `- skill: common-project-coding-conf` 条目

### find-skills 接入(2026-08-18)

- **V1.0 NEW** — 从 [vercel-labs/skills](https://github.com/vercel-labs/skills) 同步 `skills/find-skills/SKILL.md` 入仓(纯文档,单文件),用途:帮助用户发现并安装 agent skill("how do I do X" / "is there a skill for X")
  - `skill-markets/find-skills/SKILL.md`(新增,标注来源)
  - `scripts/find-skills-guard.py`(新增,guard-smith 委派生成,aspects=[structure])
  - `registry/skills.yaml` 加条目(1 structure guard + 1 L1 pre-commit gate + maintainer guard-smith),total_skills 48 → 49
  - `skill-markets/CAPABILITY-MAP.md` + `SECURITY-MAP.md` 各加 L0 行(评分 5.0,纯文档无风险)
  - **未涉及**:`.husky/<name>-gate`(与其他 skill 一致,挂 `.husky/pre-commit` 共担)
- **配套执行层重构**:`src/execution/skill-install-control.mjs` 的 `executeInstall/executeUninstall` 委托 `installer.mjs` 同一入口,删除内联 cpSync/symlinkSync 重复实现,统一 junction/copy 行为(消除双代码漂移风险)。`tests/unit/test_skill_install_control.mjs` 11/11 通过。

### github-kownledge-helper 全量沉淀(2026-08-16)

- **references 全量沉淀 V1.0** — 按 skill-evolution 协议,把 `D:\workspace\github-kownledge-helper\AGENT.md`(341 行 / 10 节)+ `.trae\rules\project-rules.md`(94 行 / 10 节)全量沉淀为 13 个 references(workflows-baseline / manifest-schema / doc-map-manager-usage / env-loadenv / reply-conventions / first-run-checklist / skill-evolution / task-start-probe / project-paths / git-workflow-rules / doc-index-rules / answer-rules / safety-cleanup)+ SKILL.md Triggers 扩展 12 行 + workflows.md 基线引用重定向。判定原则:通用约定沉淀,具体项目配置(env 名/路径前缀)仅作"示例"段
  - **A 类 8 个**(AGENT.md §3-§10 未吸收):manifest Schema / 4 大工作流基线 / doc-map-manager 使用 / load_env 收口 / 回复规范 / 首次自检 / 技能演进 / 任务启动探测
  - **B 类 5 个**(project-rules §1-§7 未吸收):路径约定 / git 工作流硬约束 / 知识索引硬约束 / 答疑红线 / 安全与清理
  - **workflows.md 重写**:因 SearchReplace 工具报告成功但实际未落盘(陷阱 §010),改用 Write 整文件替换 5 处,Read 验证全部落盘

### github-kownledge-helper 接入(2026-08-16)

- **V1.0 NEW** — 本地 GitHub 仓库管家技能接入合规体系(skill-creation-workflow §3.1 协议先行 + 多维度一致)
  - `skill-markets/github-kownledge-helper/SKILL.md` 加 YAML frontmatter(name/version/description/audience/requires.skills doc-map-manager),catalog V2 校验从 FAIL 转为 PASS
  - `scripts/github-kownledge-helper-guard.py`(新增,forge-skill-guard.py 自动生成,aspects=[structure])
  - `registry/skills.yaml` 加条目(1 structure guard + 1 L1 pre-commit gate + maintainer guard-smith),total_skills 47 → 48
  - `skill-markets/CAPABILITY-MAP.md` + `SECURITY-MAP.md` 各加 L0 行(评分 5.0,实跑 trae-security-review scan_skills_dir.py V2.1 → HIGH 0 + MEDIUM 0 + LOW 0)
  - **未涉及**:`.husky/<name>-gate`(其他 skill 普遍未建,与 forge-skill-guard 生成的 L1 pre-commit guard 已自动挂到 `.husky/pre-commit` 共担路径)
  - **6 项兜底验证全 PASS**:`node src/guards/skill-registration-guard.mjs`(单 skill + 全量)/ `python tests/catalogs/_check_skill_catalog.py` / `python scripts/github-kownledge-helper-guard.py` / `python scripts/skill-security-guard.py` / `python scripts/skill-capability-guard.py`

### fullstack4TraeV11 升级(2026-08-16)

- **V11.8.5** — 协议层承诺 → 脚本落地(13/14 done + 1 留置)
  - 新增 `scripts/project-priority-resolver.py`(resolve_skills 伪代码实现)
  - 新增 `scripts/secrets-detector.py`(Article XVII Secret Redaction 10 类 pattern)
  - 新增 `scripts/bug-state-machine-validator.py`(5 状态机制校验)
  - 详见 [skill-markets/fullstack4TraeV11/CHANGELOG.md V11.8.5 条目](skill-markets/fullstack4TraeV11/CHANGELOG.md)
- **V11.8.5.P1** — §3.7 #10 commit 准入最小集程序化落地
  - 新增 `scripts/commit-minimum-check.py`(4 项准入校验:typecheck compileall / spot-check json / admin 探针 urllib 5s 超时 / lint 预存 pyflakes → warnings jsonl)
  - 新增 `tests/unit/test_commit_minimum_check.py`(16 用例全 PASS in 11.80s)
  - 收尾 P3-6 commit-minimum-check.py 留置(`references/todos/P3-6-commit-minimum.md` status pending → done)
  - 详见 [skill-markets/fullstack4TraeV11/CHANGELOG.md V11.8.5.P1 条目](skill-markets/fullstack4TraeV11/CHANGELOG.md)
  - **同步触发 doc-sync-guard** 6 项(README / CHANGELOG / SECURITY-MAP / CAPABILITY-MAP / AGENTS.md / registry/skills.yaml)一并落本 commit
- **V11.8.6** — V12 物理隔离思想在 V11 主版本内渐进落地(6 步,不升主版本)
  - 新增 `templates/change-dir-layout-v12-preview.md` — V12 物理布局模板(V11 可选,fact/ + stage/{11}/ + archive/)
  - 新增 `templates/hooks/process-layer-guard.sh` — 路径校验 hook(3 规则,Git Bash + macOS + Linux 跨平台)
  - 新增 `tests/unit/test_stage_gate_reset.py` — `--reset-to` 7 用例全 PASS(PASS/边界/FAIL 三态)
  - 新增 `tests/unit/test_encoding_windows.py` — Windows PYTHONIOENCODING=utf-8 兜底 3 用例(沿用 P3-6)
  - `scripts/init-from-zero.py` 新增 `--layout v12-preview` 参数 + Step 4.5 创建 `_v12-preview-template/` 骨架(11 stage 子目录 + 14 README)
  - `scripts/stage-gate.py` 新增 `--reset-to` 子命令 + `cmd_reset_to` 函数(保留 fact/ + 清 stage/{N+1} ~ stage/5/accept + 不动 archive/)
  - `references/sub-agent-rules.md §1.0` 新增"V11 主版本可选 V12 物理布局"指针(MUST + 2 NEVER)
  - 4 个 agents 加产物落位规则(jarvis + backend-implementer + frontend-implementer + test-expert)
  - 详见 [skill-markets/fullstack4TraeV11/CHANGELOG.md V11.8.6 条目](skill-markets/fullstack4TraeV11/CHANGELOG.md)
  - 物理归档 P3-6 → `references/todos/archive/done/2026-08-16-batch-repair-2/`
  - **同步触发 doc-sync-guard** 7 项(README / CHANGELOG / SECURITY-MAP / CAPABILITY-MAP / AGENTS.md / registry/skills.yaml / skill-level README)一并落本 commit
- **audit-fix-2026-08-16** — guard-smith audit B 方案 3 件系统化缺口修补落地
  - **guard-smith sub-agent 委派完成**(白名单内):
    - `skill-markets/guard-gate-smith/SKILL.md §1.1.1` 增补(+35 行,非 schema 字段注释行豁免规则表 + 硬约束 3 条 + 治理边界算法)
    - `src/guards/skill-registration-guard.mjs` 顶部 docstring 增补(+9 行,守卫本体只校验 schema 不校验注释)
  - **主代理直接 Edit**:`AGENTS.md §1.11 铁律 11 增补条款`(+16 行,与 §1.1.1 + docstring 三方一致)
  - 主上下文兜底验证(§2.4 SOP Step 6,2026-08-16):
    * `node src/guards/skill-registration-guard.mjs` → ✅ PASS
    * `node scripts/guard-router.mjs guard-gate-smith` → ✅ PASS
    * `node tests/unit/test_guard_router.mjs` → ✅ 4/4
    * `npm run lint` → ✅ 29 文件
    * `python -m pytest` → ✅ 262/262 passed(0 回归)
  - 新建 todo: `references/todos/audit-fix-2026-08-16.md`(status done)
  - 协议语义真空闭合:豁免范围明文化 + 硬约束明文化 + 治理边界算法程序化
- **mentioned-but-not-parsed closure(2026-08-16)** — top 5 全量验证 5/5 已落地
  - 主上下文核查 + 源码 grep 双重核对子代理 B 报告 top 5:
    - #1 project-priority-resolver.py + run-all-guards.py L43-72/L183-199 → ✅ done
    - #2 state-card-validator.py 17+ 字段 + visual_evidence 硬门槛 → ✅ done
    - #4 state-machine.yaml 消费方:stage-gate + _lib_state_card + run-all-guards → ✅ done
    - #5 repair-flow-gate.py + Stage 6 SKILL.md L114-130 4 步强制流程 → ✅ done
    - #6 run-all-guards.py resolve_registry_dir 项目级 .trae/registry/ 自动探测 → ✅ done
  - 14 条协议层差距全部 done(批修 + V11.8.5.P1 + V11.8.6 三批 commit 累积)
  - V11 协议层闭环度 100%(18/18 done);剩余 V12-ROOT(等用户授权 V12 ADR,主版本升级独立轨道)
  - **扩展核查(用户复述后追加)** — 完整 14 条(非仅 top 5)全量验证 14/14 已落地:
    - #3 state-card-validator.py L133-139 Stage 4/review visual_evidence + verified_at + read_by_main_context → ✅ done
    - #7 run-all-guards.py L92-93 + L108-127 stack-gate 交叉校验(stacks[].gates/guards ⊆ gates.yaml/guards.yaml) → ✅ done
    - #8 project-priority-resolver.py L5 §14.5 项目级 rules 优先 + L38 读 project_rules_skills → ✅ done
    - #9 secrets-detector.py L67 regex 11 类(api_key/token/password/passwd/pwd/secret/access_key/client_secret 等)+ L20 6+ 字符 → ✅ done
    - #10 bug-state-machine-validator.py(批修新增,5 状态机 + 7 转换矩阵) → ✅ done
    - #11 change-status.py L55-58 + setup-feature.py L137-150 双路径强制 audit_state_card_change → ✅ done
    - #12 proactive-scan.py L88/134/174/195/196/270/271 _invalidated 白名单 + L247 上下文窗口 200 字符 + L286 反例说明跳过 → ✅ done
    - #13 commit-minimum-check.py V11.8.5.P1 → ✅ done
    - #14 templates/hooks/pre-stage.sh L7-119 + launch-guard.sh L40 强制 stage-gate.py 调用 → ✅ done
  - 详见 [skill-markets/fullstack4TraeV11/references/todos/mentioned-but-not-parsed-closure.md](skill-markets/fullstack4TraeV11/references/todos/mentioned-but-not-parsed-closure.md)

### fullstack4TraeV11 V11.8.7.1(2026-08-18)— 5 项用户硬要求 3 连修 + V11-AP17 修复

- **5 项用户硬要求 3 连修**(用户 2026-08-18 拍板,V11.8.7.1 闭项):
  - `init-from-zero.py`:`--layout` 移除 `v11-default` 兼容值(只留 `v12-preview` + 隐式默认),`create_project_module()` 强保 module 存在(避免空目录)
  - `spec-purge.py`:`archive_keep_v12_layout()` 不再展平 archive 子目录(保留 stage/ + fact/ 物理结构)
  - `_lib_paths.py` 合并 `paths` + `project_paths` + `check_paths_config` 3 个分散模块(单文件 ≈ 180 行,引用统一)
  - `check_paths_config.py` 提升为项目侧独立守卫脚本(从 `_lib_paths` 抽出,独立触发)
  - `references/project-structure.md` 加 `docs/modules/` 不存在必检项
- **V11-AP17 修复**(doc-sync-gate 死锁):
  - `templates/hooks/doc-sync-gate.py` 移除 `docs/modules/` 死锁检查(原因为 init-from-zero.py 创建占位 .gitkeep,但 V11 规范无 stage 写 modules/ 内容,导致 PreToolUse 永远 BLOCK)
  - 真相源迁移:`docs/specs/changes/_module.md`(项目级) + `fact/module.md`(change 级)
  - `references/trap-instructions.yaml` 加 V11-AP17 反例
- **新增资产**:
  - `references/config.example.yaml` / `project-gitignore-template.md` / `state-card.schema.json`(3 份资产 schema 与模板)
  - `templates/ci/v12-gate.yml`(替代 `v11-gate.yml`,rename 而非删除)
  - `scripts/_lib_paths.py` / `check_paths_config.py` / `_todoapp_e2e.py` / `_todoapp_e2e_v2.py` / `_total_verify.py`(5 个新/独立脚本)
  - `skill-markets/fullstack4TraeV11/.gitignore`(本地保护 `case-studies/` 等外部测试项目)
- **case-driven-skill-audit 接入(.agents/skills,非 skill-markets)**
  - **V1.0.0 NEW** — 审计方法论技能,定位"通过实跑 case 评估 skill 真假"而非读文档判定
  - 触发关键词:`case study` / `实跑 case` / `走完整流水线` / `skill 升级调研` / `skill 真假` / `演练收集经验` / `case-driven audit`
  - 包含 SKILL.md + 1 references( `case-2-evidence.md`,case 2 desktop-pet-v11 实跑证据)
  - 详见 [.agents/skills/case-driven-skill-audit/SKILL.md](.agents/skills/case-driven-skill-audit/SKILL.md)
- **auto-task/fullstackselfimproving**
  - 新增 auto-task 协议入口,内容为 fullstack skill 自改进场景的 prompt 模板
  - 配合 `auto-task/daily-vibe-coding` 形成 auto-task 体系
- **audit-cycle 闭环归档(2026-08-17)**:
  - `references/todos/archive/done/2026-08-17-audit-cycle/` 新增 5 个文件:
    - `audit-fix-2026-08-16.md` / `audit-fix-2026-08-17.md` / `audit-fix-2026-08-17-followup.md`
    - `case-2-desktop-pet-v11-audit.md`(case-driven 实跑证据)
    - `mentioned-but-not-parsed-closure.md`(top 5 + 完整 14 条全量验证)
  - `references/todos/audit-cycle-2026-08-17.md` 主文件状态更新
- **工具链更新**:
  - `trap-instructions.yaml` 新增 AP16 + AP17 两条反例
  - `goal-mode/gate/acceptance_manifest.yaml` 加 acceptance_manifest 字段
  - `github-kownledge-helper/agents/.gitkeep` + `references/doc-map-manager-usage.md` 加 agents/ 子目录规范
- **详见**:[skill-markets/fullstack4TraeV11/CHANGELOG.md V11.8.7.1](skill-markets/fullstack4TraeV11/CHANGELOG.md) + [V11-AP17 trap 修复说明](skill-markets/fullstack4TraeV11/references/trap-instructions.yaml)

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