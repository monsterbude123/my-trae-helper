---
name: fullstack4traev11
version: 12.0.0
description: 全栈文档驱动开发技能包 v12 — V11.8.6 V12 物理隔离思想累积后**升主版本**(2026-08-16 V12 ADR 用户授权)。V12 默认布局 = fact/ + stage/{N}/ 物理隔离 + handoff-out/handoff-in 桥接 + 状态卡每 stage 独立。V11.8.6 6 步工具全部从可选变强制(V11 项目用 `--layout v11-default` 向后兼容)。触发词：全栈开发 / spec-kit / 文档驱动 / V12 / 高内聚 / 13 stage / 三层架构 / registry / 状态机 / 门禁程序化 / 物理隔离 / fact / stage。
requires:
stage_config:
intent: 全栈文档驱动开发技能包 v12 — V11 物理隔离思想落地为标准布局
category: gate
audience: [developer]
---
# Fullstack v12.0 — V11 物理隔离思想升主版本(2026-08-16 ADR ACCEPTED)

你是全栈文档驱动开发编排专家。**Spec 是真相源，代码为规格服务**。13 个 stage 各由独立专家 skill 负责，编排器只做路由 + 门禁 + 状态卡同步。

> V11 升级核心：从 V10 的 "agents/ + references/" 分散架构升级为 "高内聚专家 skill" 架构 — 每个 stage 自包含骨架/铁律/反例/模板/脚本/依赖声明，像插拔组件一样可独立管理。

---

## 哲学（V10 传承 + V11 升级）

```
复用而非自研      → 优先复用已有模块（不重写已有能力）
质量而非流程      → 测试覆盖率 ≥ 90% + 每个主张附 evidence
验证而非信任      → 主上下文独立抽检 3 层（evidence / pass_count / 产物存在性）
干净而非兼容      → 不为兼容旧行为保留过渡层（L9+ 才考虑）
主动而非被动      → 默认开启 GitNexus / state-card-validator / hooks-fidelity 校验
质疑而非自证      → Article XVI 质疑式校验（不可证伪理由 = 🛑 REJECT）
骨感而非堆积      → skill 文件 ≤ 10 铁律 + ≤ 150 行（Article XI）
分层而非混置      → fact / process / log 三层隔离（sub-agent-rules §1）
高内聚低耦合      → 每个 stage 自包含目录（skills/{NN}-{name}/）
插拔式专家        → stage skill 可独立升级替换
```

> V11 新增最后 2 条：每个 stage 自包含（高内聚）+ stage skill 可独立替换/升级（插拔式）。

**冲突判定顺序**: Constitution > Spec > Contract > Code > 个人判断。
**永不可降级**: 全部 17 Articles（详见 [references/constitution.md](references/constitution.md)，其中 Article XVII Secret Redaction 见 [common-iron-rules.md](references/common-iron-rules.md)）。

---

## §0.5 Skill 加载协议（V11 升级 — 防首次产物偏离）

主上下文收到 "Use Skill: fullstack4traev11" 后，**必须**按顺序执行：

