---
title: V7 → V11 进化时间线 + 轴心思想继承清单
description: 全栈文档驱动技能从 V7 到 V11 的完整进化轨迹，记录每个版本的增量、丢失项与轴心思想。本文档是 V12+ 升级时的**前置必读**，升级前必查本文件并维护。
layer: fact
maintenance: mandatory
maintenance_trigger:
  - "新增 V11.x.x 版本"
  - "新增 Article / 反例 / 铁律"
  - "修复铁律丢失项"
  - "删除/重构 references/ 或 skills/"
  - "任何 fullstack-skill-architect 触发的升级会话"
---

# V7 → V11 进化时间线 + 轴心思想继承清单

> **📌 文档定位**：本文件是 V11 阶段的"进化记忆"与"轴心思想仓库"。它记录三件事：
>
> 1. **每一代的关键增量** —— 不为升级而升级，确认每个变更的可追溯收益。
> 2. **每一代的可观察丢失** —— 避免反复重造轮子或丢失核心能力。
> 3. **跨代保留的轴心思想** —— 即使 SKILL.md 改版也不能改的核心命题。
>
> **🔧 维护强制**：见顶部 frontmatter `maintenance_trigger`。任何升级触发条件命中时，**必须**：
>
> - 更新本文件的"轴心思想清单"（新思想加入 / 旧思想若被覆盖则归档到「已弃用」段）
> - 在本文件"时间线"段追加新版本的 delta
> - 在 PR / commit message 中引用本文件（`Refs: references/v7-to-v11-evolution.md`）

---

## §A 轴心思想（跨代继承，V12+ 不可覆盖）

这些命题是 fullstack4Trae 系列的**核心承诺**。即使代码重构、Agent 替换、流水线升级，**这些思想必须保留**。任何覆盖提议需走 Article XVI 质疑性校验（[references/common-iron-rules.md](common-iron-rules.md)）。

| # | 轴心思想 | 首次提出 | 当前落地位置 |
|---|---------|---------|-------------|
| 1 | **规格优先于实现**（无 approved spec 不写代码） | V8 | Article II (constitution.md) + Stage 1 Spec |
| 2 | **契约不可单方面修改**（破坏性变更走 BREAKING 流程） | V8 | Article III + Stage 2 Contract |
| 3 | **TDD 唯一路径**（RED → GREEN → REFACTOR + DRIFT CHECK） | V8 | Article IV + Stage 3 Implement |
| 4 | **可验证声明**（command + output + file:line 三件套） | V8 | Article V + Completion Report 4 字段 |
| 5 | **归档不可变**（archive/ 只读） | V8 | Article VIII + Stage 5 Accept |
| 6 | **异会话验证**（主上下文必二次抽检子代理自评） | V10.4 | Article IX + §-1.5 机械验证协议 |
| 7 | **视觉真实验证**（PIL 解码 + 直方图 + 关键区域采样） | V10.4 | Article XI + Stage 3.5 Real Verify |
| 8 | **文档诚实**（state-card / INDEX 声称的 INV 必在 spec.md 落地） | V10.5 | Article XII + state-card-protocol.md |
| 9 | **骨架是债**（🟡 骨架 ≥14 天未推进必冻结或归档） | V10.5 | Article XIII |
| 10 | **腐化可检测**（rot-detector 必跑，proactive-scan 10 项） | V10.4-10 | Article XIV + Stage 4.5 Rot Scan |
| 11 | **障碍诚实汇报**（5 字段阻塞报告） | V10.10 | Article XV + phase-gate --verify-rot-scan |
| 12 | **禁止编造抽象理由**（理解偏差 / 流程裁剪 / 心理障碍等不可证伪理由） | V10.10 | Article XVI + reason-classifier.py |
| 13 | **质疑性校验必走**（根因 / 责任主体 / 重叠 / 修复成本 4 维度） | V10.12 | skeptical-validation-protocol.md |
| 14 | **可见产物是唯一信任基础**（启动 = 完成 的软指标必须升级为 5 类硬定义） | V10.10 | Stage 3.5 §0.10 |
| 15 | **同类约定清单化**（不依赖 agent 主观理解"同类"） | V10.12 | §0.5.1 10 项强制清单 |
| 16 | **失忆机制设计**（文档分层 fact/process/log，子代理禁读 process 层） | V10.11 | document-layer.md |
| 17 | **物理隔离优先于逻辑区分**（_invalidated/ 屏蔽区） | V9.1 → V11 stage-physical-isolation.md | stage-physical-isolation.md |
| 18 | **Completion Report 必附证据**（无报告 = 🛑 退回） | V9.1 | §4 Completion Report 协议 |

