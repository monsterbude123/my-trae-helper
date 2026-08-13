# 技能市场能力地图

> 单一事实来源。新增技能前先查此地图，确认不重复。脚本复用前先查共享注册表。
> 
> 维护规则：新增/删除/改依赖 → 同步更新此文件。地图与 SKILL.md 不一致时，以地图为准。

---

## 一、技能索引

### L0 基座（无外部依赖，独立可用）

| 技能 | 类型 | 一句话 | 脚本/工具 |
|------|------|--------|----------|
| [coding-xinfa](coding-xinfa/SKILL.md) | 纯Skill | 通用编码心法 + Goal Mode + 完成审计 + 风格规范 | 无 |
| [goal-mode](goal-mode/SKILL.md) | Agent驱动 | 目标追逐协议 — 持久化任务执行 + 审计门禁 + 阻塞检测 | 无（Agent: goal, auditor, planner） |
| [ponytail4Trae](ponytail4Trae/AGENTS.md) | 纯Skill | 懒人开发模式 — 最简实现、减少依赖、删除优先 | 无（子Skill: ponytail, review, debt, help） |
| [gitnexus4Trae](gitnexus4Trae/AGENTS.md) | 纯Skill | GitNexus 代码智能 — 探索、调试、影响分析、重构、CLI | 无（子Skill: cli, debugging, exploring, guide, impact-analysis, refactoring） |
| [browser-use-cloud](browser-use-cloud/SKILL.md) | 纯Skill | Browser Use 浏览器自动化 — 网页抓取、自动操作、结构化提取 | api_check.py, batch_sessions.py, structured_extract.py, webhook_server.py |
| [openapi-doc-exporter](openapi-doc-exporter/SKILL.md) | 纯Skill | OpenAPI → Markdown 文档导出，框架无关 | render_md.py, split_by_prefix.py, validate_openapi.py |
| [deep-research](deep-research/SKILL.md) | 纯Skill | 多源深度研究 — firecrawl/exa MCP 综合 + 引用报告（V1.0 NEW 2026-08-13 蒸馏自 ECC .agents/skills/deep-research，按 §11 接入治理） | 无（依赖 MCP: firecrawl 或 exa，至少 1 个） |
| [trae-professional](trae-professional/SKILL.md) | 纯Skill | TRAE IDE 专业知识库 | 无 |
| [product-teardown](product-teardown/AGENTS.md) | 纯Skill | 产品拆解分析 — 6 维度解构 + PRD 生成 | 无（子Skill: analyze, prd） |
| [vision-audit](vision-audit/SKILL.md) | 纯Skill | UI/UX 视觉验收 — Qwen3-VL 分析截图 | vision-audit.mjs, vision-audit.py |
| [shuxia-novel-engine](shuxia-novel-engine/SKILL.md) | Agent驱动 | 小说创作引擎 — 世界观构建、剧情编织、一致性审计 | 12 脚本（check, combat, drama, enumerate, evaluate, ripple 等） |
| [modelscope-assistant](modelscope-assistant/SKILL.md) | 纯Skill | 魔搭社区助手 — 模型搜索、SDK 调用、微调指导 | mymodelscope/ Python 库 + scan-models.ps1 |
| [test-experience](test-experience/SKILL.md) | 纯Skill | 测试开发经验库 — mock/fixture/异步陷阱 | 无（⚠ 已整合到 acceptance-discipline） |
| [test-partition-runner](test-partition-runner/SKILL.md) | 纯Skill | 测试阻塞解决 — 分区定位坏测试 | 无（⚠ 已整合到 acceptance-discipline） |
| [e2e-module-audit](e2e-module-audit/SKILL.md) | 纯Skill | E2E 双模式验证 — 批量验收 + 即时诊断 | 无（⚠ 已整合到 acceptance-discipline） |
| [doc-map-manager](doc-map-manager/SKILL.md) | 纯Skill | 文档地图管理器 — 结构化索引构建 + 多模式查询（grab/lookup/fuzzy/semantic/file） | build-index.py, query-index.py |
| [vibe-coding-standards](vibe-coding-standards/SKILL.md) | 纯Skill | Vibe Coding 组件编写原则 — AGENTS.md/Rules/Skills/Subagents 结构规范与防击穿策略 | 无 |
| [project-rules-gate](project-rules-gate/SKILL.md) | 纯Skill | 项目级 Rules 强制加载与子代理门禁 — 把 .trae/rules/ 锻造为 project_rules_skills 入口 skill + 强制 sub-agent [PROJECT-RULES-GATE] 头。V11 同名协议独立分发版(v0.2 加 --move 物理移走 + frontmatter 自动注入) | forge_project_rules_skill.py |
| [skill-optimization-method](skill-optimization-method/SKILL.md) | 纯Skill | 技能包优化升级方法论 — 体积诊断 + 外部对标 + 缺口对照 + 最小修复（项目级） | 无 |
| [session-distiller](session-distiller/SKILL.md) | 纯Skill | 会话蒸馏器 — 从完整会话历史中提炼高质量方法论、最佳实践和可复用技能包 | 无 |
| [trae-local-data-export](trae-local-data-export/SKILL.md) | 纯Skill | Trae IDE 本地数据导出 — 整合 ZedeX/trae-chat-decrypt + cgint/ai-data-extraction，产出 JSON/TXT/SQLite 三大产物 | 7 脚本（extract_key ×2 / decrypt_db / verify / export_sessions / extract_trae_jsonl / sanitize_export） |

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
| [game-production-kit](game-production-kit/SKILL.md) | 纯Skill | 游戏制作工具箱 — 7 阶段编排器（引擎确认→剧情→素材→脚本→门禁→构建→部署），引擎可替换架构。内含 7 子技能 | 子技能: game-story-design, game-asset-pipeline, game-quality-gate, voice-character-design, voice-acting-skill, webgal-scripting, webgal-engine-build |

