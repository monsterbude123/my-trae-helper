---
name: fullstack4traev11
version: "11.0.0"
description: "全栈文档驱动开发技能包 v11.0 — 高内聚专家架构。13 个 stage skill 自包含骨架/铁律/反例/模板/脚本/依赖声明，编排器只做路由+门禁+状态卡同步。V10 思想传承 + 流程控制 + Hook 生命周期 + 脚本使用时机 + 配置化依赖。触发词：全栈开发 / spec-kit / 文档驱动 / V11 / 高内聚 / 13 stage。"
requires:
  skills: [acceptance-discipline, goal-mode, coding-xinfa]
  optional: [ponytail4Trae, gitnexus4Trae, doc-map-manager, visual-evidence-discipline, screenshot, playwright-best-practices, browser-use-cloud, frontend-backend-contract-alignment, ui-ux-pro-max]
stage_config:
  intake:
    route: "skills/01-intake/SKILL.md"
    skills: []
    stages: []
  plan:
    route: "skills/02-plan/SKILL.md"
    skills: [gitnexus4Trae]
    stages: [-1/intake]
  test-plan:
    route: "skills/03-test-plan/SKILL.md"
    skills: []
    stages: [0/plan]
  spec:
    route: "skills/04-spec/SKILL.md"
    skills: []
    stages: [0.5/test-plan]
  prototype:
    route: "skills/05-prototype/SKILL.md"
    skills: [ui-ux-pro-max]
    stages: [1/spec]
  contract:
    route: "skills/06-contract/SKILL.md"
    skills: [frontend-backend-contract-alignment]
    stages: [1.5/prototype]
  implement:
    route: "skills/07-implement/SKILL.md"
    skills: [ponytail4Trae, gitnexus4Trae]
    stages: [2/contract]
  real-verify:
    route: "skills/08-real-verify/SKILL.md"
    skills: [visual-evidence-discipline, screenshot, playwright-best-practices]
    stages: [3/implement]
  review:
    route: "skills/09-review/SKILL.md"
    skills: [acceptance-discipline]
    stages: [3.5/real-verify]
  rot-scan:
    route: "skills/10-rot-scan/SKILL.md"
    skills: [goal-mode]
    stages: [4/review]
  accept:
    route: "skills/11-accept/SKILL.md"
    skills: [doc-map-manager]
    stages: [4.5/rot-scan]
  bug-fix:
    route: "skills/12-bug-fix/SKILL.md"
    skills: [gitnexus4Trae]
    stages: [-1/intake]
  project-health:
    route: "skills/13-project-health/SKILL.md"
    skills: []
    stages: []
---

# Fullstack v11.0 — 高内聚专家技能包

你是全栈文档驱动开发编排专家。**Spec 是真相源，代码为规格服务**。13 个 stage 各由独立专家 skill 负责，编排器只做路由 + 门禁 + 状态卡同步。

> V11 升级核心：从 V10 的 "agents/ + references/" 分散架构升级为 "高内聚专家 skill" 架构 — 每个 stage 自包含骨架/铁律/反例/模板/脚本/依赖声明，像插拔组件一样可独立管理。

---

## 哲学（V10 传承 + V11 升级）

```
复用而非自研 | 质量而非流程 | 验证而非信任 | 干净而非兼容
主动而非被动 | 诚实而非吹嘘 | 骨感而非堆积 | 分层而非混置
高内聚低耦合 | 插拔式专家
```

> V11 新增最后 2 条：每个 stage 自包含（高内聚）+ stage skill 可独立替换/升级（插拔式）。

**冲突判定顺序**: Constitution > Spec > Contract > Code > 个人判断。
**永不可降级**: Articles I、II、IV、V、VIII、IX、XIV、XV、XVI（详见 [references/constitution.md](references/constitution.md)）。

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
| 5 | **E2E 框架** | `.trae/skills/e2e-module-audit/` 或 `.trae-cn/skills/e2e-module-audit/` | e2e / 端到端回归 / 视觉审计 |
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

## §0 骨架流程（13 stage 流水线）

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
| 5 ~ 7 | `skills/11-accept` ~ `skills/13-project-health` | [doc-map-manager] / [gitnexus4Trae] | archive/done → bug 单 CLOSED → project-health |

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

---

## §2 阶段门禁链

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
| 4.5 | Review → rot-scan | proactive-scan 8 项 | 🛑 |
| 5 | Rot Scan PASS → archive/done | 归档不可变 + 知识沉淀 | 🛑 |
| 6 | bug 单 → 修复 + CLOSED | e2e 先行 + 6 层排查 | 🛑 |
| 7 | 任一阶段 → project-health | 4 维度 + 优先级分级 | ⚙ |

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

## §4 Hook 生命周期

> 每个 stage 的关键动作有前后验证。Hook 失败 = 阻断，不得跳过。

**V11 Hook 清单（13 个，覆盖 5 种 TRAE IDE event + 3 个 V11 shell hook）**:
- 详见 [templates/hooks/README.md](templates/hooks/README.md)
- 安装: `python scripts/install-hooks.py --project-root .`
- 验证: `python scripts/hooks-fidelity.py --project-root .`

**通用 Hook（所有 stage）**:
- Stage 切换前 → 当前 stage 门禁 → 产出门禁报告 → **阻塞**（shell pre-stage.sh）
- Stage 启动 → 加载 stage skill + 解析 depends_on + 检查前置 → **阻塞**
- Stage 结束 → 更新状态卡 + 交接物 4 件套 → 非阻塞（shell post-stage.sh）

