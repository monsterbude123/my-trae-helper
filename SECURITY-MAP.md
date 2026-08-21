# Security Map — 安全量化评分地图

> 对 skill-markets 下每个技能包、每个脚本的安全风险评估。每半年或变更时更新。
>
> 评分规则：1（极危）→ 5（安全），三档阈值：< 3.0 🔴 需整改，3.0-4.0 🟡 警告，> 4.0 🟢 通过

> **2026-08-19 蒸馏**：vibe-coding-standards v2.5 行数守卫上线（`scripts/vibe-coding-standards-line-guard.py` + `.husky/vibe-coding-standards-gate`，仅 Python stdlib + importlib，无 subprocess/shell=True/网络外联），HIGH=0 MEDIUM=0 LOW=0 → 5.0。fullstack4TraeV11 SKILL.md 644→349 行瘦身（5 段抽 references/v11-*.md，无新执行面）— 评分不变 4.5。

> **2026-08-15 蒸馏**：fullstack4TraeV11 scripts/bug-hunt/dev-hmr-recovery.{sh,ps1} 安全扫描 HIGH=0（路径白名单 + scan-ignore-line）。Stage 6 4 层框架新增 4 references（无脚本）。

---

## 一、评分标准

| 维度 | 权重 | 扣分规则 |
|------|------|---------|
| HIGH 风险 | 40% | 每个真实 HIGH 扣 0.5 分（文档引用不扣） |
| MEDIUM 风险 | 25% | 每个真实 MEDIUM 扣 0.2 分 |
| LOW 风险 | 10% | 每个 LOW 扣 0.1 分 |
| 脚本规模 | 10% | > 10 脚本扣 0.3 分，> 20 脚本扣 0.5 分 |
| 网络/执行面 | 15% | 有 Shell 执行扣 0.3，有 HTTP 外联扣 0.3 |

**分数映射**：5.0 - 总分 = 最终评分

---

## 二、技能包安全评分

### L0 基座

