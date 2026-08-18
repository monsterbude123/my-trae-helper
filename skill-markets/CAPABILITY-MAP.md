# 技能市场能力地图

> 单一事实来源。新增技能前先查此地图，确认不重复。脚本复用前先查共享注册表。

> **2026-08-15 升级**：fullstack4TraeV11 V11.8.4 提交准入最小集与全量验收分层（Stage 3.5/4.5 异步化），Stage 6 重构为 4 层分层决策框架（V11.8.3）。详见各 skill CHANGELOG。
>
> **2026-08-16 升级**：fullstack4TraeV11 V11.8.5 协议层承诺 → 脚本落地（13/14）— 新增 3 个脚本 + 6 个 references + 79 单测。详见 V11.8.5 CHANGELOG。
>
> 维护规则：新增/删除/改依赖 → 同步更新此文件。地图与 SKILL.md 不一致时，以地图为准。
>
| find-skills V1.0 接入 | 2026-08-18 | vercel-labs/skills 同步 SKILL.md 入仓(单文件纯文档),src/execution/skill-install-control.mjs 委托 installer.mjs | [skill-markets/find-skills/SKILL.md](find-skills/SKILL.md) + [src/execution/skill-install-control.mjs](../../src/execution/skill-install-control.mjs) |

> **Last Updated**: 2026-08-16（聚合归档 V11.8.5 脚本落地）

| V11.8.5 | 2026-08-16 | project-priority-resolver / secrets-detector / bug-state-machine-validator + todos 全套 | [scripts/README.md L40-42](fullstack4TraeV11/scripts/README.md) + [references/todos/README.md §2](fullstack4TraeV11/references/todos/README.md) |
| V11.8.5.P1 | 2026-08-16 | commit-minimum-check.py + 4 项准入校验(typecheck/spot-check/admin 探针/lint 预存) | [scripts/commit-minimum-check.py](fullstack4TraeV11/scripts/commit-minimum-check.py) + [tests/unit/test_commit_minimum_check.py](fullstack4TraeV11/tests/unit/test_commit_minimum_check.py) |
| V11.8.6 | 2026-08-16 | V12 物理隔离渐进:init-from-zero --layout v12-preview + process-layer-guard.sh + stage-gate --reset-to + 4 个 agent 落位规则 | [templates/change-dir-layout-v12-preview.md](fullstack4TraeV11/templates/change-dir-layout-v12-preview.md) + [templates/hooks/process-layer-guard.sh](fullstack4TraeV11/templates/hooks/process-layer-guard.sh) + [tests/unit/test_stage_gate_reset.py](fullstack4TraeV11/tests/unit/test_stage_gate_reset.py) |
| audit-fix-2026-08-16 | 2026-08-16 | guard-smith audit B 方案 3 件修补:guard-gate-smith §1.1.1 + skill-registration-guard docstring + AGENTS.md §1.11 增补 | [skill-markets/guard-gate-smith/SKILL.md §1.1.1](guard-gate-smith/SKILL.md) + [src/guards/skill-registration-guard.mjs 顶部 docstring](src/guards/skill-registration-guard.mjs) + [AGENTS.md §1.11 增补条款](AGENTS.md) |
| mentioned-but-not-parsed closure | 2026-08-16 | top 5 全量验证 — 5/5 已落地(批修 + V11.8.5.P1 + V11.8.6 三批 commit 累积) | [references/todos/mentioned-but-not-parsed-closure.md](fullstack4TraeV11/references/todos/mentioned-but-not-parsed-closure.md) + [audit-history §2 top 5](fullstack4TraeV11/references/todos/audit-history/2026-08-16-mentioned-but-not-parsed.md) |
| V12.0.0 主版本升级 | 2026-08-16 | V12 ADR ACCEPTED → 8 步实施落地(SKILL.md frontmatter 11.5.0 → 12.0.0 + init-from-zero --layout 默认 v12-preview + --upgrade-to-v11 子命令 + 5 个 references/skill 文件 V12 默认化) | [V12-ADR-DRAFT.md](fullstack4TraeV11/references/todos/v12-physical-isolation/V12-ADR-DRAFT.md) + [CHANGELOG.md V12.0.0 条目](fullstack4TraeV11/CHANGELOG.md) |

---

## 一、技能索引

### L0 基座（无外部依赖，独立可用）