> **维护提示**：未来若新增 Article（如 XVIII），请在本表追加行，并在 frontmatter 同步。

---

## §V0 v0 思想档（无法追溯到具体版本的基础命题）

> **📦 归档定位**：本段记录 fullstack4Trae 系列在 V8 之前就存在的"基础思想"——它们无法精确归属到 V7 / V8 某个 changelog（仓库无可溯源记录），但构成了 V8+ 所有轴心思想的**底层命题**。
>
> 任何 V12+ 升级若与本段命题冲突，必须：
>
> 1. 在 PR 中明确标注「v0 思想覆盖」并附论证
> 2. 走 Article XVI 质疑性校验 4 维度（[references/skeptical-validation-protocol.md](skeptical-validation-protocol.md)）
> 3. 不通过则不能合并

| # | v0 思想 | 哲学源头（不可溯源仅注记） | 当前落地位置（V11 引用） |
|---|--------|-----------------------|-----------------|
| V0-1 | **规格与代码分离**（spec 是真相源，code 服务 spec） | 软件工程经典（Brooks《人月神话》/ Parnas 模块化） | [constitution.md Article II](constitution.md) + [glossary.md §Spec](glossary.md) + [../skills/04-spec/SKILL.md](../skills/04-spec/SKILL.md) |
| V0-2 | **TDD 三步循环**（RED → GREEN → REFACTOR） | Kent Beck 1999《Test-Driven Development》 | [constitution.md Article IV](constitution.md) + [../skills/07-implement/SKILL.md](../skills/07-implement/SKILL.md) |
| V0-3 | **OpenSpec WHEN-THEN-AND + SHALL 语义** | RFC 2119 / IETF 关键字约定（1997） | [glossary.md §OpenSpec](glossary.md) + [../skills/04-spec/SKILL.md](../skills/04-spec/SKILL.md) + [../skills/04-spec/templates/spec-template.md](../skills/04-spec/templates/spec-template.md) |
| V0-4 | **Delta Spec 思想**（ADDED / MODIFIED / REMOVED） | 数据库 schema migration / Git diff / Linux kernel changelog | [../skills/04-spec/SKILL.md](../skills/04-spec/SKILL.md) + [../skills/04-spec/templates/spec-template.md](../skills/04-spec/templates/spec-template.md) |
| V0-5 | **单一真相源**（Single Source of Truth, SSoT） | 软件工程经典（DRY 原则 / Parnas） | [../../CAPABILITY-MAP.md](../../CAPABILITY-MAP.md) + [../../../SECURITY-MAP.md](../../../SECURITY-MAP.md) + [../skills/01-intake/SKILL.md §state-card](../skills/01-intake/SKILL.md) |
| V0-6 | **事实/过程/日志 三层分离** | 12-Factor App 日志原则 + 学术信息系统分层 | [references/document-layer.md](document-layer.md) + [references/sub-agent-rules.md §1](sub-agent-rules.md) |
| V0-7 | **质疑性 / 证伪优先**（Skeptical Validation） | 卡尔·波普尔《猜想与反驳》/ 科学哲学 | [references/skeptical-validation-protocol.md](skeptical-validation-protocol.md) + [constitution.md Article XVI](constitution.md) |
| V0-8 | **Completion Report 必附证据** | 工程交付规范（PR 描述 / change log） | [sub-agent-rules.md §4](sub-agent-rules.md) + [../SKILL.md §4](../SKILL.md) |
| V0-9 | **报告分级（L1~L4）按受众分层** | ITIL 事件分级 / RFC 文档分级 | [report-growth.md](report-growth.md) + [../SKILL.md §7](../SKILL.md) |
| V0-10 | **子代理委派头部固定字段**（[MUST-READ] [PIPELINE] 等 6 字段） | Function Calling / gRPC metadata 注入模式 | [sub-agent-rules.md §5](sub-agent-rules.md) + [../SKILL.md §1.5](../SKILL.md) |
| V0-11 | **路径权限分离**（读/写/删 三类权限矩阵） | Unix 文件权限模型 / Docker rootless | [project-iron-laws.md §C](project-iron-laws.md) |
| V0-12 | **破坏性操作必走 trash 兜底** | Apple Trash / Windows Recycle Bin 设计 | [project-iron-laws.md §C](project-iron-laws.md) + [skill-market-control-design.md](skill-market-control-design.md) |
| V0-13 | **path.resolve 误删源**（symlink 跟随） | Linux symlink 语义（canonical vs logical path） | [project-iron-laws.md §A R-2](project-iron-laws.md) |
| V0-14 | **change-id = {YYYY-MM-DD}-{kebab-name}** | ISO 8601 日期格式 + kebab-case 命名约定 | [project-iron-laws.md §D](project-iron-laws.md) + [state-card-protocol.md](state-card-protocol.md) |
| V0-15 | **物理隔离优先于逻辑区分**（Docker 镜像层思路） | Docker overlay filesystem / git worktree | [stage-physical-isolation.md](stage-physical-isolation.md) + [../skills/12-bug-fix/SKILL.md](../skills/12-bug-fix/SKILL.md) |
| V0-16 | **hooks-fidelity 自检**（写入与执行一致性） | GitHub Actions workflow 检查 / Terraform plan | [../scripts/hooks-fidelity.py](../scripts/hooks-fidelity.py) + [../SKILL.md §0.5.2](../SKILL.md) |
| V0-17 | **Acceptance Gates 4 维评分**（代码/API/UIUX/边界） | CMMI 评估方法 / OWASP 测试维度 | [constitution.md Article V](constitution.md) + [../skills/09-review/SKILL.md](../skills/09-review/SKILL.md) |
| V0-18 | **Bug 录入触发条件**（触发词识别 + 询问用户是否录入） | Jira / GitHub Issues 工作流 | [../SKILL.md §8](../SKILL.md) + [../skills/12-bug-fix/SKILL.md](../skills/12-bug-fix/SKILL.md) |
| V0-19 | **同类约定清单化**（不依赖主观理解"同类"） | OWASP Top 10 列表化 / POSIX 命名约定 | [../SKILL.md §0.5.1](../SKILL.md) + [../skills/01-intake/anti-patterns/](../skills/01-intake/anti-patterns/) |
| V0-20 | **证据三层验证**（command + output + file:line） | 法律证据链 / 科学实验可复现性 | [skeptical-validation-protocol.md](skeptical-validation-protocol.md) + [sub-agent-rules.md §2](sub-agent-rules.md) |