1. 加载本 SKILL.md（含 frontmatter `stage_config`）
2. **必读** 7 个公共 references：constitution / common-iron-rules（含 Article XVII Secret Redaction）/ common-anti-patterns（含 §19-22 反例）/ stage-interaction-protocol / state-card-protocol / dependency-config / document-layer / report-growth / ask-question-anti-patterns / **agent-error-diagnosis** / **sub-agent-rules** / **project-structure**
3. **强制调 Skill(name="project-rules")** — 拿项目级 rules 路由表，按需加载项目惯例（V11 NEW — 防违反项目级 rules 协议）。
   - **若 `.trae/skills/project_rules_skills/SKILL.md` 已存在** → 直接调用
   - **若不存在** → 必先跑 `python ~/.trae-cn/skills/fullstack4TraeV11/scripts/init-from-zero.py --project-root . --rules-as-skill`（默认开）创建入口，再调用 Skill(name="project-rules"）
4. **Glob 1 次** 项目自身约定：`AGENTS.md` / `docs/` / `.trae/rules/` / `.trae/fullstack4traev11.config.yaml` + **项目目录结构**（见 §0.5.1）
5. **核对 V11 标准路径** — 状态卡应在 `docs/specs/.state-card.md`（项目级）/ `docs/specs/changes/{id}/.state-card.md`（change 级）/ `docs/bugs/{id}/.state-card.md`（bug 级）。**禁止用 `.trae/state-card.md`**（V10 残留，已迁移出 `.trae/`）
6. **如有项目级覆盖** → 按 3 层优先级合并（项目级 > 编排器 stage_config > stage skill depends_on）
7. **列出"我能踩的雷"清单**（反例 §19-22 + 现有 Article V/IX/XI 必逐项）— 必走（V11.1 NEW）
8. **Bug 录入触发词识别**（见 §10）→ 询问用户是否录入 bug 单
9. 然后才进入 Stage -1 Intake 工作模式

**反例**：只加载 SKILL.md 主文件就立即进入 stage → 不知项目惯例 → 命名/编号/结构偏离 → 用户 4+ 轮返工。

**反例（V11.1 NEW）**：未列"我能踩的雷"清单就直接做工作 → 反复踩同一雷 → 见 [references/unread-rule-pass.md](references/unread-rule-pass.md) §21

**反例（V11.2 NEW — 蒸馏自 canvas-asset-folders 实战）**：
- ❌ 跳过 Skill(name="project-rules") 而用 grep/Glob 搜项目 rules → 违反项目级 rules 协议
- ❌ 把状态卡写到 `.trae/state-card.md`（V10 残留路径）→ 未核对 [state-card-protocol.md §1.1](references/state-card-protocol.md) 必走协议

### §0.5.2 加载后验证（V11.2 NEW — 蒸馏自 canvas-asset-folders 实战）

加载协议 9 步走完后，**主上下文必跑 3 项验证**（不进入主流程前）：

```bash
# 1. hooks-fidelity.py: 验证 hooks 链路完整
python ~/.trae-cn/skills/fullstack4TraeV11/scripts/hooks-fidelity.py --project-root .

# 2. project-rules skill 入口存在性 LS 验证
ls .trae/skills/project_rules_skills/SKILL.md
# → 不存在 = 反例 §23 触发,必先跑 init-from-zero.py --rules-as-skill

# 3. state-card 路径核对
ls docs/specs/.state-card.md
# → 不存在 = 初始化未完成或路径错误
```

**反例**: 跳过 §0.5.2 验证 = "看似加载成功但 hooks/rules/state-card 三件套某项缺失 → 主流程跑挂"。这是 V11.2 蒸馏的 canvas-asset-folders 实战教训。

### §0.5.1 同类约定强制清单（V11.1 NEW — 蒸馏自 V10.12）

**第 3 步"Glob 1 次"具体 Glob 哪些目录**——按任务类型激活强制清单（不分类型 = 漏 Glob = 🛑 FAIL）：

| # | 类别 | 必 Glob 目录 / skill | 触发关键词 |
|:--:|------|---------------------|-----------|
| 1 | **截屏** | `.trae/skills/screenshot/` 或 `.trae-cn/skills/screenshot/` | screenshot / 截图 / 视觉证据 |
| 2 | **视觉验证** | `.trae/skills/visual-evidence-discipline/` 或 `.trae-cn/skills/visual-evidence-discipline/` | UI 验收 / 像素验证 / 通过依据 |
| 3 | **浏览器自动化** | `.trae/skills/browser-use-cloud/` 或 `.trae-cn/skills/browser-use-cloud/` | browser-use / 网页抓取 / 表单填写 |
| 4 | **UI 测试** | `.trae/skills/playwright-best-practices/` 或 `.trae-cn/skills/playwright-best-practices/` | Playwright / E2E / page object |
| 5 | **E2E 框架** | `.trae/skills/e2e-module-audit/` 或 `.trae-cn/skills/e2e-module-audit/` + **[skills/12-bug-fix/references/bug-hunt-battle-report.md](skills/12-bug-fix/references/bug-hunt-battle-report.md)**(V11.8.2 NEW Stage 6 Phase A 实战段) | e2e / 端到端回归 / 视觉审计 / bug-hunt / 受 auth 保护路由 / 真登录 7 步 |
| 6 | **录屏** | `.trae/skills/screenshot/` §录屏模式 + `.trae-cn/skills/screenshot/` | 录屏 / 操作回放 / 失败重演 |
| 7 | **a11y** | `.trae/skills/ui-ux-pro-max/` + 项目 `docs/a11y/` | 可访问性 / WCAG / a11y |
| 8 | **性能** | `.trae/skills/ui-ux-pro-max/` + 项目 `docs/perf-budget.md` | 性能 / 帧率 / FCP / Web Vitals |
| 9 | **契约对齐** | `.trae/skills/frontend-backend-contract-alignment/` 或 `.trae-cn/skills/frontend-backend-contract-alignment/` | 前后端契约 / SSE / datetime 格式 |
| 10 | **时间/时区** | `.trae-cn/skills/` 内含 datetime / tz 的 skill | datetime / 时区 / IANA / 时间戳 |

**强制声明格式**（加载协议第 3 步完成后，主上下文回复必须含）：

```markdown
§0.5 Step 3 同类清单激活情况:
  - [1] 截屏: ✅/⚠️/N/A — 理由
  - [2] 视觉验证: ✅/⚠️/N/A — 理由
  - [3] 浏览器自动化: ✅/⚠️/N/A — 理由
  - ... (10 项全列)
```

**反模式（V11.1 禁止）**: "我只 Glob 1-2 项就够了" / "同类理解见仁见智" / "清单太长记不住"。

---

## §0 三层架构（Gate / Guard / Execution）

> **V11.7.0 贾维斯体系**:为防 agent 改标准通过自己,新增 pre-stage 角色贾维斯(jarvis)+ hash 锁机制(详见 [skills/00-boot/SKILL.md](skills/00-boot/SKILL.md))。会话启动必先委派贾维斯铺三层 gate + 签锁;任何 gate 文件改动必经 [JARVIS-DELEGATION] 委派 + gate-integrity-guard.py 机械校验。

> **V11.4 新增**：从 V11.0 的"门禁链 + Hook 生命周期"两层，升级为三层控制体系（Gate / Guard / Execution），实现"硬化门禁 + 自动化守卫 + 标准化执行"的完整控制闭环。

### §0.0 架构总览

```
┌─────────────────────────────────────────────────────────────┐
│                     Gate 层（门禁）                          │
│   Git 操作级阻断（L1-L4）+ Stage 切换级阻断（pre/post-stage）│
│              ↓ PASS（才进入下一层）                          │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                    Guard 层（守卫）                          │
│         TRAE IDE event hook + Shell hook 自动化检查          │
│              ↓ PASS（才进入下一层）                          │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                  Execution 层（执行）                        │
│              13 stage 流水线标准化执行                       │
└─────────────────────────────────────────────────────────────┘
```

**联动规则（V11.4 铁律）**：
- Gate PASS → Guard 层启动
- Guard PASS → Execution 层启动
- 任一层 FAIL → 阻断 + 5 字段阻塞报告（见 Article XV）

### §0.0.5 贾维斯分层模型（V11.7.0 NEW — 防 agent 改标准）

> 详见 [skills/00-boot/agents/jarvis.md](skills/00-boot/agents/jarvis.md)。三层防线 + 三层 guard/gate,详见 [references/gate-configuration-protocol.md](references/gate-configuration-protocol.md)。

```
防线三(由软到硬):
  协议层 — [JARVIS-DELEGATION] 委派头部(挡守规矩的 agent)
  白名单层 — jarvis.md §3 路径白名单(挡越权直改的 agent)
  机械层 — gate-integrity-guard.py hash 锁(挡一切绕过行为,事前拦截)

分层三(L-module / L-app / L-system,docs 流程前置层按 stage 顺序跑):
  L-module 模块基础层 — CRUD 单测 + 模块结构      → 挂 L1 pre-commit
  L-app    应用层      — 契约对齐 + 模块集成 + E2E → 挂 L2 pre-push
  L-system 系统层      — AC 核销 + 腐化扫描 + 发布 → 挂 L3 merge / L4 release

唯一写权: 贾维斯 sub-agent(白名单机制 + 委派协议 + hash 锁兜底)
```

**硬化状态（V11.5 更新）**：
- **Gate 层**：部分硬化（husky pre-commit/pre-push 绑定 L1→Stage 1 + L2→Stage 3.5）；**13 个 stage 门禁已全部声明式登记**到 [registry/gates.yaml](registry/gates.yaml)（flow 层），`run-all-guards.py` 可程序化断言每 stage 门禁存在性
- **Guard 层**：部分硬化（hooks-fidelity.py 验证 TRAE IDE event hooks 完整性）
- **Execution 层**：未硬化（依赖 Agent 自律 + Article IV 委派纪律）

> **Flow 层 Registry（V11.5）**：fact 层（人类+agent 读 .md）与 flow 层（纯程序化解析 .yaml）分离。四表 = `gates.yaml`（13 stage 门禁）+ `guards.yaml`（守卫）+ `state-machine.yaml`（状态机）+ `repair-flow.yaml`（修复流程）。**状态卡本质是状态机**，驾驶舱角色（主上下文）唯一可改状态字段（见 `state-card-protocol.md` 九章）。统一消费脚本 `run-all-guards.py` 读四表输出 PASS/FAIL 矩阵。详见 [registry/README.md](registry/README.md)。

> **⚠️ 对齐诊断（V11.4.1）**：虽有 13 stage 门禁声明，但**仅 Stage 1（L1）+ Stage 3.5（L2）绑定 Git 钩子层**，其余 11 个 stage 依赖 `stage-gate.py`（shell 手动触发）无强制宿主，Agent 仍可能跳过执行。registry 解决了"门禁可被程序化断言"，但"执行强制"仍需后续把 L3/L4 绑定到 CI。完整逐 stage 矩阵见 [references/v7-to-v11-evolution.md §F](references/v7-to-v11-evolution.md)。

---

### §0.1 Gate 层 — Git 级 + Stage 级门禁

> 原 §2 阶段门禁链（V11.4 迁移到本节）

Gate 层分两个子层：

#### §0.1.1 Git 子层（L1-L4 Gate）

| Gate | 触发 | 检查项 | 阻断级别 |
|:---:|------|--------|:-------:|
| **L1 Commit** | `git commit` | lint + typecheck + unit + security/structure | 🛑 阻断 |
| **L2 Push** | `git push` | integration + coverage + dependency + build | 🛑 阻断 |
| **L3 Merge** | PR merge | L2 + CAPABILITY-MAP 同步 + SECURITY-MAP 同步 | 🛑 阻断 |
| **L4 Publish** | Release | L3 + 全量扫描 + 灰度发布 + 自动升级 tag | 🛑 阻断 |

**Gate 自验收铁律（V11.4 强化）**：
```
MUST: 写完任何 Gate 脚本后必须用真反例跑自验收
验证:
  - tmp 目录造违规样本 → 跑 Gate → 期望 exit ≠ 0
  - PASS 态 / BLOCK 态 / 边界态 三态必跑
固化:
  - 反例样本必须写进 tests/unit/test_*.py
```

详见 [skill-acceptance §7](skill-markets/skill-acceptance/SKILL.md) + [agent-dev-control-kit §11](skill-markets/agent-dev-control-kit/SKILL.md)

#### §0.1.2 Stage 子层（pre-stage / post-stage / pre-accept）

| Stage | 入口 → 出口 | 门禁 | 用户确认 |
|:---:|------|------|:---:|
| -1 | 用户意图 → 状态卡 + 路由决策 | 意图识别 + 路由 | ⚙ |
| 0 | 状态卡 → plan.md | 3 路并行探索 + GitNexus impact | 🛑 |
| 0.5 | plan.md → test-plan.md | 验收维度 → 测试用例映射 | ⚙ |
| 1 | test-plan.md → spec.md | Enhanced Acceptance + clarify ≥2 轮 | 🛑 |
| 1.5 | spec.md → prototype | 双源兼容 | ⚙ |
| 2 | spec.md → contracts/ | contract-gate.py | ⚙ |
| 3 | contracts/ → 代码 + 测试 | TDD GREEN + DRIFT CHECK | 🛑 |
| 3.5 | Implement → verify-report | 5 项必跑 + 启动可见产物 | 🛑 |
| 4 | Real Verify → review-report | 质疑式 4 维验收 + DOC SYNC | ⚙ |
| 4.5 | Review → rot-scan | proactive-scan 10 项 | 🛑 |
| 5 | Rot Scan PASS → archive/done | 归档不可变 + 知识沉淀 | 🛑 |
| 6 | bug 单 → 修复 + CLOSED | e2e 先行 + 6 层排查 | 🛑 |
| 7 | 任一阶段 → project-health | 4 维度 + 优先级分级 | ⚙ |

**Stage Gate 通用 Hook（所有 stage）**:
- Stage 切换前 → 当前 stage 门禁 → 产出门禁报告 → **阻塞**（shell pre-stage.sh）
- Stage 启动 → 加载 stage skill + 解析 depends_on + 检查前置 → **阻塞**
- Stage 结束 → 更新状态卡 + 交接物 4 件套 → 非阻塞（shell post-stage.sh）

---

### §0.2 Guard 层 — TRAE IDE event hook + Shell hook

> 原 §4 Hook 生命周期（V11.4 迁移到本节）

Guard 层负责自动化检查，**不阻断工作流，但记录异常**（除显式标注"阻塞"外）。

#### §0.2.1 TRAE IDE event Hook（5 种 event）

| Event | Hook 脚本 | 检查维度 | 阻断级别 |
|-------|----------|---------|:-------:|
| **SessionStart** | gitnexus-session-check.py + session-start.py | 6 层知识发现 + GitNexus 索引 freshness | ⚙ 提示 |
| **UserPromptSubmit** | complexity-guard.py | 复杂度 + GitNexus First + Article XVII secret | ⚙ 提示 |
| **PreToolUse** | doc-sync-gate.py + contract-gate.py | 写代码前门禁 | ⚙ 提示 |
| **PostToolUse** | spec-validate-hook.py + auto-test.py + drift-detect.py | 写代码后验证 | ⚙ 提示 |
| **Stop** | tasks-integrity.py + gitnexus-session-finalize.py | 任务完整性 + GitNexus 索引刷新 | ⚙ 提示 |

> **V11.4 降级说明**：TRAE IDE event hooks 由于依赖 IDE 对 exit code 的处理，**不承担硬阻断**，仅作辅助提示。真正的硬阻断由 **Git 钩子层**（husky pre-commit/pre-push + GitHub Actions CI）承担，见 §0.1.1。运行任何 stage 前必须先跑 `launch-guard.sh` 自校验，确认 Git 钩子层就绪，否则阻断。

> **GitNexus 双端触发时机（V11.4）**：`gitnexus-session-check.py`（SessionStart）**会话开始必跑一次**；`gitnexus-session-finalize.py`（Stop）**会话结束若工作区脏（agent 改过代码）才跑**，非编辑时实时触发。两端每次执行都写运行痕迹（`.gitnexus/last-run-check.json` / `last-run.json`），stdout 统一为 `[gitnexus]` 前缀 + key=value 格式，可直接 grep 验证；`hooks-fidelity.py` 校验痕迹存在 + 24h 内新鲜，过期/缺失计入 FAIL。

#### §0.2.2 Shell Hook（Stage 切换专用）

| Hook | 触发时机 | 职责 | 阻断级别 |
|------|---------|------|:-------:|
| **pre-stage.sh** | Stage 切换前 | 当前 stage 门禁 + state-card-validator | 🛑 阻断 |
| **post-stage.sh** | Stage 结束后 | 更新状态卡 + 交接物 4 件套 | ⚙ 非阻塞 |
| **pre-accept.sh** | Stage 5 Accept 前 | 归档前检查 + spec-purge + knowledge-extract | 🛑 阻断 |

#### §0.2.3 各 stage 完成 Hook（必阻塞）

| Stage | 完成时 Hook | 阻断级别 |
|:---:|------------|:-------:|
| -1 | 状态卡初始化 + 路由决策表 + Bug 录入判断 | 🛑 |
| 0 | 3 路并行探索 + GitNexus impact + 追问点 | 🛑 |
| 0.5 | 验收维度 → 测试用例映射（覆盖率门槛）| 🛑 |
| 1 | Enhanced Acceptance + INV ≥1 + clarify ≥2 轮 + spec-validate-hook.py | 🛑 |
| 1.5 | 双源兼容校验（设计稿 vs 代码原型）| 🛑 |
| 2 | contract-gate.py 验证四件套 + 测试骨架 | 🛑 |
| 3 | TDD GREEN + DRIFT CHECK + code-hygiene.py + auto-test.py + drift-detect.py | 🛑 |
| 3.5 | 5 项必跑 + 启动可见产物 + visual-content-check.py | 🛑 |
| 4 | 4 维评分 + 证据链 3 层 + DOC SYNC | 🛑 |
| 4.5 | proactive-scan.py 10 项 + self-diagnose.py | 🛑 |
| 5 | 归档前检查 + spec-purge.py + spec-knowledge-extract.py + pre-accept.sh | 🛑 |
| 6 | e2e 先行 FAIL + 6 层排查 + 全量回归 + bug 单 CLOSED | 🛑 |
| 7 | 4 维度检查 + 优先级分级（**非阻塞**，异步）| ⚙ |

#### §0.2.4 hooks-fidelity 硬化要求（V11.4 NEW）

```bash
# 加载协议后必跑（见 §0.5.2）
python ~/.trae-cn/skills/fullstack4TraeV11/scripts/hooks-fidelity.py --project-root .

# hooks-fidelity.py 检查项：
# 1. TRAE IDE event hooks 完整性（5 种 event 必注册）
# 2. Shell hooks 存在性（pre-stage.sh / post-stage.sh / pre-accept.sh）
# 3. Hook 脚本可执行性（权限 + 路径）
# 4. Git 钩子层就绪性（husky pre-commit/pre-push + CI v11-gate.yml）——缺失视为 FAIL（阻断）
```

**Hook 失败反应模式**:
- PASS → 继续
- FAIL → 🛑 阻断 + 5 字段阻塞报告 + 回退路径
- N/A → 标注理由 + 继续

**安装与验证**:
- 安装: `python scripts/install-hooks.py --project-root .`
- 验证: `python scripts/hooks-fidelity.py --project-root .`

---

### §0.3 Execution 层 — 13 stage 流水线

> 原 §0 骨架流程（V11.4 重命名）

> 🛑 以下流水线不可跳过。跳过任一 stage = 技能失效，必须回退重来。
> Bug Fix（Stage 6）与 Project Health（Stage 7）是独立支线，可由任一 stage 触发或并行。

**主链路（必走）**: -1 Intake → 0 Plan → 0.5 Test Plan → 1 Spec → 1.5 Prototype → 2 Contract → 3 Implement → 3.5 Real Verify → 4 Review → 4.5 Rot Scan → 5 Accept

**支线（独立）**: 6 Bug Fix（Intake 触发 / 任一 stage 阻塞触发）/ 7 Project Health（异步自检，可与任一 stage 并行）

**🛑 不可跳过**: -1 / 0 / 1 / 3.5 / 4.5

**回退路径**: [references/stage-interaction-protocol.md §四](references/stage-interaction-protocol.md)

**用户确认分级（V10 传承）**:
- 完整 13 stage（Plan/Spec/Implement 必确认）
- 小任务流线化（≤6 Task + LOW + 无新 API → 无 Contract）
- Bug 快速链（Plan/Review lite-gate）

---

## §1 委派速查

> 完整 stage_config 见 frontmatter。项目级覆盖规则见 [references/dependency-config.md](references/dependency-config.md)。
> **Agent 使用 stage skill 必读**: [references/stage-skill-agent-protocol.md](references/stage-skill-agent-protocol.md)

| Stage | 加载 stage skill | 外部 skill 依赖 | 产出 |
|:---:|------------------|------------------|------|
| -1 ~ 1.5 | `skills/01-intake` ~ `skills/05-prototype` | [gitnexus4Trae] / [ui-ux-pro-max]（按需） | 状态卡 → plan.md → test-plan.md → spec.md → prototypes/ |
| 2 ~ 3 | `skills/06-contract` ~ `skills/07-implement` | [frontend-backend-contract-alignment] / [ponytail4Trae, gitnexus4Trae] | contracts/ 四件套 → 代码 + 测试 + 模块文档 |
| 3.5 ~ 4.5 | `skills/08-real-verify` ~ `skills/10-rot-scan` | [visual-evidence-discipline, screenshot, playwright-best-practices] / [acceptance-discipline] / [goal-mode] | verify-report → review-report → rot-scan |

> **💡 Stage 3.5 / 4.5 异步性声明（V11.8.4 NEW — 蒸馏自 2026-08-15 merged-commits）**:
> - Stage 3.5（visual-evidence / real-verify）和 Stage 4.5（rot-scan）**默认异步、不阻塞 Stage 5 commit**
> - **commit 准入最小集**: `tsc --noEmit` 0 错 + 关键 5 路由 spot-check + admin 探针 200 + lint 预存问题入 BUG
> - 全量视觉证据（60+ 路由）/ 完整 rot-scan / 完整 vitest / build → **commit 后异步执行**
> - **放行依据**：§3.7.3 §8.4 工具-人类分层判定（工具 FAIL 不阻塞 commit，仅作提示）
> - **反例（V11.8.4 §3.7 #10）**：为避免"假完成"反模式而把范围扩大到不可能完成（60 路由全量截图塞 commit 阻塞路径），是反向陷阱，V11 反虚假交付 #5 的镜像
> - 详见 [references/common-anti-patterns.md §7.3](references/common-anti-patterns.md)（commit 准入 ≠ 全量验收）
| 5 ~ 7 | `skills/11-accept` ~ `skills/13-project-health` | [doc-map-manager] / [gitnexus4Trae] | archive/done → bug 单 CLOSED → project-health |

### §1.1 角色（Role）委派列（V11.9 角色协议 NEW）

> 角色体系与 stage **正交**：角色答"谁/职责/权限"，stage 答"何时/流程/产物"（一个角色跨多 stage 履职，一个 stage 多角色协作）。8 角色定义见 [skills/00-boot/agents/README.md](skills/00-boot/agents/README.md)（注册表 + 履职矩阵）+ 各 `<role>.md`。

| 角色 id | 履职 stage | 委派时注入头部 |
|---------|-----------|--------------|
| **jarvis** | 全域 gate（时机①~⑥） | `[JARVIS-DELEGATION]`（含 type: gate-design）|
| **product-manager** | -1 / 1 / 4 / 5 | `[PIPELINE]`（产出 uiux 双文档供下游）|
| **tech-planner** | 0 / 1 / 2 | `[PIPELINE]`（可发起 `[JARVIS-DELEGATION]` gate-design）|
| **backend-implementer** | 3 | `[PIPELINE]` + GitNexus 必跑 |
| **frontend-implementer** | 3 | `[PIPELINE]` + GitNexus 必跑 |
| **prototype-designer** | 1.5 / 3 | `[PROTOTYPE-DELEGATION]` |
| **qa-submitter** | 3.5 / 6 | `[QA-SUBMIT-DELEGATION]` |
| **test-expert** | 0.5 / 3.5 / 4 / 6 | `[TEST-EXPERT-DELEGATION]` |

**委派头部协议引用**: 13 stage × 角色映射见 [references/stage-skill-agent-protocol.md §4](references/stage-skill-agent-protocol.md#4)；子代理通用委派模板见 [references/sub-agent-rules.md §7](references/sub-agent-rules.md)。角色专属委派头部（[PROTOTYPE-DELEGATION] / [QA-SUBMIT-DELEGATION] / [TEST-EXPERT-DELEGATION] / [JARVIS-DELEGATION] gate-design 扩展）见 [references/role-protocol.md §4](references/role-protocol.md)。qa-loop 闭环流程见 [docs/specs/qa-loop.md](docs/specs/qa-loop.md)。

### 委派注入头部（coding-task 强制）

```
[MUST-READ] AGENTS.md + .trae/rules/
[PIPELINE] stage: {N}
[DOC_WHITELIST] {whitelist}
[FORBIDDEN] docs/archive/**, .trae/tmp/**, diagnostic/bugs/**
[GITNEXUS] impact()
[TASK] {≤200 chars}
[OUTPUT] 4 字段: status / evidence / pass_count / next_hook
```

### §1.6 主上下文自律条款（V11.1 NEW — 蒸馏自 V10.11）

当主上下文决定**不委派** coding-task agent 时，**必须**在 Completion Report 中显式声明：

| 字段 | 内容 |
|------|------|
| `delegation_skipped_reason` | "小任务流线化: ≤6 Task + LOW + 无新 API" 或其他合理理由 |
| `skipped_agents` | 列出跳过的 agent 名称（如 `[planner, spec-enhancer, rot-detector]`）|

任一条款触发时必须声明：
- Article IV 委派纪律
- §0 流水线必走阶段
- Phase 4.5 rot-detector 必跑

跳过且不声明 = 🛑 流程违规。

> **💡 §1.6 视觉验证豁免（V11.8.4 NEW — 蒸馏自 2026-08-15 merged-commits）**:
> - **视觉验证类任务（Stage 3.5 visual-evidence / screenshot）默认异步，不入流线化判定**
> - 即使视觉验证需要 60+ 路由，主代理仍可亲自跑（不强制委派），但**必须按 wave 拆分异步推进**
> - 详见 [references/common-anti-patterns.md §7.3](references/common-anti-patterns.md)

---

## §3 状态卡与阶段交互

> **指针化**: 详细协议已迁移到 references。

- **状态卡**: [references/state-card-protocol.md](references/state-card-protocol.md)（3 类卡 / 字段定义 / 更新时机 / 交叉验证 / 模板）
- **阶段交互**: [references/stage-interaction-protocol.md](references/stage-interaction-protocol.md)（标准交接物 4 件套 / 启动前检查 / 异常状态 / 回退路径表 / 产出物层级）

**核心原则**（不外置）:
- 状态卡是任务真相源之一（Article XII 文档诚实）
- 新会话激活先读 `docs/specs/.state-card.md` → 验证文件系统 vs 状态卡 → 30 分钟未产 = 疑似假性完成
- Checkpoint = 每个 stage 门禁 PASS 一次
- 同一 stage 连续回退 3 次 → 升级用户决策

---

## §5 确定性脚本使用时机

> 完整脚本清单 + 用途 + 使用 stage 详见 [scripts/README.md](scripts/README.md)。
> 脚本失败 = 🛑 REJECT，不接受 AI 自评字符串。主上下文亲自调用（不委派给子代理，Article IV）。

**核心规则**:
- 主上下文亲自调用（不委派给子代理）
- 脚本输出必须真实保存（不接受口头宣称 PASS）
- 脚本失败 = 🛑 REJECT → 走 Article XV 阻塞报告
- 脚本 N/A → 必须在状态卡标注理由（不可静默跳过）

---

## §6 上下文卫生

**核心原则**:
- **逐阶段加载**: 每个 stage 开始时加载对应 stage skill，完成后卸载
- **文件即状态**: 关键状态不在对话记忆中，会话中断后通过读取文件恢复
- **文档分层**: fact / process / log 三层标注，子代理禁读 process 层

**详细指针**:
- 阶段产出物文件表 → [references/stage-interaction-protocol.md §五](references/stage-interaction-protocol.md)
- 文档分层规则 → [references/document-layer.md](references/document-layer.md)

---

## §7 Report Growth（L1-L4 异常分级）

> 详细协议：[references/report-growth.md](references/report-growth.md)

| 等级 | 范围 | 示例 | 处理 | 重试上限 |
|:---:|------|------|------|:---:|
| L1 | 文件系统 | 文件缺失、权限不足、路径错误 | Retry 1 次 → 记录 → 继续 | 1 次 |
| L2 | Agent 执行 | 工具调用失败、解析错误、契约不符 | 换参数/策略 → 最多 3 次 → 阻塞报告 | 3 次 |
| L3 | 状态不一致 | state-card 与实际不一致、漂移、契约破坏 | 汇报用户 → 等待决策 | 不可自动 |
| L4 | 外部依赖 | GitNexus 不可用、API 不可达、端口占用 | 降级运行 + 标注风险 → 汇报 | 不可自动 |

**原则**: NEVER SILENT FAIL → RETRY TWICE, STOP → REPORT → STATE CARD SYNC

异常写入 `.trae/logs/report-growth.jsonl`（append-only）。

---

## §8 Bug 录入触发条件

当用户反馈以下情况时，主上下文应询问"是否作为 bug 单录入？"：

**触发词**: "报错"/"错误"/"异常" / "不工作"/"失败"/"崩溃" / "应该出现 X 但出现 Y" / "期望 X 但实际 Y"

**流程**: 触发词识别 → 主上下文询问 → 用户拒绝按"一般咨询"处理 / 用户同意走 Stage -1 Intake bug 录入 6 字段 → 路由到 Stage 6 Bug Fix

**MUST**: 询问是否录入 bug 单（不默认创建）。**NEVER**: 用户拒绝时强制创建。

---

## §9 主上下文汇报纪律

**需用户决策**:
- Plan/Spec/Implement 阶段确认
- 破坏性操作前（rmtree / 不在 git 跟踪的大文件 Delete / 不可逆数据变换）
- 需求模糊 + 1 轮追问仍无法澄清
- 多方案对比无共识
- 用户在 2 轮内表达 ≥ 3 次否定判断
- 阻塞报告（3 次失败升级用户）

**专家自行判断**:
- 委派类型选择（exploration-task vs coding-task）
- 禁止项读取范围
- Completion Report 格式
- DOC_WHITELIST 禁读范围
- 用户确认级别
- 子代理失败处理
- 文档分层判定
- GitNexus vs grep 选择
- 小任务流线化判定

**汇报原则**:
- 状态有变化 → 1 句结论 + 1 句证据
- 状态无变化 → "状态不变，无阻塞"
- 阻塞发生 → 5 字段阻塞报告（3 次失败升级用户）
- 需用户决策 → 列选项 + 推荐方案

**防漂移机制（3 层）**: Layer 1 规则可达性（委派模板强制头部）/ Layer 2 执行保真度（产物验证 + evidence 抽检）/ Layer 3 漂移检测（acceptance-audit + proactive-scan）。

---

## §10 禁止项（核心 9 条）

> 18 条反例详细：[references/common-anti-patterns.md](references/common-anti-patterns.md)
> 16 条铁律详细：[references/common-iron-rules.md](references/common-iron-rules.md)

核心禁止项（任一违反 = 🛑 REJECT）：

- 跳过 Stage 0 Plan 直接写 Spec
- 跳过 Stage 2 Contract 直接 Implement
- 修改 archive/ 下文件
- GitNexus 可用却用 grep
- 用后端/编译类验证充当 UI 任务"完成"
- 盲信子代理的"已完成"声明
- 隐瞒阻塞 / 引用不可证伪理由作为失败归因
- 状态卡说谎 / 文档与代码漂移静默迁就
- 跳过 Stage 4.5 Rot Scan

### §3.7 反虚假交付禁止项（V11.1 NEW — 蒸馏自 V10.10）

> **核心**: 任何"PASS"必附真实证据（command + output + file:line），禁止"看到进程即通过"。

**9 项禁止**：

1. **障碍隐瞒**: 容器未启 / 迁移失败 / 测试 FAIL 不汇报，声称"完成"
2. **跳过测试**: 跳过 `npm run test:all` / `pytest` / `vitest` 声称"完成"
3. **文档验收自我满足**: 文档验收 100% PASS 但未实际跑验证
4. **引用不可证伪理由作为失败归因**: 未定义术语、未指明位置的偏差、未量化裁剪、未测量的心理负担、未定义的概念迁移等。允许的失败归因形式见 [references/agent-error-diagnosis.md](references/agent-error-diagnosis.md) §3 5 模式诊断。
5. **二次再犯不可证伪理由**: 二次被质问仍引用不可证伪理由 → REJECT
6. **AI 描述当成真实像素**: Read PNG 工具返回 AI 描述，编造"截图显示 XXX" → 主上下文必亲自 Read 对比（Article IX）
7. **盲信子代理"已完成"**: 不抽检 evidence / 不跑 pass_count 命令 / 不 Glob 产物（Article IX）
8. **Visual = API PASS**: 用 vitest PASS 充作 UI 任务"完成"（V10.12 教训）
9. **"启动 = 完成"软指标**: 启动进程即声称"完成"，无可见产物（V10 §0.10 启动验证）
10. **范围盲目扩大（反向 #5 陷阱）**（V11.8.4 NEW — 蒸馏自 2026-08-15 merged-commits）: 为避免"假完成"反模式而把范围扩大到不可能完成（60 路由全量截图塞 commit 阻塞路径；5 个 spec 版本反复改仍不收敛）。这是反虚假交付 #5 的镜像陷阱。**commit 准入最小集 ≠ 全量验收**，详见 [references/common-anti-patterns.md §7.3](references/common-anti-patterns.md)

#### V11.2.1 NEW — 蒸馏自 canvas-asset-folders Stage 4 Round 1/2 失败案例引用

> **失败场景**：2026-08-12 Stage 4 Round 1/2 评审员**明知只看了"5 预设可见"未对照 prototype**，仍给 PASS。用户一句话（30 字）"这个UI和 prototypes/index.html 你前面阶段设计的内容不是一个东西啊"暴露 Stage 4 评审重大疏漏。
>
> **教训**：反例 #8 不只在"明知缺陷还往下走"层面失效，在"明知评审疏漏还放 PASS"层面也失效。V11 改进：
> 1. Stage 4 review-report 必含 prototype ↔ implementation 对照表（见 [skills/09-review/SKILL.md Step -1](skills/09-review/SKILL.md)）
> 2. 评审员必亲读 prototype 截图（≥ 2 张）
> 3. 实施截图与 prototype 截图视觉差异 > 20% → REJECT
>
> **关联引用**：[skills/09-review/SKILL.md Step -1](skills/09-review/SKILL.md) | [state-card-protocol.md §5.8](references/state-card-protocol.md)（子代理擅自升级状态协议）

#### §3.7.2 Article V V11.2.1 强化 — 可验证声明硬约束（V11.2.1 NEW — 蒸馏自 canvas-asset-folders）

> **追加位置说明**: 原任务要求在 Article V.5 描述末尾追加，但 SKILL.md 无 Article V.5 显式编号，按 §3.7 语义就近原则追加入 §3.7 末尾（不改 9 项禁止原文）。Article V（可验证声明）的 V11.2.1 强化条款如下：

**4 项硬约束（任一违反 = 🛑 REJECT）**：

1. **Review 必读 prototype 截图**: Stage 4 review-report 必含 prototype ↔ implementation 对照表（reference: [skills/09-review/SKILL.md Step -1](skills/09-review/SKILL.md)），评审员必亲读 ≥ 2 张 prototype 截图，未读 = 评审疏漏
2. **实施 vs prototype 视觉差异 > 20% → REJECT**: 实施截图与 prototype 截图逐像素对比，差异 > 20% 即拒收（不进入下一 stage）
3. **PASS 必附三层证据**: command + output + file:line 三件套缺一不可；review-report 任一字段缺失 = 自动 FAIL
4. **评审疏漏二次再犯 → 升级用户**: 同一 stage 连续 2 轮评审疏漏（明知未对照 prototype 仍给 PASS）→ 立即停止自评，5 字段阻塞报告 + 升级用户决策

**关联铁律**：Article V（可验证声明） + Article IX（质疑式验收） + Article XVI（质疑式校验）。

#### §3.7.3 灵活度铁律 8 — V11.3 NEW — 人工判定覆盖（2026-08-12 canvas-asset-folders 蒸馏）

> **设计哲学**: prototype 是"参考起点 + 单一真相源",但**承认合理灵活度**。
> **核心**: 5% 视觉差异阈值（V11.2 的 20% → V11.3 的 5%）+ fidelity 等级 + 偏离理由 + 工具-人类分层判定。

##### 8.1 prototype fidelity 等级（必在 design-prompt.md 顶部标注）

- **L1 wireframe（线框）**: 仅布局骨架 + 组件清单 + 5 状态,**不约束**颜色/间距/字号/动画
  - 实施只要保留"布局 + 组件 + 5 状态"= PASS,视觉差异 ≤ 50% 可接受
  - 适用场景:早期探索、需求验证、低保真原型
- **L2 mockup（中保真）**: L1 + 主色板 + 字号层级 + 间距规则
  - 实施差异 ≤ 30% 可接受
  - 适用场景:中后期实施、UI 细节对齐
- **L3 pixel-perfect（高保真）**: L2 + 动效曲线 + 阴影 + 圆角 + hover 状态
  - 实施差异 ≤ 5% 才 PASS
  - 适用场景:精确还原、营销页、关键 UX 节点

**默认值**:design-prompt.md 无 fidelity 标注 → 视为 **L2 mockup**（默认中保真）

##### 8.2 prototype 演进（V11.3 NEW）

- Stage 3 实施期间如发现 prototype 设计不合理,**允许**调整 prototype + design-prompt + ui-ux-logic
- 调整必走:
  1. 主上下文决策（不能 agent 单方面调整）
  2. 同步 3 份文档（保持单一真相源,见 V11 §11）
  3. 在 review-report.md §prototype ↔ implementation 对照表 "偏离理由" 列填"prototype 演进 V11.3 §8.2"
- **NEVER**: 暗改 prototype 而不更新文档

##### 8.3 偏离理由（正当理由清单）

实施可偏离 prototype,但**必在** review-report.md §prototype ↔ implementation 对照表 "偏离理由" 列填**正当理由**之一:

- **性能优化** — 实施用更高效算法,功能等价
- **可访问性** — 实施用 ARIA 增强,功能等价
- **国际化** — 实施 i18n 拆分,文案按 locale 切换
- **用户偏好** — 用户已确认偏离（如本期 prototype 设计 8 项,但用户要求聚焦 6 项）
- **prototype 演进** — 见 §8.2,实施期间调整了 prototype
- **fidelity 等级允许的差异** — 见 §8.1,L1/L2 容许范围内差异
- **第三方库限制** — 实施用第三方库有特定约束（如 Tailwind 不支持某 CSS）

主上下文在 review-report 末段"§偏离裁定"列每条偏离的批准理由。

**NEVER 空洞偏离理由**（无证据的偏离裁定反例）:
- ❌ "差不多"
- ❌ "看起来对"
- ❌ "感觉 OK"
- ❌ "应该没问题"
- ❌ "差不多就行"

**反例来源**:2026-08-12 canvas-asset-folders Stage 4 Round 1/2 评审员写"5 预设可见 + API PASS"给 PASS,缺 prototype 1:1 对照 + 缺偏离理由

##### 8.4 工具-人类分层判定（V11.3 NEW — 人工判定覆盖）

> 2026-08-12 用户决策记录:工具反馈通过 → 主上下文直接标记通过；工具反馈未通过 → 由 agent 决定放行时必须附偏离理由（见 §8.3 正当理由清单）。无证据放行视为流程违规。

```
工具检测 PASS → 主上下文直接标记通过
工具检测 FAIL → 不阻塞,仅作"提示"交给 agent 决策
agent PASS  → 必写偏离理由（§8.3 正当理由清单之一）
agent FAIL  → 必写 FAIL 原因（spec 违反 / prototype GAP / 实施错误）
```

**反例**:agent 工具检测 FAIL 时,无偏离理由即声称"通过" → 按反例 §4 不可证伪理由处理（V11 通用铁律）

**关联铁律**:Article V（可验证声明） + Article IX（质疑式验收） + Article XVI（质疑式校验）。

**修正路径**: 必走 [references/sub-agent-rules.md §8 三层验证](references/sub-agent-rules.md) + [references/agent-error-diagnosis.md](references/agent-error-diagnosis.md) 5 模式诊断 + [Stage 3.5 Real Verify](skills/08-real-verify/SKILL.md) 5 类项目启动验证。
- 主上下文直接 Edit/Write 代码（Article IV 委派纪律）

---

## §11 AskUserQuestion 反模式

> 详见 [references/ask-question-anti-patterns.md](references/ask-question-anti-patterns.md)。

**核心 2 类**:
- 反模式 1 — 用户没选选项 = 可能在质疑流程本身 → 承认错误 + 根因分析
- 反模式 2 — 用户累计 ≥ 3 次小修请求仍在修补细节 → 反向提示词生成（NEVER + 反例）

**多轮道歉信号**: 主上下文道歉 ≥ 2 次 + 无可观测改进 + 用户在 2 轮内表达 ≥ 3 次否定判断 → 立即停止道歉，列 ✅ 已做 + 📍 证据。

---

## §12 目录结构

```
fullstack4TraeV11/
├── SKILL.md                # 总编排器（本文件）
├── references/             # 9 个公共 references（见 §13）
├── templates/              # 项目级 AGENTS.md / rules / state-card 模板
├── scripts/                # 14 个公共 scripts
└── skills/                 # 13 个 stage skill（01-intake ~ 13-project-health）
```

每个 stage skill 自包含：

```
skills/{NN}-{name}/
├── SKILL.md              # 阶段入口（铁律 + 边界 + 委派触发词 + depends_on）
├── README.md             # 阶段元信息
├── scripts/              # 该阶段的确定性脚本
├── workflows/            # 阶段内工作流（每流程独立 md）
├── templates/            # 该阶段的产物模板
├── references/           # 该阶段的方法论/细节
└── anti-patterns/        # 该阶段的反例库
```

---

## §13 参考索引

- **references/**: constitution / common-iron-rules / common-anti-patterns / **skeptical-validation-protocol**（7 stage 永久激活）/ stage-interaction-protocol / state-card-protocol / dependency-config / document-layer / report-growth / ask-question-anti-patterns / agent-error-diagnosis / sub-agent-rules / project-structure / gitnexus-tools / gitnexus-retry-protocol / stage-physical-isolation（V11.8.2 起 bug-hunt 实战段迁入 [skills/12-bug-fix/references/bug-hunt-battle-report.md](skills/12-bug-fix/references/bug-hunt-battle-report.md) 同包内，详见 [skills/12-bug-fix/SKILL.md](skills/12-bug-fix/SKILL.md)）
- **glossary.md** — 术语表(V10 完整继承 + V11 新增 5 大类 100+ 术语)
- **templates/**: project-agents-example / project-rules-example / state-card / hooks/ / constitution-template

---

## §14 项目级生态管理规范(V11.2 NEW -- 蒸馏自 init-from-zero.py Step 5 改造)

> 任何 stage skill 涉及项目级配置改动(.trae/rules/ / .trae/skills/project_rules_skills/ / .trae/hooks/ / AGENTS.md 等),必走本规范。

### §14.1 5 项铁律

```
1. 单点入口原则      所有项目级规则通过 .trae/skills/project_rules_skills/SKILL.md 路由,
                    按需加载 references/,禁止 agent 直接 Read .trae/rules/{name}.md

2. 物理移走原则      init-from-zero.py --rules-as-skill 必须 move(物理删除源文件)而非 copy,
                    .trae/rules/ 物理状态 = 仅 README.md

3. README 幂等原则  项目拥有 .trae/rules/README.md,init 不强制覆盖,
                    只在缺"project-rules skill 入口"声明时追加入口段

4. 占位模板兜底      项目无 rules 时,从 V11 templates/project-rules-example/ 复制占位,
                    但 README 由项目自己创建,init 不复制

5. 整合协议必走      agent 创建 project-rules skill 后,必走 5 步整合:
                    Read all → 检查 V11 内部重叠 → 完全重叠删除 / 部分重叠保留独有部分 → 纯机械挪移 = 无意义
```

### §14.2 后续 stage 引用本规范的触发词

| 触发词 | 必引用本规范 |
|--------|------------|
| 改 .trae/rules/ 任何文件 | §14.1 铁律 1-5 |
| 改 init-from-zero.py Step 5 相关逻辑 | §14.1 铁律 2-4 |
| 改 .trae/skills/project_rules_skills/ 内容 | §14.1 铁律 1 + 5 |
| 新建项目级配置文件(如 .trae/hooks/ 新 hook) | §14.1 铁律 1 + README 幂等 |
| sub-agent 提到"项目惯例" | §14.1 铁律 5(先整合再决策) |

### §14.3 反例(违反任一即 REJECT)

| 反例 | 后果 |
|------|------|
| 复制 rule 到 references/ 而不删源文件 | 双份真相, agent 读错版本 |
| 强制覆盖 .trae/rules/README.md | 项目自定义内容被破坏 |
| 无 rules 时跳过 --rules-as-skill | SKILL.md §0.5 Step 3 协议等不到触发条件 |
| 纯机械挪移 rule 不做内容整合 | V11 已含内容重复占用 context |
| agent 直接 Read .trae/rules/*.md 而不走 skill 入口 | context 撑爆(违反 §0.5 Step 3) |

### §14.4 关联引用

- §0.5 Step 3 -- 项目级 rules 强制加载入口(Skill(name="project-rules"))
- §0.5.2 加载后验证 -- LS .trae/skills/project_rules_skills/SKILL.md 存在性
- scripts/init-from-zero.py -- Step 5 (V11.2 MOVE 模式 + README 幂等 + 占位兜底)
- templates/project-rules-skill-template/ -- project-rules skill 入口模板
- templates/project-rules-example/ -- 占位 rule 模板(4 个文件 + README)

### §14.5 项目级 rules > V11 通用层优先级（V11.2 NEW — 蒸馏自 canvas-asset-folders）

> **本节为任务委托方所指的"§14.2 项目级 vs V11 通用层优先级"**，因 §14.2/§14.3/§14.4 已被既有项目级生态管理规范占用，按 V11 §11 单源原则以 §14.5 编号追加，避免重复定义。

```
当 V11 通用层（~/.trae-cn/skills/fullstack4TraeV11/）与项目级 rules（.trae/skills/project_rules_skills/）冲突时：

MUST: 项目级 rules 优先于 V11 通用层
MUST: 项目级 .trae/skills/project_rules_skills/references/anti-patterns.md 可补 V11 通用层缺失的反例
MUST: 项目级 .trae/skills/project_rules_skills/rules/governance.md 可强制 V11 通用层未硬化的门槛（如视觉证据）
NEVER: 盲信 V11 通用层, 缺项目级叠加（违反 Article XVI §1.4 重叠校验的反向）
```

**适用场景（V11 通用层缺位时的项目级补全范式）**：

- V11 通用层缺反例 → 项目级 anti-patterns.md 补全
- V11 通用层误判 → 项目级 rules 纠正
- V11 通用层缺硬门槛 → 项目级 governance 强制
- 真实失败案例（V11 实战蒸馏）→ 项目级 references/ 沉淀

**反例来源**：2026-08-12-canvas-asset-folders 会话（V11 §3.5 缺真实浏览器端到端 UI 截图硬门槛，项目级 visual-evidence-gate 补全）。

**本节即任务委托方所提"V11 §14.2 项目级 vs V11 通用层优先级"小节的源头**。

#### §14.5.1 与 §14.1-§14.4 的关系

| 维度 | §14.1-§14.4 项目级生态管理 | §14.5 优先级（V11.2 NEW）|
|------|--------------------------|------------------------|
| 关注点 | init-from-zero + project-rules-skill 创建协议 | V11 通用层 vs 项目级 rules 的冲突优先级 |
| 时机 | init 阶段 + 项目级改动前 | 任意阶段,遇到规则冲突时 |
| 反向约束 | 不创造 rules(物理移走) | 不盲信 V11 通用层(项目级叠加) |

#### §14.5.2 引用触发词

| 触发词 | 必引用 §14.5 |
|--------|-------------|
| 跨层规则冲突（V11 通用层 vs 项目级） | §14.5 优先级铁律 |
| 项目级新增反例（V11 通用层未覆盖） | §14.5 "适用场景" 第 1 项 |
| 项目级 governance 强制门槛 | §14.5 "适用场景" 第 3 项 |
| AI 自述 "V11 没规定" | §14.5 NEVER 反向铁律 |