| 技能 | 类型 | 一句话 | 脚本/工具 |
|------|------|--------|----------|
| [coding-xinfa](coding-xinfa/SKILL.md) | 纯Skill | 通用编码心法 + 精简 Goal Mode 提要 + 完成审计 + 风格规范（三角互引总目录） | 无（related: goal-mode, ponytail4Trae） |
| [goal-mode](goal-mode/SKILL.md) | Agent驱动 | 目标追逐完整协议 — 六步审计门禁 + Agent 编排（goal-mode, goal-auditor, goal-planner） | 无（related: coding-xinfa, ponytail4Trae） |
| [ponytail4Trae](ponytail4Trae/AGENTS.md) | 纯Skill | 懒人开发模式 — 最简实现 + 过度工程审查 + ponytail: 标记技术债 + 快速参考 | 无（子Skill: ponytail, review, debt, help；related: coding-xinfa, goal-mode） |
| [gitnexus4Trae](gitnexus4Trae/AGENTS.md) | 纯Skill | GitNexus 代码智能 — 探索、调试、影响分析、重构、CLI | 无（子Skill: cli, debugging, exploring, guide, impact-analysis, refactoring） |
| [browser-use-cloud](browser-use-cloud/SKILL.md) | 纯Skill | Browser Use 浏览器自动化 — 网页抓取、自动操作、结构化提取 | api_check.py, batch_sessions.py, structured_extract.py, webhook_server.py |
| [openapi-doc-exporter](openapi-doc-exporter/SKILL.md) | 纯Skill | OpenAPI → Markdown 文档导出，框架无关 | render_md.py, split_by_prefix.py, validate_openapi.py |
| [deep-research](deep-research/SKILL.md) | 纯Skill | 多源深度研究 — firecrawl/exa MCP 综合 + 引用报告（V1.0 NEW 2026-08-13 蒸馏自 ECC .agents/skills/deep-research，按 §11 接入治理） | 无（依赖 MCP: firecrawl 或 exa，至少 1 个） |
| [trae-professional](trae-professional/SKILL.md) | 纯Skill | TRAE IDE / TRAE Work / TRAE APP 专业知识库（2026-08-14 同步 docs.trae.cn 全 22 个分类）| 无 |
| [product-teardown](product-teardown/AGENTS.md) | 纯Skill | 产品拆解分析 — 6 维度解构 + PRD 生成 | 无（子Skill: analyze, prd） |
| [vision-audit](vision-audit/SKILL.md) | 纯Skill | UI/UX 视觉验收 — Qwen3-VL 分析截图 | vision-audit.mjs, vision-audit.py |
| [shuxia-novel-engine](shuxia-novel-engine/SKILL.md) | Agent驱动 | 小说创作引擎 — 世界观构建、剧情编织、一致性审计 | 12 脚本（check, combat, drama, enumerate, evaluate, ripple 等） |
| [modelscope-assistant](modelscope-assistant/SKILL.md) | 纯Skill | 魔搭社区助手 — 模型搜索、SDK 调用、微调指导 | mymodelscope/ Python 库 + scan-models.ps1 |
| [minimax-multimodal](minimax-multimodal/SKILL.md) | 纯Skill | MiniMax(海螺 AI)开放平台多模态 — 6 大模态可跑通 Python 客户端(文本/图像/视频/语音/音乐/视觉) | 12 脚本(_client + 6 模态 + verify_all + run_all + 4 check_*) + 7 references + 31 pytest 测试;**2026-08-14 实跑 PASS** — 国内 `api.minimaxi.com` 真实 Key 验证 6/6 模态端到端通过(产物落 `output/`) |
| [test-experience](test-experience/SKILL.md) | 纯Skill | **⚠ DEPRECATED** → acceptance-discipline（兼容壳）| 无 |
| [test-partition-runner](test-partition-runner/SKILL.md) | 纯Skill | **⚠ DEPRECATED** → acceptance-discipline（兼容壳）| 无 |
| [e2e-module-audit](e2e-module-audit/SKILL.md) | 纯Skill | **⚠ DEPRECATED** → acceptance-discipline（兼容壳）| 无 |
| [doc-map-manager](doc-map-manager/SKILL.md) | 纯Skill | 文档地图管理器 — 结构化索引构建 + 多模式查询（grab/lookup/fuzzy/semantic/file） | build-index.py, query-index.py |
| [vibe-coding-standards](vibe-coding-standards/SKILL.md) | 纯Skill | Vibe Coding 组件编写原则 — AGENTS.md/Rules/Skills/Subagents 结构规范与防击穿策略 | 无 |
| [project-rules-gate](project-rules-gate/SKILL.md) | 纯Skill | 项目级 Rules 强制加载与子代理门禁 — 把 .trae/rules/ 锻造为 project_rules_skills 入口 skill + 强制 sub-agent [PROJECT-RULES-GATE] 头。V11 同名协议独立分发版(v0.2 加 --move 物理移走 + frontmatter 自动注入) | forge_project_rules_skill.py |
| [skill-optimization-method](skill-optimization-method/SKILL.md) | 纯Skill | 技能包优化升级方法论 — 体积诊断 + 外部对标 + 缺口对照 + 最小修复（项目级） | 无 |
| [session-distiller](session-distiller/SKILL.md) | 纯Skill | 会话蒸馏器 — 从完整会话历史中提炼高质量方法论、最佳实践和可复用技能包 | 无 |
| [trae-local-data-export](trae-local-data-export/SKILL.md) | 纯Skill | Trae IDE 本地数据导出 — 整合 ZedeX/trae-chat-decrypt + cgint/ai-data-extraction，产出 JSON/TXT/SQLite 三大产物 | 7 脚本（extract_key ×2 / decrypt_db / verify / export_sessions / extract_trae_jsonl / sanitize_export） |
| [agent-dev-control-kit](agent-dev-control-kit/SKILL.md) | 纯Skill | Agent 开发控制体系 — 三层控制(Execution+Guard+Gate) + 快速失败 + 标准模板 | 无（模板文件在 templates/）|
| [github-kownledge-helper](github-kownledge-helper/SKILL.md) | 纯Skill | 本地 GitHub 仓库管家 — ADD/UPDATE/UPDATE-ALL/QUERY/SYNC-TO 五大工作流 + 命令模式 + 踩坑记录；TS CLI 化（pnpm ghh add/update/sync-to/sync-docs/verify-docs）；项目专属 | 22 references(13 新增:workflows-baseline/manifest-schema/doc-map-manager-usage/env-loadenv/reply-conventions/first-run-checklist/skill-evolution/task-start-probe/project-paths/git-workflow-rules/doc-index-rules/answer-rules/safety-cleanup;+9 原有:commands/workflows/workflows-aggregate/workflows-protocols/workflows-sync-to/cli-development/tdd/doc-verify/pitfalls)；**2026-08-16 全量沉淀**:AGENT.md + project-rules.md → 13 个 references(通用约定沉淀,具体项目配置仅作示例段)；**软依赖**: doc-map-manager（独立 Skill 已发布，CLI 落本项目根） |
| [find-skills](find-skills/SKILL.md) | 纯Skill | 帮用户发现并安装 agent skill — "how do I do X" / "is there a skill for X" / "can you do X" 等意图触发。2026-08-18 从 [vercel-labs/skills](https://github.com/vercel-labs/skills) 同步入仓 | 无(单 SKILL.md 文件,纯文档,无脚本) |

### L1 集成层（整合 L0 能力）

| 技能 | 类型 | 一句话 | 依赖 |
|------|------|--------|------|
| [acceptance-discipline](acceptance-discipline/SKILL.md) | Agent驱动 | 统一验收体系 — 单测/集成/E2E/性能/安全/门禁 | test-experience, e2e-module-audit, test-partition-runner（已整合） |

### L2 编排层（依赖 L1）

| 技能 | 类型 | 一句话 | 依赖 |
|------|------|--------|------|
| [fullstack4TraeV9](fullstack4TraeV9/SKILL.md) | Agent驱动 | 全栈文档驱动开发 v8 — 10 Agent 流水线 + 驾驶舱 + 圆桌 + 漂移回流 + 依赖自检 | **硬依赖**: acceptance-discipline；**软引用**: ponytail4Trae, gitnexus4Trae, doc-map-manager |
| [fullstack4TraeV9](fullstack4TraeV9/SKILL.md) | Agent驱动 | 全栈文档驱动开发 v9 — OpenSpec 驱动 + 7 阶段流水线 + Contract-First + TDD + 漂移检测（⚠ V10 已替代） | **硬依赖**: acceptance-discipline；**软引用**: ponytail4Trae, gitnexus4Trae, doc-map-manager |
| [fullstack4TraeV10](fullstack4TraeV10/SKILL.md) | Agent驱动 | 全栈文档驱动开发 v10 — 复用 Trae 内置 Plan/Spec + 5 阶段 + 四维验收 + 铁律分层（V10.12.2 含：§0.5.1 同类约定 10 项 + §0.10 启动验证可见产物 + skeptical-validation-protocol 质疑性校验 + reviewer §Step 2.4/2.5/2.6 Test Plan Gate + 产品侧验收 + 自动循环 + reason-classifier.py 抽象理由检测 + test-plan.md + test-plan-example.md）| **硬依赖**: acceptance-discipline；**软引用**: ponytail4Trae, gitnexus4Trae, doc-map-manager, visual-evidence-discipline, screenshot, frontend-backend-contract-alignment, playwright-best-practices, browser-use-cloud |
| [fullstack4TraeV11](fullstack4TraeV11/SKILL.md) | Agent驱动 | 全栈文档驱动开发 v11 — 13 stage + Flow 层 Registry(五表) + 3 层控制(Gate/Guard/Execution) + V11.6.0 AC 核销门禁(取代评分) + V11.7.0 贾维斯门禁守护(防 agent 改标准,协议+白名单+hash锁)+ Stage 4 Review → ac-gate.py + L-module/app/system 分层模型 + 17 反例(3 贾维斯)| **硬依赖**: acceptance-discipline; **软引用**: ponytail4Trae, gitnexus4Trae, doc-map-manager; **内化**: visual-evidence-discipline, frontend-backend-contract-alignment, ui-ux-pro-max |
| [game-production-kit](game-production-kit/SKILL.md) | 纯Skill | 游戏制作工具箱 — 7 阶段编排器（引擎确认→剧情→素材→脚本→门禁→构建→部署），引擎可替换架构。内含 7 子技能 | 子技能: game-story-design, game-asset-pipeline, game-quality-gate, voice-character-design, voice-acting-skill, webgal-scripting, webgal-engine-build |

### L3 配置模板（绑定 L0~L2）

| 技能 | 类型 | 一句话 | 绑定 |
|------|------|--------|------|
| [fullstack-auto](fullstack-auto/SKILL.md) | 配置模板 | 项目级 `.trae/` 配置一键部署 | fullstack + coding-xinfa + goal-mode + GitNexus + ponytail |

### 独立群岛（内部密集交叉，与外部无关）

| 技能 | 类型 | 一句话 | 规模 |
|------|------|--------|------|
| [comfyui-api-skills](comfyui-api-skills/SKILL.md) | 纯Skill | ComfyUI 视频制作全流程 — 15 子技能编排 | 15 子Skill + 10 脚本 + lib/ 共享库 |
| [trae-security-review](trae-security-review/SKILL.md) | Agent驱动 | 双引擎安全审查 — AI 驱动的代码安全审查 + Skill 目录静态扫描（含 19 类平台兼容性识别） | 2 Agent + 4 脚本 + 3 参考文档 + 2 lib |
| [vibe-coding-diagnosis](vibe-coding-diagnosis/SKILL.md) | 纯Skill | Vibe Coding 项目合规自检诊断 — 三步流程(定类型→套矩阵→出诊断)，9类项目 × 6维度(A-F) × 体量分级 | 3 参考文档 + 1 模板 |
| [docsify-doc-builder](docsify-doc-builder/SKILL.md) | 纯Skill | UE 5 风格 docsify 文档系统 — 顶栏/多级分类/面包屑/右侧页内目录 + Mermaid 全屏/导出 + Markmap 思维导图（默认全部展开） | 1 SKILL + 4 ps1/sh 脚本（init-docs/serve/check-env/generate-sidebar）+ 6 模板（index.html/custom.css/_sidebar/_navbar/README/logo.svg） |

### DEPRECATED 兼容壳（2026-08-14 聚合归档）

> 以下 skill 已并入上层 skill，仅保留**根级独立 SKILL.md + redirect 兼容壳**用于向后兼容触发词。CLI `add` 时应被识别为 DEPRECATED 并引导用户改用上层 skill。

| 兼容壳 | 重定向目标 | 归档原因 |
|--------|-----------|---------|
| [test-experience](test-experience/SKILL.md) | [acceptance-discipline](acceptance-discipline/SKILL.md) | 已整合进 `agents/unit-test-agent.md` + `references/bad-test-cases.md` |
| [test-partition-runner](test-partition-runner/SKILL.md) | [acceptance-discipline](acceptance-discipline/SKILL.md) | 已整合进 `agents/blockage-resolver-agent.md` |
| [e2e-module-audit](e2e-module-audit/SKILL.md) | [acceptance-discipline](acceptance-discipline/SKILL.md) | 已整合进 `agents/e2e-audit-agent.md`（双工作流） |
| [skills-security-scan](skills-security-scan/SKILL.md) | [trae-security-review](trae-security-review/SKILL.md) | 扫描能力迁入 `scan_skills_dir.py V2.1`（8 类 + 三层白名单）；平台识别迁入 `scripts/lib/platform_detector.py` |

### 游戏制作群岛（单一 Kit 入口，内部 7 子技能）

| 技能 | 类型 | 一句话 | 依赖 |
|------|------|--------|------|
| [game-production-kit](game-production-kit/SKILL.md) | 编排器 | 游戏制作工具箱 — 7 阶段编排器（引擎确认→剧情→素材→脚本→门禁→构建→部署），引擎可替换。Phase 0/1/2/4 引擎无关，Phase 3/5/6 按引擎路由 | 子技能: game-story-design, game-asset-pipeline, game-quality-gate, voice-character-design, voice-acting-skill, webgal-scripting, webgal-engine-build |
| [webgal-create-deploy-skill](webgal-create-deploy-skill/SKILL.md) | 遗留包装 | WebGAL 创建部署 — 已重构为 game-production-kit | → `game-production-kit` |

---

## 二、共享能力注册表

> 以下脚本/工具被多个技能包引用。新增脚本前先查此表，避免重复造轮子。

| 能力 | 提供者 | 消费者 | 类型 | 说明 |
|------|--------|--------|------|------|
| 视觉验收 | `vision-audit/scripts/vision-audit.mjs` | acceptance-discipline, e2e-module-audit, fullstack-auto | Node.js 脚本 | Playwright 截图 → Qwen3-VL 分析 |
| 视觉验收 (Python) | `vision-audit/scripts/vision-audit.py` | acceptance-discipline | Python 脚本 | 同上，Python 版，支持 --resize 缩放 |
| 线框图识别 | `vision-audit/scripts/vision-audit.py --describe` | vision-audit（内部） | Python 模式 | 截图 → ASCII 线框图；VL 不可用时降级输出 MCP read_media_file 指令 |
| 项目 Rules 锻造器 | `project-rules-gate/scripts/forge_project_rules_skill.py` | fullstack4TraeV11（init-from-zero.py --rules-as-skill 等价）, 任何想给子代理加规则门禁的项目 | Python 脚本 | 把 .trae/rules/ 收纳为 .trae/skills/project_rules_skills/ 入口 skill + 改写 README 为强制入口 |
| 项目环境初始化 | `fullstack4TraeV7/templates/scripts/env-init.py` | fullstack-auto | Python 脚本 | 一键初始化项目 .trae/ 配置 |
| 驾驶舱渲染 | `fullstack4TraeV7/templates/scripts/render-cockpit.py` | fullstack4TraeV7（内部） | Python 脚本 | 渲染 Cockpit 状态卡 |
| ComfyUI API 客户端 | `comfyui-api-skills/scripts/lib/comfy_client.py` | comfyui 全部 15 子技能 | Python 库 | ComfyUI REST API 封装 |
| ComfyUI 工作流缓存 | `comfyui-api-skills/scripts/lib/workflow_cache.py` | comfyui-api, comfyui-workflow-builder | Python 库 | 工作流 JSON 缓存 |
| ComfyUI 知识库 | `comfyui-api-skills/scripts/lib/web_kb.py` | model_kb.py | Python 库 | Web 知识库爬取 |
| 文档索引构建 | `doc-map-manager/scripts/build-index.py` | fullstack4TraeV7（doc-updater + reviewer） | Python 脚本 | 文档增量索引 + DOC SYNC 缺口检测 + --git-diff |
| 文档索引查询 | `doc-map-manager/scripts/query-index.py` | fullstack4TraeV7（全部 6 agent） | Python 脚本 | --grab/--lookup/--fuzzy/--semantic/--file 五模式查询 |
| 技能变更控制 | `src/execution/skill-change-control.mjs` | create/init 命令 | Node.js 模块 | 新建/修改/删除技能（CP1~CP6 风险判定+备份+回滚+审计） |
| 技能安装控制 | `src/execution/skill-install-control.mjs` | add/remove/update 命令 | Node.js 模块 | 安装/卸载技能（CP1~CP6 依赖验证+冲突检查+备份+审计） |
| 技能安全守卫 | `scripts/skill-security-guard.py` | verify 命令 + Git hooks | Python 脚本 | 调用 trae-security-review/scan_skills_dir.py + 真实风险检测 |
| 技能结构守卫 | `scripts/skill-structure-guard.py` | verify 命令 + Git hooks | Python 脚本 | 目录命名 + SKILL.md frontmatter + 铁律数量 |
| 技能依赖守卫 | `src/guards/skill-dependency-guard.mjs` | verify 命令 + Git hooks | Node.js 模块 | 硬依赖完整性 + 软依赖降级影响 |
| 技能能力守卫 | `scripts/skill-capability-guard.py` | verify 命令 + Git hooks | Python 脚本 | 脚本去重 + CAPABILITY-MAP.md 同步 |
| **技能注册表守卫**（NEW 2026-08-14 §3 收紧方案 A）| `src/guards/skill-registration-guard.mjs` | pre-commit / pre-push / L3 PR | Node.js + yaml 包 | 校验 `registry/skills.yaml` 完整性:每个根 skill 必带同名 guard + gate 注册,script/hook 文件存在,maintainer=guard-smith 白名单 |
| **Guard 路由器**（NEW 2026-08-14 §3 收紧方案 A）| `scripts/guard-router.mjs` | pre-commit step 3 + verify | Node.js + yaml 包 | 按 skill 名查 `registry/skills.yaml` → 依次执行该 skill 注册的 guards(每个 skill 自治 guard 雏形) |
| **Skill 专属守卫 wrapper**（NEW 2026-08-14 §3 拆分方案 A）| `scripts/<name>-guard.py` × 47 | guard-router 调用 | Python wrapper + importlib | 每个 skill 自带一个 guard wrapper,通过 importlib 加载共享的 structure/security 守卫并合并结果。模板由 `scripts/forge-skill-guard.py` 生成,杜绝 47 份风格漂移 |
| **Forge 模板生成器**（NEW 2026-08-14 §3 拆分方案 A）| `scripts/forge-skill-guard.py` | 手动 / guard-smith agent | Python | 接收 skill 名列表 → 生成对应的 scripts/<name>-guard.py。支持 `--all` 批量 / `--dry-run` 预览 |
| **守卫共享工具**（NEW 2026-08-14 §3 拆分方案 A）| `scripts/_guard_lib.py` | wrapper 内部使用 | Python | 提供 `cli_main(check_fn, label)` 统一入口:JSON 输出 + exit 0/1 + 自动去重 warnings |
| **AC 核销门禁**（V11.6.0+ NEW）| `skill-markets/fullstack4TraeV11/scripts/ac-gate.py` | V11 Stage 4 Review + 任何用 V11 的项目 | Python | 6 列矩阵 G1-G5 校验(G1 矩阵段存在 / G2 ≥1 行有效 / G3 逐行核销 / G4 spec 全覆盖 / G5 TC 防编造),任一 FAIL = BLOCK,取代 4 维评分制 |
| **贾维斯 gate installer**（V11.7.0+ NEW）| `skill-markets/fullstack4TraeV11/scripts/gate-installer.py` | V11 目标项目初始化 / 分层新增 | Python | 读 V11 `registry/gates.yaml` 按 layer(docs/module/app/system)生成 `gates/gate-config.json` + `.husky/pre-{commit,push}`(已注入 hash 锁 prelude),仅贾维斯 sub-agent 可调 |
| **贾维斯 hash 锁**（V11.7.0+ NEW）| `skill-markets/fullstack4TraeV11/scripts/gate-integrity-guard.py` | V11 hooks 前置 + 贾维斯 `gate-installer` 时机② | Python | `--generate` 签 sha256 锁 / `--verify` 校验(V11.7.0 P0 漏洞堵:BLOCK 状态下默认拒绝重签,需 `--force --reason "[JARVIS-DELEGATION] 编号"`)|
| **V11 文档入口同步工具**（V11.7.0+ NEW）| `skill-markets/fullstack4TraeV11/scripts/v11-doc-sync.py` | V11 升级时 + CI `v11-doc-check.yml` | Python | `--sync` 批量给文档加 V11.x 入口标记(L1 完整 8 行 / L4 极简 1 行) / `--check` 校验全 V11 文档含标记 / `--mark` 自定义入口文本 |
| **V11 PR 文档入口标记 CI**（V11.8.0+ NEW）| `.github/workflows/v11-doc-check.yml` | V11 改动 PR 自动跑 | yml | paths filter `skill-markets/fullstack4TraeV11/**` → `python v11-doc-sync.py --check` → missing=0 PASS / missing>0 BLOCK |
| **V11 PR 安全扫描 CI**（V11.8.0+ NEW）| `.github/workflows/v11-security-check.yml` | V11 改动 PR 自动跑 | yml | paths filter `skill-markets/fullstack4TraeV11/**` → `python trae-security-review scan_skills_dir.py` → PASS fail = exit 0 / BLOCKED/WARNING = 评论 + exit 1 |
| **技能文档同步门禁**（2026-08-15 NEW 横切守卫）| `scripts/doc-sync-guard.py` | pre-commit Step 7 | Python stdlib + subprocess 调 git diff/show | 横切守卫(2026-08-15 NEW)— 每次 commit 检查:若改了某个 skill 的 "实质性内容"(SKILL.md / references/*.md / scripts/* / agents/*.md 语义行 > 7 或 SKILL.md frontmatter 关键字段变更),要保证项目侧 6 项说明文档(README/AGENTS/CHANGELOG/CAPABILITY-MAP/SECURITY-MAP/registry/skills.yaml)+ skill 一级"给人类看的说明性文档"(README/AGENTS/CHANGELOG/INDEX/GUIDE)同步更新,否则硬阻断(exit 1)。脚本支持 `--self-test` 自检模式跑 6 个反例(实质变更/注释/空行/frontmatter/全部同步/子目录 README)。registry/skills.yaml 注册 meta skill `doc-sync`(白名单跳过 skill-markets 目录校验) |

---

## 三、依赖关系图

```
L0 基座（独立可用，无外部依赖）
┌──────────────────────────────────────────────────────────────┐
│ coding-xinfa   goal-mode   ponytail4Trae   gitnexus4Trae     │
│ browser-use-cloud   openapi-doc-exporter   trae-professional  │
│ product-teardown   vision-audit   shuxia-novel-engine        │
│ Voice-Acting-Script-Skill   modelscope-assistant             │
│ doc-map-manager   agent-dev-control-kit                      │
│ ⚠ test-experience  ⚠ test-partition-runner  ⚠ e2e-module-audit │
└──────────────────────────────────────────────────────────────┘
        │                    │                    │
        │   (已整合)          │   (已整合)          │   (已整合)
        ▼                    ▼                    ▼
┌──────────────────────────────────────────────────────────────┐
│ L1 集成层                                                     │
│ acceptance-discipline ← 整合 test-experience + e2e + partition│
│   agents: unit-test, integration-test, e2e-audit,             │
│           perf, security, gate-keeper, blockage-resolver      │
└──────────────────────────────────────────────────────────────┘
        │
        │ 硬依赖（阶段 40-accept 委托）
        ▼
┌──────────────────────────────────────────────────────────────┐
│ L2 编排层                                                     │
│ fullstack4TraeV7 → 软引用 ponytail, gitnexus                  │
│   agents: intake, proposal, spec, contract, planner,          │
│           implementer, reviewer, debugger, doc-updater        │
│ fullstack4TraeV9 → 软引用 ponytail, gitnexus                  │
│   agents: intake, definer, spec-writer, contract-writer,       │
│           implementer, reviewer, debugger                      │
│ fullstack4TraeV10 → 软引用 ponytail, gitnexus                  │
│   agents: planner, spec-enhancer, contract-writer,             │
│           implementer, reviewer, debugger                      │
└──────────────────────────────────────────────────────────────┘
        │
        │ 配置绑定
        ▼
┌──────────────────────────────────────────────────────────────┐
│ L3 配置模板                                                   │
│ fullstack-auto ← 绑定 fullstack + coding-xinfa + goal-mode    │
│                       + gitnexus + ponytail                   │
└──────────────────────────────────────────────────────────────┘

独立群岛（密集内部交叉，不连外部）
┌──────────────────────────────────────────────────────────────┐
│ comfyui-api-skills (15 子Skill 共享 1 个 scripts/)            │
│   comfyui-api → comfyui-workflow-builder → comfyui-inventory  │
│   comfyui-video-production → video-pipeline + voice-pipeline  │
│   comfyui-character-gen → workflow-builder + inventory        │
│   ... (全部 15 子技能内部网状交叉引用)                          │
└──────────────────────────────────────────────────────────────┘

游戏制作群岛（单一 Kit 入口，内含 7 子技能，7 阶段流水线，引擎可替换）
┌──────────────────────────────────────────────────────────────┐
│ game-production-kit/                                          │
│   Phase 0: Engine Confirmation → 引导 or 路由                 │
│   Phase 1: game-story-design/      # 剧情策划（引擎无关）      │
│   Phase 2: game-asset-pipeline/    # 素材管线（引擎无关）      │
│       │     ├── 图像 → comfyui-api-skills                     │
│       │     ├── 音效/BGM → comfyui-api-skills                 │
│       │     ├── 角色配音 → voice-character-design              │
│       │     └── TTS → voice-acting-skill                      │
│   Phase 3: 脚本编写（引擎路由）                                │
│       │     ├── webgal-scripting/    # WebGAL 脚本             │
│       │     ├── renpy-scripting/     # Ren'Py 脚本（待建）      │
│       │     └── ...                  # 其他引擎（可扩展）       │
│   Phase 4: game-quality-gate/      # 质量门禁（引擎无关）      │
│   Phase 5: 引擎构建（引擎路由）                                │
│       │     ├── webgal-engine-build/ # WebGAL 构建             │
│       │     ├── renpy-engine-build/  # Ren'Py 构建（待建）      │
│       │     └── godogen (ext)       # Godot 构建（外部）        │
│   Phase 6: Deploy → online          │
│                                                                │
│ 扩展方式：换引擎 = 替换 Phase 3 + Phase 5 + Phase 6 三个路由入口│
│ 前 4 阶段（0/1/2/4）引擎无关，任何引擎复用同一管线               │
└──────────────────────────────────────────────────────────────┘
```

---

## 四、维护规则

### 新增技能

1. 在「技能索引」对应层级添加一行
2. 标注依赖关系（硬依赖 / 软引用 / 无）
3. **依赖检查：声明了 requires 的技能，加载时必须执行 §四 依赖完整性验证流程**
4. 如有脚本，确认未在「共享能力注册表」中重复

### 新增脚本

1. 先查「共享能力注册表」是否已有同类脚本
2. 若有 → 复用，不复制副本
3. 若无 → 创建后在此注册

### 删除脚本

1. 先确认「消费者」列为空
2. 若有消费者 → 通知消费者迁移后再删

### 修改依赖

1. 同时更新 SKILL.md 的 `requires` YAML 字段
2. 同时更新「技能索引」和「依赖关系图」
3. **同时更新「降级影响表」中的降级说明**

### 地图冲突仲裁

地图与 SKILL.md 不一致时，**以地图为准**。发现不一致 → 修正 SKILL.md。

---

## 四、依赖完整性验证（V8 NEW）

> **标准**: 任何声明了 `requires` 的技能，加载前必须执行本验证。缺失依赖不得静音降级。

### 验证规则

| 依赖类型 | 字段 | 缺失行为 |
|---------|------|---------|
| 硬依赖 | `requires.skills` | 🛑 阻断加载，提示用户安装该技能 |
| 软依赖 | `requires.optional` | ⚠️ 警告用户降级影响，用户确认后继续 |

### 降级影响表

| 被依赖技能 | 依赖者 | 降级后果 |
|-----------|--------|---------|
| acceptance-discipline | fullstack4TraeV9 | 🛑 阻断 — 验收门禁不可跳过 |
| acceptance-discipline | fullstack4TraeV10 | 🛑 阻断 — 四维验收门禁不可跳过 |
| ponytail4Trae | fullstack4TraeV9 | ⚠️ 代码可能过度工程，无懒人模式提示 |
| ponytail4Trae | fullstack4TraeV10 | ⚠️ 代码可能过度工程，无懒人模式提示 |
| gitnexus4Trae | fullstack4TraeV9 | ⚠️ 影响面分析降级为 grep，存在盲区风险 |
| gitnexus4Trae | fullstack4TraeV10 | ⚠️ 影响面分析降级为 grep，存在盲区风险 |
| doc-map-manager | fullstack4TraeV9 | ⚠️ 文档索引无法自动更新，DOC SYNC 不完整 |
| doc-map-manager | fullstack4TraeV10 | ⚠️ 文档索引无法自动更新，DOC SYNC 不完整 |
| acceptance-discipline | fullstack4traev9 | 🛑 阻断 — 验收门禁不可跳过 |
| ponytail4Trae | fullstack4traev9 | ⚠️ 代码可能过度工程，无懒人模式提示 |
| gitnexus4Trae | fullstack4traev9 | ⚠️ 影响面分析降级为 grep，存在盲区风险 |
| doc-map-manager | fullstack4traev9 | ⚠️ 文档索引无法自动更新，DOC SYNC 不完整 |

> **2026-08-14 聚合说明**：test-experience / e2e-module-audit / test-partition-runner 三个 L0 skill 已并入 acceptance-discipline（内部子体系），不再作为独立外部依赖。其原降级后果已并入 acceptance-discipline 的硬依赖降级链。skills-security-scan 同理并入 trae-security-review。

### 项目级工作流(`.agents/skills/`,非云端分发)

| Skill | 类型 | 用途 | 关键产物 |
|-------|------|------|---------|
| [project-rule-skill](file:///D:/workspace/my-trae-helper/.agents/skills/project-rule-skill/SKILL.md) | 纯Skill | 项目级规则加载网关 — 任何任务开始前必走 | 3 references(skill-creation / protocol-coverage / skills-development) |
| [security-review](file:///D:/workspace/my-trae-helper/.agents/skills/security-review/SKILL.md) | 纯Skill | 代码安全审查 — 5 类漏洞 + 密钥检测 | 5 references |
| [self-improving-agent](file:///D:/workspace/my-trae-helper/.agents/skills/self-improving-agent/SKILL.md) | 纯Skill | 跨会话经验沉淀 — LEARN/ERROR/FEATURE_REQUESTS | assets/{LEARNINGS,SKILL-TEMPLATE} + 3 references + openclaw hooks |
| [case-driven-skill-audit](file:///D:/workspace/my-trae-helper/.agents/skills/case-driven-skill-audit/SKILL.md)(**V1.0 NEW 2026-08-17**) | 纯Skill | 演练驱动 skill 审计 — 7 步工作流(选题 → 子代理委派 → 硬验收 → 暴露漏洞) | 1 reference(case-2-evidence 实战证据) |

### 完整协议

> 依赖检查完整流程 + 加载时机械验证 + 降级影响模板 → [vibe-coding-standards/references/skill-dependency-check.md](vibe-coding-standards/references/skill-dependency-check.md)

| [skill-bundle](skill-bundle/SKILL.md) | 纯Skill | 子 skills 装载规范 v1.0 — 父包目录结构、命名空间、CLI bundle 命令、3 道闸(deprecation/version/name-conflict)、7 项守卫(BND-001~007)、L1-L4 Gate 自动接入 | bundle 命令 + install-guards.mjs + 07_bundle_structure.py(3 模式) |


| [guard-approver](guard-approver/SKILL.md) | 纯Skill | 保护路径守卫 v1.0 — 4 Tier 保护 + 3 类身份 + 4 步决策流,防止 agent 越权修改 .husky/.github/scripts 等关键路径 | change-guard-approver.mjs + .trae/identity/{skill-roles,protected-paths}.yaml |