### v0 思想 vs 轴心思想（§A）的区别

| 维度 | §A 轴心思想 | §V0 v0 思想 |
|------|------------|------------|
| **溯源** | V8+ 某 changelog 可追溯 | 哲学源头经典 / 行业标准 / 通用工程实践 |
| **变更门槛** | V12+ 必须保留，冲突需 Article XVI 校验 | V12+ 须明确论证，覆盖需 Article XVI 校验 |
| **覆盖方式** | 重写文档结构可保留 | 替换文档结构需附 v0 思想覆盖声明 |
| **数量** | 18 条（V8+） | 20 条（V0）|

---

## §B 时间线（V10 → V11，仓库可溯源 + V11 内部 patch 节点）

> **V7 / V8 / V9 ❓** — 仓库无可溯源 changelog。§A 轴心思想提及 V8+ 来源的 18 条命题；§V0 20 条基础命题无法溯源到具体版本。本节**仅整理 V10 → V11**（用户指令 2026-08-14）。

### §B.0 V10 → V11 快速摘要（一图速览）

| 版本 | 阶段数 | Article 数 | 核心增量 | 主要丢失 | 触发背景 |
|------|:---:|:---:|---------|---------|---------|
| **V10.1~10.3** | 7 阶段 | 14 | 流水线优化 + 5 维评分硬门禁 | 一刀切硬门禁（V10.5 后改软门禁） | 评分一致性争议 |
| **V10.4** | 7 + Phase 4.5 | 14 | rot-detector + proactive-scan.py（腐化可检测） | acceptance-audit `cargo test` 误报 | TDD 即时 + 视觉验证 |
| **V10.5** | 同上 | 16（+XII / XIII） | 文档诚实 + 骨架是债 | — | state-card 撒谎 |
| **V10.6** | 同上 | 16 | Evidence 独立抽检 | 主上下文工作量陡增 | 子代理自评失真 |
| **V10.8** | 同上 | 16 | 反虚假交付 + 严重度分层（P0/P1/P2/P4） | review-to-accept 不再单一 | 用户决策疲劳 |
| **V10.9** | 同上 | 16 | project-health-auditor + 防失真 4 机制 | — | 反复返工根因诊断 |
| **V10.10** | 7 + Phase 3.5 | 16（+XV / XVI） | 真实验证（5 项必跑）+ reason-classifier.py | reviewer 16 条铁律膨胀 | 防虚假交付根因 |
| **V10.11** | 同上 | 16 | 机械化门禁 + Bug 录入 6 字段 | 流程变重 | 主上下文自律条款 |
| **V10.12** | 同上 | 16 | 同类约定清单化 + 启动验证可见产物 | ≤10 铁律 + ≤150 行硬约束（**2026-08-14 已解除**） | 文档失忆 |
| **V11.0.0** | **13 stage** | 17（+XVII） | **高内聚专家架构**：-1 Intake → 7 Project Health + 24 脚本 + 8 模板 + 9 references | 66 处 V10 runtime 路径被替换；主上下文需读 14+ 文件 | 蒸馏式重构 |
| **V11.1** | 同上 | 17 | Article XVII Secret Redaction + §0.5.1 同类约定清单 | — | canvas-asset-folders 实战 |
| **V11.2** | 同上 | 17 | project-level ecosystem + Article V 强化（可验证声明硬约束） + prototype-backfill-check.py | — | canvas-asset-folders Stage 4 失败 |
| **V11.2.1** | 同上 | 17 | §3.7.2 可验证声明硬约束（追加 9 项禁止） + fidelity 等级（L1/L2/L3） | — | 视觉验证误判 |
| **V11.3** | 同上 | 17 | §3.7.3 灵活度铁律 8（人工判定覆盖）+ §8.4 工具-人类分层判定 + 5% 视觉差异阈值 | 20% 视觉差异阈值（→ 5%）+ research/ 目录（-39 文件）+ 53 个 V10 过渡产物 | canvas-asset-folders Stage 4 Round 1/2 |

