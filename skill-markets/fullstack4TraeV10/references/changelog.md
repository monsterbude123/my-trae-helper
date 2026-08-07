# CHANGELOG

## v10.8.0 (2026-08-05)

**经验吸收整合 — 反踩坑铁律 + 破坏性操作红线 + 严重度分层 + 小任务流线化 + 质疑式验收官**

- **新增** 反踩坑 6 条铁律（SKILL.md §2 V10.8 NEW 标注）
- **新增** 破坏性操作 4 步协议（references/reset-and-verify-protocol.md）
- **新增** 严重度分层 P0/P1/P2/P4（SKILL.md §3 禁止项按场景分组）
- **新增** 小任务流线化门禁链例外（SKILL.md §0 — ≤6 Task + LOW 可跳过 Contract 阶段）
- **新增** 通过依据 3 类分层（references/acceptance-gates-v10.md）
- **新增** `references/bug-workflow.md` — 19 方法论吸收（含 5 步 Intake 防御 / 5 步精简流程 / Ponytail 决策 ladder / 类型系统陷阱 / 反例库）
- **新增** `references/reviewer-templates.md` — reviewer 模板库（验收基准拆解 / 事实证据索要 / Completion Report / 四维验收 checklists）
- **新增** `references/clarify-checklist.md` — Spec 澄清检查清单
- **重构** `agents/reviewer.md` — 质疑式验收官角色（ZERO TRUST / EVIDENCE MANDATORY / ACTIVE FALSIFICATION / REQUIREMENT TRACING 四铁律 + 双轨制证据索要）
- **新增** process-rot-analysis.md §4.5.5 项目特定敏捷流程误删反模式（5 类项目特定信号 + 自检 3 问）
- **新增** process-rot-analysis.md §4.5.6 四类反例共性（V10.8 补丁更新）
- **新增** SKILL.md fullstack4TraeV10 边界声明（通用门禁底线 vs 项目敏捷流程加速通道协同）
- **新增** Article XIV — rot-detector 必跑（Phase 4.5 不可跳过，补遗到 Constitution）
- **修复** phase-gate.py 中文乱码（全面重写 UTF-8 编码）
- **修复** acceptance-audit.py _audit_uiux 函数空行结构异常（约 60 个空行压缩）
- **修复** proactive-scan.py run_deprecated_scan dead code（--no-deprecated-scan 参数被覆盖）
- **修复** complexity-guard.py os 未 import 导致 hook 静默失效
- **修复** session-start.py specs_dir 未定义导致 Step 4 崩溃
- **修复** change-status.py project_root 未定义导致 spec-purge 检测崩溃
- **修复** check_prerequisites.py _check_prereqs 函数 project_root/feature 未传入
- **修复** SKILL.md §6 脚本表缺失 5 个核心脚本（phase-gate / check_prerequisites / code-hygiene / check_integration_contract / acceptance-audit / self-diagnose）
- **修复** SKILL.md L16 §15-§17 断链（改为 §2 腐烂点 15-17）
- **修复** process-rot-analysis.md §4.5.5 编号重复（第二个改为 §4.5.7）
- **修复** project-structure.md ARCHITECTURE.md/DECISIONS.md 断链（改为项目级路径）
- **清理** 删除过时 scenarios 文件 + __pycache__ 目录 + .pyc 文件
- **变更** 版本 10.5.0 → 10.8.0 + Constitution 13 → 14 Articles

## v10.6.0 (2026-08-01)

**Evidence 独立抽检 — 防虚假汇报**

- **新增** SKILL.md §-1.5 D 段 — V10.6 Evidence 独立抽检机制
  - 主上下文对 agent 返回的 evidence 亲自验证（Read file:line ≤50 行）
  - 验证文件存在性 / 内容匹配 / pass_count 一致性
  - 不匹配 = 🛑 REJECT（虚假汇报）+ 计入失败计数
- **新增** 禁止依赖清单（意图声明 / 部分进度 / 之前记忆 / "看起来没问题" / 推测性答案 / 代理解释）
- **新增** 不匹配典型模式（evidence 指向空行 / pass_count 造假 / status ✓ 但文件不存在）
- **变更** 版本 10.5.0 → 10.6.0