### L3 配置模板（绑定 L0~L2）

| 技能 | 类型 | 一句话 | 绑定 |
|------|------|--------|------|
| [fullstack-auto](fullstack-auto/SKILL.md) | 配置模板 | 项目级 `.trae/` 配置一键部署 | fullstack + coding-xinfa + goal-mode + GitNexus + ponytail |

### 独立群岛（内部密集交叉，与外部无关）

| 技能 | 类型 | 一句话 | 规模 |
|------|------|--------|------|
| [comfyui-api-skills](comfyui-api-skills/SKILL.md) | 纯Skill | ComfyUI 视频制作全流程 — 15 子技能编排 | 15 子Skill + 10 脚本 + lib/ 共享库 |
| [trae-security-review](trae-security-review/SKILL.md) | Agent驱动 | 双引擎安全审查 — AI 驱动的代码安全审查 + Skill 目录静态扫描 | 2 Agent + 1 脚本 + 3 参考文档 |
| [vibe-coding-diagnosis](vibe-coding-diagnosis/SKILL.md) | 纯Skill | Vibe Coding 项目合规自检诊断 — 三步流程(定类型→套矩阵→出诊断)，9类项目 × 6维度(A-F) × 体量分级 | 3 参考文档 + 1 模板 |
| [docsify-doc-builder](docsify-doc-builder/SKILL.md) | 纯Skill | UE 5 风格 docsify 文档系统 — 顶栏/多级分类/面包屑/右侧页内目录 + Mermaid 全屏/导出 + Markmap 思维导图（默认全部展开） | 1 SKILL + 4 ps1/sh 脚本（init-docs/serve/check-env/generate-sidebar）+ 6 模板（index.html/custom.css/_sidebar/_navbar/README/logo.svg） |

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

---

## 三、依赖关系图

```
L0 基座（独立可用，无外部依赖）
┌──────────────────────────────────────────────────────────────┐
│ coding-xinfa   goal-mode   ponytail4Trae   gitnexus4Trae     │
│ browser-use-cloud   openapi-doc-exporter   trae-professional  │
│ product-teardown   vision-audit   shuxia-novel-engine        │
│ Voice-Acting-Script-Skill   modelscope-assistant             │
│ doc-map-manager                                              │
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
| test-experience | acceptance-discipline | ⚠️ 测试编写质量降低，陷阱可能重复踩 |
| e2e-module-audit | acceptance-discipline | ⚠️ E2E 验收降级为手动 |
| test-partition-runner | acceptance-discipline | ⚠️ 测试阻塞时无法自动分区定位 |

### 完整协议

> 依赖检查完整流程 + 加载时机械验证 + 降级影响模板 → [vibe-coding-standards/references/skill-dependency-check.md](vibe-coding-standards/references/skill-dependency-check.md)