### V10.1~10.3 — 流水线优化 + 5 维评分硬门禁

- 📈 4 → 5 维度（+ artifact_schema）
- 📈 acceptance-audit.py 实跑机械验证
- 📈 V10.3.7 drift_detect 第 6 维度
- 📉 5 维度硬门禁（任一 < PASS = REJECT）一刀切

### V10.4 — 腐化可检测

- 📈 rot-detector agent
- 📈 proactive-scan.py（5 项腐化扫描）
- 📈 4 条新 Article：IX TDD 即时 / X 异会话验证 / XI 视觉真实验证 / XIV rot-detector 必跑
- 📈 self-diagnose / orphan-detector / dist-hash-check / visual-content-check
- 📈 Phase 4.5 Proactive Rot Scan
- 📉 acceptance-audit.py `cargo test` regex 多次修补误报

### V10.5 — 文档诚实

- 📈 2 条新 Article：XII 文档诚实 / XIII 骨架是债
- 📈 3 项腐化扫描：self-aggrandizing-doc / state-card-staleness / stub-pileup
- 📈 rot-reinforcer Cycle 1

### V10.6 — Evidence 独立抽检

- 📈 主上下文亲自验证子代理 evidence
- 📈 禁止依赖清单（意图声明 / 部分进度 / 之前记忆 / 推测性答案 / 代理解释）
- 📉 主上下文工作量陡增