## v10.5.0 (2026-07-31)

**rot-reinforcer Cycle 1 实战驱动更新 — 3 新腐烂点修复**

- **新增** `proactive-scan.py` 3 项新 check (5→8 项):
  - `self-aggrandizing-doc` (腐烂点 15) — 抽 state-card/INDEX 中 `INV-XXX` vs spec.md 实际 INV,`doc_claims - spec_actual` 比例 > 30% → 🛑 FAIL
  - `state-card-staleness` (腐烂点 16) — `.state-card.md` mtime (>24h WARN, >72h FAIL) + change 数量一致性
  - `stub-pileup` (腐烂点 17) — `docs/specs/changes/*/` 中只 define.md 的 stub 比例,>40% WARN, >60% FAIL
- **新增** `self-diagnose.py` 第 4 项 check `proactive-v105-coverage` — 验 proactive-scan.py 含 3 新函数 + INV_RE 锚定 + 阈值常量
- **新增** 2 条不可协商 Articles (总数 11→13):
  - **Article XII — 文档诚实 (Document Honesty)** — state-card/INDEX 声称的 INV 必在 spec.md 落地,不可自评"完成"无证据
  - **Article XIII — 骨架是债 (Stub is Debt)** — 🟡 骨架 = 隐性技术债,14 天未推进必冻结或归档
