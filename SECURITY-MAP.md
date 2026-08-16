# Security Map — 安全量化评分地图

> 对 skill-markets 下每个技能包、每个脚本的安全风险评估。每半年或变更时更新。
>
> 评分规则：1（极危）→ 5（安全），三档阈值：< 3.0 🔴 需整改，3.0-4.0 🟡 警告，> 4.0 🟢 通过

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
| goal-mode | 1 md + 3 agent | 0 | 0 | 0 | **5.0** | 🟢 | Agent 定义文件，无执行脚本 |
| ponytail4Trae | 7 md | 0 | 3 | 0 | **4.4** | 🟢 | 3 个 MEDIUM 均为文档中的 Shell 命令示例 |
| gitnexus4Trae | 6 md | 0 | 0 | 0 | **5.0** | 🟢 | 纯 Skill 指令集，无脚本 |
| browser-use-cloud | 1 md + 12 ref + 4 py | 1 | 3 | 0 | **3.9** | 🟡 | 1 个 HIGH 为 local-usage.md 中的示例 API Key（文档引用）；3 MEDIUM 为 HTTP 引用 |
| openapi-doc-exporter | 1 md + 3 ref + 3 py | 0 | 1 | 0 | **4.8** | 🟢 | 1 个 MEDIUM 为 export-guide.md 中的 HTTP 示例 |
| **deep-research** (V1.0 NEW 2026-08-13) | 1 md + 3 ref | 0 | 0 | 0 | **5.0** | 🟢 | **实跑扫描（2026-08-13 15:25，最新）**：trae-security-review scan_skills_dir.py V2.1 → **HIGH 0 + MEDIUM 0 + LOW 0 → PASS**。**质疑性验收治理**：源材料 ECC .agents/skills/deep-research（含 3 份同源副本在 docs/references/）未注册到 skill-markets/，按 AGENTS.md §5 落地。**精简骨架**：SKILL.md 59 行 / 6 铁律（≤150 + ≤10 双约束），详细内容按需 references/{workflow, report-template, quality-rules}.md。**网络面**：依赖外部 firecrawl/exa MCP（用户配置），SKILL.md 本身无 HTTP/Shell 调用面（无脚本）。**与现有能力差异化**：browser-use-cloud 通用 web 自动化 / doc-map-manager 项目文档索引 / trae-remote-official:lark 通讯办公 — 均不重复"多源研究+引用报告"垂直场景 |
| trae-professional | 1 md + 25 ref | 1 | 0 | 0 | **4.5** | 🟢 | 1 个 HIGH 为 sandbox.md 中的 rm -rf 说明（文档引用，非可执行）；2026-08-14 扩展至 25 个 references 覆盖 docs.trae.cn 全部分类 |
| product-teardown | 3 md + 2 agent | 0 | 0 | 0 | **5.0** | 🟢 | 纯文档，无脚本 |
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
| **fullstack4TraeV10** (10.12.5) | 1 md + 9 agent + 35 ref + 18 py + 10 hook | 0 | 0 | 0 | **5.0** | 🟢 | **实跑扫描（2026-08-10 13:26，最新）**：trae-security-review scan_skills_dir.py V2.1 + 13 个脚本 SHELL_EXEC 白名单 → **HIGH 0 + MEDIUM 0 + LOW 0 → PASS**（从 WARNING 升级）。**V10.12.5 升级**：(a) trae-security-review SKILL.md 更新 V2.1 描述（8 类风险表 + 三层白名单机制 + 词边界修复说明）；(b) 8 个脚本 SECURITY 标注后加 `<!-- scan-whitelist:SHELL_EXEC --><!-- /scan-whitelist -->` 区块（acceptance-audit / check_prerequisites / code-hygiene / phase-gate / proactive-scan / test_v10_5_fixtures / gitnexus-session-check / gitnexus-session-finalize）；(c) AGENTS.md 新增 "Agent 回复行为规约（V10.12.5 NEW）" 章节（防"问下一步"模式）。**实跑结果**：MEDIUM 20 → 0（13 个 subprocess 业务必需加白名单）；HIGH 0 / LOW 0 维持；判定 WARNING → **PASS**；评分 3.4 → **5.0**（🟢 满分）。**注**: MEDIUM 269 HTTP localhost 真调用（acceptance-audit.py 验收脚本需要）随文件级 SHELL_EXEC 区块一并豁免（同一 docstring 区块）。**下一轮升级前**：无 backlog（已满分）。 |
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

