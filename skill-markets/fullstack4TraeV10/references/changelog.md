# CHANGELOG

## v10.3.4 (2026-07-28)

**腐烂点清理 — Trae Plan/Spec 引用跟随迁移**

- **修复** SKILL.md L4 description / L12 / L17 哲学 / L123-138 阶段叙事：移除"复用 Trae IDE 内置 Plan/Spec"主路径描述，统一为"派生自 spec-kit 五阶段文档驱动"
- **修复** README.md 6 处（设计哲学 mindmap / Phase 1 mermaid / 实战路线 / 版本演进）：Trae /plan、/spec 命令 → spec-kit plan.md/spec.md 格式
- **修复** agents/planner.md 3 处：Trae /plan 输出 → spec-kit plan.md 格式
- **修复** agents/spec-enhancer.md 8 处：双源兼容描述（spec-kit 主路径 + Trae Spec Mode 保留为 fallback）
- **修复** scripts/migrate-v9-to-v10.py L37/L249：AI 重新进入路径从 Trae /spec → spec-kit
- **重命名** scripts/change-status.py `detect_spec_mode()` → `detect_spec_kind()`（语义与 Trae 模式解耦）
- **保留** references/prototype.md 中 Trae Work 引用（真实外部工具）
- **保留** scripts/common.py / templates/spec-template.md 中"借鉴 spec-kit"归属声明（正确）
- **保留** Trae Hook 环境变量（IDE 标准集成）
- **保留** references/changelog.md 中历史 Trae 引用（历史记录不可改写）
- **变更** 版本 10.3.3 → 10.3.4

## v10.3.3 (2026-07-28)

**接入契约 — 后续模块"接入即用"硬门禁**

- **新增** `scripts/check_integration_contract.py`（5 项硬门禁：直 fetch / 直 keydown / 缺 ModuleDef / 缺 Rust Module trait / 事件命名）
- **新增** phase-gate `--phase integration-contract` 阶段门禁
- **新增** AIGCMediaDesktop foundation 7 处契约：A/B/C/D/E
  - EventPayloads 扩展点 + `<domain>:<action>` 命名约定
  - `registerShortcut()` 公开 hook
  - `createModuleSlice` 工厂 + 自动 reset()
  - 后端 `Module` trait + `ModuleRegistry`
  - `EmptyState` 泛化（title/description/icon/action）
- **新增** 09-models 接入契约 demo（不替换旧 api-client.ts，新增 api/apiClient.ts 作为新模块范例）
- **文档** foundation-integration-guide.md §11-14 接入契约总览 + 09-models demo + V10 门禁说明 + 工作流
- **变更** 版本 10.3.2 → 10.3.3

## v10.3.2 (2026-07-28)

**腐烂点修复 — cargo test regex 误匹配**

- **修复** `acceptance-audit.py:99-110` cargo test 输出正则误匹配函数名 `...marks_failed` → "1 failed" 误报；改为严格匹配 `test result: ok. N passed; M failed` 格式
- **修复** 同一行 npm/jest 兼容（`Tests: N passed`）
- **变更** 版本 10.3.1 → 10.3.2

## v10.3.1 (2026-07-28)

**腐烂点修复 — 验收脚本判定逻辑**

- **修复** `acceptance-audit.py:107-115` cargo test 退出码 101 但 0 failed → 警告但 PASS（之前误判 FAIL）
- **修复** `acceptance-audit.py:176-177` api 维度加端口 listen 探测（防止后端没起 → 0/5 假 PASS）
- **修复** `acceptance-audit.py:53-57, 90` Tauri 项目 cargo test cwd 改为 src-tauri（之前报 `could not find Cargo.toml`）
- **变更** 版本 10.3.0 → 10.3.1

## v10.3.0 (2026-07-27)

**实战驱动更新 — AIGCMediaDesktop 实战暴露的腐烂点**

- **新增** `scripts/acceptance-audit.py`（真实验收脚本）— AIGCMediaDesktop 92 分 AI 自评能蒙混过关的根因
- **新增** `check_prerequisites.py --phase acceptance-precheck` — spec.md `## E2E` 段 ≥50% 勾选 + 0 ⏳
- **新增** `acceptance-audit.py --strict-artifacts` artifact_schema 维度 — 校验 spec.md + tasks.md + 4 件 contracts（events.md 双名兼容）
- **兼容** events.md ↔ event-contracts.md（acceptance-audit + spec-knowledge-extract 双名循环）
- **兼容** docs/reports/review-latest.md ↔ acceptance-scorecard-{date}.md（phase-gate._find_review_report fallback）
- **兼容** contracts/test-skeleton/ ↔ contracts/test-skeleton.md（phase-gate._has_tests 接受 .md 单文件）
- **文档** SKILL.md §-1.5 机械验证协议（必读，引用 agent-机械验证.md + acceptance-audit.py）
- **文档** references/contract-first.md §5 扩展件（项目自定义件命名规范）
- **文档** references/artifact-schema.md §二 工件定义表新增 define / prototype / review 3 行
- **变更** 验收维度 4 → 5（新增 artifact_schema）
- **变更** 版本 10.2.0 → 10.3.0