- **新增** 3 个 V10.5 self-test fixture (`scripts/__self_tests__/V10.5-{fixture,staleness-fixture,stub-fixture}/`) + `test_v10_5_fixtures.py` 验证 3 check 均正确报 FAIL
- **新增** `docs/rot-discoveries/.state-card.md` (rot-reinforcer 状态卡) + `2026-07-31-AIGCMediaDesktop.md` (腐烂点发现报告)
- **变更** SKILL.md 10.4 → 10.5 + 哲学段补"诚实而非吹嘘" / "骨感而非堆积" + Constitution 11→13 Articles
- **变更** constitution-template.md 1.1.0 → 1.2.0 + +Articles XII/XIII
- **变更** rot-detector.md 腐烂点参考表 +3 项 (rot #15-#17) + V10.5 升级说明
- **变更** proactive-scan.py: 5 → 8 项 check + 标题 V10.4 → V10.5
- **修复** AIGCMediaDesktop rot #15 (state-card 9→2 跨模块不变量自我吹嘘, 78% 失效) + rot #16 (state-card 47h 未更新 + 2 change 缺失) + rot #17 (骨架 11/19 = 58% 破窗警戒)
- **战绩**: rot-reinforcer Cycle 1 完成,rot-detector 腐烂点覆盖 1-14 → 1-17 (3/17 实战暴露新腐烂点)

## v10.4.0 (2026-07-30)

**实战暴露 5 大腐烂点 — 视觉假阳性 / 自验自签 / 孤儿测试 / 隐式 build / Agent 不主动诊断**

- **新增** 4 条不可协商 Articles (总数 10→14，含 XIV 补遗):
  - **Article IX — TDD 即时** — 改实现/删组件 → 立即同步改测试/删测试
  - **Article X — 异会话验证** — 自评 = self_attested,主上下文必二次抽检
  - **Article XI — 视觉真实验证** — PIL 解码 + 直方图 + 关键区域采样（解决 PNG magic OK 但内容空白假阳性）
  - **Article XIV — rot-detector 必跑** — Phase 4.5 不可跳过（V10.8 补遗到 Constitution）
- **新增** 1 个 Agent: `agents/rot-detector.md` — 主动诊断腐化,不靠用户问
- **新增** Phase 4.5: Proactive Rot Scan（双层）
  - 4.5.1 Self-Diagnose: `self-diagnose.py` (Meta 自我诊断 — 检测器自身无腐烂)
  - 4.5.2 Proactive Scan: `proactive-scan.py` (5 项腐化扫描目标项目)
- **新增** 5 个脚本:
  - `scripts/self-diagnose.py` — Meta 自我诊断（regex/阈值/锚定检测）
  - `scripts/orphan-detector.py` — 孤儿测试/组件检测
  - `scripts/dist-hash-check.py` — Bundle 一致性检查（binary 嵌入 JS chunk hash vs dist/assets）
  - `scripts/proactive-scan.py` — 5 项腐化扫描包
  - `scripts/visual-content-check.py` — 视觉内容深度校验（PIL 解码 + 直方图 + 象限亮度）
- **新增** phase-gate.py 3 个新 phase: `orphan-precheck` / `bundle-check` / `proactive-scan`
- **新增** `references/process-rot-analysis.md` — 腐烂点 9-14 详细分析 + 修复原则
- **新增** `references/reset-and-verify-protocol.md` — Stage 0-3 主上下文自证协议
- **新增** SKILL.md §0 Phase 4.5 段 + §-1.5 §C 视觉证据硬门禁 V10.4 升级 3 层
- **变更** 版本 10.3.8 → 10.4.0 + Constitution 10 → 14 Articles

## v10.3.8 (2026-07-28)

**实战驱动更新 — 主上下文重置与真实验收协议**

- **新增** `references/reset-and-verify-protocol.md` — Stage 0-3 主上下文自证协议（防虚假验收）
- **文档** SKILL.md §1.6 主上下文保护意识（引用 reset-and-verify-protocol）
- **案例** 实战记录 3 个腐烂点（虚假 audit / binary 过期 / mod.rs 缺失）
- **变更** 版本 10.3.7 → 10.3.8

## v10.3.7 (2026-07-28)

**实战驱动更新 — 6 维度审计 + 零残留验证 + drift 检测**

- **新增** `acceptance-audit.py` 第 6 维度 `drift_detect`（contracts/ vs 实际 import/export 漂移扫描，捕获契约/代码命名不一致）
- **新增** `code-hygiene.py --check-bak` 子命令（Article III §3.2 零残留验证，rglob *.bak.* + 非零退出）
- **修复** drift_detect 误匹配 Markdown 表格内 `interface`/`type` 关键词（改为仅扫描 ```typescript 代码块）
- **修复** drift_detect rglob 模式 `*.{ts,tsx}` 改为分别 rglob（Python rglob 不支持 brace expansion）
- **修复** 00-01-foundation 真实漂移 HealthInfo → HealthCheckResponse（contracts 改名匹配后端实现）
- **变更** 验收维度 5 → 6（新增 drift_detect）
- **变更** 版本 10.3.6 → 10.3.7

## v10.3.6 (2026-07-28)

**实战驱动更新 — 00-02 app-shell 推进暴露的腐烂点**

- **新增** `phase-gate.py` V10_STRICT_REVIEW 环境变量开关（默认=1，禁止 fallback，必须 review-latest.md）
- **修复** acceptance-audit artifact_schema 与 API 维度对 api-contracts.md 处理矛盾（纯前端也需创建占位文件）
- **修复** V10 简化 spec.md YAML `v10_drop: tasks.md` 与 artifact-schema.md 强制要求矛盾（记录为待统一）
- **变更** 版本 10.3.5 → 10.3.6

## v10.3.5 (2026-07-28)

**实战驱动 hotfix — 归档 00-01 暴露的 5 P0 腐烂点**

- **修复** `acceptance-audit.py` TODO_PATTERN 移除 XXX（避免 `xxx-0/1/2` 占位符误伤，V10 实战暴露）
- **修复** `SKILL.md` description 矛盾（spec-kit + Trae Work 输入输出明确）
- **修复** `phase-gate.py` review 阶段强制 docs/reports/{feature}/review-latest.md 存在
- **新增** `acceptance-gates-v10.md` §3.2 零残留规则（Article III 禁止 .bak 副本）
- **新增** `SKILL.md` §1.5 reviewer 行加 [MUST] acceptance-audit 注入项
- **变更** 版本 10.3.4 → 10.3.5

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
**新增文件**: references/artifact-schema.md + 5 个 scripts/ + 13 个 templates/（8 hooks + 1 json + 1 readme + 3 scripts）+ ~~scenarios/v9.2-scenario-walkthrough.md~~（V10.8 已删除: V9.2 旧内容腐烂,引用不存在的 agent/脚本）
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