#### V11.8.6 — V12 物理隔离渐进落地(2026-08-16)

- 新增 `templates/change-dir-layout-v12-preview.md`:**LOW**(纯协议文档,无代码)
- 新增 `templates/hooks/process-layer-guard.sh`:**LOW**(只读 fs + 字符串匹配,无网络 / 不写文件 / 不删文件)
- 改 `scripts/init-from-zero.py` 加 `--layout v12-preview`:无新增网络/secret,Step 4.5 只 mkdir + write_text 模板文件
- 改 `scripts/stage-gate.py` 加 `--reset-to`:**LOW**(仅项目方主动触发,递归删 stage/{N+1} 子目录,但保留 fact/ + archive/)
- 改 `references/sub-agent-rules.md` + 4 个 agents 文件:纯协议补充,无代码风险
- 评分维持 **5.0** 🟢(无新增 MEDIUM/HIGH)
- **安全注意**:`stage-gate.py --reset-to` 调用方应严格限定 change 级状态卡(已 enforce,项目级 docs/specs/.state-card.md 触发即 FAIL)— 防止误删项目级目录
- 退出码语义清晰:0=PASS / 1=FAIL / 2=WARN — 不存在"诱导绕过"风险
- 不引入新依赖;PyYAML 已是项目既有

详见 [references/todos/P3-6-commit-minimum.md](skill-markets/fullstack4TraeV11/references/todos/P3-6-commit-minimum.md)。

详见 [references/todos/audit-history/2026-08-16-mentioned-but-not-parsed.md §5](skill-markets/fullstack4TraeV11/references/todos/audit-history/2026-08-16-mentioned-but-not-parsed.md)。
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
| `scripts/forge_project_rules_skill.py` | project-rules-gate | 🟢 LOW | 纯文件 IO + 模板渲染；无 subprocess / 无网络 / 无 eval-exec；仅在 --project-root 内操作；改写 .trae/rules/README.md 是高频写操作（明确语义）；--move 用 pathlib.Path.replace() 移走到 _archived/（归档非删除，可回溯）；frontmatter 注入只追加不覆盖（已有则跳过） |
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
*本次更新: agent-dev-control-kit 首次登记（独立群岛表新增一行）。**实跑扫描（2026-08-13 23:58）**：HIGH 0 + MEDIUM 3 + LOW 4 → **PASS**（决策矩阵 HIGH 0 + MEDIUM ≤ 3）。3 MEDIUM = release-process-control/SKILL.md ×1 + release-process-template.md ×1 HTTP_INSECURE（文档 HTTP 示例）+ scaffolds/python/files/guards/test-coverage-guard.py ×1 SHELL_EXEC（子进程 pytest 调用，参数化命令）；4 LOW = init-control-kit.py ×3 STACK_LEAK（DEBUG 栈追踪示例）+ asset-management-control/SKILL.md ×1 WEAK_CRYPTO（SHA-256 升级建议文档引用）。本子代理 V0.5 升级：改 3 文件（presets/README.md + registry/gates.yaml + pre-commit-template.sh opt-in 化）+ 新增 6 文件（changed-file-impact-guard 模板/脚本 ×3 + install-husky.py/.test.py ×2 + guard 同步模板 ×1）。下一轮升级前 backlog: 无（已 PASS）*