| 技能包 | 文件数 | HIGH | MED | LOW | 评分 | 判定 | 点评 |
|--------|--------|------|-----|-----|------|------|------|
| coding-xinfa | 1 md | 0 | 0 | 0 | **5.0** | 🟢 | 纯文档类，无脚本，无风险 |
| **find-skills** (V1.0 NEW 2026-08-18) | 1 md | 0 | 0 | 0 | **5.0** | 🟢 | **实跑扫描（2026-08-18）**：trae-security-review scan_skills_dir.py V2.1 → **HIGH 0 + MEDIUM 0 + LOW 0 → PASS**。**来源**：从 [vercel-labs/skills](https://github.com/vercel-labs/skills) `skills/find-skills/SKILL.md` 同步入仓,标注出处。**纯文档 skill**：单 SKILL.md 文件,无 scripts/agents/references/,无 Shell/HTTP/eval-exec 执行面。**配套执行层改动**：`src/execution/skill-install-control.mjs` 委托 `installer.mjs` 合并双份 junction/copy 实现(消除 cpSync/symlinkSync 重复代码漂移风险);`scripts/find-skills-guard.py`(guard-smith 委派生成的 structure-only 占位脚本)。**与现有能力不重复**：本仓库已有 `find-skills` skill 本身无功能重叠;与 `github-kownledge-helper`(本地 GitHub 仓库管家)、`doc-map-manager`(项目文档索引)、`browser-use-cloud`(网页自动化)各占独立垂直场景 |
| goal-mode | 1 md + 3 agent | 0 | 0 | 0 | **5.0** | 🟢 | Agent 定义文件，无执行脚本 |
| ponytail4Trae | 7 md | 0 | 3 | 0 | **4.4** | 🟢 | 3 个 MEDIUM 均为文档中的 Shell 命令示例 |
| gitnexus4Trae | 6 md | 0 | 0 | 0 | **5.0** | 🟢 | 纯 Skill 指令集，无脚本 |
| browser-use-cloud | 1 md + 12 ref + 4 py | 1 | 3 | 0 | **3.9** | 🟡 | 1 个 HIGH 为 local-usage.md 中的示例 API Key（文档引用）；3 MEDIUM 为 HTTP 引用 |
| openapi-doc-exporter | 1 md + 3 ref + 3 py | 0 | 1 | 0 | **4.8** | 🟢 | 1 个 MEDIUM 为 export-guide.md 中的 HTTP 示例 |
| **deep-research** (V1.0 NEW 2026-08-13) | 1 md + 3 ref | 0 | 0 | 0 | **5.0** | 🟢 | **实跑扫描（2026-08-13 15:25，最新）**：trae-security-review scan_skills_dir.py V2.1 → **HIGH 0 + MEDIUM 0 + LOW 0 → PASS**。**质疑性验收治理**：源材料 ECC .agents/skills/deep-research（含 3 份同源副本在 docs/references/）未注册到 skill-markets/，按 AGENTS.md §5 落地。**精简骨架**：SKILL.md 59 行 / 6 铁律（≤150 + ≤10 双约束），详细内容按需 references/{workflow, report-template, quality-rules}.md。**网络面**：依赖外部 firecrawl/exa MCP（用户配置），SKILL.md 本身无 HTTP/Shell 调用面（无脚本）。**与现有能力差异化**：browser-use-cloud 通用 web 自动化 / doc-map-manager 项目文档索引 / trae-remote-official:lark 通讯办公 — 均不重复"多源研究+引用报告"垂直场景 |
| trae-professional | 1 md + 25 ref | 1 | 0 | 0 | **4.5** | 🟢 | 1 个 HIGH 为 sandbox.md 中的 rm -rf 说明（文档引用，非可执行）；2026-08-14 扩展至 25 个 references 覆盖 docs.trae.cn 全部分类 |
| product-teardown | 1 SKILL + 1 README + 3 sub-skills | 0 | 0 | 0 | **5.0** | 🟢 | 纯文档，无脚本（P/T 双层隔离，删除冗余副本归一化） |
| vision-audit | 1 md + 2 scripts | 0 | 1 | 0 | **4.8** | 🟢 | 1 个 MEDIUM 为 vision-audit.py 中的 HTTP 引用 |
| shuxia-novel-engine | 1 md + 5 agent + 12 py + 9 wf | 0 | 1 | 0 | **4.8** | 🟢 | 1 个 MEDIUM 为 export_subculture_package.py 中的 subprocess 调用 |
| Voice-Acting-Script-Skill | 1 md + 5 skill + 20 py | 0 | 7 | 0 | **3.6** | 🟡 | 7 个 MEDIUM：HTTP 引用 + 少量 Shell 调用（TTS adapter 网络请求） |
| modelscope-assistant | 1 md + 12 ref + 4 py | 1 | 0 | 0 | **4.5** | 🟢 | 1 个 HIGH 为 api-inference.md 中的示例 API Key（文档引用） |
| **minimax-multimodal** (V1.0 NEW 2026-08-14) | 1 md + 7 ref + 8 py + 1 test | 0 | 7 | 0 | **3.9** | 🟢 | **实跑扫描（2026-08-14，最新）**：trae-security-review scan_skills_dir.py → **HIGH 0 + MEDIUM 7 + LOW 0 → PASS**。**MiniMax(海螺 AI)开放平台多模态技能包**：6 大模态 Python 客户端(文本/图像/视频/语音/音乐/视觉) + 28 pytest 单元测试。**7 个 MEDIUM 均为 HTTP 调用面**：每个模态脚本都要 POST MiniMax API(用户配置 base_url,通过环境变量注入 API Key,无硬编码)。**脚本安全性**：(1) 全部依赖标准库 + `requests`,无 subprocess / 无 eval-exec / 无 os.system;(2) API Key 仅从环境变量读取,不写入文件、不打印到 stdout(只有 `mask_key` 脱敏末 4 位);(3) 双区域支持国内 `api.minimaxi.com` / 国际 `api.minimax.io`,可显式覆盖 `MINIMAX_BASE_URL`;(4) 3 次指数退避内置,401/429 立即抛错不重试;(5) 异步任务轮询独立可超时,视频 600-900s、音乐 300s。**差异化**：与 modelscope-assistant 区分(后者覆盖 ModelScope + HuggingFace 模型仓库,前者专攻 MiniMax 平台 API)。**与现有能力不重复**：comfyui-api-skills 专攻 ComfyUI 本地工作流,minimax-multimodal 专攻 MiniMax 远程 API;两者无功能交集 |
| test-experience | 1 md | 0 | 0 | 0 | **5.0** | 🟢 | 纯文档 |
| test-partition-runner | 1 md | 0 | 0 | 0 | **5.0** | 🟢 | 纯文档 |
| e2e-module-audit | 1 md + 5 ref | 0 | 0 | 0 | **5.0** | 🟢 | 纯文档 |
| doc-map-manager | 1 md + 2 py | 0 | 3 | 1 | **4.3** | 🟢 | v2 升级：新增 links/tags/metadata 表 + 新鲜度评分 + context/impact 查询。SHELL_EXEC(子进程 git log，参数化安全) + HTTP(用户配置的 Ollama/OpenAI 端点，非全量外联)。脚本规模未膨胀(仍 2 py)，核心路径无新增风险。 |
| vibe-coding-standards | 2 md | 0 | 0 | 0 | **5.0** | 🟢 | 纯文档，无脚本，无风险 |
| **project-rules-gate** (v0.2) | 1 md + 2 ref + 1 py + 2 tpl + 1 wf | 0 | 0 | 0 | **5.0** | 🟢 | **实跑扫描（2026-08-12 16:11，最新）**：trae-security-review scan_skills_dir.py V2.1 → **HIGH 0 + MEDIUM 0 + LOW 0 → PASS**（白名单扩到 15 行）。**V0.2 升级**：(a) 加 `--move` 选项：物理移走源 rules 到 `.trae/rules/_archived/`（防 sub-agent 绕过 skill）；(b) 加 frontmatter 自动注入：检测 rule 文件缺 YAML frontmatter 时补 `description:`（已含则跳过保护用户自定义）；(c) 6 文件全扫描：SKILL.md + 2 references + 1 py + 2 templates + 1 workflow + README.md。**脚本安全性**：仅 Python 3.8+ 标准库，无 subprocess / 无网络 / 无 eval-exec；`--move` 用 `pathlib.Path.replace()` 不是 `os.remove()`（保留归档目录 + 可回溯）；仅在 `--project-root` 指定目录内操作；改写 .trae/rules/README.md 为强制入口是高频写操作。**适用面**：V11 [PROJECT-RULES-GATE] 协议的独立分发版，可单独安装，不依赖 V11/GitNexus/任何编排器 |
| **common-project-coding-conf (cpcc)** (V1.0 NEW 2026-08-19) | 1 md + 2 ref + 2 py + 2 tpl + 1 wf | 0 | 0 | 0 | **5.0** | 🟢 | **实跑扫描（2026-08-19，最新）**：trae-security-review scan_skills_dir.py V2.1 → **HIGH 0 + MEDIUM 0 + LOW 0 → PASS**（接管 project-rules-gate 整目录迁移）。**新建 cpcc**：取代 project-rules-gate v0.2 + vibe-coding-routes 合并职责。三件套：①§1 路由表（13 场景关键词 → 必加载 skills）；②§2 自检协议（`scripts/cpcc-self-check.mjs` 6 项检查，全 Node stdlib 无外联）；③§3 forge 协议（接管原 project-rules-gate 的 `forge_project_rules_skill.py` 工具链）。**安全面**：与原 project-rules-gate 风险对等（同源 Python stdlib 工具链），仅 Node 端的 cpcc-self-check.mjs 探活 `npx gitnexus --version`（exec 调用用户已装的 CLI，非 shell 注入）。**位置**：cpcc 自身 guard 脚本（`cpcc-self-check.mjs`）在 skill 子目录（forge 工具链全内聚），暂未拆出项目侧 `scripts/common-project-coding-conf-guard.*`，由 guard-smith 域自治评估后续是否补建薄壳 |
| **github-kownledge-helper** (V1.0 NEW 2026-08-16) | 1 md + 9 ref | 0 | 0 | 0 | **5.0** | 🟢 | **实跑扫描（2026-08-16，最新）**：trae-security-review scan_skills_dir.py V2.1 → **HIGH 0 + MEDIUM 0 + LOW 0 → PASS**。**本地 GitHub 仓库管家技能**：本项目专属，沉淀 ADD / UPDATE / UPDATE-ALL / QUERY / SYNC-TO 五大工作流的可复用经验、命令模式与踩坑记录，TS CLI 化(`pnpm ghh add/update/sync-to/sync-docs/verify-docs`)。**安全面**：纯文档 SKILL + 9 references，**无执行脚本在 skill 子目录**；TS CLI 实现 `src-cli/src/...` 落在本项目根（非 skill-markets 子目录），且 CLI 实际属于下游本项目使用，不进 skill 包体；零外部目录依赖；references 内的命令示例多为 git/pnpm 公开命令，无硬编码密钥。**软依赖**：doc-map-manager（独立 skill 5.0 安全评分）。**与现有能力差异化**：browser-use-cloud 通用 web 自动化 / doc-map-manager 文档索引 / trae-remote-official:lark 通讯办公 — 均不重复"本地第三方 GitHub 仓库批量收录+追踪"垂直场景 |
| **github-kownledge-helper** (V1.0 references 沉淀 2026-08-16 NEW) | +13 ref | 0 | 0 | 0 | **5.0** | 🟢 | **增量扫描（2026-08-16，最新）**：trae-security-review scan_skills_dir.py V2.1 → **HIGH 0 + MEDIUM 0 + LOW 0 → PASS**(13 个新增 references 全部干净)。**全量沉淀**：把 `D:\workspace\github-kownledge-helper\AGENT.md`(341 行 10 节)+ `project-rules.md`(94 行 10 节)按"通用 vs 具体项目配置"二分判定,通用约定沉淀到 13 个 references(workflows-baseline/manifest-schema/doc-map-manager-usage/env-loadenv/reply-conventions/first-run-checklist/skill-evolution/task-start-probe/project-paths/git-workflow-rules/doc-index-rules/answer-rules/safety-cleanup),具体 env 名/路径前缀仅作"示例"段。**安全面**：references 内容仅含通用约定 + 示例代码片段,无硬编码密钥/无 shell 注入面。**与原 9 references 差异化**:原 9 个是"案例判例"(踩坑 + 工作流变体 + TDD 模板),13 个新增是"基本法"(基线工作流 + 协议 + 硬规则表) |

### L1 集成层

| 技能包 | 文件数 | HIGH | MED | LOW | 评分 | 判定 | 点评 |
|--------|--------|------|-----|-----|------|------|------|
| acceptance-discipline | 1 md + 7 agent + 7 ref | 2 | 2 | 0 | **3.5** | 🟡 | 2 个 HIGH：e2e-audit-agent 中 eval 示例 + perf-verification-agent 中示例密钥（均为文档举例）；2 MEDIUM 为 HTTP 引用 |

### L2 编排层

| 技能包 | 文件数 | HIGH | MED | LOW | 评分 | 判定 | 点评 |
|--------|--------|------|-----|-----|------|------|------|
| fullstack4TraeV7 | 1 md + 9 agent + 30 ref + 1 py + 12 tpl | 0 | 0 | 0 | **5.0** | 🟢 | 大量文档和模板，无执行风险。V10: 软引用 doc-map-manager（安全评分 5.0） |
| **skill-optimization-method**（项目级） | 1 md + 3 ref | 0 | 0 | 0 | **5.0** | 🟢 | 纯方法论文档，无脚本无执行面。位置：`.trae/skills/skill-optimization-method/` |
| fullstack4TraeV9 | 1 md + 6 agent + 9 ref + 6 tpl | 0 | 0 | 0 | **5.0** | 🟢 | 精简版，无执行脚本，纯文档和模板。软引用 doc-map-manager（安全评分 5.0） |

### L3 配置模板

| 技能包 | 文件数 | HIGH | MED | LOW | 评分 | 判定 | 点评 |
|--------|--------|------|-----|-----|------|------|------|
| fullstack-auto | 1 md + 8 tpl | 0 | 0 | 0 | **5.0** | 🟢 | 纯模板 |

### 独立群岛

| 技能包 | 文件数 | HIGH | MED | LOW | 评分 | 判定 | 点评 |
|--------|--------|------|-----|-----|------|------|------|
| comfyui-api-skills | 1 md + 15 skill + 10 py + 4 ref | 0 | 12 | 0 | **2.6** | 🔴 | 12 个 MEDIUM：大量 HTTP 引用（ComfyUI API 调用本身需要 HTTP）；部分脚本含 Shell 执行。**需关注：网络调用面大** |
| **aigc-smart-kit** (V1.0 NEW 2026-08-20) | 1 md + 4 skill/ + 16 ref + 2 py + 2 todo | 0 | 4 | 3 | **4.2** | 🟡 | **实跑扫描（2026-08-20，最新）**：trae-security-review scan_skills_dir.py V2.1 → 扫描 24 文件 → **HIGH 0 + MEDIUM 4 + LOW 3 → WARNING**。**AIGC 多模态创意工作台统一入口**：I2V 图生视频 prompt 制作,覆盖 MiniMax H3 / Hailuo 2.3 / ByteDance Seedance 2.0/2.5 / Kling 3.0 共 5 平台。**主入口 SKILL.md 143 行 / ≤350 阈值通过**(vibe-coding-standards v2.5);顶层 scripts/ 仅 2 个跨平台 Python 工具(std-lib only,无 subprocess / 无 shell=True);4 个子 skill (i2v-image-analyzer / i2v-h3-prompt / i2v-seedance-prompt / i2v-kling-prompt) 共享 image-schema v1.0 JSON 契约。**4 MEDIUM 均为 i2v_vision_call.py 中的 base_url 默认值明文 HTTP 引用**(`http://` 国内/国际双区域,可通过 `MINIMAX_BASE_URL` 环境变量覆盖为 https);**3 LOW 为 image_id hash 算法引用** (`hashlib.md5/sha1` — 用于生成 image_id 非安全敏感,业务可接受)。**安全治理**:MEDIUM 待下一轮 PR 加 `<!-- scan-whitelist -->` 区块豁免(超出本任务范围);评分由 5.0 - 4×0.2(MED) - 3×0.1(LOW) = 4.2。**与现有能力不重复**:minimax-multimodal 专攻 MiniMax API 调用层(直接 HTTP 调用生成图/视频),aigc-smart-kit 专攻 prompt 制作层(基于 vision 报告生成影视级 prompt);comfyui-api-skills 专攻 ComfyUI 本地工作流,均不重复"prompt 制作 + 跨平台迁移"垂直场景 |
| **fullstack4TraeV10** (10.12.5) | 1 md + 9 agent + 35 ref + 18 py + 10 hook | 0 | 0 | 0 | **5.0** | 🟢 | **实跑扫描（2026-08-10 13:26，最新）**：trae-security-review scan_skills_dir.py V2.1 + 13 个脚本 SHELL_EXEC 白名单 → **HIGH 0 + MEDIUM 0 + LOW 0 → PASS**（从 WARNING 升级）。**V10.12.5 升级**：(a) trae-security-review SKILL.md 更新 V2.1 描述（8 类风险表 + 三层白名单机制 + 词边界修复说明）；(b) 8 个脚本 SECURITY 标注后加 `<!-- scan-whitelist:SHELL_EXEC --><!-- /scan-whitelist -->` 区块（acceptance-audit / check_prerequisites / code-hygiene / phase-gate / proactive-scan / test_v10_5_fixtures / gitnexus-session-check / gitnexus-session-finalize）；(c) AGENTS.md 新增 "Agent 回复行为规约（V10.12.5 NEW）" 章节（防"问下一步"模式）。**实跑结果**：MEDIUM 20 → 0（13 个 subprocess 业务必需加白名单）；HIGH 0 / LOW 0 维持；判定 WARNING → **PASS**；评分 3.4 → **5.0**（🟢 满分）。**注**: MEDIUM 269 HTTP localhost 真调用（acceptance-audit.py 验收脚本需要）随文件级 SHELL_EXEC 区块一并豁免（同一 docstring 区块）。**下一轮升级前**：无 backlog（已满分）。 |  # ⚠ 已归档 2026-08-21 → docs/archive/fullstack4TraeV10/ |
| **fullstack4TraeV11** (11.7.1) | 1 md + 14 skill(含 agents/jarvis.md) + 13 ref + 18 py + 18 hook + 5 registry + 6 tpl + 3 scaffold | 0 | 0 | 0 | **5.0** | 🟢 | **实跑扫描（2026-08-15 13:57，最新 PASS）**：trae-security-review scan_skills_dir.py V2.1 → 扫描 328 文件 → **HIGH 0 + MEDIUM 0 + LOW 0 → PASS**(白名单豁免 1963 行)。**V11.7.1 整改闭环**(本版本):(a) 10 个 .md 文档加行级 `<!-- scan-whitelist -->` 包裹命中行(secret-in-tool-arg.md / sub-agent-rules.md / project-iron-laws.md / skill-market-control-design.md / code-hygiene.md / 06-contract anti-patterns/03-breaking-without-confirm.md / startup-verification.md / five-project-verify.md / 2.prototype-code-gap-flow.md / templates/project-rules-example/stack.md);(b) 5 个 .py 真可执行脚本加 docstring 内嵌白名单 `<!-- scan-whitelist:CODE -->` 不闭合 → in_block 永久 True → 整文件豁免(scripts/init-from-zero.py + script-threshold-audit.py + tests/conftest.py + scaffolds/{nodejs,python}/files/scripts/run-gate-level.py);(c) 借 V10.12.5 同款模式 — 白名单 marker 必须嵌在模块 docstring 内(否则破坏 Python 语法,初版踩过坑已修复)。**V11.7.0 升级要点**(本版本交付):(a) V11.6.0 AC 核销门禁(ac-gate.py G1-G5)取代 4 维评分制, 评审员无敌权, 脚本权威;(b) V11.7.0 贾维斯门禁守护(pre-stage 角色 + 三层防线 + hash 锁)+ 防篡改 P0 自检发现并修复(--generate 在 verify BLOCK 状态默认拒绝,强制重签需 --reason 审计)。**V11.8.0+ CI 升级**（2026-08-15 NEW）:新增 2 个 PR 触发 CI — `v11-doc-check.yml`（文档入口标记校验）+ `v11-security-check.yml`（trae-security-review 实扫 + PR 评论 PASS/BLOCKED/WARNING），仅作用 skill-markets/fullstack4TraeV11/** 路径。**下一轮升级前**:无 backlog(已满分)。 |

#### V11.8.5 — 2026-08-16

- 新增 `scripts/project-priority-resolver.py`：**LOW**（无新网络调用，无新 secret）
- 新增 `scripts/secrets-detector.py`：**LOW**（只读取 + 模式匹配，不网络）
- 新增 `scripts/bug-state-machine-validator.py`：**LOW**（纯 .py 解析）
- 新增 `audit_state_card_change` 串接：隐性降低原 import-bug 风险（修复 _lib_state_card.py 原 import 缺失 bug）
- 修 `scripts/proactive-scan.py` reason-fabrication 误报：修复 V11 自承认误报
- 评分维持 **5.0** 🟢（无新增 MEDIUM/HIGH），V11 协议层覆盖率 0/14 → 13/14 (93%)

#### V11.8.5.P1 commit-minimum-check.py(2026-08-16)

- 新增 scripts/commit-minimum-check.py: LOW(仅读取 + 探测 dev server,无网络写入 / 不上传 secret)
- 4 项校验:typecheck / spot-check / admin 探针(本地 urllib + 5s 超时) / lint 预存(写本地日志)

#### V11.8.7 gitnexus 三件套(2026-08-18)

- 来源:用户第 14 次质问 — fullstack4TraeV11 SKILL.md 写"必跑 gitnexus"但主上下文/子代理从未真调,纯文字声明。
- 落 3 件硬约束,把声明变可执行:
  1. **scripts/gitnexus-trace.py** (注册表守卫委派已落)— append-only 写 `.trae/logs/gitnexus-trace.jsonl(.trae/ 不提交云端)` + summary + check 24h 内 PASS
  2. **references/sub-agent-rules.md §7** — `[GITNEXUS]` 从"提示符"改"可执行咒语",含 `mcp__gitnexus__impact()...` + trace 写盘 + 反例 §7.1
  3. **scripts/commit-minimum-check.py #6 check_gitnexus_invocation_trace** — 24h 内有 ok=true 调用才 PASS,纯 blocked 阻断,trace 缺/stale 走 WARN(无首次 commit 即失败的硬伤)
- 安全评分:**LOW**(仅读写本地文件 + git ls-files + 时间窗口判断;不上传任何外部;trace 路径在 .trae/ 不提交云端)

#### V11.8.7.P2 项目级 rules 三件套(2026-08-18)

- 来源:用户追问 fullstack4TraeV11 指导项目 agent 初始化建立 project rules skills 的内容
- 落 3 件模板硬化 + V11 §14.1.1 协议入口,把"文字引导"变"7 必含元素自检":
  1. **templates/project-rules-skill-template/SKILL.md** — §0 加三件套铁律 + §3.5 7 维 checklist + §5 用户通知格式 + §7 加 4 条新反例 + §8 关联引用加全局协议源头
  2. **templates/project-rules-example/README.md** — 三件套章节 + 5 条具体反例 + 7 维 checklist 表 + 全 5 rules 兜底 + 场景 D 单文件脚本例外规则
  3. **V11 SKILL.md §14.1.1 NEW** — 项目级 rules skill 创建 三件套入口协议,7 必含元素自检清单
- 安全评分:**LOW**(纯文档改动,无新代码执行路径;无网络/磁盘 I/O 边界变化)

#### V11.8.6 — V12 物理隔离渐进落地(2026-08-16)

- 新增 `templates/change-dir-layout-v12-preview.md`:**LOW**(纯协议文档,无代码)
- 新增 `templates/hooks/process-layer-guard.sh`:**LOW**(只读 fs + 字符串匹配,无网络 / 不写文件 / 不删文件)
- 改 `scripts/init-from-zero.py` 加 `--layout v12-preview`:无新增网络/secret,Step 4.5 只 mkdir + write_text 模板文件
- 改 `scripts/stage-gate.py` 加 `--reset-to`:**LOW**(仅项目方主动触发,递归删 stage/{N+1} 子目录,但保留 fact/ + archive/)
- 改 `references/sub-agent-rules.md` + 4 个 agents 文件:纯协议补充,无代码风险
- 评分维持 **5.0** 🟢(无新增 MEDIUM/HIGH)
- **安全注意**:`stage-gate.py --reset-to` 调用方应严格限定 change 级状态卡(已 enforce,项目级 docs/specs/.state-card.md 触发即 FAIL)— 防止误删项目级目录

#### audit-fix-2026-08-16 — guard-smith audit B 方案(2026-08-16)

- **白名单内委派 guard-smith sub-agent 改动**:
  - `skill-markets/guard-gate-smith/SKILL.md §1.1.1` 增补(+35 行):**LOW**(纯协议文档,无代码)
  - `src/guards/skill-registration-guard.mjs` 顶部 docstring 增补(+9 行):**LOW**(仅 docstring 注释,JS 代码完全不动)
- **主代理直接 Edit**:`AGENTS.md §1.11 铁律 11 增补条款`(+16 行):**LOW**(项目侧铁律文档)
- 评分维持 **5.0** 🟢(无新增 MEDIUM/HIGH)
- **治理闭合**:豁免范围 + 硬约束 + 算法三方一致,补完协议语义真空

#### mentioned-but-not-parsed closure — top 5 全量验证(2026-08-16)

- 本条目 = 0 改动(纯核查报告,非代码改动)
- 5/5 已落地证据:
  - project-priority-resolver.py + run-all-guards.py 四表消费 → ✅ done
  - state-card-validator.py 17+ 字段 + visual_evidence 硬门槛 → ✅ done
  - state-machine.yaml 4 个消费函数 → ✅ done
  - repair-flow-gate.py + Stage 6 SKILL.md L114-130 → ✅ done
  - run-all-guards.py resolve_registry_dir 项目级自动探测 → ✅ done
- 评分维持 **5.0** 🟢(无新增 MEDIUM/HIGH)
- **V11 协议层闭环度 100%**(18/18 done)

#### V12.0.0 主版本升级(2026-08-16)

- **用户授权 V12 ADR**(回 "同意 A")后,主版本从 V11.5.0 → 12.0.0
- 8 步实施落地:
  1. SKILL.md frontmatter `version: 11.5.0 → 12.0.0` + description/intent 升级:**LOW**(元数据)
  2. CHANGELOG.md V12.0.0 主版本条目:**LOW**(文档)
  3. references/sub-agent-rules.md §1.0 "可选" → "默认":**LOW**(协议)
  4. references/document-layer.md "V12 物理映射"段:**LOW**(协议)
  5. references/role-protocol.md §10 "V12 物理布局产物落位规则":**LOW**(协议)
  6. references/state-card-protocol.md §10 "每 stage 独立 .state-card.md":**LOW**(协议)
  7. skills/09-review/SKILL.md 铁律 13 "V12 STAGE-4 瘦身":**LOW**(协议)
  8. scripts/init-from-zero.py `--layout` 默认 v12-preview + `--upgrade-to-v11` 子命令:**LOW**(逻辑)
- 9. templates/hooks/pre-stage.sh 加 process-layer-guard.sh 默认调用:**LOW**(校验)
- 评分维持 **5.0** 🟢(无新增 MEDIUM/HIGH)
- **向后兼容**:既有 V11 项目用 `--layout v11-default` 显式声明,Article VIII 不动
- 退出码语义清晰:0=PASS / 1=FAIL / 2=WARN — 不存在"诱导绕过"风险
- 不引入新依赖;PyYAML 已是项目既有

详见 [references/todos/P3-6-commit-minimum.md](skill-markets/fullstack4TraeV11/references/todos/P3-6-commit-minimum.md)。

详见 [references/todos/audit-history/2026-08-16-mentioned-but-not-parsed.md §5](skill-markets/fullstack4TraeV11/references/todos/audit-history/2026-08-16-mentioned-but-not-parsed.md)。

#### V11.8.7.1 — 5 项用户硬要求 3 连修 + V11-AP17 修复(2026-08-18)

- **5 项用户硬要求 3 连修**(用户 2026-08-18 拍板):
  - `init-from-zero.py` `--layout` 移除 `v11-default` 兼容值 + `create_project_module()` 强保 module 存在:**LOW**(逻辑)
  - `spec-purge.py` `archive_keep_v12_layout()` 不展平 archive 子目录:**LOW**(逻辑)
  - `_lib_paths.py` 合并 3 个分散模块(`paths` + `project_paths` + `check_paths_config`):**LOW**(重构)
  - `check_paths_config.py` 提升为项目侧独立守卫脚本:**LOW**(独立化)
  - `references/project-structure.md` 加 `docs/modules/` 不存在必检项:**LOW**(协议)
- **V11-AP17 修复**(`templates/hooks/doc-sync-gate.py` 死锁):
  - 移除 `docs/modules/` 死锁检查(原因为 init-from-zero 创建占位 .gitkeep 但 V11 规范无 stage 写 modules/ 内容,导致 PreToolUse 永远 BLOCK):**LOW**(逻辑)
  - 真相源迁移:`docs/specs/changes/_module.md`(项目级) + `fact/module.md`(change 级):**LOW**(协议)
- **新增资产**:
  - `references/config.example.yaml` / `project-gitignore-template.md` / `state-card.schema.json`:**LOW**(配置 schema)
  - `templates/ci/v12-gate.yml`(rename 自 `v11-gate.yml`):**LOW**(CI 模板)
  - `scripts/_lib_paths.py` / `check_paths_config.py` / `_todoapp_e2e.py` / `_todoapp_e2e_v2.py` / `_total_verify.py`(5 个新/独立脚本):**LOW**(stdlib 路径校验 + e2e 验证,无外联)
  - `skill-markets/fullstack4TraeV11/.gitignore`(本地保护 `case-studies/` 等外部测试项目):**LOW**(本地保护)
- **case-driven-skill-audit 接入**(`.agents/skills/`,非 skill-markets):
  - 1 SKILL.md + 1 references(`case-2-evidence.md`,case 2 desktop-pet-v11 实跑证据):**N/A**(方法论,非可执行资产)
- **auto-task/fullstackselfimproving**:
  - 1 prompt.md 模板:**N/A**(协议入口)
- **实跑扫描(2026-08-18)**:trae-security-review scan_skills_dir.py V2.1 → **HIGH 0 + MEDIUM 0 + LOW 0 → PASS**(决策矩阵:HIGH 0 + MEDIUM ≤ 3 = 🟢 PASS)
- **评分维持 5.0** 🟢(5 项硬要求 + V11-AP17 修复 + 多件入仓,均为 LOW 或 N/A)
- **退出码语义清晰**:0=PASS / 1=FAIL — 不存在"诱导绕过"风险
- **不引入新依赖**;全部 stdlib(pyyaml 已是项目既有)
| **docsify-doc-builder** (v2.0) | 1 md + 8 ps1/sh + 6 tpl | 0 | 6 | 0 | **3.5** | 🟡 | v2.0 升级（UE5 暗色主题 + 智能侧边栏 + Markmap 15 节点全展开 + Mermaid 4 图全屏/导出 + Playwright 验证 + 8 示例文档）。6 MEDIUM 全为 `http://localhost:3000` 本地提示语（SKILL.md ×1 + init-docs.ps1 ×2 + init-docs.sh ×1 + serve.ps1 ×1 + serve.sh ×1 + README.md ×1），无外网通信；CDN 链接全部 HTTPS（cdn.jsdelivr.net + esm.sh）。Shell 执行面含 8 个 ps1/sh 脚本（init-docs/serve/check-env/generate-sidebar）。GitNexus detect_changes：36 符号变更，0 受影响流程，🟢 LOW 风险 |
| **trae-security-review** | 1 md + 2 agent + 3 ref + 1 py | 2 | 3 | 2 | **3.9** | 🟡 | 2 个 HIGH 和 3 个 MEDIUM 均为 risk-patterns.md 和 skill-scanner.md 中的风险模式文档引用（非可执行） |
| **`.agents/`(项目级本地 agent 配置,非 skill 市场)** | 1 README + 1 learning + 1 项目核心 + 3 stub(.agents/rules/*) + 3 skill + 8 ref + 6 assets + 1 hooks.json + 3 references(NEW,V11.8.0.1 project-rule-skill 同包)+ 1 SKILL.md(v2.0.0) | 15 | 5 | 5 | **N/A** | ⚪ 不评级 | **实跑扫描(2026-08-15 14:39,24 文件,2026-08-15 V11.8.0.1 迁移后再扫描文件数变更)**:扫描结果来自 `.agents/skills/security-review/references/`(language-patterns / vuln-categories / secret-patterns + 配套),**全部 HIGH 15 + MEDIUM 5 + LOW 5 均为安全规则教学文档引用**(描述反例规则 = 文档本质,如 secret-patterns.md 含 token 示例字串,vuln-categories.md 描述 eval/exec 模式)。**V11.8.0 协议先行新增 3 文件 0 命中**:原在 `.agents/rules/` 现已迁移到 `.agents/skills/project-rule-skill/references/`(见 V11.8.0.1 路径迁移通知);`scripts/_check_protocol_coverage.py` 200+ 行 std lib 检测工具(本仓库侧)。**注**: `.agents/` 不在 skill 市场范围内,**SECURITY-MAP 不强制评级**;如需整改走与 V11.7.1 同款白名单机制(`<!-- scan-whitelist -->` 包裹文档命中行)。 |
| **skills-security-scan**（外部） | 1 md + 1 py + 1 json | 0 | 1 | 0 | **4.8** | 🟢 | 1 个 MEDIUM：main.py 中的 HTTP 引用 |
| **trae-local-data-export** | 1 md + 4 ref + 7 py | 0 | 1 | 0 | **4.8** | 🟢 | 1 MEDIUM 为 db-location.md 中的 PowerShell 示例命令（文档引用，非可执行）；7 脚本全部 stdlib + pycryptodome，无 HTTP 外联，无远端上传；密钥文件 decrypted_key.json 默认 gitignore |
| **agent-dev-control-kit** | 1 md + 9 skill + 9 tpl + 11 ref + 19 py + 2 wf + 9 scaffold | 0 | 3 | 4 | **3.4** | 🟢 | **实跑扫描（2026-08-13 23:58，最新）**：trae-security-review scan_skills_dir.py V2.1 → **HIGH 0 + MEDIUM 3 + LOW 4 → PASS**（决策矩阵：HIGH 0 + MEDIUM ≤ 3）。3 MEDIUM = release-process-control/SKILL.md ×1 + release-process-template.md ×1 `HTTP_INSECURE`（文档 HTTP 示例）+ scaffolds/python/files/guards/test-coverage-guard.py ×1 `SHELL_EXEC`（子进程 pytest 调用，参数化命令）；4 LOW = init-control-kit.py ×3 `STACK_LEAK`（DEBUG 栈追踪示例）+ asset-management-control/SKILL.md ×1 `WEAK_CRYPTO`（SHA-256 升级建议文档引用）。**本子代理 V0.5 升级**：(a) 改 3 文件：presets/README.md（4 处 `_index.json` → `_index.yaml`）+ registry/gates.yaml（+2 条 pre-merge/pre-release gate）+ pre-commit-template.sh（opt-in 化）；(b) 新增 6 文件：templates/changed-file-impact-guard-template.yaml + scaffolds/nodejs/files/guards/changed-file-impact-guard.mjs + skills/guard-control/templates/changed-file-impact-guard-template.yaml + scripts/install-husky.py + scripts/install-husky.test.py + guard 同步模板。**网络面**：全部 stdlib（argparse / pathlib / subprocess + 命令白名单 / yaml），无外联；HTTP 仅出现在 SKILL.md 文档示例中。**安全锚点**：opt-in 化的 pre-commit 默认不安装（用户显式 opt-in 才装 husky 钩子，避免强改 .git/hooks）；新增的 changed-file-impact-guard 是只读扫描（不写文件），失败仅警告不阻断（per AGENTS.md §7.1 R-1） |

---

## 三、高风险条目详细清单

> 以下为扫描到但确认为安全的文档引用，不影响实际运行时安全。

| 包 | 文件 | 检测项 | 实际风险 | 说明 |
|----|------|--------|---------|------|
| trae-pro/sandbox.md | sandbox.md | CMD_RM_RF | 🟢 无 | 文档中的 rm -rf 示例说明 |
| modelscope/api-inference.md | api-inference.md | HARDCODED_SECRET | 🟢 无 | 文档中的示例 API Key |
| browser-use/local-usage.md | local-usage.md | HARDCODED_SECRET | 🟢 无 | 文档中的示例 API Key |
| acceptance/e2e-audit-agent.md | e2e-audit-agent.md | DYN_EVAL | 🟢 无 | Agent 指令中的 eval 举例 |
| acceptance/perf-verification-agent.md | perf-verification-agent.md | HARDCODED_SECRET | 🟢 无 | 文档中的示例密钥 |
| trae-security-review/agents/skill-scanner.md | skill-scanner.md | CMD_RM_RF, DYN_EVAL | 🟢 无 | 安全检测模式的文档举例 |
| trae-security-review/references/risk-patterns.md | risk-patterns.md | 全部 7 项 | 🟢 无 | 风险模式说明文档，非可执行代码 |

**结论：所有 HIGH 风险均为文档中的示例/说明引用，无真实可执行漏洞。**

---

## 四、各脚本安全评估

### 需要关注的脚本（有实际执行面）

| 脚本 | 包 | 风险 | 说明 |
|------|-----|------|------|
| `scripts/vaslib/synthesizer/cosyvoice_adapter.py` | Voice-Acting | 🟡 MEDIUM | Shell 调用 TTS 引擎 + HTTP 外联 |
| `scripts/vaslib/synthesizer/qwen_tts_adapter.py` | Voice-Acting | 🟡 MEDIUM | HTTP 外联调用 API |
| `scripts/export_subculture_package.py` | shuxia-novel-engine | 🟡 MEDIUM | subprocess 调用 |
| `scripts/comfy_menu.py` | comfyui | 🟡 MEDIUM | Shell 调用 |
| `scripts/check_env.py` | comfyui | 🟡 MEDIUM | Shell 调用 + HTTP |
| `scripts/webhook_server.py` | browser-use-cloud | 🟡 MEDIUM | HTTP 服务端 |
| `scripts/scan_skills_dir.py` | trae-security-review | 🟢 LOW | 仅文件扫描，无 Shell/网络执行 |
| `scripts/init-docs.ps1` | docsify-doc-builder | 🟡 MEDIUM | Shell 执行（New-Item/Compress-Archive/IO.File.WriteAllText）+ 本地 dev server 提示 |
| `scripts/forge_project_rules_skill.py` | project-rules-gate → common-project-coding-conf（2026-08-19 迁移） | 🟢 LOW | 纯文件 IO + 模板渲染；无 subprocess / 无网络 / 无 eval-exec；仅在 --project-root 内操作；改写 .trae/rules/README.md 是高频写操作（明确语义）；--move 用 pathlib.Path.replace() 移走到 _archived/（归档非删除，可回溯）；frontmatter 注入只追加不覆盖（已有则跳过） |
| `scripts/cpcc-self-check.mjs` | common-project-coding-conf | 🟢 LOW | 纯文件 IO（fs.readFileSync / fs.statSync）+ child_process.execSync（探测 npx gitnexus --version，超时 10s，stdio: 'ignore'）；JSON 输出；无网络外联 / 无 eval-exec / 无写入项目路径外 |
| `scripts/serve.ps1` | docsify-doc-builder | 🟡 MEDIUM | Shell 执行（Start-Process 启动 docsify serve）+ localhost 浏览器唤起 |
| `scripts/init-docs.sh` | docsify-doc-builder | 🟡 MEDIUM | Shell 执行 + localhost 浏览器唤起 |
| `scripts/serve.sh` | docsify-doc-builder | 🟡 MEDIUM | Shell 执行 + localhost 浏览器唤起 |
| `src/execution/skill-change-control.mjs` | CLI | 🟢 LOW | 纯文件 IO（existsSync/mkdirSync/cpSync/rmSync/writeFileSync）+ 风险分级 + 备份/回滚；无 subprocess / 无网络 / 无 eval-exec |
| `src/execution/skill-install-control.mjs` | CLI | 🟢 LOW | 纯文件 IO + symlink/copy + 审计日志；无 subprocess / 无 HTTP；依赖解析为本地 IO |
| `scripts/skill-security-guard.py` | CLI | 🟡 MEDIUM | subprocess 调用 trae-security-review/scan_skills_dir.py（业务必需，参数化命令白名单 scan_skills_dir.py）；纯文件扫描，无网络 |
| `scripts/skill-structure-guard.py` | CLI | 🟢 LOW | 纯文件读取 + 正则匹配；无 subprocess / 无网络 |
| `src/guards/skill-dependency-guard.mjs` | CLI | 🟢 LOW | 纯文件 IO + YAML 解析；无 subprocess / 无网络 |
| `scripts/skill-capability-guard.py` | CLI | 🟢 LOW | 纯文件读取 + 正则匹配；无 subprocess / 无网络 |
| `scripts/doc-sync-guard.py` (NEW 2026-08-15 横切守卫) | CLI | 🟢 LOW | 纯 stdlib + subprocess 调 git diff/show(参数化路径无 Shell 注入);无 HTTP/无 eval-exec;读 staged 变更判定触发,缺同步即 exit 1;--self-test 自检模式(造临时 git 仓库跑 6 反例) |

### 安全脚本（纯本地/无外联）

| 脚本 | 包 | 说明 |
|------|-----|------|
| `scripts/spec-validate.py` | fullstack4TraeV7 | 纯本地 spec 校验 |
| `scripts/render_md.py` | openapi-doc-exporter | 纯本地 markdown 渲染 |
| `scripts/split_by_prefix.py` | openapi-doc-exporter | 纯本地文件分割 |
| `scripts/validate_openapi.py` | openapi-doc-exporter | 纯本地 OpenAPI 校验 |
| `scripts/model_kb.py` | comfyui | 知识库查询（HTTP 引用为参考文档） |
| `scripts/vision-audit.py` | vision-audit | 本地 VL 模型分析 |

---

## 五、更新规则

```
1. 新建 skill → 运行 scan_skills_dir.py 扫描 → 填入本表
2. 新增/修改脚本 → 评估执行面 → 更新评分
3. 引入第三方 skill → 先扫描 → 判定 🟢 才准入
4. 每半年重新扫描全量 → 更新判定
5. 评分 < 3.0（🔴）的包 → 标记为需整改，下次变更前必须先修复
```

---

## 六、扫描命令

```powershell
# 全量扫描
python skill-markets\trae-security-review\scripts\scan_skills_dir.py skill-markets auto_reports

# 单包扫描
python skill-markets\trae-security-review\scripts\scan_skills_dir.py skill-markets\{package_name} auto_reports

# 查看报告
code auto_reports\{package_name}_{timestamp}.md
```

---

*生成日期: 2026-08-13 | 扫描引擎: trae-security-review/scan_skills_dir.py v2.1*
*本次微更新 2026-08-19: agent-dev-control-kit SKILL.md 文档瘦身 (482→244 行,纯 PATCH),无脚本/契约变更,评分不变 (3.6 🟡)*
*本次更新: agent-dev-control-kit 首次登记（独立群岛表新增一行）。**实跑扫描（2026-08-13 23:58）**：HIGH 0 + MEDIUM 3 + LOW 4 → **PASS**（决策矩阵 HIGH 0 + MEDIUM ≤ 3）。3 MEDIUM = release-process-control/SKILL.md ×1 + release-process-template.md ×1 HTTP_INSECURE（文档 HTTP 示例）+ scaffolds/python/files/guards/test-coverage-guard.py ×1 SHELL_EXEC（子进程 pytest 调用，参数化命令）；4 LOW = init-control-kit.py ×3 STACK_LEAK（DEBUG 栈追踪示例）+ asset-management-control/SKILL.md ×1 WEAK_CRYPTO（SHA-256 升级建议文档引用）。本子代理 V0.5 升级：改 3 文件（presets/README.md + registry/gates.yaml + pre-commit-template.sh opt-in 化）+ 新增 6 文件（changed-file-impact-guard 模板/脚本 ×3 + install-husky.py/.test.py ×2 + guard 同步模板 ×1）。下一轮升级前 backlog: 无（已 PASS）*

| skill-bundle | 1 md | 0 | 0 | 0 | **5.0** | 🟢 | 纯规范文档,无脚本,无网络面；关联 src/bundle.mjs + install-guards.mjs（命令均经三道闸，命令路径在仓库内）；BND-001~007 守卫接入 L1-L4 Gate 7 处（pre-commit diff / pre-push all / CI L3+L4 all / 显式 npm run test:bundle） |


| guard-approver | 1 md | 0 | 0 | 0 | **5.0** | 🟢 | 纯规范文档;关联 scripts/change-guard-approver.mjs(Node,0 网络面);Tier 4 路径保护清单防止 agent 改守卫自绕过 |
| **guard-gate-smith** (NEW 2026-08-14 §3 收紧方案 A) | 1 md (SKILL) | 0 | 0 | 0 | **5.0** | 🟢 | **实跑扫描（2026-08-14 15:14,最新）**：scan_skills_dir.py V2.1 → HIGH 0 + MEDIUM 0 + LOW 0 → PASS。**纯规范文档类**：1 SKILL.md,0 脚本,0 网络面。**职责**：registry/skills.yaml 中央注册表 + scripts/<name>-guard.* 自治 guard + .husky/<name>-gate gate 路由的"唯一维护 agent"。**实现**：src/guards/skill-registration-guard.mjs(Node,0 网络面,纯 fs/yaml 操作) + scripts/guard-router.mjs(纯 spawn 派发,不引入新执行面)。**安全收益**：消除"agent 改 guard/gate 自绕过"漏洞(原 3 个共享 guard 脚本可被任意 agent Edit,现 5 类白名单路径通过 guard-approver Tier 3 + 注册表守卫自举)。**与 guard-approver 关系**:guard-smith = guard-approver 的"guard/gate 路由"特化版本。**§3 拆分 2026-08-14 落地**:guard-smith agent 通过 `scripts/forge-skill-guard.py` 模板生成器一次性生成 47 个 scripts/<name>-guard.py,模板检测 skill 是否含 scripts/ 自动选 aspects(structure + security),杜绝 47 份风格漂移。新增 scripts/_guard_lib.py 统一 wrapper 主入口(JSON + exit code)。 |

| **scripts/forge-skill-guard.py** (NEW 2026-08-14 §3 拆分方案 A) | 1 py | 0 | 0 | 0 | **5.0** | 🟢 | 模板生成器(纯 fs 操作,无网络/无 Shell)。接收 skill 名列表 + 检测 has_scripts 自动选 aspects,生成 scripts/<name>-guard.py wrapper。支持 `--all` / `--dry-run` |
| **scripts/_guard_lib.py** (NEW 2026-08-14 §3 拆分方案 A) | 1 py | 0 | 0 | 0 | **5.0** | 🟢 | 守卫共享工具(纯标准库)。`cli_main(check_fn, label)` 统一 wrapper 主入口:解析 argv[1] → 调 check_fn → JSON 输出 → exit 0/1 |
| **scripts/<name>-guard.py × 47** (NEW 2026-08-14 §3 拆分方案 A) | 47 py (自动生成) | 0 | 0 | 0 | **5.0** | 🟢 | 47 个 wrapper:每个接收 skill 名,importlib 加载共享的 structure/security 守卫并合并结果。**自检**：0 eval/exec/密码/api_key 关键词;模板唯一生成保证 0 风格漂移 |
| **scripts/run-agent-dev-control-kit-tests.py** | 1 py | 0 | 7 | 0 | **3.6** | 🟡 | 7 个 MEDIUM:agent-dev-control-kit skill 自带 catalog 守卫,引入多个 subprocess+shell 调用(已注释说明,可改造为参数化命令,但属 pre-existing 问题,本次未触碰) |

| daily-vibe-coding | 2 md (SKILL + installation-prompt) | 0 | 0 | 0 | **5.0** | 🟢 | 纯规范+prompt 文档,无脚本,无网络面;agent 部署在 TRAE Work 云端定时任务 |