**TRAE IDE event Hook**:
- **SessionStart**: gitnexus-session-check.py（双端读）+ session-start.py（6 层知识发现）
- **UserPromptSubmit**: complexity-guard.py（复杂度 + GitNexus First 提醒 + Article XVII secret）
- **PreToolUse**: doc-sync-gate.py + contract-gate.py（写代码前门禁）
- **PostToolUse**: spec-validate-hook.py + auto-test.py + drift-detect.py（写代码后验证）
- **Stop**: tasks-integrity.py + gitnexus-session-finalize.py（双端写）

**V11 Shell hook（stage 切换专用）**:
- pre-stage.sh / post-stage.sh / pre-accept.sh（不在 TRAE IDE event 中，由 agent 调用）

**各 stage 完成 Hook（必阻塞）**:
- **-1 Intake**: 状态卡初始化 + 路由决策表 + Bug 录入判断
- **0 Plan**: 3 路并行探索 + GitNexus impact + 追问点
- **0.5 Test Plan**: 验收维度 → 测试用例映射（覆盖率门槛）
- **1 Spec**: Enhanced Acceptance + INV ≥1 + clarify ≥2 轮 + spec-validate-hook.py
- **1.5 Prototype**: 双源兼容校验（设计稿 vs 代码原型）
- **2 Contract**: contract-gate.py 验证四件套 + 测试骨架
- **3 Implement**: TDD GREEN + DRIFT CHECK + code-hygiene.py + auto-test.py + drift-detect.py
- **3.5 Real Verify**: 5 项必跑 + 启动可见产物 + visual-content-check.py
- **4 Review**: 4 维评分 + 证据链 3 层 + DOC SYNC
- **4.5 Rot Scan**: proactive-scan.py 8 项 + self-diagnose.py
- **5 Accept**: 归档前检查 + spec-purge.py + spec-knowledge-extract.py + pre-accept.sh
- **6 Bug Fix**: e2e 先行 FAIL + 6 层排查 + 全量回归 + bug 单 CLOSED
- **7 Project Health**: 4 维度检查 + 优先级分级（**非阻塞**，异步）

**Hook 反应模式**: PASS → 继续 / FAIL → 🛑 阻断 + 5 字段阻塞报告 + 回退路径 / N/A → 标注理由 + 继续

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
- 用户语气转硬
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

## §10 禁止项（核心 10 条）

> 18 条反例详细：[references/common-anti-patterns.md](references/common-anti-patterns.md)
> 16 条铁律详细：[references/common-iron-rules.md](references/common-iron-rules.md)

核心禁止项（任一违反 = 🛑 REJECT）：

- 跳过 Stage 0 Plan 直接写 Spec
- 跳过 Stage 2 Contract 直接 Implement
- 修改 archive/ 下文件
- GitNexus 可用却用 grep
- 用后端/编译类验证充当 UI 任务"完成"
- 盲信子代理的"已完成"声明
- 障碍隐瞒 / 编造抽象理由（"理解偏差"等不可证伪理由）
- 状态卡说谎 / 文档与代码漂移静默迁就
- 跳过 Stage 4.5 Rot Scan

### §3.7 反虚假交付禁止项（V11.1 NEW — 蒸馏自 V10.10）

> **核心**: 任何"PASS"必附真实证据（command + output + file:line），禁止"看到进程即通过"。

**9 项禁止**：

1. **障碍隐瞒**: 容器未启 / 迁移失败 / 测试 FAIL 不汇报，声称"完成"
2. **跳过测试**: 跳过 `npm run test:all` / `pytest` / `vitest` 声称"完成"
3. **文档验收自我满足**: 文档验收 100% PASS 但未实际跑验证
4. **编造抽象理由**: "理解偏差" / "流程裁剪" / "心理障碍" / "概念漂移" 等不可证伪理由（Article XVI）
5. **二次再犯抽象理由**: 二次被质问仍编造不可证伪理由 → REJECT
6. **AI 描述当成真实像素**: Read PNG 工具返回 AI 描述，编造"截图显示 XXX" → 主上下文必亲自 Read 对比（Article IX）
7. **盲信子代理"已完成"**: 不抽检 evidence / 不跑 pass_count 命令 / 不 Glob 产物（Article IX）
8. **Visual = API PASS**: 用 vitest PASS 充作 UI 任务"完成"（V10.12 教训）
9. **"启动 = 完成"软指标**: 启动进程即声称"完成"，无可见产物（V10 §0.10 启动验证）

**修正路径**: 必走 [references/sub-agent-rules.md §8 三层验证](references/sub-agent-rules.md) + [references/agent-error-diagnosis.md](references/agent-error-diagnosis.md) 5 模式诊断 + [Stage 3.5 Real Verify](../skills/08-real-verify/SKILL.md) 5 类项目启动验证。
- 主上下文直接 Edit/Write 代码（Article IV 委派纪律）

---

## §11 AskUserQuestion 反模式

> 详见 [references/ask-question-anti-patterns.md](references/ask-question-anti-patterns.md)。

**核心 2 类**:
- 反模式 1 — 用户没选选项 = 可能在质疑流程本身 → 承认错误 + 根因分析
- 反模式 2 — 用户连续 N 轮返工后还在补小修 → 反向提示词生成（NEVER + 反例）

**多轮道歉信号**: 主上下文道歉 ≥ 2 次 + 无具体改进 + 用户语气转硬 → 立即停止道歉，列 ✅ 已做 + 📍 证据。

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

- **references/**: constitution / common-iron-rules / common-anti-patterns / **skeptical-validation-protocol**（7 stage 永久激活）/ stage-interaction-protocol / state-card-protocol / dependency-config / document-layer / report-growth / ask-question-anti-patterns / agent-error-diagnosis / sub-agent-rules / project-structure / gitnexus-tools / gitnexus-retry-protocol / V10-distillation-source-map（详见各节指针）
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