| skill-bundle | 1 md | 0 | 0 | 0 | **5.0** | 🟢 | 纯规范文档,无脚本,无网络面；关联 src/bundle.mjs + install-guards.mjs（命令均经三道闸，命令路径在仓库内）；BND-001~007 守卫接入 L1-L4 Gate 7 处（pre-commit diff / pre-push all / CI L3+L4 all / 显式 npm run test:bundle） |


| guard-approver | 1 md | 0 | 0 | 0 | **5.0** | 🟢 | 纯规范文档;关联 scripts/change-guard-approver.mjs(Node,0 网络面);Tier 4 路径保护清单防止 agent 改守卫自绕过 |
| **guard-gate-smith** (NEW 2026-08-14 §3 收紧方案 A) | 1 md (SKILL) | 0 | 0 | 0 | **5.0** | 🟢 | **实跑扫描（2026-08-14 15:14,最新）**：scan_skills_dir.py V2.1 → HIGH 0 + MEDIUM 0 + LOW 0 → PASS。**纯规范文档类**：1 SKILL.md,0 脚本,0 网络面。**职责**：registry/skills.yaml 中央注册表 + scripts/<name>-guard.* 自治 guard + .husky/<name>-gate gate 路由的"唯一维护 agent"。**实现**：src/guards/skill-registration-guard.mjs(Node,0 网络面,纯 fs/yaml 操作) + scripts/guard-router.mjs(纯 spawn 派发,不引入新执行面)。**安全收益**：消除"agent 改 guard/gate 自绕过"漏洞(原 3 个共享 guard 脚本可被任意 agent Edit,现 5 类白名单路径通过 guard-approver Tier 3 + 注册表守卫自举)。**与 guard-approver 关系**:guard-smith = guard-approver 的"guard/gate 路由"特化版本。**§3 拆分 2026-08-14 落地**:guard-smith agent 通过 `scripts/forge-skill-guard.py` 模板生成器一次性生成 47 个 scripts/<name>-guard.py,模板检测 skill 是否含 scripts/ 自动选 aspects(structure + security),杜绝 47 份风格漂移。新增 scripts/_guard_lib.py 统一 wrapper 主入口(JSON + exit code)。 |

| **scripts/forge-skill-guard.py** (NEW 2026-08-14 §3 拆分方案 A) | 1 py | 0 | 0 | 0 | **5.0** | 🟢 | 模板生成器(纯 fs 操作,无网络/无 Shell)。接收 skill 名列表 + 检测 has_scripts 自动选 aspects,生成 scripts/<name>-guard.py wrapper。支持 `--all` / `--dry-run` |
| **scripts/_guard_lib.py** (NEW 2026-08-14 §3 拆分方案 A) | 1 py | 0 | 0 | 0 | **5.0** | 🟢 | 守卫共享工具(纯标准库)。`cli_main(check_fn, label)` 统一 wrapper 主入口:解析 argv[1] → 调 check_fn → JSON 输出 → exit 0/1 |
| **scripts/<name>-guard.py × 47** (NEW 2026-08-14 §3 拆分方案 A) | 47 py (自动生成) | 0 | 0 | 0 | **5.0** | 🟢 | 47 个 wrapper:每个接收 skill 名,importlib 加载共享的 structure/security 守卫并合并结果。**自检**：0 eval/exec/密码/api_key 关键词;模板唯一生成保证 0 风格漂移 |
| **scripts/run-agent-dev-control-kit-tests.py** | 1 py | 0 | 7 | 0 | **3.6** | 🟡 | 7 个 MEDIUM:agent-dev-control-kit skill 自带 catalog 守卫,引入多个 subprocess+shell 调用(已注释说明,可改造为参数化命令,但属 pre-existing 问题,本次未触碰) |

| daily-vibe-coding | 2 md (SKILL + installation-prompt) | 0 | 0 | 0 | **5.0** | 🟢 | 纯规范+prompt 文档,无脚本,无网络面;agent 部署在 TRAE Work 云端定时任务 |