### V10.8 — 反虚假交付 + 严重度分层

- 📈 反踩坑 6 条铁律
- 📈 破坏性操作 4 步协议（reset-and-verify-protocol）
- 📈 严重度分层 P0/P1/P2/P4
- 📈 小任务流线化门禁（≤6 Task + LOW 可跳过 Contract）
- 📈 通过依据 3 类分层
- 📈 bug-workflow.md（19 方法论吸收）
- 📉 review-to-accept 不再单一

### V10.9 — 项目健康度 + 防失真

- 📈 project-health-auditor agent
- 📈 模板覆盖机制（3 层栈）
- 📈 技能包自身腐败治理（19 处修正）
- 📈 防失真 4 大机制（加载协议 / AskUserQuestion 反模式 / 必读清单 / 反复返工根因诊断）

### V10.10 — 真实验证（防虚假交付根因）

- 📈 2 条 Article：XV 障碍诚实 / XVI 禁止编造抽象理由
- 📈 Phase 3.5 真实验证（5 项必跑）
- 📈 §0.10 启动验证硬约束
- 📈 §3.7 反虚假交付禁止项
- 📈 reason-classifier.py 6 类抽象理由检测
- 📈 proactive-scan.py +2 项（obstacle-honesty + reason-fabrication）
- 📉 Agent 规则膨胀（reviewer.md 16 条铁律触发 §11 临时放宽）

### V10.11 — 机械化门禁 + Bug 录入

- 📈 phase-gate.py --verify-rot-scan
- 📈 §1.6 主上下文自律条款（delegation_skipped_reason + skipped_agents）
- 📈 process-doc-locations.md（fact/process/log 三层）
- 📈 Phase B.0 Bug 录入 6 字段
- 📉 流程变重（先跑机械门禁再 review）

### V10.12 — 同类约定清单化 + 启动验证硬约束

- 📈 §0.5.1 同类约定 10 项强制清单
- 📈 §0.10 启动验证可见产物（5 类项目分别定义产物）
- 📈 skeptical-validation-protocol.md（4 维度质疑性校验）
- 📈 test-plan.md + §Step 2.4 前置门禁
- 📈 §Step 2.5 产品侧验收 + §Step 2.6 自动循环
- 📈 Agent 减肥回 10 条（SUITE 模式合并）
- 📉 AGENTS.md §11 例外条款被废弃
- 📉 引入 ≤10 铁律 + ≤150 行硬约束（**2026-08-14 已解除**）

### V11.0.0 — 高内聚专家架构

- 📈 13 stage skill（-1 Intake → 0 Plan → 0.5 Test Plan → 1 Spec → 1.5 Prototype → 2 Contract → 3 Implement → 3.5 Real Verify → 4 Review → 4.5 Rot Scan → 5 Accept + 6 Bug Fix + 7 Project Health）
- 📈 17 Articles 宪法（+Article XVII Secret Redaction，V11.1）
- 📈 24 个公共脚本 + 8 个公共模板 + 9 个公共 references
- 📈 3 层依赖配置（user-level / V11 / 项目级）
- 📈 独立部署（不依赖 V10 目录）
- 📉 全部 66 处 V10 runtime 路径被替换
- 📉 agent 文件 13 个分散在 skills/ 子目录，主上下文需读 14+ 文件才能完整理解