## v10.2.0 (2026-07-27)

- SKILL.md §-1.5 机械验证协议（初版）
- 5 维度软门禁 → 5 维度硬门禁

## v10.1.0 (2026-07-26)

- **变更** review_report.md 字符串匹配 → 4 维度量化打分（PASS/FAIL/N/A）
- **变更** 阶段门禁改为硬门禁（任一维度 < PASS = REJECT 整个 change）

---

## v9.2.0

**Stage 1: OpenSpec 思想内化**
- **哲学段**：SKILL.md 新增 "fluid not rigid / specs grow / delta over rewrite / enablers not gates" 五原则
- **Delta Spec**：spec-writer 改为 Brownfield 场景写 ADDED/MODIFIED/REMOVED/RENAMED
- **Spec 累积生长**：reviewer Step 6 "Spec 累积合并"（delta → 主 spec）
- **Fluid 工作流**：工件依赖定义为"使能器"（新 references/artifact-schema.md）
- **机械化流程吸收**：`#### Scenario:` 格式铁律、MODIFIED 完整复制铁律、tasks.md checkbox 格式、proposal 模板

**Stage 2: 确定性脚本**
- `scripts/spec-validate.py` — Spec 格式机械验证
- `scripts/spec-merge.py` — Delta 机械合并到主 Spec
- `scripts/change-status.py` — 文件系统真相读取

**Stage 3: Hook 体系移植与安装脚本**
- `scripts/install-hooks.py` — 从技能包安装 hooks 到目标项目（**新增核心脚本**）
- 移植 8 个 .ps1 Hook 脚本到 `templates/hooks/`: session-start / doc-sync-gate / contract-gate / spec-validate-hook / auto-test / drift-detect / tasks-integrity / complexity-guard
- 移植 3 个 .py 支持脚本到 `templates/scripts/`: env-init / render-cockpit / log-agent-prompt
- 移植 hooks.json + README.md 到 `templates/hooks/`
- 所有移植文件已更新版本引用: V8→V9, fullstack4traev8→fullstack4traev9, docs/specs/changes→docs/specs, proposal.md→define.md

- `scripts/migrate-v8-to-v9.py` — V8 项目一键迁移到 V9.2（hooks 安装 + 目录拍平 + state-card 转换 + 清理）

**修改文件**: SKILL.md（35 处 + §6.1 Hook 安装段 + §6 脚本表）+ 4 个 agent + intake + changelog
**新增文件**: references/artifact-schema.md + 5 个 scripts/ + 13 个 templates/（8 hooks + 1 json + 1 readme + 3 scripts）+ scenarios/v9.2-scenario-walkthrough.md
**版本号**: 9.1.0 → 9.2.0

## v9.1.0
- 回补 5 项 V8 核心协议（面向 Trae Work 适配，内嵌而非新建文件）：
  - **Completion Report 协议**：每个 Agent 末尾强制产出结构化交付报告（§4），主上下文机械验证
  - **AOP 移交自检**：每个 Agent 末尾 3 项移交前自问清单
  - **委派注入模板**：SKILL.md §1.5 委派注入表，主上下文委派时强制注入 [MUST] 项
  - **Report-Growth 错误升级**：§3 禁止项新增"Agent 异常写入 `.trae/logs/report-growth.jsonl`"
  - **Refactor 回流隔离**：implementer 追加 L1 物理隔离旧产物到 `_invalidated/`
- intake agent：Completion Report 含 `dedup_result` 字段，AOP 自检强制去重搜索
- SKILL.md 版本号 9.0.0 → 9.1.0，描述更新为"面向 Trae Work 优化，保留 V8 核心协议"
- 文件数不变（30），总行数增加约 220 行（均在已有文件末尾）

## v9.0.0
- 采用 OpenSpec 格式替代自定义 Spec 格式
- 6→7 阶段流水线：新增 Define 阶段（合并 Proposal+Plan+Closure）
- 子代理 6→7：新增 definer agent
- references 9→16：新增 define-format / bug-workflow / artifact-lifecycle，增强 acceptance-gates / drift-detect
- SKILL.md 从 84 行扩至 121 行，铁律 4→8 条，禁止项 4→8 条
- 补齐核心门禁：5 维度量化打分、Visual Gate、归档 3 门禁、回流判定树、Bug 快速链、Cockpit 启动感知、DELTA ONLY、工件生命周期
- 保留 V8 核心能力的 90%+，文件数较 V8 减少 31%