### V11.1 — Secret 红化 + 同类约定清单化

- 📈 Article XVII Secret Redaction（V11.0 已加编号）
- 📈 §0.5.1 同类约定 10 项强制清单（V10.12 引入，V11.1 强化）
- 📈 §1.6 主上下文自律条款（V10.11 引入，V11.1 内联到 SKILL.md）
- 📈 §3.7 反虚假交付禁止项（V10.10 引入，V11.1 扩展）
- 📈 [SKILL.md §1.6](../SKILL.md) — 主上下文禁读 + 子代理禁单方面修改（V10.11 引入，V11.1 内联）

### V11.2 — 项目级生态 + 可验证声明强化

- 📈 §14 项目级生态管理（init-from-zero.py Step 5 改造）
- 📈 §14.5 项目级 rules > V11 通用层优先级
- 📈 Article V V11.2.1 强化：可验证声明硬约束（追加 9 项禁止）
- 📈 [prototype-backfill-check.py](../scripts/prototype-backfill-check.py) — V11.2 NEW 原型双产物最低门禁

### V11.2.1 — 可验证声明硬约束 + Fidelity 等级

- 📈 §3.7.2 Article V 强化：9 项禁止项（V10.5 文档诚实的硬约束升级）
- 📈 Fidelity L1 / L2 / L3 等级（wireframe / mockup / pixel-perfect）
- 📈 20% 视觉差异阈值（**V11.3 改 5%**）

### V11.3 — 灵活度铁律 8 + 工具-人类分层判定

- 📈 §3.7.3 灵活度铁律 8 — 人工判定覆盖
- 📈 §8.2 prototype 演进（V11.3 NEW）— 实施期 prototype 调整协议
- 📈 §8.4 工具-人类分层判定（V11.3 NEW）
- 📈 5% 视觉差异阈值（V11.2 的 20% → V11.3 的 5%）
- 📈 [stage-physical-isolation.md](stage-physical-isolation.md) — 物理隔离规范
- 📈 stage-gate-pre-stage.sh — husky 式硬门禁
- 📉 删除 research/ 整个目录（-39 文件）
- 📉 删除 53 个 V10 过渡产物
- 📉 体积 -50%
- 📉 **承认 V11.0 蒸馏时留有 V10 残渣**

### V11.4~V11.5 — 文档整合期（2026-08-14 当前）

- 📈 文档 v7-to-v11-evolution.md §V0 思想档首次建立（20 条基础命题归档）
- 📈 V11 markdown 引用路径修正（126 个悬空链接全部清零，2026-08-14 收尾）
- 📈 §§ 编号规范统一（vibe-coding-standards v2.5 弹性引用）
- 📈 反例 §19-22 清单化（V11 §0.5.1 配合）
- 📈 阶段模板示例中的占位 endpoint / plan.md / spec.md 改为非链接说明
- 📉 移除 GitHub Actions（v11.4 评估为过度工程，依赖 husky 即可）
- 📉 V11 3 个 state-card 字段从 int 改 string（避免向后兼容债）
- 📉 移除 4 个 V10 `auto-test` 双 agent 比较脚本（实测误判率高）

### 未来版本（V12+ 占位）

> 任何 V12+ 升级需在本节追加 delta 段，并走 §E 维护协议。

---

## §C 沧海遗珠 — V11 已丢失但应恢复（已审）

| 项 | 原属版本 | 现状 | 修复决策 |
|----|---------|------|---------|
| **state-card >80 行强制重置** | V9 铁律 #9 | V11 仅"文档诚实"无阈值 | **不恢复**（与"vibe-coding-standards v2.5 弹性"冲突；用 state-card-validator.py 机械检查替代） |
| **_invalidated/ 屏蔽区协议**（agent 不可读） | V9.1 §3 第 19 项 | V11 无 | **不恢复**（V11 stage-physical-isolation.md 已替代，stage 切换时隔离而非读屏蔽） |
| **干净重置详细流程** | V9 铁律 #11 | V11 仅"连续回退 3 次升级用户" | **不恢复**（V10.8 reset-and-verify-protocol.md 4 步协议已替代） |
| **V10 → V11 迁移脚本** | V9.2 migrate-v8-to-v9.py 范式 | V11 无对应 | **已修复**（见 [scripts/upgrade-from-v10.py](../scripts/upgrade-from-v10.py)） |
| **V8 Completion Report 3 字段 → V10 4 字段** | V9.1 `agent`/`artifacts`/`status` | V11 仍 4 字段 | **不恢复**（4 字段版本演进合理） |
| **V8 AOP 移交自检（3 项自问清单）** | V9.1 | V10/V11 未内联 | **不恢复**（已并入 sub-agent-rules.md §5 移交自检） |
| **intake agent `dedup_result` 字段** | V9.1 | V11 无 | **不恢复**（V11 intake stage 已重写，去重逻辑在 §-1 路由） |
| **Evidence 独立抽检**（主上下文亲自 Read ≤50 行） | V10.6 §-1.5 D 段 | V11 references/-1.5 段已外置 | **不内联**（保留外置，但 §-1.5 机械验证协议应在 SKILL.md 头部引用） |
| **§11 AGENTS.md 例外条款** | V10.12.1 临时放宽到 ≤16 ≤250 | V10.12.2 减肥回 10 条 | **不恢复**（2026-08-14 已解除硬约束） |

> **维护提示**：未来若发现新的沧海遗珠，按本表格式追加，并标注修复决策（恢复 / 不恢复 / 不内联）。

---

## §D 已弃用 — 演进中被替换或废弃

| 项 | 替换为 | 弃用原因 |
|----|--------|---------|
| 5 维度硬门禁（任一 < PASS = REJECT） | 4 维评分 + evidence 抽检 | V10.5 之后改为软门禁 + 优先级分层 |
| ≤10 铁律 + ≤150 行硬约束 | vibe-coding-standards v2.5 弹性 100~350 行 | 2026-08-14 解除（机械守卫已删除硬编码） |
| Reviewer 16 条铁律临时例外 | 10 条 SUITE 合并 | V10.12.2 减肥回 10 |
| V10 acceptance-audit.py `cargo test` regex 误报 | 严格 `test result: ok. N passed; M failed` | V10.3.2 修补 |
| `aggrandizing` 等英文非正式词汇 | `self-aggrandizing-doc` | V10.5 重命名（已无情绪化词） |

---

## §E 维护协议（升级时强制走）

1. **升级前**：Read 本文件 §A「轴心思想」+ §B「时间线」，确认升级目标不与现有轴心冲突。
2. **升级中**：任何 Article / 反例 / 铁律新增必须：
   - 在本文件 §A 追加轴心思想行（如新增 Article）
   - 在本文件 §B 时间线追加 delta 段
   - 在 commit / PR message 引用 `Refs: references/v7-to-v11-evolution.md`
3. **升级后**：检查是否有"丢弃但应恢复"项（§C），按修复决策执行。
4. **情绪化词语检查**：所有 references/SKILL.md 新增文本必须用「理智、克制、精确」字词。**禁用**：「革命性」「革命」「无敌」「最强」「甩」「碾压」「N 倍」「惊人」等。
5. **质疑性校验**：任何 P0 / P1 修复或升级方案必走 [references/skeptical-validation-protocol.md](skeptical-validation-protocol.md) 4 维度。

---

*最后更新：2026-08-14（V11.3 后）— 升级 fullstack-skill-architect / V12 触发时同步维护*